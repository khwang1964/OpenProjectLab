from __future__ import annotations

from types import MappingProxyType

import pytest

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


def test_validate_response_mapping_accepts_required_fields() -> None:
    response = _response(
        {
            "title": "Modern Java",
            "weeks": [],
        }
    )

    validated = validate_response_mapping(
        response,
        required_fields={
            "title": str,
            "weeks": list,
        },
    )

    assert validated == {
        "title": "Modern Java",
        "weeks": [],
    }


def test_validate_response_mapping_accepts_additional_fields() -> None:
    response = _response(
        {
            "title": "Modern Java",
            "weeks": [],
            "language": "zh-TW",
        }
    )

    validated = validate_response_mapping(
        response,
        required_fields={
            "title": str,
            "weeks": list,
        },
    )

    assert validated["title"] == "Modern Java"
    assert validated["weeks"] == []
    assert validated["language"] == "zh-TW"


def test_validate_response_mapping_accepts_mapping_content() -> None:
    response = _response(
        MappingProxyType(
            {
                "title": "Modern Java",
                "weeks": [],
            }
        )
    )

    validated = validate_response_mapping(
        response,
        required_fields={
            "title": str,
            "weeks": list,
        },
    )

    assert validated == {
        "title": "Modern Java",
        "weeks": [],
    }


def test_validate_response_mapping_does_not_mutate_response_content() -> None:
    content = {
        "title": "Modern Java",
        "weeks": [],
    }
    response = _response(content)

    validated = validate_response_mapping(
        response,
        required_fields={
            "title": str,
            "weeks": list,
        },
    )

    assert response.content is content
    assert response.content == {
        "title": "Modern Java",
        "weeks": [],
    }
    assert validated == response.content


def test_validate_response_mapping_returns_independent_mapping() -> None:
    content = {
        "title": "Modern Java",
        "weeks": [],
    }
    response = _response(content)

    validated = validate_response_mapping(
        response,
        required_fields={
            "title": str,
            "weeks": list,
        },
    )

    assert validated is not content

    validated["title"] = "Changed"

    assert response.content["title"] == "Modern Java"


@pytest.mark.parametrize(
    ("required_fields", "expected"),
    [
        ({}, {"title": "Modern Java"}),
        ({"title": str}, {"title": "Modern Java"}),
    ],
)
def test_validate_response_mapping_supports_minimal_field_contracts(
    required_fields: dict[str, type[object]],
    expected: dict[str, object],
) -> None:
    response = _response({"title": "Modern Java"})

    validated = validate_response_mapping(
        response,
        required_fields=required_fields,
    )

    assert validated == expected
