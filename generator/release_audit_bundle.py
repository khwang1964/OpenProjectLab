from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from generator.release_automation import (
    VerificationDocumentError,
    VerificationReportCodec,
    VerificationReportEncoder,
    VerificationRequestCodec,
    VerificationRequestEncoder,
)

SCHEMA_VERSION = "1"


class AuditBundleCompatibilityCategory(StrEnum):
    CURRENT = "CURRENT"
    MIGRATABLE = "MIGRATABLE"
    FUTURE = "FUTURE"
    UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True, slots=True, order=True)
class AuditBundleMigrationEdge:
    source_schema: str
    target_schema: str
    step: str


@dataclass(frozen=True, slots=True)
class AuditBundleSchemaCompatibility:
    observed_schema: str
    current_schema: str
    category: AuditBundleCompatibilityCategory
    migration_steps: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AuditBundleMigrationPlan:
    source_schema: str
    target_schema: str
    steps: tuple[str, ...]
    preview_fingerprint: str


@dataclass(frozen=True, slots=True)
class AuditBundleMigrationRequest:
    source_sha256: str
    target_schema: str
    preview_fingerprint: str
    distinct_output: bool


@dataclass(frozen=True, slots=True)
class AuditBundleMigrationResult:
    source_schema: str
    target_schema: str
    steps: tuple[str, ...]
    output_document: str
    output_sha256: str
    receipt: str


@dataclass(frozen=True, slots=True)
class AuditBundleMigrationReceipt:
    source_schema: str
    target_schema: str
    steps: tuple[str, ...]
    source_sha256: str
    output_sha256: str
    plan_fingerprint: str


@dataclass(frozen=True, slots=True, order=True)
class AuditBundleMigrationReceiptFinding:
    path: str
    message: str


@dataclass(frozen=True, slots=True)
class AuditBundleMigrationReceiptVerification:
    findings: tuple[AuditBundleMigrationReceiptFinding, ...]

    @property
    def is_valid(self) -> bool:
        return not self.findings


class AuditBundleMigrationError(ValueError):
    """A stable, user-visible migration-planning failure."""


@dataclass(frozen=True, slots=True)
class AuditBundleSchemaRegistry:
    current_schema: str
    supported_schemas: tuple[str, ...]
    future_schemas: tuple[str, ...] = ()
    migration_edges: tuple[AuditBundleMigrationEdge, ...] = ()

    def __post_init__(self) -> None:
        if not self.current_schema:
            raise ValueError("current schema must be nonempty")
        if self.supported_schemas != tuple(sorted(set(self.supported_schemas))):
            raise ValueError("supported schemas must be sorted and unique")
        if self.future_schemas != tuple(sorted(set(self.future_schemas))):
            raise ValueError("future schemas must be sorted and unique")
        if self.current_schema not in self.supported_schemas:
            raise ValueError("current schema must be supported")
        if set(self.supported_schemas) & set(self.future_schemas):
            raise ValueError("supported and future schemas must be disjoint")
        if self.migration_edges != tuple(sorted(set(self.migration_edges))):
            raise ValueError("migration edges must be sorted and unique")
        for edge in self.migration_edges:
            if (
                not edge.source_schema
                or not edge.target_schema
                or not edge.step
                or edge.source_schema == edge.target_schema
            ):
                raise ValueError("migration edges must be explicit and non-reflexive")
            if edge.source_schema not in self.supported_schemas:
                raise ValueError("migration edge source must be supported")
            if edge.target_schema not in self.supported_schemas:
                raise ValueError("migration edge target must be supported")

    def _paths(self, source: str, target: str) -> tuple[tuple[AuditBundleMigrationEdge, ...], ...]:
        paths: list[tuple[AuditBundleMigrationEdge, ...]] = []

        def visit(
            schema: str,
            path: tuple[AuditBundleMigrationEdge, ...],
            visited: frozenset[str],
        ) -> None:
            if schema == target:
                paths.append(path)
                return
            for edge in self.migration_edges:
                if edge.source_schema == schema and edge.target_schema not in visited:
                    visit(edge.target_schema, path + (edge,), visited | {edge.target_schema})

        visit(source, (), frozenset({source}))
        return tuple(paths)

    def classify(self, observed_schema: str) -> AuditBundleSchemaCompatibility:
        if observed_schema == self.current_schema:
            category = AuditBundleCompatibilityCategory.CURRENT
            steps: tuple[str, ...] = ()
        elif observed_schema in self.future_schemas:
            category = AuditBundleCompatibilityCategory.FUTURE
            steps = ()
        elif observed_schema not in self.supported_schemas:
            category = AuditBundleCompatibilityCategory.UNSUPPORTED
            steps = ()
        else:
            paths = self._paths(observed_schema, self.current_schema)
            if len(paths) == 1:
                category = AuditBundleCompatibilityCategory.MIGRATABLE
                steps = tuple(edge.step for edge in paths[0])
            else:
                category = AuditBundleCompatibilityCategory.UNSUPPORTED
                steps = ()
        return AuditBundleSchemaCompatibility(
            observed_schema,
            self.current_schema,
            category,
            steps,
        )

    def plan(self, source_schema: str, target_schema: str) -> AuditBundleMigrationPlan:
        if target_schema not in self.supported_schemas:
            raise AuditBundleMigrationError("$.target_schema: unsupported target schema")
        if source_schema not in self.supported_schemas:
            raise AuditBundleMigrationError("$.source_schema: unsupported source schema")
        paths = self._paths(source_schema, target_schema)
        if not paths:
            raise AuditBundleMigrationError("$.migration: no explicit migration path")
        if len(paths) != 1:
            raise AuditBundleMigrationError("$.migration: ambiguous migration path")
        steps = tuple(edge.step for edge in paths[0])
        if not steps:
            raise AuditBundleMigrationError("$.migration: source already uses target schema")
        payload = json.dumps(
            {
                "source_schema": source_schema,
                "steps": list(steps),
                "target_schema": target_schema,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return AuditBundleMigrationPlan(source_schema, target_schema, steps, _sha256(payload))


DEFAULT_SCHEMA_REGISTRY = AuditBundleSchemaRegistry(
    current_schema=SCHEMA_VERSION,
    supported_schemas=("0", "1"),
    future_schemas=("2",),
    migration_edges=(AuditBundleMigrationEdge("0", "1", "upgrade-0-to-1"),),
)


def inspect_audit_bundle_schema(document: str) -> str:
    try:
        payload = json.loads(document, object_pairs_hook=_strict_object)
    except (json.JSONDecodeError, TypeError) as error:
        raise VerificationDocumentError("audit bundle is not valid JSON") from error
    if not isinstance(payload, dict) or not isinstance(payload.get("schema_version"), str):
        raise VerificationDocumentError("audit bundle schema_version must be a string")
    return payload["schema_version"]


def _upgrade_0_to_1(document: str) -> str:
    try:
        payload = json.loads(document, object_pairs_hook=_strict_object)
    except (json.JSONDecodeError, TypeError) as error:
        raise VerificationDocumentError("audit bundle is not valid JSON") from error
    if not isinstance(payload, dict) or payload.get("schema_version") != "0":
        raise AuditBundleMigrationError("$.schema_version: migration step requires schema 0")
    payload["schema_version"] = "1"
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _sha256(document: str) -> str:
    return hashlib.sha256(document.encode("utf-8")).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise VerificationDocumentError(f"duplicate field: {key}")
        result[key] = value
    return result


@dataclass(frozen=True, slots=True)
class VerificationAuditBundle:
    schema_version: str
    request_document: str
    report_document: str
    request_sha256: str
    report_sha256: str
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("unsupported audit-bundle schema version")
        for name, digest in (
            ("request_sha256", self.request_sha256),
            ("report_sha256", self.report_sha256),
        ):
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise ValueError(f"{name} must be 64 lowercase hexadecimal characters")
        if self.metadata != tuple(sorted(self.metadata)):
            raise ValueError("metadata must be sorted")
        keys = [key for key, _ in self.metadata]
        if len(keys) != len(set(keys)) or any(not key for key in keys):
            raise ValueError("metadata keys must be nonempty and unique")


class VerificationAuditBundleBuilder:
    @staticmethod
    def build(
        request_document: str, report_document: str, metadata: dict[str, str] | None = None
    ) -> VerificationAuditBundle:
        request = VerificationRequestCodec.decode(request_document)
        report = VerificationReportCodec.decode(report_document)
        canonical_request = VerificationRequestEncoder.encode(request)
        canonical_report = VerificationReportEncoder.encode(report)
        return VerificationAuditBundle(
            SCHEMA_VERSION,
            canonical_request,
            canonical_report,
            _sha256(canonical_request),
            _sha256(canonical_report),
            tuple(sorted((metadata or {}).items())),
        )


class VerificationAuditBundleCodec:
    _FIELDS = frozenset(
        {
            "schema_version",
            "request_document",
            "report_document",
            "request_sha256",
            "report_sha256",
            "metadata",
        }
    )

    @staticmethod
    def encode(bundle: VerificationAuditBundle) -> str:
        payload = {
            "metadata": dict(bundle.metadata),
            "report_document": bundle.report_document,
            "report_sha256": bundle.report_sha256,
            "request_document": bundle.request_document,
            "request_sha256": bundle.request_sha256,
            "schema_version": bundle.schema_version,
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @classmethod
    def decode(cls, document: str) -> VerificationAuditBundle:
        try:
            payload = json.loads(document, object_pairs_hook=_strict_object)
        except (json.JSONDecodeError, TypeError) as error:
            raise VerificationDocumentError("audit bundle is not valid JSON") from error
        if not isinstance(payload, dict) or set(payload) != cls._FIELDS:
            raise VerificationDocumentError("audit bundle fields do not match the schema")
        metadata = payload["metadata"]
        if not isinstance(metadata, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in metadata.items()
        ):
            raise VerificationDocumentError("audit bundle metadata must map strings to strings")
        try:
            bundle = VerificationAuditBundle(
                payload["schema_version"],
                payload["request_document"],
                payload["report_document"],
                payload["request_sha256"],
                payload["report_sha256"],
                tuple(sorted(metadata.items())),
            )
        except (TypeError, ValueError) as error:
            raise VerificationDocumentError(str(error)) from error
        if cls.encode(bundle) != document:
            raise VerificationDocumentError("audit bundle is not canonical JSON")
        return bundle


type AuditBundleMigrationStep = Callable[[str], str]
DEFAULT_MIGRATION_STEP_REGISTRY: tuple[tuple[str, AuditBundleMigrationStep], ...] = (
    ("upgrade-0-to-1", _upgrade_0_to_1),
)


class AuditBundleMigrationExecutor:
    @staticmethod
    def execute(
        request: AuditBundleMigrationRequest,
        source_document: str,
        *,
        schema_registry: AuditBundleSchemaRegistry = DEFAULT_SCHEMA_REGISTRY,
        step_registry: tuple[
            tuple[str, AuditBundleMigrationStep], ...
        ] = DEFAULT_MIGRATION_STEP_REGISTRY,
    ) -> AuditBundleMigrationResult:
        if not request.distinct_output:
            raise AuditBundleMigrationError("$.output: distinct output is required")
        if request.source_sha256 != _sha256(source_document):
            raise AuditBundleMigrationError("$.source_sha256: source identity mismatch")
        source_schema = inspect_audit_bundle_schema(source_document)
        plan = schema_registry.plan(source_schema, request.target_schema)
        if request.preview_fingerprint != plan.preview_fingerprint:
            raise AuditBundleMigrationError("$.preview_fingerprint: accepted plan mismatch")
        if step_registry != tuple(sorted(step_registry, key=lambda item: item[0])):
            raise AuditBundleMigrationError("$.steps: migration registry is not ordered")
        names = tuple(name for name, _ in step_registry)
        if len(names) != len(set(names)):
            raise AuditBundleMigrationError("$.steps: migration registry is ambiguous")
        handlers = dict(step_registry)
        output_document = source_document
        for step in plan.steps:
            handler = handlers.get(step)
            if handler is None:
                raise AuditBundleMigrationError(f"$.steps: unknown migration step: {step}")
            output_document = handler(output_document)
        try:
            output_bundle = VerificationAuditBundleCodec.decode(output_document)
        except VerificationDocumentError as error:
            raise AuditBundleMigrationError("$.migration: target verification failed") from error
        if output_bundle.schema_version != plan.target_schema:
            raise AuditBundleMigrationError("$.schema_version: target verification failed")
        output_sha256 = _sha256(output_document)
        receipt = json.dumps(
            {
                "output_sha256": output_sha256,
                "plan_fingerprint": plan.preview_fingerprint,
                "source_schema": plan.source_schema,
                "source_sha256": request.source_sha256,
                "steps": list(plan.steps),
                "target_schema": plan.target_schema,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        return AuditBundleMigrationResult(
            plan.source_schema,
            plan.target_schema,
            plan.steps,
            output_document,
            output_sha256,
            receipt,
        )


_MIGRATION_RECEIPT_FIELDS = frozenset(
    {
        "output_sha256",
        "plan_fingerprint",
        "source_schema",
        "source_sha256",
        "steps",
        "target_schema",
    }
)


def _require_sha256(value: object, path: str) -> str:
    if not isinstance(value, str) or len(value) != 64:
        raise VerificationDocumentError(f"{path}: expected a SHA-256 hex digest")
    try:
        int(value, 16)
    except ValueError as error:
        raise VerificationDocumentError(f"{path}: expected a SHA-256 hex digest") from error
    if value != value.lower():
        raise VerificationDocumentError(f"{path}: expected lowercase SHA-256 hex")
    return value


class AuditBundleMigrationReceiptCodec:
    @staticmethod
    def encode(receipt: AuditBundleMigrationReceipt) -> str:
        return json.dumps(
            {
                "output_sha256": receipt.output_sha256,
                "plan_fingerprint": receipt.plan_fingerprint,
                "source_schema": receipt.source_schema,
                "source_sha256": receipt.source_sha256,
                "steps": list(receipt.steps),
                "target_schema": receipt.target_schema,
            },
            sort_keys=True,
            separators=(",", ":"),
        )

    @classmethod
    def decode(cls, document: str) -> AuditBundleMigrationReceipt:
        try:
            payload = json.loads(document, object_pairs_hook=_strict_object)
        except (json.JSONDecodeError, TypeError) as error:
            raise VerificationDocumentError("migration receipt is not valid JSON") from error
        if not isinstance(payload, dict):
            raise VerificationDocumentError("migration receipt must be a JSON object")
        observed = frozenset(payload)
        if observed != _MIGRATION_RECEIPT_FIELDS:
            unknown = sorted(observed - _MIGRATION_RECEIPT_FIELDS)
            missing = sorted(_MIGRATION_RECEIPT_FIELDS - observed)
            detail = unknown[0] if unknown else missing[0]
            category = "unknown" if unknown else "missing"
            raise VerificationDocumentError(f"$.{detail}: {category} receipt field")
        schemas = (payload["source_schema"], payload["target_schema"])
        if not all(isinstance(item, str) and item for item in schemas):
            raise VerificationDocumentError("$.schema: expected nonempty schema identities")
        steps = payload["steps"]
        if not isinstance(steps, list) or not all(isinstance(item, str) and item for item in steps):
            raise VerificationDocumentError("$.steps: expected ordered nonempty strings")
        fingerprint = _require_sha256(payload["plan_fingerprint"], "$.plan_fingerprint")
        receipt = AuditBundleMigrationReceipt(
            payload["source_schema"],
            payload["target_schema"],
            tuple(steps),
            _require_sha256(payload["source_sha256"], "$.source_sha256"),
            _require_sha256(payload["output_sha256"], "$.output_sha256"),
            fingerprint,
        )
        if cls.encode(receipt) != document:
            raise VerificationDocumentError("migration receipt is not canonical JSON")
        return receipt


class AuditBundleMigrationReceiptVerifier:
    @staticmethod
    def verify(
        source_document: str,
        output_document: str,
        receipt_document: str,
        *,
        schema_registry: AuditBundleSchemaRegistry = DEFAULT_SCHEMA_REGISTRY,
    ) -> AuditBundleMigrationReceiptVerification:
        receipt = AuditBundleMigrationReceiptCodec.decode(receipt_document)
        source_schema = inspect_audit_bundle_schema(source_document)
        output_bundle = VerificationAuditBundleCodec.decode(output_document)
        plan = schema_registry.plan(source_schema, receipt.target_schema)
        observed = {
            "$.output_sha256": (_sha256(output_document), receipt.output_sha256),
            "$.plan_fingerprint": (plan.preview_fingerprint, receipt.plan_fingerprint),
            "$.source_schema": (source_schema, receipt.source_schema),
            "$.source_sha256": (_sha256(source_document), receipt.source_sha256),
            "$.steps": (plan.steps, receipt.steps),
            "$.target_schema": (output_bundle.schema_version, receipt.target_schema),
        }
        findings = tuple(
            AuditBundleMigrationReceiptFinding(path, "does not match observed migration")
            for path, (actual, recorded) in sorted(observed.items())
            if actual != recorded
        )
        return AuditBundleMigrationReceiptVerification(findings)


@dataclass(frozen=True, slots=True, order=True)
class VerificationAuditBundleFinding:
    path: str
    message: str


@dataclass(frozen=True, slots=True)
class VerificationAuditBundleValidation:
    findings: tuple[VerificationAuditBundleFinding, ...]

    @property
    def is_valid(self) -> bool:
        return not self.findings


class VerificationAuditBundleValidator:
    @staticmethod
    def validate(bundle: VerificationAuditBundle) -> VerificationAuditBundleValidation:
        findings: list[VerificationAuditBundleFinding] = []
        if _sha256(bundle.request_document) != bundle.request_sha256:
            findings.append(
                VerificationAuditBundleFinding(
                    "$.request_sha256", "does not match request_document"
                )
            )
        if _sha256(bundle.report_document) != bundle.report_sha256:
            findings.append(
                VerificationAuditBundleFinding("$.report_sha256", "does not match report_document")
            )
        for path, decoder, document in (
            ("$.request_document", VerificationRequestCodec.decode, bundle.request_document),
            ("$.report_document", VerificationReportCodec.decode, bundle.report_document),
        ):
            try:
                decoder(document)
            except VerificationDocumentError as error:
                findings.append(VerificationAuditBundleFinding(path, str(error)))
        return VerificationAuditBundleValidation(tuple(sorted(findings)))


class VerificationAuditBundleRenderer:
    @staticmethod
    def to_json(
        bundle: VerificationAuditBundle, validation: VerificationAuditBundleValidation | None = None
    ) -> str:
        payload: dict[str, Any] = {
            "metadata": dict(bundle.metadata),
            "report_sha256": bundle.report_sha256,
            "request_sha256": bundle.request_sha256,
            "schema_version": bundle.schema_version,
        }
        if validation is not None:
            payload["findings"] = [
                {"message": item.message, "path": item.path} for item in validation.findings
            ]
            payload["valid"] = validation.is_valid
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def to_text(
        bundle: VerificationAuditBundle, validation: VerificationAuditBundleValidation | None = None
    ) -> str:
        lines = [
            f"schema: {bundle.schema_version}",
            f"request: sha256:{bundle.request_sha256}",
            f"report: sha256:{bundle.report_sha256}",
        ]
        if validation is not None:
            lines.append(f"valid: {str(validation.is_valid).lower()}")
            lines.extend(f"{item.path}: {item.message}" for item in validation.findings)
        return "\n".join(lines)
