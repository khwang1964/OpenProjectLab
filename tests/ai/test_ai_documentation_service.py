from __future__ import annotations

from generator.ai.documentation import AIDocumentDraft
from generator.ai.documentation_service import AIDocumentationService
from generator.ai.models import AIRequest, AIResponse
from generator.ai.testing import FakeAIProvider


def _request() -> AIRequest:
    return AIRequest(
        task="documentation.generate",
        instructions="Generate a structured documentation draft.",
        context={
            "topic": "AI Integration",
            "audience": "maintainers",
        },
        response_contract="documentation.draft.v1",
    )


def _response() -> AIResponse:
    return AIResponse(
        content={
            "title": "AI Integration Overview",
            "format": "markdown",
            "content": "# AI Integration\n\nStructured documentation draft.\n",
        },
        metadata={
            "provider": "fake",
            "model": "deterministic-test-model",
        },
    )


def test_generate_documentation_returns_document_draft() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    service = AIDocumentationService(
        provider=provider,
    )

    draft = service.generate(_request())

    assert isinstance(draft, AIDocumentDraft)
    assert draft.title == "AI Integration Overview"
    assert draft.format == "markdown"


def test_generate_documentation_passes_request_to_provider_unchanged() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    service = AIDocumentationService(
        provider=provider,
    )
    request = _request()

    service.generate(request)

    assert provider.requests == (request,)


def test_generate_documentation_preserves_draft_content() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    service = AIDocumentationService(
        provider=provider,
    )

    draft = service.generate(_request())

    assert draft.content == ("# AI Integration\n\nStructured documentation draft.\n")


def test_generate_documentation_is_deterministic_with_fake_provider() -> None:
    response = _response()

    first = AIDocumentationService(
        provider=FakeAIProvider(
            responses=(response,),
        ),
    ).generate(_request())

    second = AIDocumentationService(
        provider=FakeAIProvider(
            responses=(response,),
        ),
    ).generate(_request())

    assert first == second


def test_generate_documentation_keeps_provider_metadata_out_of_draft() -> None:
    provider = FakeAIProvider(
        responses=(_response(),),
    )
    service = AIDocumentationService(
        provider=provider,
    )

    draft = service.generate(_request())

    assert not hasattr(draft, "provider")
    assert not hasattr(draft, "model")
    assert not hasattr(draft, "metadata")


def test_documentation_service_uses_injected_provider() -> None:
    first_service = AIDocumentationService(
        provider=FakeAIProvider(
            responses=(_response(),),
        ),
    )
    second_service = AIDocumentationService(
        provider=FakeAIProvider(
            responses=(
                AIResponse(
                    content={
                        "title": "Plain Text Draft",
                        "format": "text",
                        "content": "Plain text documentation.",
                    },
                    metadata={"provider": "fake"},
                ),
            ),
        ),
    )

    assert first_service.generate(_request()).format == "markdown"
    assert second_service.generate(_request()).format == "text"
