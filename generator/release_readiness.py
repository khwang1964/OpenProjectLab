"""Deterministic, offline release-readiness stability evaluation."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Any

from generator.release_automation import VerificationDocumentError

_REVISION = re.compile(r"[0-9a-f]{40}")


class StabilityOutcome(StrEnum):
    READY = "READY"
    BLOCKED = "BLOCKED"
    INDETERMINATE = "INDETERMINATE"


@dataclass(frozen=True, slots=True)
class ReleaseReadinessStabilitySnapshot:
    repository: str
    revision: str
    observed_revision: str
    required_checks_passed: bool
    focused_passed: int
    focused_failed: int
    regression_passed: int
    regression_failed: int
    coverage_percent: float
    coverage_threshold: float
    audit_chain_accepted: bool
    supported_surfaces: tuple[str, ...]
    known_limitations: tuple[str, ...]
    release_blockers: tuple[str, ...]
    collected_at: str


@dataclass(frozen=True, slots=True)
class ReleaseReadinessStabilityPolicy:
    repository: str
    revision: str
    required_surfaces: tuple[str, ...]


@dataclass(frozen=True, slots=True, order=True)
class StabilityFinding:
    path: str
    reason: str
    message: str


@dataclass(frozen=True, slots=True)
class StabilityEvaluation:
    outcome: StabilityOutcome
    findings: tuple[StabilityFinding, ...]


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise VerificationDocumentError(f"duplicate field: {key}")
        result[key] = value
    return result


def _object(document: str, fields: frozenset[str]) -> dict[str, Any]:
    try:
        value = json.loads(document, object_pairs_hook=_pairs)
    except (json.JSONDecodeError, TypeError) as error:
        raise VerificationDocumentError("document must be valid JSON") from error
    if not isinstance(value, dict):
        raise VerificationDocumentError("document must be one JSON object")
    unknown = set(value) - fields
    missing = fields - set(value)
    if unknown:
        raise VerificationDocumentError(f"unknown fields: {', '.join(sorted(unknown))}")
    if missing:
        raise VerificationDocumentError(f"missing fields: {', '.join(sorted(missing))}")
    return value


def _strings(value: Any, path: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise VerificationDocumentError(f"{path} must be an array of nonempty strings")
    result = tuple(value)
    if result != tuple(sorted(set(result))):
        raise VerificationDocumentError(f"{path} must be sorted and unique")
    return result


class ReleaseReadinessStabilitySnapshotCodec:
    FIELDS = frozenset(
        field.name for field in ReleaseReadinessStabilitySnapshot.__dataclass_fields__.values()
    )

    @classmethod
    def decode(cls, document: str) -> ReleaseReadinessStabilitySnapshot:
        value = _object(document, cls.FIELDS)
        for name in ("repository", "collected_at"):
            if not isinstance(value[name], str) or not value[name]:
                raise VerificationDocumentError(f"$.{name} must be a nonempty string")
        for name in ("revision", "observed_revision"):
            if not isinstance(value[name], str) or not _REVISION.fullmatch(value[name]):
                raise VerificationDocumentError(
                    f"$.{name} must be a 40-character lowercase revision"
                )
        for name in ("required_checks_passed", "audit_chain_accepted"):
            if type(value[name]) is not bool:
                raise VerificationDocumentError(f"$.{name} must be boolean")
        for name in ("focused_passed", "focused_failed", "regression_passed", "regression_failed"):
            if type(value[name]) is not int or value[name] < 0:
                raise VerificationDocumentError(f"$.{name} must be a nonnegative integer")
        for name in ("coverage_percent", "coverage_threshold"):
            if (
                type(value[name]) not in (int, float)
                or not math.isfinite(value[name])
                or not 0 <= value[name] <= 100
            ):
                raise VerificationDocumentError(f"$.{name} must be finite and between 0 and 100")
        if value["focused_failed"] and value["focused_passed"] == 0:
            raise VerificationDocumentError("contradictory focused-test evidence")
        value["supported_surfaces"] = _strings(value["supported_surfaces"], "$.supported_surfaces")
        value["known_limitations"] = _strings(value["known_limitations"], "$.known_limitations")
        value["release_blockers"] = _strings(value["release_blockers"], "$.release_blockers")
        return ReleaseReadinessStabilitySnapshot(**value)

    @staticmethod
    def encode(snapshot: ReleaseReadinessStabilitySnapshot) -> str:
        return json.dumps(
            {
                field: getattr(snapshot, field)
                for field in sorted(ReleaseReadinessStabilitySnapshotCodec.FIELDS)
            },
            sort_keys=True,
            separators=(",", ":"),
        )


class ReleaseReadinessStabilityPolicyCodec:
    FIELDS = frozenset(("repository", "revision", "required_surfaces"))

    @classmethod
    def decode(cls, document: str) -> ReleaseReadinessStabilityPolicy:
        value = _object(document, cls.FIELDS)
        if not isinstance(value["repository"], str) or not value["repository"]:
            raise VerificationDocumentError("$.repository must be a nonempty string")
        if not isinstance(value["revision"], str) or not _REVISION.fullmatch(value["revision"]):
            raise VerificationDocumentError("$.revision must be a 40-character lowercase revision")
        return ReleaseReadinessStabilityPolicy(
            value["repository"],
            value["revision"],
            _strings(value["required_surfaces"], "$.required_surfaces"),
        )


class ReleaseReadinessStabilityEvaluator:
    @staticmethod
    def evaluate(
        snapshot: ReleaseReadinessStabilitySnapshot, policy: ReleaseReadinessStabilityPolicy
    ) -> StabilityEvaluation:
        findings: list[StabilityFinding] = []
        indeterminate = False

        def add(path: str, reason: str, message: str, uncertain: bool = False) -> None:
            nonlocal indeterminate
            findings.append(StabilityFinding(path, reason, message))
            indeterminate = indeterminate or uncertain

        if snapshot.repository != policy.repository:
            add(
                "$.repository",
                "REPOSITORY_MISMATCH",
                "repository identity does not match policy",
                True,
            )
        if snapshot.revision != policy.revision or snapshot.observed_revision != policy.revision:
            add(
                "$.revision",
                "REVISION_MISMATCH",
                "evidence is not bound to the policy revision",
                True,
            )
        if not snapshot.required_checks_passed:
            add(
                "$.required_checks_passed", "REQUIRED_CHECKS_FAILED", "required checks did not pass"
            )
        if snapshot.focused_failed or snapshot.focused_passed == 0:
            add(
                "$.focused_failed",
                "FOCUSED_TESTS_FAILED",
                "focused tests did not establish readiness",
            )
        if snapshot.regression_failed or snapshot.regression_passed == 0:
            add(
                "$.regression_failed",
                "REGRESSION_FAILED",
                "full regression did not establish readiness",
            )
        if snapshot.coverage_percent < snapshot.coverage_threshold:
            add(
                "$.coverage_percent",
                "COVERAGE_BELOW_THRESHOLD",
                "coverage is below its recorded threshold",
            )
        if not snapshot.audit_chain_accepted:
            add("$.audit_chain_accepted", "AUDIT_CHAIN_NOT_ACCEPTED", "audit chain is not accepted")
        missing = sorted(set(policy.required_surfaces) - set(snapshot.supported_surfaces))
        if missing:
            add("$.supported_surfaces", "SUPPORTED_SURFACE_MISSING", ", ".join(missing), True)
        if snapshot.release_blockers:
            add("$.release_blockers", "RELEASE_BLOCKER", ", ".join(snapshot.release_blockers))
        ordered = tuple(sorted(findings))
        outcome = StabilityOutcome.READY
        if ordered:
            outcome = StabilityOutcome.INDETERMINATE if indeterminate else StabilityOutcome.BLOCKED
        return StabilityEvaluation(outcome, ordered)


class StabilityEvaluationRenderer:
    @staticmethod
    def to_json(evaluation: StabilityEvaluation) -> str:
        return (
            json.dumps(
                {
                    "findings": [
                        {"message": f.message, "path": f.path, "reason": f.reason}
                        for f in evaluation.findings
                    ],
                    "outcome": evaluation.outcome,
                },
                sort_keys=True,
                separators=(",", ":"),
            )
            + "\n"
        )

    @staticmethod
    def to_text(evaluation: StabilityEvaluation) -> str:
        lines = [f"outcome: {evaluation.outcome}"]
        lines.extend(f"{f.path}: {f.reason}: {f.message}" for f in evaluation.findings)
        return "\n".join(lines) + "\n"
