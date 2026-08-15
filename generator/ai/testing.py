"""Deterministic testing support for AI integration contracts."""

from __future__ import annotations

from collections.abc import Iterable

from .models import AIRequest, AIResponse


class FakeAIProvider:
    """Deterministic AI provider for unit, contract, integration, and E2E tests."""

    def __init__(
        self,
        *,
        responses: Iterable[AIResponse] = (),
        failures: Iterable[Exception] = (),
    ) -> None:
        self._responses = list(responses)
        self._failures = list(failures)
        self._requests: list[AIRequest] = []

    @property
    def requests(self) -> tuple[AIRequest, ...]:
        """Return recorded requests in invocation order."""
        return tuple(self._requests)

    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        """Record a request and return or raise the next configured outcome."""
        self._requests.append(request)

        if self._failures:
            raise self._failures.pop(0)

        if self._responses:
            return self._responses.pop(0)

        raise RuntimeError("FakeAIProvider has no configured response.")
