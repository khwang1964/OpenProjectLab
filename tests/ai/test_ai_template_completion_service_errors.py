from __future__ import annotations

import pytest

from generator.ai.errors import AIResponseValidationError
from generator.ai.models import AIRequest, AIResponse
from generator.ai.template_completion_service import AITemplateCompletionService
from generator.ai.testing import FakeAIProvider


def _request() -> AIRequest:
    return AIRequest(
        task="template.complete",
        instructions="Complete a structured template draft.",
        context={"template_name": "week/README.md.j2"},
        response_contract="template.completion.v1",
    )


def test_complete_propagates_provider_failure() -> None:
    provider = FakeAIProvider(
        failures=(RuntimeError("simulated provider failure"),),
    )
    service = AITemplateCompletionService(
        provider=provider,
    )

    with pytest.raises(
        RuntimeError,
        match="simulated provider failure",
    ):
        service.complete(_request())


def test_complete_propagates_response_validation_failure() -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content=None,
                metadata={"provider": "fake"},
            ),
        ),
    )
    service = AITemplateCompletionService(
        provider=provider,
    )

    with pytest.raises(AIResponseValidationError):
        service.complete(_request())


def test_complete_propagates_missing_field_failure() -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content={
                    "template_name": "week/README.md.j2",
                    "content": "# Week\n",
                },
                metadata={"provider": "fake"},
            ),
        ),
    )
    service = AITemplateCompletionService(
        provider=provider,
    )

    with pytest.raises(
        AIResponseValidationError,
        match="context_keys",
    ):
        service.complete(_request())


def test_complete_propagates_invalid_context_key_failure() -> None:
    provider = FakeAIProvider(
        responses=(
            AIResponse(
                content={
                    "template_name": "week/README.md.j2",
                    "content": "# Week {{ week.number }}\n",
                    "context_keys": [
                        "week.number",
                        123,
                    ],
                },
                metadata={"provider": "fake"},
            ),
        ),
    )
    service = AITemplateCompletionService(
        provider=provider,
    )

    with pytest.raises(
        AIResponseValidationError,
        match="context_keys",
    ):
        service.complete(_request())


def test_provider_failure_records_request_before_raising() -> None:
    provider = FakeAIProvider(
        failures=(RuntimeError("simulated provider failure"),),
    )
    service = AITemplateCompletionService(
        provider=provider,
    )
    request = _request()

    with pytest.raises(RuntimeError):
        service.complete(request)

    assert provider.requests == (request,)


def test_template_completion_failure_has_no_filesystem_side_effect(
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
    service = AITemplateCompletionService(
        provider=provider,
    )

    with pytest.raises(AIResponseValidationError):
        service.complete(_request())

    assert list(tmp_path.iterdir()) == []
