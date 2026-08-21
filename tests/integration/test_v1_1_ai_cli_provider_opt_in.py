"""Executable contract for the v1.1.6.7 provider opt-in boundary."""

from __future__ import annotations

from pathlib import Path

import pytest

from generator.ai.providers.openai import OpenAIProviderAdapter
from generator.cli.ai_provider import resolve_experimental_provider

ROOT = Path(__file__).parents[2]


class _RecordingFactory:
    def __init__(self) -> None:
        self.api_keys: list[str] = []

    def __call__(self, *, api_key: str) -> object:
        self.api_keys.append(api_key)
        return object()


def test_explicit_openai_selection_uses_injected_factory() -> None:
    factory = _RecordingFactory()

    provider = resolve_experimental_provider(
        name="openai",
        client_factory=factory,
        api_key=" secret ",
        model="gpt-test",
        timeout_seconds=12.5,
    )

    assert isinstance(provider, OpenAIProviderAdapter)
    assert factory.api_keys == ["secret"]


@pytest.mark.parametrize("name", ["", "   ", "unknown", "local-response"])
def test_provider_name_fails_closed_before_client_construction(name: str) -> None:
    factory = _RecordingFactory()

    with pytest.raises(ValueError):
        resolve_experimental_provider(
            name=name,
            client_factory=factory,
            api_key="secret",
            model="gpt-test",
            timeout_seconds=10.0,
        )

    assert factory.api_keys == []


def test_missing_factory_fails_closed() -> None:
    with pytest.raises(ValueError, match="client factory"):
        resolve_experimental_provider(
            name="openai",
            client_factory=None,
            api_key="secret",
            model="gpt-test",
            timeout_seconds=10.0,
        )


@pytest.mark.parametrize("api_key", [None, "", "   "])
def test_missing_api_key_fails_before_client_construction(api_key: str | None) -> None:
    factory = _RecordingFactory()

    with pytest.raises(ValueError, match="API key"):
        resolve_experimental_provider(
            name="openai",
            client_factory=factory,
            api_key=api_key,
            model="gpt-test",
            timeout_seconds=10.0,
        )

    assert factory.api_keys == []


def test_provider_boundary_has_no_sdk_environment_or_test_double_ownership() -> None:
    source = (ROOT / "generator" / "cli" / "ai_provider.py").read_text(encoding="utf-8")

    assert "import openai" not in source
    assert "OPENAI_API_KEY" not in source
    assert "os.environ" not in source
    assert "FakeAIProvider" not in source


def test_production_ai_parser_remains_unregistered() -> None:
    from generator.cli.main import build_parser

    parser = build_parser()
    choices = parser._subparsers._group_actions[0].choices
    assert "ai" not in choices
