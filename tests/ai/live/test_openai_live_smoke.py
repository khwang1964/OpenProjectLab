from __future__ import annotations

import os

import pytest

from generator.ai.models import AIRequest, AIResponse
from generator.ai.providers.openai import OpenAIProviderAdapter

pytestmark = pytest.mark.ai_live


def _require_openai_api_key() -> str:
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        pytest.skip("OPENAI_API_KEY is required for live OpenAI provider tests.")

    return api_key


def test_openai_live_smoke() -> None:
    api_key = _require_openai_api_key()

    openai = pytest.importorskip(
        "openai",
        reason="The OpenAI Python SDK is required for live OpenAI tests.",
    )

    client = openai.OpenAI(
        api_key=api_key,
        timeout=30.0,
        max_retries=0,
    )
    adapter = OpenAIProviderAdapter(
        client=client,
        model=os.getenv(
            "OPENAI_TEST_MODEL",
            "gpt-4.1-mini",
        ),
        timeout_seconds=30.0,
    )

    response = adapter.generate(
        AIRequest(
            task="live.smoke",
            instructions=(
                "Return a very short plain-text response confirming the request succeeded."
            ),
            context={
                "purpose": "OpenProjectLab live provider smoke test",
            },
            response_contract=None,
        )
    )

    assert isinstance(response, AIResponse)
    assert isinstance(response.content, str)
    assert response.content.strip()
    assert response.metadata["provider"] == "openai"
