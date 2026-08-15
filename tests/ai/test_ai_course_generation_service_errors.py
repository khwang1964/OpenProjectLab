from __future__ import annotations

import pytest

from generator.ai.errors import AIResponseValidationError
from generator.ai.models import AIRequest, AIResponse
from generator.ai.service import AICourseGenerationService
from generator.ai.testing import FakeAIProvider


def _request() -> AIRequest:
    return AIRequest(
        task="courseware.generate",
        instructions="Generate a structured course.",
        context={"course_id": "modern-java"},
        response_contract="courseware.course.v1",
    )


def test_generate_course_propagates_provider_failure() -> None:
    provider = FakeAIProvider(
        failures=(RuntimeError("simulated provider failure"),),
    )
    service = AICourseGenerationService(
        provider=provider,
    )

    with pytest.raises(
        RuntimeError,
        match="simulated provider failure",
    ):
        service.generate_course(_request())


def test_generate_course_propagates_response_validation_failure() -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content=None,
                metadata={"provider": "fake"},
            ),
        ),
    )
    service = AICourseGenerationService(
        provider=provider,
    )

    with pytest.raises(AIResponseValidationError):
        service.generate_course(_request())


def test_generate_course_propagates_missing_field_validation_failure() -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content={
                    "course_id": "modern-java",
                    "title": "Modern Java",
                    "language": "zh-TW",
                },
                metadata={"provider": "fake"},
            ),
        ),
    )
    service = AICourseGenerationService(
        provider=provider,
    )

    with pytest.raises(
        AIResponseValidationError,
        match="weeks",
    ):
        service.generate_course(_request())


def test_generate_course_preserves_domain_validation_failure() -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content={
                    "course_id": "modern-java",
                    "title": "Modern Java",
                    "language": "zh-TW",
                    "weeks": [
                        {
                            "number": 0,
                            "title": "Invalid Week",
                        }
                    ],
                },
                metadata={"provider": "fake"},
            ),
        ),
    )
    service = AICourseGenerationService(
        provider=provider,
    )

    with pytest.raises(ValueError):
        service.generate_course(_request())


def test_generate_course_preserves_duplicate_week_domain_failure() -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content={
                    "course_id": "modern-java",
                    "title": "Modern Java",
                    "language": "zh-TW",
                    "weeks": [
                        {
                            "number": 1,
                            "title": "First",
                        },
                        {
                            "number": 1,
                            "title": "Duplicate",
                        },
                    ],
                },
                metadata={"provider": "fake"},
            ),
        ),
    )
    service = AICourseGenerationService(
        provider=provider,
    )

    with pytest.raises(ValueError):
        service.generate_course(_request())


def test_generate_course_failure_has_no_filesystem_side_effect(
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
    service = AICourseGenerationService(
        provider=provider,
    )

    with pytest.raises(AIResponseValidationError):
        service.generate_course(_request())

    assert list(tmp_path.iterdir()) == []


def test_provider_failure_records_request_before_raising() -> None:
    provider = FakeAIProvider(
        failures=(RuntimeError("simulated provider failure"),),
    )
    service = AICourseGenerationService(
        provider=provider,
    )
    request = _request()

    with pytest.raises(RuntimeError):
        service.generate_course(request)

    assert provider.requests == (request,)
