"""Structural validation helpers for provider-independent AI responses."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from .errors import AIResponseValidationError
from .models import AIResponse


def validate_response_mapping(
    response: AIResponse,
    *,
    required_fields: Mapping[str, type[object]],
) -> dict[str, Any]:
    """Validate mapping-shaped AI response content and return an independent copy."""
    content = response.content

    if not isinstance(content, Mapping):
        raise AIResponseValidationError("AI response content must be a mapping.")

    for field, expected_type in required_fields.items():
        if field not in content:
            raise AIResponseValidationError(f"AI response is missing required field: {field}")

        value = content[field]

        if not isinstance(value, expected_type):
            raise AIResponseValidationError(
                f"AI response field {field!r} must be of type {expected_type.__name__}."
            )

    return dict(content)
