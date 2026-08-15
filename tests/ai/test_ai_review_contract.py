from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from generator.ai.models import AIResponse
from generator.ai.review import (
    AIReviewFinding,
    AIReviewResult,
    map_review_response,
)


def _response(content: object) -> AIResponse:
    return AIResponse(
        content=content,
        metadata={
            "provider": "fake",
            "model": "deterministic-test-model",
        },
    )


def test_map_review_response_builds_review_result() -> None:
    response = _response(
        {
            "findings": [
                {
                    "category": "accuracy",
                    "severity": "error",
                    "message": "The example contains an incorrect claim.",
                    "recommendation": "Correct the example before publication.",
                },
                {
                    "category": "clarity",
                    "severity": "warning",
                    "message": "The explanation is difficult to follow.",
                    "recommendation": "Add a shorter introductory explanation.",
                },
            ]
        }
    )

    result = map_review_response(response)

    assert isinstance(result, AIReviewResult)
    assert len(result.findings) == 2
    assert all(isinstance(item, AIReviewFinding) for item in result.findings)


def test_review_finding_preserves_structured_fields() -> None:
    response = _response(
        {
            "findings": [
                {
                    "category": "clarity",
                    "severity": "warning",
                    "message": "The explanation is ambiguous.",
                    "recommendation": "Clarify the terminology.",
                }
            ]
        }
    )

    result = map_review_response(response)
    finding = result.findings[0]

    assert finding.category == "clarity"
    assert finding.severity == "warning"
    assert finding.message == "The explanation is ambiguous."
    assert finding.recommendation == "Clarify the terminology."


def test_review_finding_order_is_deterministic() -> None:
    response = _response(
        {
            "findings": [
                {
                    "category": "first",
                    "severity": "info",
                    "message": "First finding.",
                    "recommendation": "First recommendation.",
                },
                {
                    "category": "second",
                    "severity": "warning",
                    "message": "Second finding.",
                    "recommendation": "Second recommendation.",
                },
            ]
        }
    )

    result = map_review_response(response)

    assert tuple(item.category for item in result.findings) == (
        "first",
        "second",
    )


def test_review_result_keeps_provider_metadata_outside_review_model() -> None:
    response = _response({"findings": []})

    result = map_review_response(response)

    assert not hasattr(result, "provider")
    assert not hasattr(result, "model")
    assert not hasattr(result, "metadata")


def test_review_result_and_findings_are_immutable() -> None:
    result = AIReviewResult(
        findings=(
            AIReviewFinding(
                category="clarity",
                severity="warning",
                message="Ambiguous wording.",
                recommendation="Clarify the wording.",
            ),
        )
    )

    with pytest.raises(FrozenInstanceError):
        result.findings = ()  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        result.findings[0].message = "Changed"  # type: ignore[misc]


def test_map_review_response_does_not_mutate_ai_response() -> None:
    content = {
        "findings": [
            {
                "category": "clarity",
                "severity": "warning",
                "message": "Ambiguous wording.",
                "recommendation": "Clarify the wording.",
            }
        ]
    }
    response = _response(content)

    result = map_review_response(response)

    assert len(result.findings) == 1
    assert response.content is content
    assert response.content == content
