from __future__ import annotations

import pytest

from generator.ai.errors import AIResponseValidationError
from generator.ai.models import AIResponse
from generator.ai.validation import validate_response_mapping


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
        True,
        ["title", "Modern Java"],
        ("title", "Modern Java"),
    ],
)
def test_validate_response_mapping_rejects_non_mapping_content(
    content: object,
) -> None:
    with pytest.raises(
        AIResponseValidationError,
        match="mapping",
    ):
        validate_response_mapping(
            _response(content),
            required_fields={"title": str},
        )


def test_validate_response_mapping_rejects_missing_required_field() -> None:
    response = _response(
        {
            "title": "Modern Java",
        }
    )

    with pytest.raises(
        AIResponseValidationError,
        match="weeks",
    ):
        validate_response_mapping(
            response,
            required_fields={
                "title": str,
                "weeks": list,
            },
        )


@pytest.mark.parametrize(
    ("content", "field", "expected_type"),
    [
        ({"title": 123}, "title", str),
        ({"weeks": "week-01"}, "weeks", list),
        ({"enabled": "yes"}, "enabled", bool),
    ],
)
def test_validate_response_mapping_rejects_wrong_required_field_type(
    content: dict[str, object],
    field: str,
    expected_type: type[object],
) -> None:
    with pytest.raises(
        AIResponseValidationError,
        match=field,
    ):
        validate_response_mapping(
            _response(content),
            required_fields={
                field: expected_type,
            },
        )


def test_validation_error_is_ai_specific_error() -> None:
    with pytest.raises(AIResponseValidationError) as exc_info:
        validate_response_mapping(
            _response(None),
            required_fields={"title": str},
        )

    assert type(exc_info.value).__name__ == "AIResponseValidationError"


def test_validation_failure_does_not_mutate_response() -> None:
    content = {
        "title": 123,
    }
    response = _response(content)

    with pytest.raises(AIResponseValidationError):
        validate_response_mapping(
            response,
            required_fields={"title": str},
        )

    assert response.content is content
    assert response.content == {
        "title": 123,
    }


def test_validation_failure_has_no_filesystem_side_effect(
    tmp_path,
) -> None:
    response = _response(None)

    with pytest.raises(AIResponseValidationError):
        validate_response_mapping(
            response,
            required_fields={"title": str},
        )

    assert list(tmp_path.iterdir()) == []
