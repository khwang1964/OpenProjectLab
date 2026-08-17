"""Harden the OpenProjectLab v1 provider-independent AI reliability boundary."""

from __future__ import annotations

import pytest

from generator.ai.errors import AIResponseValidationError
from generator.ai.models import AIRequest, AIResponse
from generator.ai.testing import FakeAIProvider
from generator.ai.validation import validate_response_mapping


def _request(task: str = "reliability") -> AIRequest:
    return AIRequest(
        task=task,
        instructions="Return deterministic structured output.",
        context={"source": "reliability-test"},
    )


@pytest.mark.parametrize(
    "content",
    [
        None,
        "not-a-mapping",
        ["not", "a", "mapping"],
        42,
    ],
)
def test_v1_ai_non_mapping_response_is_rejected(content: object) -> None:
    """Reject malformed provider output before downstream mapping."""
    response = AIResponse(content=content, metadata={})

    with pytest.raises(AIResponseValidationError):
        validate_response_mapping(
            response,
            required_fields={"course_id": str},
        )


def test_v1_ai_missing_required_field_is_rejected() -> None:
    """Reject incomplete structured output deterministically."""
    response = AIResponse(
        content={"title": "Course"},
        metadata={},
    )

    with pytest.raises(AIResponseValidationError):
        validate_response_mapping(
            response,
            required_fields={
                "course_id": str,
                "title": str,
            },
        )


def test_v1_ai_wrong_required_field_type_is_rejected() -> None:
    """Reject required fields whose runtime types violate the contract."""
    response = AIResponse(
        content={
            "course_id": "demo",
            "week_count": "4",
        },
        metadata={},
    )

    with pytest.raises(AIResponseValidationError):
        validate_response_mapping(
            response,
            required_fields={
                "course_id": str,
                "week_count": int,
            },
        )


def test_v1_ai_validation_returns_copy_not_provider_mapping() -> None:
    """Keep validation output isolated from the provider-owned mapping."""
    content = {
        "course_id": "demo",
        "week_count": 4,
    }
    response = AIResponse(content=content, metadata={})

    validated = validate_response_mapping(
        response,
        required_fields={
            "course_id": str,
            "week_count": int,
        },
    )
    validated["week_count"] = 8

    assert content["week_count"] == 4


def test_v1_fake_provider_records_request_before_configured_failure() -> None:
    """Preserve request observability when the provider fails."""
    failure = RuntimeError("provider unavailable")
    provider = FakeAIProvider(failures=(failure,))
    request = _request()

    with pytest.raises(RuntimeError, match="provider unavailable"):
        provider.generate(request)

    assert provider.requests == (request,)


def test_v1_fake_provider_exhaustion_is_explicit_and_records_request() -> None:
    """Fail explicitly instead of falling back to network or hidden behavior."""
    provider = FakeAIProvider()
    request = _request("exhausted")

    with pytest.raises(RuntimeError, match="no configured response"):
        provider.generate(request)

    assert provider.requests == (request,)


def test_v1_fake_provider_failure_precedes_configured_response() -> None:
    """Keep deterministic failure precedence when both outcomes are configured."""
    response = AIResponse(content={"ok": True}, metadata={})
    provider = FakeAIProvider(
        responses=(response,),
        failures=(ValueError("first failure"),),
    )
    first_request = _request("first")
    second_request = _request("second")

    with pytest.raises(ValueError, match="first failure"):
        provider.generate(first_request)

    assert provider.generate(second_request) is response
    assert provider.requests == (first_request, second_request)


def test_v1_fake_provider_repeated_sequence_is_deterministic() -> None:
    """Equivalent configured providers produce equivalent ordered outcomes."""
    responses = (
        AIResponse(content={"value": 1}, metadata={}),
        AIResponse(content={"value": 2}, metadata={}),
    )
    first = FakeAIProvider(responses=responses)
    second = FakeAIProvider(responses=responses)
    requests = (_request("one"), _request("two"))

    first_results = tuple(first.generate(request) for request in requests)
    second_results = tuple(second.generate(request) for request in requests)

    assert first_results == second_results == responses
    assert first.requests == second.requests == requests
