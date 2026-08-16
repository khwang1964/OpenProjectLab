"""Marketplace artifact integrity verification.

Step 7.5 scope:
- deterministic SHA-256 digest calculation
- verification against ``IntegrityMetadata``
- explicit mismatch and unsupported-algorithm failures

This module does not establish publisher trust or authenticity, acquire
artifacts, install packages, activate plugins, execute generators, or perform
filesystem/network side effects.
"""

from __future__ import annotations

import hashlib
import hmac

from .models import IntegrityMetadata


class ArtifactIntegrityError(Exception):
    """Raised when artifact content fails integrity verification."""


class UnsupportedIntegrityAlgorithmError(ArtifactIntegrityError):
    """Raised when the verifier does not support the declared algorithm."""


def _require_bytes(content: bytes) -> bytes:
    if not isinstance(content, bytes):
        raise TypeError("artifact content must be bytes")
    return content


def sha256_digest(content: bytes) -> str:
    """Return the deterministic lowercase SHA-256 digest for ``content``."""
    payload = _require_bytes(content)
    return hashlib.sha256(payload).hexdigest()


def verify_integrity(
    content: bytes,
    metadata: IntegrityMetadata,
) -> None:
    """Verify artifact bytes against integrity metadata.

    The current Marketplace contract supports SHA-256 verification only.
    A mismatch raises ``ArtifactIntegrityError``. Unsupported algorithms raise
    ``UnsupportedIntegrityAlgorithmError``.
    """
    payload = _require_bytes(content)

    if not isinstance(metadata, IntegrityMetadata):
        raise TypeError("metadata must be IntegrityMetadata")

    if metadata.algorithm != "sha256":
        raise UnsupportedIntegrityAlgorithmError(
            f"unsupported integrity algorithm: {metadata.algorithm}"
        )

    actual_digest = sha256_digest(payload)

    if not hmac.compare_digest(
        actual_digest.lower(),
        metadata.digest.lower(),
    ):
        raise ArtifactIntegrityError("Marketplace artifact integrity mismatch")
