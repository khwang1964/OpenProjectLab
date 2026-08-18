"""Release automation primitives for OpenProjectLab."""

from .identity import (
    ReleaseIdentity,
    ReleaseIdentityError,
    ReleaseTagConflictError,
    expected_release_tag,
    read_canonical_version,
    validate_release_identity,
)

__all__ = [
    "ReleaseIdentity",
    "ReleaseIdentityError",
    "ReleaseTagConflictError",
    "expected_release_tag",
    "read_canonical_version",
    "validate_release_identity",
]
