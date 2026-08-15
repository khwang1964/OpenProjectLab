"""Application service for AI-assisted course generation."""

from __future__ import annotations

from generator.courseware.models import Course

from .courseware import map_course_response
from .models import AIRequest
from .protocols import AIProvider


class AICourseGenerationService:
    """Orchestrate provider invocation and courseware mapping."""

    def __init__(
        self,
        *,
        provider: AIProvider,
    ) -> None:
        self._provider = provider

    def generate_course(
        self,
        request: AIRequest,
    ) -> Course:
        """Generate and map a structured AI response into a Course."""
        response = self._provider.generate(request)
        return map_course_response(response)
