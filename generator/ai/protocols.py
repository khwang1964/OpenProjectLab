"""Protocols for provider-independent AI integrations."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from .models import AIRequest, AIResponse


@runtime_checkable
class AIProvider(Protocol):
    """Generate an AI response from an OpenProjectLab AI request."""

    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        """Generate a response for the supplied request."""
        ...
