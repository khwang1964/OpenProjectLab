"""Contract tests for the Marketplace artifact acquisition boundary.

Step 7.5 acquisition is intentionally deterministic and no-network.
The acquirer returns artifact bytes only. It does not verify integrity,
install, activate, register, execute, or write generated output.

Out of scope:
- HTTP/remote repositories
- integrity verification
- installation/activation
- plugin registration
- generator execution
- Courseware filesystem output
"""

from __future__ import annotations

from collections.abc import Mapping

import pytest

from generator.marketplace.acquisition import (
    ArtifactAcquisitionError,
    ArtifactPayloadNotFoundError,
    InMemoryArtifactAcquirer,
)
from generator.marketplace.models import (
    ArtifactCoordinate,
    ArtifactIdentity,
    ArtifactType,
    ArtifactVersion,
    CompatibilityRequirement,
    DistributionMetadata,
    IntegrityMetadata,
    MarketplaceArtifact,
)


def _artifact(
    *,
    namespace: str = "community",
    name: str = "modern-java-templates",
    version: str = "1.0.0",
) -> MarketplaceArtifact:
    return MarketplaceArtifact(
        schema_version=1,
        identity=ArtifactIdentity(
            namespace=namespace,
            name=name,
        ),
        version=ArtifactVersion(version),
        artifact_type=ArtifactType.TEMPLATE,
        description=f"{namespace}/{name}@{version}",
        compatibility=CompatibilityRequirement(">=0.7,<1.0"),
        distribution=DistributionMetadata(
            kind="package",
            reference=f"{namespace}-{name}-{version}",
        ),
        integrity=IntegrityMetadata(
            algorithm="sha256",
            digest="a" * 64,
        ),
    )


def _payloads(
    artifact: MarketplaceArtifact,
    payload: bytes,
) -> Mapping[ArtifactCoordinate, bytes]:
    return {
        artifact.coordinate: payload,
    }


class TestInMemoryArtifactAcquirer:
    def test_acquires_bytes_for_exact_artifact_coordinate(self) -> None:
        artifact = _artifact()
        payload = b"artifact payload"
        acquirer = InMemoryArtifactAcquirer(
            _payloads(
                artifact,
                payload,
            )
        )

        assert acquirer.acquire(artifact) == payload

    def test_returns_bytes(self) -> None:
        artifact = _artifact()
        acquirer = InMemoryArtifactAcquirer(
            _payloads(
                artifact,
                b"artifact payload",
            )
        )

        assert isinstance(
            acquirer.acquire(artifact),
            bytes,
        )

    def test_repeated_acquisition_is_deterministic(self) -> None:
        artifact = _artifact()
        payload = b"same payload"
        acquirer = InMemoryArtifactAcquirer(
            _payloads(
                artifact,
                payload,
            )
        )

        assert acquirer.acquire(artifact) == acquirer.acquire(artifact)

    def test_missing_payload_raises_explicit_error(self) -> None:
        artifact = _artifact()
        acquirer = InMemoryArtifactAcquirer()

        with pytest.raises(ArtifactPayloadNotFoundError):
            acquirer.acquire(artifact)

    def test_different_versions_have_independent_payloads(self) -> None:
        first = _artifact(version="1.0.0")
        second = _artifact(version="2.0.0")
        acquirer = InMemoryArtifactAcquirer(
            {
                first.coordinate: b"v1",
                second.coordinate: b"v2",
            }
        )

        assert acquirer.acquire(first) == b"v1"
        assert acquirer.acquire(second) == b"v2"

    def test_rejects_non_artifact_input(self) -> None:
        acquirer = InMemoryArtifactAcquirer()

        with pytest.raises(TypeError):
            acquirer.acquire(object())  # type: ignore[arg-type]

    def test_constructor_requires_coordinate_keys(self) -> None:
        artifact = _artifact()

        with pytest.raises(TypeError):
            InMemoryArtifactAcquirer(
                {
                    artifact.identity: b"payload",
                }  # type: ignore[dict-item]
            )

    @pytest.mark.parametrize(
        "payload",
        [
            "text",
            bytearray(b"payload"),
            memoryview(b"payload"),
            None,
            123,
        ],
    )
    def test_constructor_requires_bytes_payloads(
        self,
        payload: object,
    ) -> None:
        artifact = _artifact()

        with pytest.raises(TypeError):
            InMemoryArtifactAcquirer(
                {
                    artifact.coordinate: payload,
                }  # type: ignore[dict-item]
            )

    def test_constructor_does_not_mutate_source_mapping(self) -> None:
        artifact = _artifact()
        source = {
            artifact.coordinate: b"payload",
        }
        original = dict(source)

        InMemoryArtifactAcquirer(source)

        assert source == original

    def test_acquired_bytes_do_not_change_when_source_mapping_changes(
        self,
    ) -> None:
        artifact = _artifact()
        source = {
            artifact.coordinate: b"original",
        }
        acquirer = InMemoryArtifactAcquirer(source)

        source[artifact.coordinate] = b"changed"

        assert acquirer.acquire(artifact) == b"original"

    def test_acquisition_does_not_verify_integrity(self) -> None:
        artifact = _artifact()
        payload = b"payload whose digest does not match metadata"
        acquirer = InMemoryArtifactAcquirer(
            _payloads(
                artifact,
                payload,
            )
        )

        # Acquisition returns bytes only. Integrity verification belongs to the
        # separate integrity boundary and must be composed explicitly.
        assert acquirer.acquire(artifact) == payload

    def test_acquisition_has_no_filesystem_side_effect_contract(
        self,
        tmp_path,
    ) -> None:
        artifact = _artifact()
        acquirer = InMemoryArtifactAcquirer(
            _payloads(
                artifact,
                b"payload",
            )
        )
        before = tuple(tmp_path.iterdir())

        acquirer.acquire(artifact)

        assert tuple(tmp_path.iterdir()) == before


class TestAcquisitionErrors:
    def test_payload_not_found_is_an_acquisition_error(self) -> None:
        assert issubclass(
            ArtifactPayloadNotFoundError,
            ArtifactAcquisitionError,
        )

    def test_missing_payload_error_identifies_coordinate(self) -> None:
        artifact = _artifact()
        acquirer = InMemoryArtifactAcquirer()

        with pytest.raises(ArtifactPayloadNotFoundError) as exc_info:
            acquirer.acquire(artifact)

        assert str(artifact.coordinate) in str(exc_info.value)
