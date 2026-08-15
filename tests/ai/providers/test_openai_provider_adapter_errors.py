from __future__ import annotations

from types import SimpleNamespace

import pytest

from generator.ai.errors import (
    AIAuthenticationError,
    AIProviderError,
    AIRateLimitError,
    AITimeoutError,
    AIUnavailableError,
)
from generator.ai.models import AIRequest
from generator.ai.providers.openai import OpenAIProviderAdapter


class AuthenticationError(Exception):
    pass


class RateLimitError(Exception):
    pass


class APITimeoutError(Exception):
    pass


class APIConnectionError(Exception):
    pass


class APIStatusError(Exception):
    pass


class FailingResponsesAPI:
    def __init__(
        self,
        failure: Exception,
    ) -> None:
        self._failure = failure
        self.calls = 0

    def create(self, **_: object) -> object:
        self.calls += 1
        raise self._failure


class FailingOpenAIClient:
    def __init__(
        self,
        failure: Exception,
    ) -> None:
        self.responses = FailingResponsesAPI(
            failure,
        )


def _request() -> AIRequest:
    return AIRequest(
        task="courseware.build",
        instructions="Build a structured course.",
        context={"course_id": "modern-java"},
        response_contract="courseware.course.v1",
    )


@pytest.mark.parametrize(
    ("provider_error", "expected_error"),
    [
        (
            AuthenticationError("auth failed"),
            AIAuthenticationError,
        ),
        (
            RateLimitError("rate limited"),
            AIRateLimitError,
        ),
        (
            APITimeoutError("timed out"),
            AITimeoutError,
        ),
        (
            APIConnectionError("connection failed"),
            AIUnavailableError,
        ),
        (
            APIStatusError("provider failed"),
            AIProviderError,
        ),
    ],
)
def test_openai_adapter_converts_recognized_provider_failures(
    provider_error: Exception,
    expected_error: type[Exception],
) -> None:
    client = FailingOpenAIClient(
        provider_error,
    )
    adapter = OpenAIProviderAdapter(
        client=client,
        model="gpt-test",
        timeout_seconds=30.0,
    )

    with pytest.raises(expected_error) as exc_info:
        adapter.generate(_request())

    assert exc_info.value.__cause__ is provider_error
    assert client.responses.calls == 1


class ProgrammingErrorResponsesAPI:
    def create(self, **_: object) -> object:
        raise TypeError("programming bug")


class ProgrammingErrorOpenAIClient:
    def __init__(self) -> None:
        self.responses = ProgrammingErrorResponsesAPI()


def test_openai_adapter_does_not_mask_programming_error() -> None:
    adapter = OpenAIProviderAdapter(
        client=ProgrammingErrorOpenAIClient(),
        model="gpt-test",
        timeout_seconds=30.0,
    )

    with pytest.raises(
        TypeError,
        match="programming bug",
    ):
        adapter.generate(_request())


def test_openai_adapter_rejects_malformed_provider_response() -> None:
    client = SimpleNamespace(
        responses=SimpleNamespace(
            create=lambda **_: SimpleNamespace(
                id="resp_bad",
                model="gpt-test",
                status="completed",
                output_text=None,
                usage=None,
            )
        )
    )
    adapter = OpenAIProviderAdapter(
        client=client,
        model="gpt-test",
        timeout_seconds=30.0,
    )

    with pytest.raises(AIProviderError):
        adapter.generate(_request())


def test_openai_provider_failure_has_no_filesystem_side_effect(
    tmp_path,
) -> None:
    adapter = OpenAIProviderAdapter(
        client=FailingOpenAIClient(
            APITimeoutError("timed out"),
        ),
        model="gpt-test",
        timeout_seconds=30.0,
    )

    with pytest.raises(AITimeoutError):
        adapter.generate(_request())

    assert list(tmp_path.iterdir()) == []
