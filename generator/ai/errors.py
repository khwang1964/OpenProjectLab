"""AI integration error types."""

from __future__ import annotations


class AIError(Exception):
    """Base error for provider-independent AI integration failures."""


class AIProviderError(AIError):
    """Raised when an AI provider invocation fails."""


class AIAuthenticationError(AIProviderError):
    """Raised when AI provider authentication fails."""


class AIRateLimitError(AIProviderError):
    """Raised when an AI provider rate limit is exceeded."""


class AITimeoutError(AIProviderError):
    """Raised when an AI provider request times out."""


class AIUnavailableError(AIProviderError):
    """Raised when an AI provider is temporarily unavailable."""


class AIResponseValidationError(ValueError):
    """Raised when an AI response violates the expected structural contract."""
