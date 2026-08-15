from __future__ import annotations

from generator.ai.models import AIRequest, AIResponse
from generator.ai.service import AICourseGenerationService
from generator.ai.testing import FakeAIProvider
from generator.courseware.models import Course, Week


def _request() -> AIRequest:
    return AIRequest(
        task="courseware.generate",
        instructions="Generate a structured course.",
        context={
            "course_id": "modern-java",
            "language": "zh-TW",
        },
        response_contract="courseware.course.v1",
    )


def _response() -> AIResponse:
    return AIResponse(
        content={
            "course_id": "modern-java",
            "title": "Modern Java",
            "language": "zh-TW",
            "weeks": [
                {
                    "number": 2,
                    "title": "Streams",
                },
                {
                    "number": 1,
                    "title": "Lambda Expressions",
                },
            ],
        },
        metadata={
            "provider": "fake",
            "model": "deterministic-test-model",
        },
    )


def test_generate_course_returns_production_course() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    service = AICourseGenerationService(
        provider=provider,
    )

    course = service.generate_course(_request())

    assert isinstance(course, Course)
    assert course.course_id == "modern-java"
    assert course.title == "Modern Java"
    assert course.language == "zh-TW"


def test_generate_course_builds_production_weeks() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    service = AICourseGenerationService(
        provider=provider,
    )

    course = service.generate_course(_request())

    assert all(isinstance(week, Week) for week in course.weeks)
    assert tuple(week.number for week in course.weeks) == (1, 2)


def test_generate_course_passes_request_to_provider_unchanged() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    service = AICourseGenerationService(
        provider=provider,
    )
    request = _request()

    service.generate_course(request)

    assert provider.requests == (request,)


def test_generate_course_is_deterministic_with_fake_provider() -> None:
    response = _response()
    first_provider = FakeAIProvider(
        responses=(response,),
    )
    second_provider = FakeAIProvider(
        responses=(response,),
    )

    first_course = AICourseGenerationService(
        provider=first_provider,
    ).generate_course(_request())
    second_course = AICourseGenerationService(
        provider=second_provider,
    ).generate_course(_request())

    assert first_course == second_course


def test_generate_course_keeps_provider_metadata_out_of_domain() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    service = AICourseGenerationService(
        provider=provider,
    )

    course = service.generate_course(_request())

    assert not hasattr(course, "provider")
    assert not hasattr(course, "model")
    assert not hasattr(course, "metadata")


def test_service_uses_injected_provider() -> None:
    first_response = _response()
    second_response = AIResponse(
        content={
            "course_id": "different-course",
            "title": "Different Course",
            "language": "en",
            "weeks": [],
        },
        metadata={"provider": "fake"},
    )

    first_service = AICourseGenerationService(
        provider=FakeAIProvider(
            responses=(first_response,),
        ),
    )
    second_service = AICourseGenerationService(
        provider=FakeAIProvider(
            responses=(second_response,),
        ),
    )

    assert first_service.generate_course(_request()).course_id == "modern-java"
    assert second_service.generate_course(_request()).course_id == "different-course"
