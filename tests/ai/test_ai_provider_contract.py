from __future__ import annotations

from typing import Protocol

from generator.ai.models import AIRequest, AIResponse
from generator.ai.protocols import AIProvider


class _ContractProvider:
    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        return AIResponse(
            content={"task": request.task},
            metadata={"provider": "contract"},
        )


def test_ai_provider_is_a_protocol() -> None:
    assert issubclass(AIProvider, Protocol)


def test_ai_provider_supports_structural_implementation() -> None:
    provider = _ContractProvider()

    request = AIRequest(
        task="courseware.generate",
        instructions="Generate courseware.",
        context={},
    )

    response = provider.generate(request)

    assert isinstance(response, AIResponse)
    assert response.content == {"task": "courseware.generate"}


def test_ai_provider_contract_uses_opl_request_and_response_models() -> None:
    provider: AIProvider = _ContractProvider()

    request = AIRequest(
        task="courseware.review",
        instructions="Review courseware.",
        context={"course_id": "modern-java"},
    )

    response = provider.generate(request)

    assert response.metadata["provider"] == "contract"


def test_ai_provider_is_runtime_checkable() -> None:
    provider = _ContractProvider()

    assert isinstance(provider, AIProvider)
