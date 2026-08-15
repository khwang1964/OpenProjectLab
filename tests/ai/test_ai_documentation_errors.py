from __future__ import annotations

import pytest

from generator.ai.documentation import map_documentation_response
from generator.ai.errors import AIResponseValidationError
from generator.ai.models import AIResponse


def _response(content: object) -> AIResponse:
    return AIResponse(
        content=content,
        metadata={"provider": "fake"},
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
def test_map_documentation_response_rejects_non_mapping_content(
    content: object,
) -> None:
    with pytest.raises(AIResponseValidationError):
        map_documentation_response(_response(content))


@pytest.mark.parametrize(
    "missing_field",
    [
        "title",
        "format",
        "content",
    ],
)
def test_map_documentation_response_rejects_missing_required_field(
    missing_field: str,
) -> None:
    content = {
        "title": "Example",
        "format": "markdown",
        "content": "# Example\n",
    }
    content.pop(missing_field)

    with pytest.raises(
        AIResponseValidationError,
        match=missing_field,
    ):
        map_documentation_response(_response(content))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", 123),
        ("format", 123),
        ("content", 123),
    ],
)
def test_map_documentation_response_rejects_wrong_field_type(
    field: str,
    value: object,
) -> None:
    content = {
        "title": "Example",
        "format": "markdown",
        "content": "# Example\n",
    }
    content[field] = value

    with pytest.raises(
        AIResponseValidationError,
        match=field,
    ):
        map_documentation_response(_response(content))


@pytest.mark.parametrize(
    "format_name",
    [
        "",
        "html",
        "rst",
        "pdf",
    ],
)
def test_map_documentation_response_rejects_unsupported_format(
    format_name: str,
) -> None:
    with pytest.raises(
        AIResponseValidationError,
        match="format",
    ):
        map_documentation_response(
            _response(
                {
                    "title": "Example",
                    "format": format_name,
                    "content": "Example content.",
                }
            )
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("title", ""),
        ("content", ""),
    ],
)
def test_map_documentation_response_rejects_empty_required_text(
    field: str,
    value: str,
) -> None:
    content = {
        "title": "Example",
        "format": "markdown",
        "content": "# Example\n",
    }
    content[field] = value

    with pytest.raises(
        AIResponseValidationError,
        match=field,
    ):
        map_documentation_response(_response(content))


def test_documentation_validation_failure_has_no_filesystem_side_effect(
    tmp_path,
) -> None:
    with pytest.raises(AIResponseValidationError):
        map_documentation_response(_response(None))

    assert list(tmp_path.iterdir()) == []
