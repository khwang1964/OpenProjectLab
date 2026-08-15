from __future__ import annotations

from collections.abc import Mapping
from dataclasses import FrozenInstanceError

import pytest

from generator.ai.models import AIRequest


def test_ai_request_preserves_required_contract_fields() -> None:
    context = {
        "course_id": "modern-java",
        "week": 1,
    }

    request = AIRequest(
        task="courseware.generate",
        instructions="Generate a deterministic Week 01 courseware draft.",
        context=context,
        response_contract="courseware.week.v1",
    )

    assert request.task == "courseware.generate"
    assert request.instructions == ("Generate a deterministic Week 01 courseware draft.")
    assert request.context == context
    assert request.response_contract == "courseware.week.v1"


def test_ai_request_allows_omitted_response_contract() -> None:
    request = AIRequest(
        task="courseware.review",
        instructions="Review the supplied courseware.",
        context={"course_id": "modern-java"},
    )

    assert request.response_contract is None


def test_ai_request_is_immutable() -> None:
    request = AIRequest(
        task="courseware.generate",
        instructions="Generate courseware.",
        context={},
    )

    with pytest.raises(FrozenInstanceError):
        request.task = "changed"  # type: ignore[misc]


def test_ai_request_does_not_require_provider_specific_types() -> None:
    request = AIRequest(
        task="courseware.generate",
        instructions="Generate courseware.",
        context={
            "course_id": "modern-java",
            "language": "zh-TW",
        },
        response_contract="courseware.course.v1",
    )

    assert isinstance(request.task, str)
    assert isinstance(request.instructions, str)
    assert isinstance(request.context, Mapping)
    assert request.response_contract == "courseware.course.v1"
