from __future__ import annotations

from types import SimpleNamespace
from typing import Any

import pytest

from generator.ai.errors import AIAuthenticationError
from generator.ai.models import AIRequest
from generator.ai.providers.openai import OpenAIProviderAdapter

_SECRET = "sk-opl-test-secret-do-not-leak"


class CredentialAwareResponsesAPI:
    def __init__(
        self,
        *,
        fail_authentication: bool = False,
    ) -> None:
        self._fail_authentication = fail_authentication
        self.calls: list[dict[str, Any]] = []

    def create(self, **kwargs: object) -> object:
        self.calls.append(dict(kwargs))

        if self._fail_authentication:
            raise PermissionError(f"authentication failed for {_SECRET}")

        return SimpleNamespace(
            id="resp_credential",
            model="gpt-test",
            status="completed",
            output_text='{"ok":true}',
            usage=None,
        )


class CredentialAwareOpenAIClient:
    def __init__(
        self,
        *,
        api_key: str,
        fail_authentication: bool = False,
    ) -> None:
        self._api_key = api_key
        self.responses = CredentialAwareResponsesAPI(
            fail_authentication=fail_authentication,
        )


def _request() -> AIRequest:
    return AIRequest(
        task="documentation.generate",
        instructions="Generate documentation.",
        context={
            "topic": "AI Integration",
        },
        response_contract="documentation.draft.v1",
    )


def test_openai_credential_does_not_enter_ai_request() -> None:
    request = _request()

    assert _SECRET not in repr(request)
    assert _SECRET not in request.instructions
    assert _SECRET not in repr(request.context)


def test_openai_credential_is_not_forwarded_in_request_payload() -> None:
    client = CredentialAwareOpenAIClient(
        api_key=_SECRET,
    )
    adapter = OpenAIProviderAdapter(
        client=client,
        model="gpt-test",
        timeout_seconds=30.0,
    )

    adapter.generate(_request())

    assert len(client.responses.calls) == 1
    assert _SECRET not in repr(client.responses.calls[0])


def test_openai_credential_does_not_enter_ai_response() -> None:
    client = CredentialAwareOpenAIClient(
        api_key=_SECRET,
    )
    adapter = OpenAIProviderAdapter(
        client=client,
        model="gpt-test",
        timeout_seconds=30.0,
    )

    response = adapter.generate(_request())

    assert _SECRET not in repr(response)
    assert _SECRET not in repr(response.metadata)


def test_sanitized_openai_authentication_error_does_not_expose_secret() -> None:
    client = CredentialAwareOpenAIClient(
        api_key=_SECRET,
        fail_authentication=True,
    )
    adapter = OpenAIProviderAdapter(
        client=client,
        model="gpt-test",
        timeout_seconds=30.0,
    )

    with pytest.raises(AIAuthenticationError) as exc_info:
        adapter.generate(_request())

    assert _SECRET not in str(exc_info.value)
    assert _SECRET not in repr(exc_info.value)


def test_openai_authentication_failure_has_no_filesystem_side_effect(
    tmp_path,
) -> None:
    client = CredentialAwareOpenAIClient(
        api_key=_SECRET,
        fail_authentication=True,
    )
    adapter = OpenAIProviderAdapter(
        client=client,
        model="gpt-test",
        timeout_seconds=30.0,
    )

    with pytest.raises(AIAuthenticationError):
        adapter.generate(_request())

    assert list(tmp_path.iterdir()) == []
