from __future__ import annotations

import pytest

from generator.ai.documentation_service import AIDocumentationService
from generator.ai.errors import AIResponseValidationError
from generator.ai.models import AIRequest, AIResponse
from generator.ai.testing import FakeAIProvider


def _request() -> AIRequest:
    return AIRequest(
        task="documentation.generate",
        instructions="Generate a structured documentation draft.",
        context={"topic": "AI Integration"},
        response_contract="documentation.draft.v1",
    )


def test_generate_documentation_propagates_provider_failure() -> None:
    provider = FakeAIProvider(
        failures=(RuntimeError("simulated provider failure"),),
    )
    service = AIDocumentationService(
        provider=provider,
    )

    with pytest.raises(
        RuntimeError,
        match="simulated provider failure",
    ):
        service.generate(_request())


def test_generate_documentation_propagates_response_validation_failure() -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content=None,
                metadata={"provider": "fake"},
            ),
        ),
    )
    service = AIDocumentationService(
        provider=provider,
    )

    with pytest.raises(AIResponseValidationError):
        service.generate(_request())


def test_generate_documentation_propagates_missing_field_failure() -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content={
                    "title": "Example",
                    "format": "markdown",
                },
                metadata={"provider": "fake"},
            ),
        ),
    )
    service = AIDocumentationService(
        provider=provider,
    )

    with pytest.raises(
        AIResponseValidationError,
        match="content",
    ):
        service.generate(_request())


def test_generate_documentation_propagates_unsupported_format_failure() -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content={
                    "title": "Example",
                    "format": "html",
                    "content": "<h1>Example</h1>",
                },
                metadata={"provider": "fake"},
            ),
        ),
    )
    service = AIDocumentationService(
        provider=provider,
    )

    with pytest.raises(
        AIResponseValidationError,
        match="format",
    ):
        service.generate(_request())


def test_provider_failure_records_request_before_raising() -> None:
    provider = FakeAIProvider(
        failures=(RuntimeError("simulated provider failure"),),
    )
    service = AIDocumentationService(
        provider=provider,
    )
    request = _request()

    with pytest.raises(RuntimeError):
        service.generate(request)

    assert provider.requests == (request,)


def test_documentation_failure_has_no_filesystem_side_effect(
    tmp_path,
) -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content=None,
                metadata={"provider": "fake"},
            ),
        ),
    )
    service = AIDocumentationService(
        provider=provider,
    )

    with pytest.raises(AIResponseValidationError):
        service.generate(_request())

    assert list(tmp_path.iterdir()) == []
