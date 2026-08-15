from __future__ import annotations

from generator.ai.models import AIRequest, AIResponse
from generator.ai.review import AIReviewFinding, AIReviewResult
from generator.ai.review_service import AIReviewService
from generator.ai.testing import FakeAIProvider


def _request() -> AIRequest:
    return AIRequest(
        task="courseware.review",
        instructions="Review the supplied courseware.",
        context={
            "course_id": "modern-java",
            "language": "zh-TW",
        },
        response_contract="courseware.review.v1",
    )


def _response() -> AIResponse:
    return AIResponse(
        content={
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
        },
        metadata={
            "provider": "fake",
            "model": "deterministic-test-model",
        },
    )


def test_review_returns_production_review_result() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    service = AIReviewService(
        provider=provider,
    )

    result = service.review(_request())

    assert isinstance(result, AIReviewResult)
    assert len(result.findings) == 2
    assert all(isinstance(finding, AIReviewFinding) for finding in result.findings)


def test_review_passes_request_to_provider_unchanged() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    service = AIReviewService(
        provider=provider,
    )
    request = _request()

    service.review(request)

    assert provider.requests == (request,)


def test_review_preserves_finding_order() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    service = AIReviewService(
        provider=provider,
    )

    result = service.review(_request())

    assert tuple(finding.category for finding in result.findings) == (
        "accuracy",
        "clarity",
    )


def test_review_is_deterministic_with_fake_provider() -> None:
    response = _response()

    first_result = AIReviewService(
        provider=FakeAIProvider(
            responses=(response,),
        ),
    ).review(_request())

    second_result = AIReviewService(
        provider=FakeAIProvider(
            responses=(response,),
        ),
    ).review(_request())

    assert first_result == second_result


def test_review_keeps_provider_metadata_out_of_result() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    service = AIReviewService(
        provider=provider,
    )

    result = service.review(_request())

    assert not hasattr(result, "provider")
    assert not hasattr(result, "model")
    assert not hasattr(result, "metadata")


def test_review_service_uses_injected_provider() -> None:
    first_response = _response()
    second_response = AIResponse(
        content={
            "findings": [
                {
                    "category": "style",
                    "severity": "info",
                    "message": "Style note.",
                    "recommendation": "Consider a shorter sentence.",
                }
            ]
        },
        metadata={"provider": "fake"},
    )

    first_service = AIReviewService(
        provider=FakeAIProvider(
            responses=(first_response,),
        ),
    )
    second_service = AIReviewService(
        provider=FakeAIProvider(
            responses=(second_response,),
        ),
    )

    first_result = first_service.review(_request())
    second_result = second_service.review(_request())

    assert first_result.findings[0].category == "accuracy"
    assert second_result.findings[0].category == "style"
