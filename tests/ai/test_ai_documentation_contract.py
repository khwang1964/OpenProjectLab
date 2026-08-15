from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from generator.ai.documentation import (
    AIDocumentDraft,
    map_documentation_response,
)
from generator.ai.models import AIResponse


def _response(content: object) -> AIResponse:
    return AIResponse(
        content=content,
        metadata={
            "provider": "fake",
            "model": "deterministic-test-model",
        },
    )


def test_map_documentation_response_builds_document_draft() -> None:
    response = _response(
        {
            "title": "AI Integration Overview",
            "format": "markdown",
            "content": "# AI Integration\n\nStructured documentation draft.\n",
        }
    )

    draft = map_documentation_response(response)

    assert isinstance(draft, AIDocumentDraft)
    assert draft.title == "AI Integration Overview"
    assert draft.format == "markdown"
    assert draft.content == ("# AI Integration\n\nStructured documentation draft.\n")


def test_document_draft_is_immutable() -> None:
    draft = AIDocumentDraft(
        title="AI Integration Overview",
        format="markdown",
        content="# AI Integration\n",
    )

    with pytest.raises(FrozenInstanceError):
        draft.title = "Changed"  # type: ignore[misc]


def test_map_documentation_response_preserves_content_exactly() -> None:
    content = "# Heading\n\n- item 1\n- item 2\n"
    response = _response(
        {
            "title": "Example",
            "format": "markdown",
            "content": content,
        }
    )

    draft = map_documentation_response(response)

    assert draft.content == content


def test_map_documentation_response_keeps_provider_metadata_out_of_draft() -> None:
    response = _response(
        {
            "title": "Example",
            "format": "markdown",
            "content": "# Example\n",
        }
    )

    draft = map_documentation_response(response)

    assert not hasattr(draft, "provider")
    assert not hasattr(draft, "model")
    assert not hasattr(draft, "metadata")


def test_map_documentation_response_does_not_mutate_ai_response() -> None:
    content = {
        "title": "Example",
        "format": "markdown",
        "content": "# Example\n",
    }
    response = _response(content)

    draft = map_documentation_response(response)

    assert draft.title == "Example"
    assert response.content is content
    assert response.content == content


@pytest.mark.parametrize(
    "format_name",
    [
        "markdown",
        "text",
    ],
)
def test_map_documentation_response_accepts_supported_formats(
    format_name: str,
) -> None:
    response = _response(
        {
            "title": "Example",
            "format": format_name,
            "content": "Example content.",
        }
    )

    draft = map_documentation_response(response)

    assert draft.format == format_name
