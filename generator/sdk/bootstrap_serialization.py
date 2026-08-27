"""Closed, deterministic JSON interchange for Bootstrap SDK values."""

from __future__ import annotations

import json
from collections.abc import Mapping
from enum import Enum
from pathlib import Path
from typing import Never

from generator.core.bootstrap_apply import BootstrapApplyResult, BootstrapApplyStepResult
from generator.core.bootstrap_dry_run import BootstrapDryRunPreview, BootstrapDryRunStep
from generator.core.bootstrap_planning import BootstrapPlan, BootstrapStep, ExpectedEffect
from generator.core.bootstrap_validation import (
    BootstrapValidationFinding,
    BootstrapValidationResult,
)
from generator.core.models import GenerationResult, WriteResult, WriteStatus
from generator.sdk.bootstrap_runtime import (
    BootstrapSdkMode,
    BootstrapSdkRequest,
    BootstrapSdkResult,
)


class BootstrapSchemaVersion(str, Enum):
    """Identify the one accepted serialization schema."""

    V1_0 = "opl.bootstrap/1.0"


class BootstrapSerializationError(ValueError):
    """Report closed-schema encoding or decoding failure."""


_ENVELOPE_KEYS = frozenset({"schema", "document_type", "payload"})


def _path(value: Path | str) -> str:
    return str(value).replace("\\", "/")


def _thaw(value: object) -> object:
    if isinstance(value, Mapping):
        return {
            str(key): _thaw(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, tuple):
        if all(
            isinstance(item, tuple) and len(item) == 2 and isinstance(item[0], str)
            for item in value
        ):
            return {item[0]: _thaw(item[1]) for item in value}
        return [_thaw(item) for item in value]
    if value is None or isinstance(value, str | int | float | bool):
        return value
    raise BootstrapSerializationError(f"Unsupported frozen value: {type(value).__name__}")


def _effect(value: ExpectedEffect) -> dict[str, object]:
    return {"kind": value.kind, "target": _path(value.target), "metadata": _thaw(value.metadata)}


def _step(value: BootstrapStep) -> dict[str, object]:
    return {
        "step_id": value.step_id,
        "generator_id": value.generator_id,
        "normalized_inputs": _thaw(value.normalized_inputs),
        "expected_effects": [_effect(item) for item in value.expected_effects],
        "mutation_allowed": value.mutation_allowed,
    }


def _plan(value: BootstrapPlan) -> dict[str, object]:
    return {
        "normalized_intent": _thaw(value.normalized_intent),
        "steps": [_step(item) for item in value.steps],
        "expected_effects": [_effect(item) for item in value.expected_effects],
    }


def _preview(value: BootstrapDryRunPreview) -> dict[str, object]:
    return {
        "steps": [
            {
                "step_id": item.step_id,
                "generator_id": item.generator_id,
                "normalized_inputs": _thaw(item.normalized_inputs),
                "expected_effects": [_effect(effect) for effect in item.expected_effects],
                "mutation_would_occur": item.mutation_would_occur,
            }
            for item in value.steps
        ],
        "expected_effects": [_effect(item) for item in value.expected_effects],
    }


def _generation(value: GenerationResult) -> dict[str, object]:
    return {
        "generator_name": value.generator_name,
        "writes": [
            {"path": _path(item.path), "status": item.status.value} for item in value.writes
        ],
        "warnings": list(value.warnings),
        "dry_run": value.dry_run,
        "manifest_updated": value.manifest_updated,
    }


def _apply(value: BootstrapApplyResult) -> dict[str, object]:
    return {
        "completed_steps": [
            {
                "step_id": item.step_id,
                "generator_id": item.generator_id,
                "generation_result": _generation(item.generation_result),
            }
            for item in value.completed_steps
        ]
    }


def _validation(value: BootstrapValidationResult) -> dict[str, object]:
    return {
        "executed_check_ids": list(value.executed_check_ids),
        "findings": [
            {
                "check_id": item.check_id,
                "severity": item.severity,
                "message": item.message,
                "subject": item.subject,
            }
            for item in value.findings
        ],
    }


def _encode(document_type: str, payload: Mapping[str, object]) -> str:
    try:
        return json.dumps(
            {
                "schema": BootstrapSchemaVersion.V1_0.value,
                "document_type": document_type,
                "payload": dict(payload),
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise BootstrapSerializationError(str(exc)) from exc


def serialize_bootstrap_request(request: BootstrapSdkRequest) -> str:
    """Encode one supported immutable SDK request canonically."""
    if not isinstance(request, BootstrapSdkRequest):
        raise BootstrapSerializationError("Expected BootstrapSdkRequest")
    if request.validation_checks:
        raise BootstrapSerializationError("Plugin validation checks are not serializable")
    return _encode(
        "bootstrap-request",
        {
            "template_root": _path(request.template_root),
            "output_root": _path(request.output_root),
            "project_slug": request.project_slug,
            "values": _thaw(request.values),
            "mode": request.mode.value,
            "overwrite": request.overwrite,
        },
    )


def serialize_bootstrap_result(result: BootstrapSdkResult) -> str:
    """Encode authoritative SDK result evidence canonically."""
    if not isinstance(result, BootstrapSdkResult):
        raise BootstrapSerializationError("Expected BootstrapSdkResult")
    return _encode(
        "bootstrap-result",
        {
            "plan": _plan(result.plan),
            "preview": _preview(result.preview) if result.preview is not None else None,
            "apply_result": _apply(result.apply_result)
            if result.apply_result is not None
            else None,
            "validation_result": (
                _validation(result.validation_result)
                if result.validation_result is not None
                else None
            ),
        },
    )


def _constant(value: str) -> Never:
    raise BootstrapSerializationError(f"Non-finite JSON number is forbidden: {value}")


def _object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise BootstrapSerializationError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def _mapping(value: object, name: str) -> dict[str, object]:
    if not isinstance(value, dict):
        raise BootstrapSerializationError(f"{name} must be an object")
    return value


def _keys(value: Mapping[str, object], expected: set[str], name: str) -> None:
    actual = set(value)
    if actual != expected:
        missing = sorted(expected - actual)
        unknown = sorted(actual - expected)
        raise BootstrapSerializationError(
            f"{name} fields mismatch; missing={missing}, unknown={unknown}"
        )


def _list(value: object, name: str) -> list[object]:
    if not isinstance(value, list):
        raise BootstrapSerializationError(f"{name} must be an array")
    return value


def _string(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise BootstrapSerializationError(f"{name} must be a string")
    return value


def _boolean(value: object, name: str) -> bool:
    if not isinstance(value, bool):
        raise BootstrapSerializationError(f"{name} must be a boolean")
    return value


def _decode(text: str, document_type: str) -> dict[str, object]:
    if not isinstance(text, str):
        raise BootstrapSerializationError("Serialized document must be text")
    try:
        value = json.loads(text, object_pairs_hook=_object, parse_constant=_constant)
    except BootstrapSerializationError:
        raise
    except (TypeError, ValueError, json.JSONDecodeError) as exc:
        raise BootstrapSerializationError(str(exc)) from exc
    envelope = _mapping(value, "document")
    _keys(envelope, set(_ENVELOPE_KEYS), "document")
    if envelope["schema"] != BootstrapSchemaVersion.V1_0.value:
        raise BootstrapSerializationError("Unsupported bootstrap schema")
    if envelope["document_type"] != document_type:
        raise BootstrapSerializationError("Unexpected bootstrap document_type")
    return _mapping(envelope["payload"], "payload")


def deserialize_bootstrap_request(text: str) -> BootstrapSdkRequest:
    """Decode one request without invoking runtime or accessing filesystem state."""
    payload = _decode(text, "bootstrap-request")
    _keys(
        payload,
        {"template_root", "output_root", "project_slug", "values", "mode", "overwrite"},
        "request payload",
    )
    values = _mapping(payload["values"], "values")
    try:
        mode = BootstrapSdkMode(_string(payload["mode"], "mode"))
        return BootstrapSdkRequest(
            template_root=Path(_string(payload["template_root"], "template_root")),
            output_root=Path(_string(payload["output_root"], "output_root")),
            project_slug=_string(payload["project_slug"], "project_slug"),
            values=values,
            mode=mode,
            overwrite=_boolean(payload["overwrite"], "overwrite"),
        )
    except (TypeError, ValueError) as exc:
        raise BootstrapSerializationError(str(exc)) from exc


def _decode_effect(value: object) -> ExpectedEffect:
    item = _mapping(value, "effect")
    _keys(item, {"kind", "target", "metadata"}, "effect")
    return ExpectedEffect(
        kind=_string(item["kind"], "effect.kind"),
        target=_string(item["target"], "effect.target"),
        metadata=_mapping(item["metadata"], "effect.metadata"),
    )


def _decode_step(value: object) -> BootstrapStep:
    item = _mapping(value, "step")
    _keys(
        item,
        {"step_id", "generator_id", "normalized_inputs", "expected_effects", "mutation_allowed"},
        "step",
    )
    return BootstrapStep(
        step_id=_string(item["step_id"], "step.step_id"),
        generator_id=_string(item["generator_id"], "step.generator_id"),
        normalized_inputs=_mapping(item["normalized_inputs"], "step.normalized_inputs"),
        expected_effects=tuple(
            _decode_effect(effect)
            for effect in _list(item["expected_effects"], "step.expected_effects")
        ),
        mutation_allowed=_boolean(item["mutation_allowed"], "step.mutation_allowed"),
    )


def _decode_plan(value: object) -> BootstrapPlan:
    item = _mapping(value, "plan")
    _keys(item, {"normalized_intent", "steps", "expected_effects"}, "plan")
    return BootstrapPlan(
        normalized_intent=_mapping(item["normalized_intent"], "plan.normalized_intent"),
        steps=tuple(_decode_step(step) for step in _list(item["steps"], "plan.steps")),
        expected_effects=tuple(
            _decode_effect(effect)
            for effect in _list(item["expected_effects"], "plan.expected_effects")
        ),
    )


def _decode_preview(value: object) -> BootstrapDryRunPreview:
    item = _mapping(value, "preview")
    _keys(item, {"steps", "expected_effects"}, "preview")
    steps: list[BootstrapDryRunStep] = []
    for raw in _list(item["steps"], "preview.steps"):
        step = _mapping(raw, "preview step")
        _keys(
            step,
            {
                "step_id",
                "generator_id",
                "normalized_inputs",
                "expected_effects",
                "mutation_would_occur",
            },
            "preview step",
        )
        steps.append(
            BootstrapDryRunStep(
                step_id=_string(step["step_id"], "preview step.step_id"),
                generator_id=_string(step["generator_id"], "preview step.generator_id"),
                normalized_inputs=_mapping(
                    step["normalized_inputs"], "preview step.normalized_inputs"
                ),
                expected_effects=tuple(
                    _decode_effect(effect)
                    for effect in _list(step["expected_effects"], "preview step.expected_effects")
                ),
                mutation_would_occur=_boolean(
                    step["mutation_would_occur"], "preview step.mutation_would_occur"
                ),
            )
        )
    return BootstrapDryRunPreview(
        steps=tuple(steps),
        expected_effects=tuple(
            _decode_effect(effect)
            for effect in _list(item["expected_effects"], "preview.expected_effects")
        ),
    )


def _decode_generation(value: object) -> GenerationResult:
    item = _mapping(value, "generation result")
    _keys(
        item,
        {"generator_name", "writes", "warnings", "dry_run", "manifest_updated"},
        "generation result",
    )
    writes: list[WriteResult] = []
    for raw in _list(item["writes"], "generation result.writes"):
        write = _mapping(raw, "write")
        _keys(write, {"path", "status"}, "write")
        try:
            status = WriteStatus(_string(write["status"], "write.status"))
        except ValueError as exc:
            raise BootstrapSerializationError(str(exc)) from exc
        writes.append(WriteResult(path=Path(_string(write["path"], "write.path")), status=status))
    warnings = tuple(_string(value, "warning") for value in _list(item["warnings"], "warnings"))
    return GenerationResult(
        generator_name=_string(item["generator_name"], "generator_name"),
        writes=tuple(writes),
        warnings=warnings,
        dry_run=_boolean(item["dry_run"], "dry_run"),
        manifest_updated=_boolean(item["manifest_updated"], "manifest_updated"),
    )


def _decode_apply(value: object) -> BootstrapApplyResult:
    item = _mapping(value, "apply result")
    _keys(item, {"completed_steps"}, "apply result")
    steps: list[BootstrapApplyStepResult] = []
    for raw in _list(item["completed_steps"], "completed_steps"):
        step = _mapping(raw, "completed step")
        _keys(step, {"step_id", "generator_id", "generation_result"}, "completed step")
        steps.append(
            BootstrapApplyStepResult(
                step_id=_string(step["step_id"], "completed step.step_id"),
                generator_id=_string(step["generator_id"], "completed step.generator_id"),
                generation_result=_decode_generation(step["generation_result"]),
            )
        )
    return BootstrapApplyResult(completed_steps=tuple(steps))


def _decode_validation(value: object) -> BootstrapValidationResult:
    item = _mapping(value, "validation result")
    _keys(item, {"executed_check_ids", "findings"}, "validation result")
    findings: list[BootstrapValidationFinding] = []
    for raw in _list(item["findings"], "findings"):
        finding = _mapping(raw, "finding")
        _keys(finding, {"check_id", "severity", "message", "subject"}, "finding")
        subject = finding["subject"]
        if subject is not None and not isinstance(subject, str):
            raise BootstrapSerializationError("finding.subject must be a string or null")
        findings.append(
            BootstrapValidationFinding(
                check_id=_string(finding["check_id"], "finding.check_id"),
                severity=_string(finding["severity"], "finding.severity"),
                message=_string(finding["message"], "finding.message"),
                subject=subject,
            )
        )
    return BootstrapValidationResult(
        executed_check_ids=tuple(
            _string(value, "check id")
            for value in _list(item["executed_check_ids"], "executed_check_ids")
        ),
        findings=tuple(findings),
    )


def deserialize_bootstrap_result(text: str) -> BootstrapSdkResult:
    """Decode immutable evidence without executing any bootstrap phase."""
    payload = _decode(text, "bootstrap-result")
    _keys(payload, {"plan", "preview", "apply_result", "validation_result"}, "result payload")
    try:
        return BootstrapSdkResult(
            plan=_decode_plan(payload["plan"]),
            preview=_decode_preview(payload["preview"]) if payload["preview"] is not None else None,
            apply_result=_decode_apply(payload["apply_result"])
            if payload["apply_result"] is not None
            else None,
            validation_result=(
                _decode_validation(payload["validation_result"])
                if payload["validation_result"] is not None
                else None
            ),
        )
    except BootstrapSerializationError:
        raise
    except (TypeError, ValueError) as exc:
        raise BootstrapSerializationError(str(exc)) from exc


__all__ = [
    "BootstrapSchemaVersion",
    "BootstrapSerializationError",
    "deserialize_bootstrap_request",
    "deserialize_bootstrap_result",
    "serialize_bootstrap_request",
    "serialize_bootstrap_result",
]
