"""High-level AI course builder use-case contract."""

from __future__ import annotations

from dataclasses import dataclass

from generator.courseware.models import Course

from .courseware import map_course_response
from .models import AIRequest
from .protocols import AIProvider


class AICourseBuildValidationError(ValueError):
    """Raised when an AI course build request or result is incomplete."""


@dataclass(frozen=True, slots=True)
class AICourseBuildRequest:
    """Describe a provider-independent high-level course build request."""

    course_id: str
    title: str
    language: str
    objectives: tuple[str, ...]
    week_count: int

    def __post_init__(self) -> None:
        if not self.course_id:
            raise AICourseBuildValidationError(
                "AI course build field 'course_id' must not be empty."
            )

        if not self.title:
            raise AICourseBuildValidationError("AI course build field 'title' must not be empty.")

        if not self.language:
            raise AICourseBuildValidationError(
                "AI course build field 'language' must not be empty."
            )

        if not self.objectives:
            raise AICourseBuildValidationError(
                "AI course build field 'objectives' must not be empty."
            )

        for index, objective in enumerate(self.objectives):
            if not objective:
                raise AICourseBuildValidationError(
                    f"AI course build field 'objectives' item at index {index} must not be empty."
                )

        if self.week_count < 1:
            raise AICourseBuildValidationError(
                "AI course build field 'week_count' must be at least 1."
            )


class AICourseBuilder:
    """Build a production Course through the shared AI provider boundary."""

    def __init__(
        self,
        *,
        provider: AIProvider,
    ) -> None:
        self._provider = provider

    def build(
        self,
        request: AICourseBuildRequest,
    ) -> Course:
        """Build a structured course and enforce use-case completeness."""
        ai_request = AIRequest(
            task="courseware.build",
            instructions=(
                "Build a structured course with the requested number of weeks "
                "and return data compatible with the OpenProjectLab course contract."
            ),
            context={
                "course_id": request.course_id,
                "title": request.title,
                "language": request.language,
                "objectives": request.objectives,
                "week_count": request.week_count,
            },
            response_contract="courseware.course.v1",
        )

        response = self._provider.generate(ai_request)
        course = map_course_response(response)

        if len(course.weeks) != request.week_count:
            raise AICourseBuildValidationError(
                "AI course build result does not satisfy requested "
                f"'week_count': expected {request.week_count}, "
                f"received {len(course.weeks)}."
            )

        return course
