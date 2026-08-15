from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from generator.ai.models import AIResponse


def test_ai_response_separates_content_from_operational_metadata() -> None:
    content = {
        "title": "Modern Java",
        "weeks": [],
    }
    metadata = {
        "provider": "fake",
        "model": "deterministic-test-model",
        "finish_reason": "stop",
    }

    response = AIResponse(
        content=content,
        metadata=metadata,
    )

    assert response.content == content
    assert response.metadata == metadata


def test_ai_response_allows_empty_metadata() -> None:
    response = AIResponse(
        content={"title": "Modern Java"},
        metadata={},
    )

    assert response.metadata == {}


def test_ai_response_is_immutable() -> None:
    response = AIResponse(
        content={"title": "Modern Java"},
        metadata={},
    )

    with pytest.raises(FrozenInstanceError):
        response.content = {"title": "Changed"}  # type: ignore[misc]


def test_ai_response_keeps_provider_metadata_outside_content() -> None:
    response = AIResponse(
        content={
            "course_id": "modern-java",
            "title": "Modern Java",
        },
        metadata={
            "provider": "fake",
            "model": "deterministic-test-model",
        },
    )

    assert "provider" not in response.content
    assert "model" not in response.content
    assert response.metadata["provider"] == "fake"
