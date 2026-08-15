from __future__ import annotations

from dataclasses import dataclass

import pytest

from generator.ai.errors import (
    AIAuthenticationError,
    AIProviderError,
    AIRateLimitError,
    AITimeoutError,
    AIUnavailableError,
)
from generator.ai.models import AIRequest, AIResponse


class StubAuthenticationError(Exception):
    pass


class StubRateLimitError(Exception):
    pass


class StubTimeoutError(Exception):
    pass


class StubUnavailableError(Exception):
    pass


class StubProviderFailure(Exception):
    pass


@dataclass(frozen=True, slots=True)
class StubProviderResponse:
    content: object


class FailingStubProviderClient:
    def __init__(
        self,
        failure: Exception,
    ) -> None:
        self._failure = failure
        self.calls = 0

    def generate(self, **_: object) -> StubProviderResponse:
        self.calls += 1
        raise self._failure


class ErrorContractProviderAdapter:
    """Test-only reference adapter defining provider error semantics."""

    def __init__(
        self,
        *,
        client: FailingStubProviderClient,
    ) -> None:
        self._client = client

    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        try:
            self._client.generate(
                instructions=request.instructions,
                context=dict(request.context),
            )
        except StubAuthenticationError as exc:
            raise AIAuthenticationError("AI provider authentication failed.") from exc
        except StubRateLimitError as exc:
            raise AIRateLimitError("AI provider rate limit exceeded.") from exc
        except StubTimeoutError as exc:
            raise AITimeoutError("AI provider request timed out.") from exc
        except StubUnavailableError as exc:
            raise AIUnavailableError("AI provider is unavailable.") from exc
        except StubProviderFailure as exc:
            raise AIProviderError("AI provider request failed.") from exc

        raise AssertionError("failing client unexpectedly returned")


def _request() -> AIRequest:
    return AIRequest(
        task="courseware.build",
        instructions="Build a structured course.",
        context={"course_id": "modern-java"},
        response_contract="courseware.course.v1",
    )


@pytest.mark.parametrize(
    ("provider_error", "expected_error", "expected_message"),
    [
        (
            StubAuthenticationError("vendor auth detail"),
            AIAuthenticationError,
            "authentication",
        ),
        (
            StubRateLimitError("vendor limit detail"),
            AIRateLimitError,
            "rate limit",
        ),
        (
            StubTimeoutError("vendor timeout detail"),
            AITimeoutError,
            "timed out",
        ),
        (
            StubUnavailableError("vendor unavailable detail"),
            AIUnavailableError,
            "unavailable",
        ),
        (
            StubProviderFailure("vendor provider detail"),
            AIProviderError,
            "request failed",
        ),
    ],
)
def test_provider_adapter_converts_recognized_failures(
    provider_error: Exception,
    expected_error: type[Exception],
    expected_message: str,
) -> None:
    client = FailingStubProviderClient(provider_error)
    adapter = ErrorContractProviderAdapter(
        client=client,
    )

    with pytest.raises(
        expected_error,
        match=expected_message,
    ) as exc_info:
        adapter.generate(_request())

    assert exc_info.value.__cause__ is provider_error
    assert client.calls == 1


class ProgrammingErrorClient:
    def generate(self, **_: object) -> StubProviderResponse:
        raise TypeError("programming bug")


class TransparentErrorContractAdapter:
    def __init__(
        self,
        *,
        client: ProgrammingErrorClient,
    ) -> None:
        self._client = client

    def generate(
        self,
        request: AIRequest,
    ) -> AIResponse:
        self._client.generate(
            instructions=request.instructions,
            context=dict(request.context),
        )
        raise AssertionError("programming-error client unexpectedly returned")


def test_provider_adapter_does_not_mask_unexpected_programming_error() -> None:
    adapter = TransparentErrorContractAdapter(
        client=ProgrammingErrorClient(),
    )

    with pytest.raises(
        TypeError,
        match="programming bug",
    ):
        adapter.generate(_request())


def test_provider_failure_has_no_filesystem_side_effect(
    tmp_path,
) -> None:
    adapter = ErrorContractProviderAdapter(
        client=FailingStubProviderClient(
            StubTimeoutError("timeout"),
        ),
    )

    with pytest.raises(AITimeoutError):
        adapter.generate(_request())

    assert list(tmp_path.iterdir()) == []
