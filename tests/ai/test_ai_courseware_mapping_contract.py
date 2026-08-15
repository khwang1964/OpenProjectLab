from __future__ import annotations

from generator.ai.courseware import map_course_response
from generator.ai.models import AIResponse
from generator.courseware.models import Course, Week


def _response(content: object) -> AIResponse:
    return AIResponse(
        content=content,
        metadata={
            "provider": "fake",
            "model": "deterministic-test-model",
        },
    )


def test_map_course_response_builds_production_course() -> None:
    response = _response(
        {
            "course_id": "modern-java",
            "title": "Modern Java",
            "language": "zh-TW",
            "weeks": [
                {
                    "number": 1,
                    "title": "Lambda Expressions",
                },
                {
                    "number": 2,
                    "title": "Streams",
                },
            ],
        }
    )

    course = map_course_response(response)

    assert isinstance(course, Course)
    assert course.course_id == "modern-java"
    assert course.title == "Modern Java"
    assert course.language == "zh-TW"


def test_map_course_response_builds_production_weeks() -> None:
    response = _response(
        {
            "course_id": "modern-java",
            "title": "Modern Java",
            "language": "zh-TW",
            "weeks": [
                {
                    "number": 1,
                    "title": "Lambda Expressions",
                },
                {
                    "number": 2,
                    "title": "Streams",
                },
            ],
        }
    )

    course = map_course_response(response)

    assert all(isinstance(week, Week) for week in course.weeks)
    assert tuple(week.number for week in course.weeks) == (1, 2)
    assert tuple(week.title for week in course.weeks) == (
        "Lambda Expressions",
        "Streams",
    )


def test_map_course_response_preserves_deterministic_week_order() -> None:
    response = _response(
        {
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
        }
    )

    course = map_course_response(response)

    assert tuple(week.number for week in course.weeks) == (1, 2)


def test_map_course_response_keeps_ai_metadata_out_of_domain() -> None:
    response = _response(
        {
            "course_id": "modern-java",
            "title": "Modern Java",
            "language": "zh-TW",
            "weeks": [],
        }
    )

    course = map_course_response(response)

    assert not hasattr(course, "provider")
    assert not hasattr(course, "model")
    assert not hasattr(course, "metadata")


def test_map_course_response_does_not_mutate_ai_response() -> None:
    content = {
        "course_id": "modern-java",
        "title": "Modern Java",
        "language": "zh-TW",
        "weeks": [
            {
                "number": 1,
                "title": "Lambda Expressions",
            }
        ],
    }
    response = _response(content)

    course = map_course_response(response)

    assert course.course_id == "modern-java"
    assert response.content is content
    assert response.content == content
    assert response.metadata == {
        "provider": "fake",
        "model": "deterministic-test-model",
    }
