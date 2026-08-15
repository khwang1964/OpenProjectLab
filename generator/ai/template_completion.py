"""Structured AI template completion models and response mapping."""

from __future__ import annotations

from dataclasses import dataclass

from .errors import AIResponseValidationError
from .models import AIResponse
from .validation import validate_response_mapping


@dataclass(frozen=True, slots=True)
class AITemplateCompletionResult:
    """Represent AI-proposed template source without applying side effects."""

    template_name: str
    content: str
    context_keys: tuple[str, ...]


def map_template_completion_response(
    response: AIResponse,
) -> AITemplateCompletionResult:
    """Map a structured AI response into an immutable template completion result."""
    content = validate_response_mapping(
        response,
        required_fields={
            "template_name": str,
            "content": str,
            "context_keys": list,
        },
    )

    template_name = content["template_name"]
    template_content = content["content"]
    raw_context_keys = content["context_keys"]

    if not template_name:
        raise AIResponseValidationError(
            "AI template completion field 'template_name' must not be empty."
        )

    if not template_content:
        raise AIResponseValidationError("AI template completion field 'content' must not be empty.")

    context_keys: list[str] = []

    for index, key in enumerate(raw_context_keys):
        if not isinstance(key, str):
            raise AIResponseValidationError(
                "AI template completion field 'context_keys' "
                f"item at index {index} must be of type str."
            )

        if not key:
            raise AIResponseValidationError(
                "AI template completion field 'context_keys' "
                f"item at index {index} must not be empty."
            )

        context_keys.append(key)

    return AITemplateCompletionResult(
        template_name=template_name,
        content=template_content,
        context_keys=tuple(context_keys),
    )
