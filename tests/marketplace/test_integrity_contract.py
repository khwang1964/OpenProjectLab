"""Contract tests for Marketplace integrity verification.

Step 7.5 scope:
- deterministic SHA-256 digest calculation
- verification against IntegrityMetadata
- explicit integrity mismatch failure
- explicit unsupported-algorithm failure
- bytes-only, side-effect-free verification

Out of scope:
- publisher trust
- authenticity/signing
- acquisition/download
- installation/activation
- filesystem mutation
- network access
"""

from __future__ import annotations

import hashlib

import pytest

from generator.marketplace.integrity import (
    ArtifactIntegrityError,
    UnsupportedIntegrityAlgorithmError,
    sha256_digest,
    verify_integrity,
)
from generator.marketplace.models import IntegrityMetadata


def _metadata_for(content: bytes) -> IntegrityMetadata:
    return IntegrityMetadata(
        algorithm="sha256",
        digest=hashlib.sha256(content).hexdigest(),
    )


class TestSha256Digest:
    @pytest.mark.parametrize(
        "content",
        [
            b"",
            b"OpenProjectLab",
            b"\x00\x01\x02\xff",
            "繁體中文".encode(),
        ],
    )
    def test_matches_hashlib_sha256(
        self,
        content: bytes,
    ) -> None:
        assert sha256_digest(content) == hashlib.sha256(content).hexdigest()

    def test_is_deterministic(self) -> None:
        content = b"same artifact payload"

        assert sha256_digest(content) == sha256_digest(content)

    def test_changed_content_changes_digest(self) -> None:
        assert sha256_digest(b"payload-a") != sha256_digest(b"payload-b")

    @pytest.mark.parametrize(
        "content",
        [
            "",
            bytearray(b"payload"),
            memoryview(b"payload"),
            None,
            123,
        ],
    )
    def test_requires_bytes(
        self,
        content: object,
    ) -> None:
        with pytest.raises(TypeError):
            sha256_digest(content)  # type: ignore[arg-type]


class TestVerifyIntegrity:
    def test_accepts_matching_sha256_digest(self) -> None:
        content = b"verified marketplace artifact"

        assert (
            verify_integrity(
                content,
                _metadata_for(content),
            )
            is None
        )

    def test_rejects_digest_mismatch(self) -> None:
        metadata = IntegrityMetadata(
            algorithm="sha256",
            digest="a" * 64,
        )

        with pytest.raises(ArtifactIntegrityError):
            verify_integrity(
                b"different content",
                metadata,
            )

    def test_mismatch_error_does_not_mutate_metadata(self) -> None:
        metadata = IntegrityMetadata(
            algorithm="sha256",
            digest="a" * 64,
        )
        original = metadata

        with pytest.raises(ArtifactIntegrityError):
            verify_integrity(
                b"different content",
                metadata,
            )

        assert metadata == original

    def test_rejects_unsupported_algorithm_explicitly(self) -> None:
        # IntegrityMetadata currently validates supported algorithms at model
        # construction time. This object bypasses __post_init__ deliberately
        # so the verifier contract remains explicit if future metadata parsing
        # admits additional algorithms before verification.
        metadata = object.__new__(IntegrityMetadata)
        object.__setattr__(metadata, "algorithm", "sha512")
        object.__setattr__(metadata, "digest", "a" * 64)

        with pytest.raises(UnsupportedIntegrityAlgorithmError):
            verify_integrity(
                b"payload",
                metadata,
            )

    @pytest.mark.parametrize(
        "content",
        [
            "",
            bytearray(b"payload"),
            memoryview(b"payload"),
            None,
        ],
    )
    def test_requires_bytes_payload(
        self,
        content: object,
    ) -> None:
        metadata = _metadata_for(b"payload")

        with pytest.raises(TypeError):
            verify_integrity(
                content,  # type: ignore[arg-type]
                metadata,
            )

    def test_requires_integrity_metadata(self) -> None:
        with pytest.raises(TypeError):
            verify_integrity(
                b"payload",
                object(),  # type: ignore[arg-type]
            )

    def test_verification_has_no_filesystem_side_effect_contract(
        self,
        tmp_path,
    ) -> None:
        content = b"payload"
        before = tuple(tmp_path.iterdir())

        verify_integrity(
            content,
            _metadata_for(content),
        )

        assert tuple(tmp_path.iterdir()) == before
