from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from generator.ai.models import AIRequest, AIResponse


@dataclass(frozen=True, slots=True)
class StubProviderResponse:
    content: object
    model: str
    finish_reason: str
    request_id: str


class StubProviderClient:
    def __init__(
        self,
        *,
        response: StubProviderResponse,
    ) -> None:
        self._response = response
        self.calls: list[dict[str, Any]] = []

    def generate(
        self,
        *,
        model: str,
        instructions: str,
        context: dict[str, object],
        response_contract: str | None,
        timeout: float,
    ) -> StubProviderResponse:
        self.calls.append(
            {
                "model": model,
                "instructions": instructions,
                "context": context,
                "response_contract": response_contract,
                "timeout": timeout,
            }
        )
        return self._response


class ContractProviderAdapter:
    """Test-only reference adapter used to define the Step 6.10 contract."""

    def __init__(
        self,
        *,
        client: StubProviderClient,
        model: str,
        timeout_seconds: float,
    ) -> None:
        self._client = client
        self._model = model
        self._timeout_seconds = timeout_seconds

    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        provider_response = self._client.generate(
            model=self._model,
            instructions=request.instructions,
            context=dict(request.context),
            response_contract=request.response_contract,
            timeout=self._timeout_seconds,
        )

        return AIResponse(
            content=provider_response.content,
            metadata={
                "provider": "stub",
                "model": provider_response.model,
                "finish_reason": provider_response.finish_reason,
                "request_id": provider_response.request_id,
            },
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


def _provider_response() -> StubProviderResponse:
    return StubProviderResponse(
        content={
            "course_id": "modern-java",
            "title": "Modern Java",
            "language": "zh-TW",
            "weeks": [],
        },
        model="stub-model",
        finish_reason="stop",
        request_id="request-001",
    )


def test_provider_adapter_accepts_ai_request_and_returns_ai_response() -> None:
    client = StubProviderClient(
        response=_provider_response(),
    )
    adapter = ContractProviderAdapter(
        client=client,
        model="stub-model",
        timeout_seconds=30.0,
    )

    response = adapter.generate(_request())

    assert isinstance(response, AIResponse)
    assert response.content == _provider_response().content


def test_provider_adapter_translates_request_deterministically() -> None:
    client = StubProviderClient(
        response=_provider_response(),
    )
    adapter = ContractProviderAdapter(
        client=client,
        model="stub-model",
        timeout_seconds=30.0,
    )

    adapter.generate(_request())

    assert client.calls == [
        {
            "model": "stub-model",
            "instructions": "Build a structured course.",
            "context": {
                "course_id": "modern-java",
                "language": "zh-TW",
            },
            "response_contract": "courseware.course.v1",
            "timeout": 30.0,
        }
    ]


def test_provider_adapter_normalizes_provider_metadata() -> None:
    client = StubProviderClient(
        response=_provider_response(),
    )
    adapter = ContractProviderAdapter(
        client=client,
        model="stub-model",
        timeout_seconds=30.0,
    )

    response = adapter.generate(_request())

    assert response.metadata == {
        "provider": "stub",
        "model": "stub-model",
        "finish_reason": "stop",
        "request_id": "request-001",
    }


def test_provider_adapter_preserves_ai_request() -> None:
    request = _request()
    original_context = dict(request.context)
    client = StubProviderClient(
        response=_provider_response(),
    )
    adapter = ContractProviderAdapter(
        client=client,
        model="stub-model",
        timeout_seconds=30.0,
    )

    adapter.generate(request)

    assert dict(request.context) == original_context


def test_provider_adapter_uses_configured_model_and_finite_timeout() -> None:
    client = StubProviderClient(
        response=_provider_response(),
    )
    adapter = ContractProviderAdapter(
        client=client,
        model="contract-model",
        timeout_seconds=12.5,
    )

    adapter.generate(_request())

    assert client.calls[0]["model"] == "contract-model"
    assert client.calls[0]["timeout"] == 12.5
    assert client.calls[0]["timeout"] > 0
