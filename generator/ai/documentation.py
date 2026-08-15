"""Structured AI documentation draft models and response mapping."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import AIResponseValidationError
from .models import AIResponse
from .validation import validate_response_mapping

_SUPPORTED_FORMATS = frozenset(
    {
        "markdown",
        "text",
    }
)


@dataclass(frozen=True, slots=True)
class AIDocumentDraft:
    """Represent structured documentation content proposed by an AI provider."""

    title: str
    format: str
    content: str


def map_documentation_response(
    response: AIResponse,
) -> AIDocumentDraft:
    """Map a structured AI response into an immutable documentation draft."""
    content = validate_response_mapping(
        response,
        required_fields={
            "title": str,
            "format": str,
            "content": str,
        },
    )

    title = content["title"]
    format_name = content["format"]
    body = content["content"]

    if not title:
        raise AIResponseValidationError("AI documentation field 'title' must not be empty.")

    if not body:
        raise AIResponseValidationError("AI documentation field 'content' must not be empty.")

    if format_name not in _SUPPORTED_FORMATS:
        raise AIResponseValidationError(
            "AI documentation field 'format' "
            f"must be one of: {', '.join(sorted(_SUPPORTED_FORMATS))}."
        )

    return AIDocumentDraft(
        title=title,
        format=format_name,
        content=body,
    )
