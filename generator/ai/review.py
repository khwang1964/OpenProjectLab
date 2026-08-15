"""Structured AI review models and response mapping."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from .errors import AIResponseValidationError
from .models import AIResponse
from .validation import validate_response_mapping

_ALLOWED_SEVERITIES = frozenset(
    {
        "info",
        "warning",
        "error",
    }
)


@dataclass(frozen=True, slots=True)
class AIReviewFinding:
    """Represent one structured advisory finding produced by AI review."""

    category: str
    severity: str
    message: str
    recommendation: str


@dataclass(frozen=True, slots=True)
class AIReviewResult:
    """Represent an ordered immutable collection of AI review findings."""

    findings: tuple[AIReviewFinding, ...]


def map_review_response(
    response: AIResponse,
) -> AIReviewResult:
    """Map a structured AI response into an immutable review result."""
    content = validate_response_mapping(
        response,
        required_fields={
            "findings": list,
        },
    )

    findings = tuple(
        _map_finding(
            value,
            index=index,
        )
        for index, value in enumerate(content["findings"])
    )

    return AIReviewResult(
        findings=findings,
    )


def _map_finding(
    value: object,
    *,
    index: int,
) -> AIReviewFinding:
    if not isinstance(value, Mapping):
        raise AIResponseValidationError(f"AI review finding at index {index} must be a mapping.")

    required_fields = (
        "category",
        "severity",
        "message",
        "recommendation",
    )

    for field in required_fields:
        if field not in value:
            raise AIResponseValidationError(
                f"AI review finding at index {index} is missing required field: {field}"
            )

        if not isinstance(value[field], str):
            raise AIResponseValidationError(
                f"AI review finding field {field!r} at index {index} must be of type str."
            )

    severity = value["severity"]

    if severity not in _ALLOWED_SEVERITIES:
        raise AIResponseValidationError(
            "AI review finding field 'severity' "
            f"at index {index} must be one of: "
            f"{', '.join(sorted(_ALLOWED_SEVERITIES))}."
        )

    return AIReviewFinding(
        category=value["category"],
        severity=severity,
        message=value["message"],
        recommendation=value["recommendation"],
    )
