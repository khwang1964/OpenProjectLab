"""Provider-independent request and response models for AI integration."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AIRequest:
    """Describe a provider-independent AI generation request."""

    task: str
    instructions: str
    context: Mapping[str, object]
    response_contract: str | None = None


@dataclass(frozen=True, slots=True)
class AIResponse:
    """Represent provider-independent AI output and operational metadata."""

    content: object
    metadata: Mapping[str, object]
