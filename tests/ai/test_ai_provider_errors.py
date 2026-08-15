from __future__ import annotations

import pytest

from generator.ai.errors import (
    AIAuthenticationError,
    AIError,
    AIProviderError,
    AIRateLimitError,
    AIResponseValidationError,
    AITimeoutError,
    AIUnavailableError,
)


@pytest.mark.parametrize(
    "error_type",
    [
        AIAuthenticationError,
        AIRateLimitError,
        AITimeoutError,
        AIUnavailableError,
    ],
)
def test_specialized_provider_errors_are_provider_errors(
    error_type: type[AIProviderError],
) -> None:
    error = error_type("provider failure")

    assert isinstance(error, AIProviderError)


@pytest.mark.parametrize(
    "error_type",
    [
        AIProviderError,
        AIAuthenticationError,
        AIRateLimitError,
        AITimeoutError,
        AIUnavailableError,
    ],
)
def test_provider_errors_are_ai_errors(
    error_type: type[AIError],
) -> None:
    error = error_type("provider failure")

    assert isinstance(error, AIError)


def test_provider_error_can_be_caught_through_ai_error_boundary() -> None:
    with pytest.raises(AIError):
        raise AITimeoutError("provider timed out")


def test_specialized_provider_error_can_be_caught_through_provider_boundary() -> None:
    with pytest.raises(AIProviderError):
        raise AIAuthenticationError("authentication failed")


def test_provider_error_preserves_message() -> None:
    error = AIRateLimitError("rate limit exceeded")

    assert str(error) == "rate limit exceeded"


def test_response_validation_error_preserves_existing_value_error_contract() -> None:
    error = AIResponseValidationError("invalid response")

    assert isinstance(error, ValueError)
    assert not isinstance(error, AIProviderError)
    assert str(error) == "invalid response"
