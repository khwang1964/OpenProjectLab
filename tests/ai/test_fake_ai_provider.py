from __future__ import annotations

import pytest

from generator.ai.models import AIRequest, AIResponse
from generator.ai.testing import FakeAIProvider


def _request(task: str = "courseware.generate") -> AIRequest:
    return AIRequest(
        task=task,
        instructions="Execute deterministic contract behavior.",
        context={"course_id": "modern-java"},
        response_contract="courseware.course.v1",
    )


def _response(title: str = "Modern Java") -> AIResponse:
    return AIResponse(
        content={
            "course_id": "modern-java",
            "title": title,
        },
        metadata={
            "provider": "fake",
            "model": "deterministic-test-model",
        },
    )


def test_fake_ai_provider_returns_configured_response() -> None:
    expected = _response()
    provider = FakeAIProvider(
        responses=(expected,),
    )

    actual = provider.generate(_request())

    assert actual == expected


def test_fake_ai_provider_records_requests_in_order() -> None:
    provider = FakeAIProvider(
        responses=(
            _response("First"),
            _response("Second"),
        ),
    )

    first = _request("courseware.generate")
    second = _request("courseware.review")

    provider.generate(first)
    provider.generate(second)

    assert provider.requests == (first, second)


def test_fake_ai_provider_returns_responses_in_order() -> None:
    first_response = _response("First")
    second_response = _response("Second")

    provider = FakeAIProvider(
        responses=(
            first_response,
            second_response,
        ),
    )

    assert provider.generate(_request()) == first_response
    assert provider.generate(_request()) == second_response


def test_fake_ai_provider_can_raise_configured_failure() -> None:
    failure = RuntimeError("simulated provider failure")
    provider = FakeAIProvider(
        failures=(failure,),
    )

    with pytest.raises(RuntimeError, match="simulated provider failure"):
        provider.generate(_request())


def test_fake_ai_provider_failure_is_deterministic_and_records_request() -> None:
    failure = RuntimeError("simulated provider failure")
    provider = FakeAIProvider(
        failures=(failure,),
    )

    request = _request("courseware.review")

    with pytest.raises(RuntimeError, match="simulated provider failure"):
        provider.generate(request)

    assert provider.requests == (request,)


def test_fake_ai_provider_requires_no_network_or_credentials() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )

    response = provider.generate(_request())

    assert response.metadata["provider"] == "fake"
