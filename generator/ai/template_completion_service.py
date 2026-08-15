"""Application service for structured AI template completion."""

from __future__ import annotations

from .models import AIRequest
from .protocols import AIProvider
from .template_completion import (
    AITemplateCompletionResult,
    map_template_completion_response,
)


class AITemplateCompletionService:
    """Orchestrate provider invocation and template completion mapping."""

    def __init__(
        self,
        *,
        provider: AIProvider,
    ) -> None:
        self._provider = provider

    def complete(
        self,
        request: AIRequest,
    ) -> AITemplateCompletionResult:
        """Generate and map a structured template completion result."""
        response = self._provider.generate(request)
        return map_template_completion_response(response)
