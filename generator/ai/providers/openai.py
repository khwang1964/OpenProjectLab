"""OpenAI provider adapter.

This module intentionally depends only on the provider-independent OPL AI
contracts. A configured OpenAI-compatible client is injected by the composition
root, which keeps credentials, network construction, and SDK ownership outside
the application layer and enables deterministic no-network tests.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ..errors import (
    AIAuthenticationError,
    AIProviderError,
    AIRateLimitError,
    AITimeoutError,
    AIUnavailableError,
)
from ..models import AIRequest, AIResponse

_AUTHENTICATION_ERROR_NAMES = frozenset(
    {
        "AuthenticationError",
        "PermissionError",
    }
)
_RATE_LIMIT_ERROR_NAMES = frozenset(
    {
        "RateLimitError",
    }
)
_TIMEOUT_ERROR_NAMES = frozenset(
    {
        "APITimeoutError",
        "TimeoutError",
    }
)
_UNAVAILABLE_ERROR_NAMES = frozenset(
    {
        "APIConnectionError",
    }
)
_PROVIDER_ERROR_NAMES = frozenset(
    {
        "APIStatusError",
        "APIError",
    }
)


class OpenAIProviderAdapter:
    """Adapt an injected OpenAI-compatible client to the OPL ``AIProvider`` contract."""

    def __init__(
        self,
        *,
        client: Any,
        model: str,
        timeout_seconds: float,
    ) -> None:
        if not model:
            raise ValueError("OpenAI provider model must not be empty.")

        if timeout_seconds <= 0:
            raise ValueError("OpenAI provider timeout_seconds must be greater than zero.")

        self._client = client
        self._model = model
        self._timeout_seconds = timeout_seconds

    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        """Generate an OPL response through the injected OpenAI client."""
        try:
            provider_response = self._client.responses.create(
                model=self._model,
                instructions=request.instructions,
                input={
                    "task": request.task,
                    "context": dict(request.context),
                    "response_contract": request.response_contract,
                },
                timeout=self._timeout_seconds,
            )
        except Exception as exc:
            self._raise_provider_error(exc)
            raise AssertionError("provider error conversion unexpectedly returned") from exc

        content = getattr(provider_response, "output_text", None)

        if not isinstance(content, str) or not content:
            raise AIProviderError("OpenAI provider returned a response without usable output text.")

        metadata: dict[str, object] = {
            "provider": "openai",
            "model": getattr(provider_response, "model", self._model),
            "response_id": getattr(provider_response, "id", None),
            "status": getattr(provider_response, "status", None),
        }

        usage = self._normalize_usage(getattr(provider_response, "usage", None))
        if usage is not None:
            metadata["usage"] = usage

        return AIResponse(
            content=content,
            metadata=metadata,
        )

    @staticmethod
    def _normalize_usage(
        usage: object,
    ) -> dict[str, object] | None:
        if usage is None:
            return None

        if isinstance(usage, Mapping):
            values = {
                "input_tokens": usage.get("input_tokens"),
                "output_tokens": usage.get("output_tokens"),
                "total_tokens": usage.get("total_tokens"),
            }
        else:
            values = {
                "input_tokens": getattr(usage, "input_tokens", None),
                "output_tokens": getattr(usage, "output_tokens", None),
                "total_tokens": getattr(usage, "total_tokens", None),
            }

        return values

    @staticmethod
    def _raise_provider_error(
        exc: Exception,
    ) -> None:
        error_name = type(exc).__name__

        if error_name in _AUTHENTICATION_ERROR_NAMES:
            raise AIAuthenticationError("OpenAI provider authentication failed.") from exc

        if error_name in _RATE_LIMIT_ERROR_NAMES:
            raise AIRateLimitError("OpenAI provider rate limit exceeded.") from exc

        if error_name in _TIMEOUT_ERROR_NAMES:
            raise AITimeoutError("OpenAI provider request timed out.") from exc

        if error_name in _UNAVAILABLE_ERROR_NAMES:
            raise AIUnavailableError("OpenAI provider is unavailable.") from exc

        if error_name in _PROVIDER_ERROR_NAMES:
            raise AIProviderError("OpenAI provider request failed.") from exc

        raise exc
