"""Application service for structured AI documentation generation."""

from __future__ import annotations

from .documentation import AIDocumentDraft, map_documentation_response
from .models import AIRequest
from .protocols import AIProvider


class AIDocumentationService:
    """Orchestrate provider invocation and documentation draft mapping."""

    def __init__(
        self,
        *,
        provider: AIProvider,
    ) -> None:
        self._provider = provider

    def generate(
        self,
        request: AIRequest,
    ) -> AIDocumentDraft:
        """Generate and map a structured documentation draft."""
        response = self._provider.generate(request)
        return map_documentation_response(response)
