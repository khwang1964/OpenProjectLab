from __future__ import annotations

import pytest

from generator.ai.errors import AIResponseValidationError
from generator.ai.models import AIRequest, AIResponse
from generator.ai.review_service import AIReviewService
from generator.ai.testing import FakeAIProvider


def _request() -> AIRequest:
    return AIRequest(
        task="courseware.review",
        instructions="Review the supplied courseware.",
        context={"course_id": "modern-java"},
        response_contract="courseware.review.v1",
    )


def test_review_propagates_provider_failure() -> None:
    provider = FakeAIProvider(
        failures=(RuntimeError("simulated provider failure"),),
    )
    service = AIReviewService(
        provider=provider,
    )

    with pytest.raises(
        RuntimeError,
        match="simulated provider failure",
    ):
        service.review(_request())


def test_review_propagates_response_validation_failure() -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content=None,
                metadata={"provider": "fake"},
            ),
        ),
    )
    service = AIReviewService(
        provider=provider,
    )

    with pytest.raises(AIResponseValidationError):
        service.review(_request())


def test_review_propagates_missing_findings_failure() -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content={},
                metadata={"provider": "fake"},
            ),
        ),
    )
    service = AIReviewService(
        provider=provider,
    )

    with pytest.raises(
        AIResponseValidationError,
        match="findings",
    ):
        service.review(_request())


def test_review_propagates_invalid_severity_failure() -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content={
                    "findings": [
                        {
                            "category": "clarity",
                            "severity": "critical",
                            "message": "Ambiguous wording.",
                            "recommendation": "Clarify the wording.",
                        }
                    ]
                },
                metadata={"provider": "fake"},
            ),
        ),
    )
    service = AIReviewService(
        provider=provider,
    )

    with pytest.raises(
        AIResponseValidationError,
        match="severity",
    ):
        service.review(_request())


def test_provider_failure_records_request_before_raising() -> None:
    provider = FakeAIProvider(
        failures=(RuntimeError("simulated provider failure"),),
    )
    service = AIReviewService(
        provider=provider,
    )
    request = _request()

    with pytest.raises(RuntimeError):
        service.review(request)

    assert provider.requests == (request,)


def test_review_failure_has_no_filesystem_side_effect(
    tmp_path,
) -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content=None,
                metadata={"provider": "fake"},
            ),
        ),
    )
    service = AIReviewService(
        provider=provider,
    )

    with pytest.raises(AIResponseValidationError):
        service.review(_request())

    assert list(tmp_path.iterdir()) == []
