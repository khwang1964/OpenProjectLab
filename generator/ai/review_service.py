"""Application service for structured AI review."""

from __future__ import annotations

from .models import AIRequest
from .protocols import AIProvider
from .review import AIReviewResult, map_review_response


class AIReviewService:
    """Orchestrate provider invocation and structured review mapping."""

    def __init__(
        self,
        *,
        provider: AIProvider,
    ) -> None:
        self._provider = provider

    def review(
        self,
        request: AIRequest,
    ) -> AIReviewResult:
        """Review supplied context and return structured advisory findings."""
        response = self._provider.generate(request)
        return map_review_response(response)
