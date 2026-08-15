from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from generator.ai.course_builder import (
    AICourseBuilder,
    AICourseBuildRequest,
)
from generator.ai.models import AIResponse
from generator.ai.testing import FakeAIProvider
from generator.courseware.models import Course, Week


def _build_request() -> AICourseBuildRequest:
    return AICourseBuildRequest(
        course_id="modern-java",
        title="Modern Java",
        language="zh-TW",
        objectives=(
            "Understand modern Java language features.",
            "Apply streams and functional programming.",
        ),
        week_count=2,
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


def test_course_build_request_is_immutable() -> None:
    request = _build_request()

    with pytest.raises(FrozenInstanceError):
        request.title = "Changed"  # type: ignore[misc]


def test_course_build_request_preserves_objective_order() -> None:
    request = _build_request()

    assert request.objectives == (
        "Understand modern Java language features.",
        "Apply streams and functional programming.",
    )


def test_build_returns_production_course() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    builder = AICourseBuilder(
        provider=provider,
    )

    course = builder.build(_build_request())

    assert isinstance(course, Course)
    assert course.course_id == "modern-java"
    assert course.title == "Modern Java"
    assert course.language == "zh-TW"


def test_build_returns_production_weeks_in_deterministic_order() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    builder = AICourseBuilder(
        provider=provider,
    )

    course = builder.build(_build_request())

    assert all(isinstance(week, Week) for week in course.weeks)
    assert tuple(week.number for week in course.weeks) == (1, 2)


def test_builder_creates_provider_request_from_course_build_request() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    builder = AICourseBuilder(
        provider=provider,
    )
    request = _build_request()

    builder.build(request)

    assert len(provider.requests) == 1

    ai_request = provider.requests[0]

    assert ai_request.task == "courseware.build"
    assert ai_request.response_contract == "courseware.course.v1"
    assert ai_request.context == {
        "course_id": "modern-java",
        "title": "Modern Java",
        "language": "zh-TW",
        "objectives": (
            "Understand modern Java language features.",
            "Apply streams and functional programming.",
        ),
        "week_count": 2,
    }


def test_builder_request_instructions_are_provider_independent() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    builder = AICourseBuilder(
        provider=provider,
    )

    builder.build(_build_request())

    ai_request = provider.requests[0]

    assert "course" in ai_request.instructions.lower()
    assert "week" in ai_request.instructions.lower()
    assert "openai" not in ai_request.instructions.lower()
    assert "anthropic" not in ai_request.instructions.lower()
    assert "gemini" not in ai_request.instructions.lower()


def test_build_is_deterministic_with_fake_provider() -> None:
    response = _response()

    first = AICourseBuilder(
        provider=FakeAIProvider(
            responses=(response,),
        ),
    ).build(_build_request())

    second = AICourseBuilder(
        provider=FakeAIProvider(
            responses=(response,),
        ),
    ).build(_build_request())

    assert first == second


def test_build_keeps_provider_metadata_out_of_course_domain() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    builder = AICourseBuilder(
        provider=provider,
    )

    course = builder.build(_build_request())

    assert not hasattr(course, "provider")
    assert not hasattr(course, "model")
    assert not hasattr(course, "metadata")
