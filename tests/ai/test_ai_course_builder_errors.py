from __future__ import annotations

import pytest

from generator.ai.course_builder import (
    AICourseBuilder,
    AICourseBuildRequest,
    AICourseBuildValidationError,
)
from generator.ai.errors import AIResponseValidationError
from generator.ai.models import AIResponse
from generator.ai.testing import FakeAIProvider


def _valid_request(
    *,
    week_count: int = 2,
) -> AICourseBuildRequest:
    return AICourseBuildRequest(
        course_id="modern-java",
        title="Modern Java",
        language="zh-TW",
        objectives=("Understand modern Java language features.",),
        week_count=week_count,
    )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("course_id", ""),
        ("title", ""),
        ("language", ""),
    ],
)
def test_course_build_request_rejects_empty_required_text(
    field: str,
    value: str,
) -> None:
    values = {
        "course_id": "modern-java",
        "title": "Modern Java",
        "language": "zh-TW",
        "objectives": ("Understand modern Java.",),
        "week_count": 1,
    }
    values[field] = value

    with pytest.raises(
        AICourseBuildValidationError,
        match=field,
    ):
        AICourseBuildRequest(**values)


def test_course_build_request_rejects_empty_objectives() -> None:
    with pytest.raises(
        AICourseBuildValidationError,
        match="objectives",
    ):
        AICourseBuildRequest(
            course_id="modern-java",
            title="Modern Java",
            language="zh-TW",
            objectives=(),
            week_count=1,
        )


def test_course_build_request_rejects_empty_objective_item() -> None:
    with pytest.raises(
        AICourseBuildValidationError,
        match="objectives",
    ):
        AICourseBuildRequest(
            course_id="modern-java",
            title="Modern Java",
            language="zh-TW",
            objectives=(
                "Understand modern Java.",
                "",
            ),
            week_count=1,
        )


@pytest.mark.parametrize(
    "week_count",
    [
        0,
        -1,
    ],
)
def test_course_build_request_rejects_invalid_week_count(
    week_count: int,
) -> None:
    with pytest.raises(
        AICourseBuildValidationError,
        match="week_count",
    ):
        _valid_request(
            week_count=week_count,
        )


def test_build_propagates_provider_failure() -> None:
    provider = FakeAIProvider(
        failures=(RuntimeError("simulated provider failure"),),
    )
    builder = AICourseBuilder(
        provider=provider,
    )

    with pytest.raises(
        RuntimeError,
        match="simulated provider failure",
    ):
        builder.build(_valid_request())


def test_build_propagates_response_validation_failure() -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content=None,
                metadata={"provider": "fake"},
            ),
        ),
    )
    builder = AICourseBuilder(
        provider=provider,
    )

    with pytest.raises(AIResponseValidationError):
        builder.build(_valid_request())


def test_build_rejects_incomplete_week_count() -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content={
                    "course_id": "modern-java",
                    "title": "Modern Java",
                    "language": "zh-TW",
                    "weeks": [
                        {
                            "number": 1,
                            "title": "Lambda Expressions",
                        }
                    ],
                },
                metadata={"provider": "fake"},
            ),
        ),
    )
    builder = AICourseBuilder(
        provider=provider,
    )

    with pytest.raises(
        AICourseBuildValidationError,
        match="week_count",
    ):
        builder.build(
            _valid_request(
                week_count=2,
            )
        )


def test_build_preserves_existing_domain_validation_failure() -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content={
                    "course_id": "modern-java",
                    "title": "Modern Java",
                    "language": "zh-TW",
                    "weeks": [
                        {
                            "number": 0,
                            "title": "Invalid Week",
                        }
                    ],
                },
                metadata={"provider": "fake"},
            ),
        ),
    )
    builder = AICourseBuilder(
        provider=provider,
    )

    with pytest.raises(ValueError):
        builder.build(
            _valid_request(
                week_count=1,
            )
        )


def test_build_failure_has_no_filesystem_side_effect(
    tmp_path,
) -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content=None,
                metadata={"provider": "fake"},
            ),
        ),
    )
    builder = AICourseBuilder(
        provider=provider,
    )

    with pytest.raises(AIResponseValidationError):
        builder.build(_valid_request())

    assert list(tmp_path.iterdir()) == []
