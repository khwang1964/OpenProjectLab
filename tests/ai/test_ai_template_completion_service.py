from __future__ import annotations

from generator.ai.models import AIRequest, AIResponse
from generator.ai.template_completion import AITemplateCompletionResult
from generator.ai.template_completion_service import AITemplateCompletionService
from generator.ai.testing import FakeAIProvider


def _request() -> AIRequest:
    return AIRequest(
        task="template.complete",
        instructions="Complete a structured template draft.",
        context={
            "template_name": "week/README.md.j2",
            "available_context_keys": [
                "week.number",
                "week.title",
            ],
        },
        response_contract="template.completion.v1",
    )


def _response() -> AIResponse:
    return AIResponse(
        content={
            "template_name": "week/README.md.j2",
            "content": "# Week {{ week.number }}: {{ week.title }}\n",
            "context_keys": [
                "week.number",
                "week.title",
            ],
        },
        metadata={
            "provider": "fake",
            "model": "deterministic-test-model",
        },
    )


def test_complete_returns_template_completion_result() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    service = AITemplateCompletionService(
        provider=provider,
    )

    result = service.complete(_request())

    assert isinstance(result, AITemplateCompletionResult)
    assert result.template_name == "week/README.md.j2"
    assert result.content == "# Week {{ week.number }}: {{ week.title }}\n"


def test_complete_passes_request_to_provider_unchanged() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    service = AITemplateCompletionService(
        provider=provider,
    )
    request = _request()

    service.complete(request)

    assert provider.requests == (request,)


def test_complete_preserves_context_key_order() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    service = AITemplateCompletionService(
        provider=provider,
    )

    result = service.complete(_request())

    assert result.context_keys == (
        "week.number",
        "week.title",
    )


def test_complete_is_deterministic_with_fake_provider() -> None:
    response = _response()

    first = AITemplateCompletionService(
        provider=FakeAIProvider(
            responses=(response,),
        ),
    ).complete(_request())

    second = AITemplateCompletionService(
        provider=FakeAIProvider(
            responses=(response,),
        ),
    ).complete(_request())

    assert first == second


def test_complete_keeps_provider_metadata_out_of_result() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    service = AITemplateCompletionService(
        provider=provider,
    )

    result = service.complete(_request())

    assert not hasattr(result, "provider")
    assert not hasattr(result, "model")
    assert not hasattr(result, "metadata")


def test_template_completion_service_uses_injected_provider() -> None:
    first_service = AITemplateCompletionService(
        provider=FakeAIProvider(
            responses=(_response(),),
        ),
    )
    second_service = AITemplateCompletionService(
        provider=FakeAIProvider(
            responses=(
                AIResponse(
                    content={
                        "template_name": "course/README.md.j2",
                        "content": "# {{ course.title }}\n",
                        "context_keys": ["course.title"],
                    },
                    metadata={"provider": "fake"},
                ),
            ),
        ),
    )

    assert first_service.complete(_request()).template_name == "week/README.md.j2"
    assert second_service.complete(_request()).template_name == "course/README.md.j2"
