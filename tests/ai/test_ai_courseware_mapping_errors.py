from __future__ import annotations

import pytest

from generator.ai.courseware import map_course_response
from generator.ai.errors import AIResponseValidationError
from generator.ai.models import AIResponse


def _response(content: object) -> AIResponse:
    return AIResponse(
        content=content,
        metadata={
            "provider": "fake",
            "model": "deterministic-test-model",
        },
    )


@pytest.mark.parametrize(
    "content",
    [
        None,
        "not-a-mapping",
        42,
        [],
    ],
)
def test_map_course_response_rejects_non_mapping_content(
    content: object,
) -> None:
    with pytest.raises(AIResponseValidationError):
        map_course_response(_response(content))


@pytest.mark.parametrize(
    "missing_field",
    [
        "course_id",
        "title",
        "language",
        "weeks",
    ],
)
def test_map_course_response_rejects_missing_course_fields(
    missing_field: str,
) -> None:
    content = {
        "course_id": "modern-java",
        "title": "Modern Java",
        "language": "zh-TW",
        "weeks": [],
    }
    content.pop(missing_field)

    with pytest.raises(
        AIResponseValidationError,
        match=missing_field,
    ):
        map_course_response(_response(content))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("course_id", 123),
        ("title", 123),
        ("language", 123),
        ("weeks", "week-01"),
    ],
)
def test_map_course_response_rejects_wrong_course_field_types(
    field: str,
    value: object,
) -> None:
    content = {
        "course_id": "modern-java",
        "title": "Modern Java",
        "language": "zh-TW",
        "weeks": [],
    }
    content[field] = value

    with pytest.raises(
        AIResponseValidationError,
        match=field,
    ):
        map_course_response(_response(content))


def test_map_course_response_rejects_non_mapping_week_item() -> None:
    response = _response(
        {
            "course_id": "modern-java",
            "title": "Modern Java",
            "language": "zh-TW",
            "weeks": ["week-01"],
        }
    )

    with pytest.raises(
        AIResponseValidationError,
        match="week",
    ):
        map_course_response(response)


@pytest.mark.parametrize(
    "missing_field",
    [
        "number",
        "title",
    ],
)
def test_map_course_response_rejects_missing_week_fields(
    missing_field: str,
) -> None:
    week = {
        "number": 1,
        "title": "Lambda Expressions",
    }
    week.pop(missing_field)

    response = _response(
        {
            "course_id": "modern-java",
            "title": "Modern Java",
            "language": "zh-TW",
            "weeks": [week],
        }
    )

    with pytest.raises(
        AIResponseValidationError,
        match=missing_field,
    ):
        map_course_response(response)


def test_invalid_week_value_is_rejected_by_existing_domain_contract() -> None:
    response = _response(
        {
            "course_id": "modern-java",
            "title": "Modern Java",
            "language": "zh-TW",
            "weeks": [
                {
                    "number": 0,
                    "title": "Invalid Week",
                }
            ],
        }
    )

    with pytest.raises(ValueError):
        map_course_response(response)


def test_duplicate_week_number_is_rejected_by_existing_domain_contract() -> None:
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
                    "number": 1,
                    "title": "Duplicate",
                },
            ],
        }
    )

    with pytest.raises(ValueError):
        map_course_response(response)


def test_mapping_failure_has_no_filesystem_side_effect(
    tmp_path,
) -> None:
    response = _response(
        {
            "course_id": "modern-java",
            "title": "Modern Java",
            "language": "zh-TW",
            "weeks": "invalid",
        }
    )

    with pytest.raises(AIResponseValidationError):
        map_course_response(response)

    assert list(tmp_path.iterdir()) == []
