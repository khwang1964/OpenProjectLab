"""Freeze the OpenProjectLab v1 provider-independent AI public contract."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from generator.ai.errors import AIResponseValidationError
from generator.ai.models import AIRequest, AIResponse
from generator.ai.protocols import AIProvider
from generator.ai.testing import FakeAIProvider
from generator.ai.validation import validate_response_mapping


def test_v1_ai_request_and_response_are_immutable_dataclasses() -> None:
    """Keep provider-independent request/response objects immutable."""
    request = AIRequest(
        task="course-outline",
        instructions="Create a course outline.",
        context={"weeks": 4},
        response_contract="course-outline-v1",
    )
    response = AIResponse(
        content={"course_id": "demo"},
        metadata={"provider": "fake"},
    )

    with pytest.raises(FrozenInstanceError):
        request.task = "changed"  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        response.content = {}  # type: ignore[misc]


def test_v1_ai_provider_protocol_is_runtime_checkable() -> None:
    """Keep the provider-independent AIProvider protocol runtime-checkable."""
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content={"ok": True},
                metadata={},
            ),
        )
    )

    assert isinstance(provider, AIProvider)


def test_v1_fake_ai_provider_is_deterministic_and_records_requests() -> None:
    """Keep deterministic configured outcomes and invocation ordering."""
    first_response = AIResponse(content={"value": 1}, metadata={})
    second_response = AIResponse(content={"value": 2}, metadata={})
    provider = FakeAIProvider(
        responses=(first_response, second_response),
    )
    first_request = AIRequest(
        task="first",
        instructions="First",
        context={},
    )
    second_request = AIRequest(
        task="second",
        instructions="Second",
        context={},
    )

    assert provider.generate(first_request) is first_response
    assert provider.generate(second_request) is second_response
    assert provider.requests == (first_request, second_request)


def test_v1_fake_ai_provider_propagates_configured_failure() -> None:
    """Keep deterministic provider-failure simulation available to core tests."""
    failure = RuntimeError("provider unavailable")
    provider = FakeAIProvider(failures=(failure,))
    request = AIRequest(
        task="failure",
        instructions="Fail",
        context={},
    )

    with pytest.raises(RuntimeError, match="provider unavailable"):
        provider.generate(request)

    assert provider.requests == (request,)


def test_v1_response_mapping_validation_returns_independent_copy() -> None:
    """Validate required fields and return a copy of mapping-shaped AI content."""
    source = {
        "course_id": "modern-java",
        "weeks": 4,
    }
    response = AIResponse(
        content=source,
        metadata={"provider": "fake"},
    )

    validated = validate_response_mapping(
        response,
        required_fields={
            "course_id": str,
            "weeks": int,
        },
    )

    assert validated == source
    assert validated is not source


@pytest.mark.parametrize(
    ("content", "required_fields"),
    [
        ("not-a-mapping", {"course_id": str}),
        ({}, {"course_id": str}),
        ({"course_id": 123}, {"course_id": str}),
    ],
)
def test_v1_invalid_ai_response_fails_structural_validation(
    content: object,
    required_fields: dict[str, type[object]],
) -> None:
    """Reject invalid AI output at the provider-independent validation boundary."""
    response = AIResponse(
        content=content,
        metadata={"provider": "fake"},
    )

    with pytest.raises(AIResponseValidationError):
        validate_response_mapping(
            response,
            required_fields=required_fields,
        )


def test_v1_fake_ai_provider_requires_explicit_configured_outcome() -> None:
    """Prevent hidden network/provider fallback in deterministic core testing."""
    provider = FakeAIProvider()
    request = AIRequest(
        task="unconfigured",
        instructions="No configured outcome",
        context={},
    )

    with pytest.raises(RuntimeError, match="no configured response"):
        provider.generate(request)
