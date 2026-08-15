"""Map validated AI responses into production courseware domain objects."""

from __future__ import annotations

from collections.abc import Mapping

from generator.courseware.models import Course, Week

from .errors import AIResponseValidationError
from .models import AIResponse
from .validation import validate_response_mapping


def map_course_response(
    response: AIResponse,
) -> Course:
    """Map a structured AI response into a production Course."""
    content = validate_response_mapping(
        response,
        required_fields={
            "course_id": str,
            "title": str,
            "language": str,
            "weeks": list,
        },
    )

    weeks = tuple(
        sorted(
            (
                _map_week(
                    item,
                    index=index,
                )
                for index, item in enumerate(content["weeks"])
            ),
            key=lambda week: week.number,
        )
    )

    return Course(
        course_id=content["course_id"],
        title=content["title"],
        language=content["language"],
        weeks=weeks,
    )


def _map_week(
    value: object,
    *,
    index: int,
) -> Week:
    if not isinstance(value, Mapping):
        raise AIResponseValidationError(f"AI response week at index {index} must be a mapping.")

    if "number" not in value:
        raise AIResponseValidationError(
            f"AI response week at index {index} is missing required field: number"
        )

    if "title" not in value:
        raise AIResponseValidationError(
            f"AI response week at index {index} is missing required field: title"
        )

    number = value["number"]
    title = value["title"]

    if not isinstance(number, int) or isinstance(number, bool):
        raise AIResponseValidationError(
            f"AI response week field 'number' at index {index} must be of type int."
        )

    if not isinstance(title, str):
        raise AIResponseValidationError(
            f"AI response week field 'title' at index {index} must be of type str."
        )

    return Week(
        number=number,
        title=title,
    )
