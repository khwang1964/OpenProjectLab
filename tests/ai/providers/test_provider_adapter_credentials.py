from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from generator.ai.errors import AIAuthenticationError
from generator.ai.models import AIRequest, AIResponse

_SECRET = "opl-test-secret-do-not-leak"


@dataclass(frozen=True, slots=True)
class CredentialAwareResponse:
    content: object
    model: str


class CredentialAwareClient:
    def __init__(
        self,
        *,
        api_key: str,
        response: CredentialAwareResponse | None = None,
        fail_authentication: bool = False,
    ) -> None:
        self._api_key = api_key
        self._response = response
        self._fail_authentication = fail_authentication
        self.calls: list[dict[str, Any]] = []

    def generate(
        self,
        *,
        instructions: str,
        context: dict[str, object],
        timeout: float,
    ) -> CredentialAwareResponse:
        self.calls.append(
            {
                "instructions": instructions,
                "context": context,
                "timeout": timeout,
            }
        )

        if self._fail_authentication:
            raise PermissionError(f"authentication failed for key {_SECRET}")

        if self._response is None:
            raise AssertionError("response must be configured")

        return self._response


class CredentialContractProviderAdapter:
    """Test-only adapter keeping credential ownership inside the client."""

    def __init__(
        self,
        *,
        client: CredentialAwareClient,
        timeout_seconds: float,
    ) -> None:
        self._client = client
        self._timeout_seconds = timeout_seconds

    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        try:
            provider_response = self._client.generate(
                instructions=request.instructions,
                context=dict(request.context),
                timeout=self._timeout_seconds,
            )
        except PermissionError as exc:
            raise AIAuthenticationError("AI provider authentication failed.") from exc

        return AIResponse(
            content=provider_response.content,
            metadata={
                "provider": "credential-stub",
                "model": provider_response.model,
            },
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


def test_credential_does_not_enter_ai_request() -> None:
    request = _request()

    assert _SECRET not in repr(request)
    assert _SECRET not in request.instructions
    assert _SECRET not in repr(request.context)


def test_credential_does_not_enter_ai_response_metadata() -> None:
    client = CredentialAwareClient(
        api_key=_SECRET,
        response=CredentialAwareResponse(
            content={
                "title": "AI Integration",
                "format": "markdown",
                "content": "# AI Integration\n",
            },
            model="credential-stub-model",
        ),
    )
    adapter = CredentialContractProviderAdapter(
        client=client,
        timeout_seconds=30.0,
    )

    response = adapter.generate(_request())

    assert _SECRET not in repr(response)
    assert _SECRET not in repr(response.metadata)
    assert response.metadata == {
        "provider": "credential-stub",
        "model": "credential-stub-model",
    }


def test_credential_is_not_forwarded_in_provider_request_payload() -> None:
    client = CredentialAwareClient(
        api_key=_SECRET,
        response=CredentialAwareResponse(
            content={"ok": True},
            model="credential-stub-model",
        ),
    )
    adapter = CredentialContractProviderAdapter(
        client=client,
        timeout_seconds=30.0,
    )

    adapter.generate(_request())

    assert len(client.calls) == 1
    assert _SECRET not in repr(client.calls[0])
    assert client.calls[0]["context"] == {
        "topic": "AI Integration",
    }


def test_sanitized_authentication_error_does_not_expose_credential() -> None:
    client = CredentialAwareClient(
        api_key=_SECRET,
        fail_authentication=True,
    )
    adapter = CredentialContractProviderAdapter(
        client=client,
        timeout_seconds=30.0,
    )

    with pytest.raises(
        AIAuthenticationError,
        match="authentication failed",
    ) as exc_info:
        adapter.generate(_request())

    assert _SECRET not in str(exc_info.value)
    assert _SECRET not in repr(exc_info.value)


def test_credential_failure_has_no_filesystem_side_effect(
    tmp_path,
) -> None:
    client = CredentialAwareClient(
        api_key=_SECRET,
        fail_authentication=True,
    )
    adapter = CredentialContractProviderAdapter(
        client=client,
        timeout_seconds=30.0,
    )

    with pytest.raises(AIAuthenticationError):
        adapter.generate(_request())

    assert list(tmp_path.iterdir()) == []
