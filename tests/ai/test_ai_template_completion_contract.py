from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from generator.ai.models import AIResponse
from generator.ai.template_completion import (
    AITemplateCompletionResult,
    map_template_completion_response,
)


def _response(content: object) -> AIResponse:
    return AIResponse(
        content=content,
        metadata={
            "provider": "fake",
            "model": "deterministic-test-model",
        },
    )


def test_map_template_completion_response_builds_result() -> None:
    response = _response(
        {
            "template_name": "week/README.md.j2",
            "content": "# Week {{ week.number }}: {{ week.title }}\n",
            "context_keys": [
                "week.number",
                "week.title",
            ],
        }
    )

    result = map_template_completion_response(response)

    assert isinstance(result, AITemplateCompletionResult)
    assert result.template_name == "week/README.md.j2"
    assert result.content == "# Week {{ week.number }}: {{ week.title }}\n"
    assert result.context_keys == (
        "week.number",
        "week.title",
    )


def test_template_completion_result_is_immutable() -> None:
    result = AITemplateCompletionResult(
        template_name="week/README.md.j2",
        content="# Week {{ week.number }}\n",
        context_keys=("week.number",),
    )

    with pytest.raises(FrozenInstanceError):
        result.template_name = "changed"  # type: ignore[misc]


def test_map_template_completion_response_preserves_context_key_order() -> None:
    response = _response(
        {
            "template_name": "course/README.md.j2",
            "content": "# {{ course.title }}\n",
            "context_keys": [
                "course.title",
                "course.language",
                "course.id",
            ],
        }
    )

    result = map_template_completion_response(response)

    assert result.context_keys == (
        "course.title",
        "course.language",
        "course.id",
    )


def test_map_template_completion_response_keeps_provider_metadata_out_of_result() -> None:
    response = _response(
        {
            "template_name": "course/README.md.j2",
            "content": "# {{ course.title }}\n",
            "context_keys": ["course.title"],
        }
    )

    result = map_template_completion_response(response)

    assert not hasattr(result, "provider")
    assert not hasattr(result, "model")
    assert not hasattr(result, "metadata")


def test_map_template_completion_response_does_not_mutate_ai_response() -> None:
    content = {
        "template_name": "course/README.md.j2",
        "content": "# {{ course.title }}\n",
        "context_keys": ["course.title"],
    }
    response = _response(content)

    result = map_template_completion_response(response)

    assert result.template_name == "course/README.md.j2"
    assert response.content is content
    assert response.content == content


def test_map_template_completion_response_allows_empty_context_keys() -> None:
    response = _response(
        {
            "template_name": "static/NOTICE.txt.j2",
            "content": "Generated notice.\n",
            "context_keys": [],
        }
    )

    result = map_template_completion_response(response)

    assert result.context_keys == ()
