"""Fail-closed experimental provider resolution for the unregistered AI CLI."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from generator.ai.protocols import AIProvider
from generator.ai.providers.openai import OpenAIProviderAdapter

_EXPERIMENTAL_PROVIDERS = frozenset({"openai"})

ClientFactory = Callable[..., Any]


def resolve_experimental_provider(
    *,
    name: str,
    client_factory: ClientFactory | None,
    api_key: str | None,
    model: str,
    timeout_seconds: float,
) -> AIProvider:
    """Resolve one explicitly selected provider using injected configuration.

    This boundary deliberately owns neither environment lookup nor SDK import.
    The future CLI composition root must supply both configuration and a client
    factory only after the user explicitly opts in with ``--provider``.
    """
    normalized_name = name.strip().lower()
    if not normalized_name:
        raise ValueError("experimental provider name must not be empty")
    if normalized_name not in _EXPERIMENTAL_PROVIDERS:
        raise ValueError(f"unsupported experimental provider: {normalized_name}")
    if client_factory is None:
        raise ValueError("experimental provider requires an injected client factory")
    if not isinstance(api_key, str) or not api_key.strip():
        raise ValueError("experimental provider requires an explicit API key")

    client = client_factory(api_key=api_key.strip())
    return OpenAIProviderAdapter(
        client=client,
        model=model,
        timeout_seconds=timeout_seconds,
    )
