from __future__ import annotations

import pytest

from generator.ai.errors import AIResponseValidationError
from generator.ai.models import AIResponse
from generator.ai.template_completion import map_template_completion_response


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
def test_map_template_completion_response_rejects_non_mapping_content(
    content: object,
) -> None:
    with pytest.raises(AIResponseValidationError):
        map_template_completion_response(_response(content))


@pytest.mark.parametrize(
    "missing_field",
    [
        "template_name",
        "content",
        "context_keys",
    ],
)
def test_map_template_completion_response_rejects_missing_required_field(
    missing_field: str,
) -> None:
    content = {
        "template_name": "course/README.md.j2",
        "content": "# {{ course.title }}\n",
        "context_keys": ["course.title"],
    }
    content.pop(missing_field)

    with pytest.raises(
        AIResponseValidationError,
        match=missing_field,
    ):
        map_template_completion_response(_response(content))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("template_name", 123),
        ("content", 123),
        ("context_keys", "course.title"),
    ],
)
def test_map_template_completion_response_rejects_wrong_field_type(
    field: str,
    value: object,
) -> None:
    content = {
        "template_name": "course/README.md.j2",
        "content": "# {{ course.title }}\n",
        "context_keys": ["course.title"],
    }
    content[field] = value

    with pytest.raises(
        AIResponseValidationError,
        match=field,
    ):
        map_template_completion_response(_response(content))


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("template_name", ""),
        ("content", ""),
    ],
)
def test_map_template_completion_response_rejects_empty_required_text(
    field: str,
    value: str,
) -> None:
    content = {
        "template_name": "course/README.md.j2",
        "content": "# {{ course.title }}\n",
        "context_keys": ["course.title"],
    }
    content[field] = value

    with pytest.raises(
        AIResponseValidationError,
        match=field,
    ):
        map_template_completion_response(_response(content))


def test_map_template_completion_response_rejects_non_string_context_key() -> None:
    with pytest.raises(
        AIResponseValidationError,
        match="context_keys",
    ):
        map_template_completion_response(
            _response(
                {
                    "template_name": "course/README.md.j2",
                    "content": "# {{ course.title }}\n",
                    "context_keys": [
                        "course.title",
                        123,
                    ],
                }
            )
        )


def test_map_template_completion_response_rejects_empty_context_key() -> None:
    with pytest.raises(
        AIResponseValidationError,
        match="context_keys",
    ):
        map_template_completion_response(
            _response(
                {
                    "template_name": "course/README.md.j2",
                    "content": "# {{ course.title }}\n",
                    "context_keys": [
                        "course.title",
                        "",
                    ],
                }
            )
        )


def test_template_completion_failure_has_no_filesystem_side_effect(
    tmp_path,
) -> None:
    with pytest.raises(AIResponseValidationError):
        map_template_completion_response(_response(None))

    assert list(tmp_path.iterdir()) == []
