from __future__ import annotations

from dataclasses import dataclass
from types import SimpleNamespace
from typing import Any

from generator.ai.models import AIRequest, AIResponse
from generator.ai.providers.openai import OpenAIProviderAdapter


@dataclass(frozen=True, slots=True)
class StubOpenAIOutputText:
    text: str


class StubResponsesAPI:
    def __init__(
        self,
        *,
        response: object,
    ) -> None:
        self._response = response
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: object) -> object:
        self.calls.append(dict(kwargs))
        return self._response


class StubOpenAIClient:
    def __init__(
        self,
        *,
        response: object,
    ) -> None:
        self.responses = StubResponsesAPI(
            response=response,
        )


def _request() -> AIRequest:
    return AIRequest(
        task="courseware.build",
        instructions="Build a structured course.",
        context={
            "course_id": "modern-java",
            "language": "zh-TW",
        },
        response_contract="courseware.course.v1",
    )


def _provider_response() -> object:
    return SimpleNamespace(
        id="resp_001",
        model="gpt-test",
        status="completed",
        output_text='{"course_id":"modern-java","weeks":[]}',
        usage=SimpleNamespace(
            input_tokens=11,
            output_tokens=7,
            total_tokens=18,
        ),
    )


def test_openai_adapter_returns_ai_response() -> None:
    client = StubOpenAIClient(
        response=_provider_response(),
    )
    adapter = OpenAIProviderAdapter(
        client=client,
        model="gpt-test",
        timeout_seconds=30.0,
    )

    response = adapter.generate(_request())

    assert isinstance(response, AIResponse)
    assert response.content == '{"course_id":"modern-java","weeks":[]}'


def test_openai_adapter_translates_request_to_responses_api() -> None:
    client = StubOpenAIClient(
        response=_provider_response(),
    )
    adapter = OpenAIProviderAdapter(
        client=client,
        model="gpt-test",
        timeout_seconds=30.0,
    )

    adapter.generate(_request())

    assert len(client.responses.calls) == 1

    call = client.responses.calls[0]

    assert call["model"] == "gpt-test"
    assert call["instructions"] == "Build a structured course."
    assert call["input"] == {
        "task": "courseware.build",
        "context": {
            "course_id": "modern-java",
            "language": "zh-TW",
        },
        "response_contract": "courseware.course.v1",
    }


def test_openai_adapter_normalizes_provider_metadata() -> None:
    client = StubOpenAIClient(
        response=_provider_response(),
    )
    adapter = OpenAIProviderAdapter(
        client=client,
        model="gpt-test",
        timeout_seconds=30.0,
    )

    response = adapter.generate(_request())

    assert response.metadata == {
        "provider": "openai",
        "model": "gpt-test",
        "response_id": "resp_001",
        "status": "completed",
        "usage": {
            "input_tokens": 11,
            "output_tokens": 7,
            "total_tokens": 18,
        },
    }


def test_openai_adapter_does_not_mutate_ai_request() -> None:
    request = _request()
    original_context = dict(request.context)
    client = StubOpenAIClient(
        response=_provider_response(),
    )
    adapter = OpenAIProviderAdapter(
        client=client,
        model="gpt-test",
        timeout_seconds=30.0,
    )

    adapter.generate(request)

    assert dict(request.context) == original_context


def test_openai_adapter_uses_configured_model() -> None:
    client = StubOpenAIClient(
        response=_provider_response(),
    )
    adapter = OpenAIProviderAdapter(
        client=client,
        model="gpt-custom",
        timeout_seconds=12.0,
    )

    adapter.generate(_request())

    assert client.responses.calls[0]["model"] == "gpt-custom"
