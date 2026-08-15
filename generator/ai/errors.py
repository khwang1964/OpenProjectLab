"""AI integration error types."""

from __future__ import annotations


class AIResponseValidationError(ValueError):
    """Raised when an AI response violates the expected structural contract."""
