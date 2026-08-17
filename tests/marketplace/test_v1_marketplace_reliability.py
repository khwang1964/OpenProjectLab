"""Harden the OpenProjectLab v1 Marketplace reliability boundary."""

from __future__ import annotations

from hashlib import sha256

import pytest

from generator.marketplace import (
    ArtifactIdentity,
    ArtifactType,
    ArtifactVersion,
    CompatibilityRequirement,
    DistributionMetadata,
    IntegrityMetadata,
    MarketplaceArtifact,
)
from generator.marketplace.acquisition import (
    ArtifactPayloadNotFoundError,
    InMemoryArtifactAcquirer,
)
from generator.marketplace.installation import (
    ArtifactAlreadyInstalledError,
    InMemoryArtifactInstaller,
)
from generator.marketplace.integrity import (
    ArtifactIntegrityError,
    verify_integrity,
)
from generator.marketplace.repository import (
    ArtifactNotFoundError,
    InMemoryMarketplaceRepository,
)


def _artifact(
    version: str,
    payload: bytes,
    *,
    name: str = "course-template",
) -> MarketplaceArtifact:
    return MarketplaceArtifact(
        schema_version=1,
        identity=ArtifactIdentity(
            namespace="openprojectlab",
            name=name,
        ),
        version=ArtifactVersion(version),
        artifact_type=ArtifactType.TEMPLATE,
        description="Reliability test artifact",
        compatibility=CompatibilityRequirement(">=1.0,<2.0"),
        distribution=DistributionMetadata(
            kind="memory",
            reference=f"{name}-{version}",
        ),
        integrity=IntegrityMetadata(
            algorithm="sha256",
            digest=sha256(payload).hexdigest(),
        ),
    )


def test_v1_missing_repository_coordinate_does_not_change_repository() -> None:
    """Keep exact-coordinate lookup failure side-effect free."""
    payload = b"payload"
    artifact = _artifact("1.0.0", payload)
    repository = InMemoryMarketplaceRepository((artifact,))

    with pytest.raises(ArtifactNotFoundError):
        repository.find(
            artifact.identity,
            ArtifactVersion("9.9.9"),
        )

    assert repository.find(artifact.identity, artifact.version) is artifact


def test_v1_missing_payload_does_not_create_installation_state() -> None:
    """Stop before installation when acquisition cannot provide bytes."""
    artifact = _artifact("1.0.0", b"expected")
    acquirer = InMemoryArtifactAcquirer()
    installer = InMemoryArtifactInstaller()

    with pytest.raises(ArtifactPayloadNotFoundError):
        acquirer.acquire(artifact)

    assert not installer.is_installed(artifact.coordinate)
    assert installer.list_installed() == ()


def test_v1_integrity_mismatch_occurs_before_installation() -> None:
    """Reject corrupt bytes without mutating installation state."""
    artifact = _artifact("1.0.0", b"expected")
    corrupt = b"corrupt"
    installer = InMemoryArtifactInstaller()

    with pytest.raises(ArtifactIntegrityError):
        verify_integrity(corrupt, artifact.integrity)

    assert not installer.is_installed(artifact.coordinate)
    assert installer.list_installed() == ()


def test_v1_duplicate_install_preserves_original_payload() -> None:
    """Never replace an existing exact-coordinate installation silently."""
    original = b"original"
    artifact = _artifact("1.0.0", original)
    installer = InMemoryArtifactInstaller()

    installer.install(artifact, original)

    with pytest.raises(ArtifactAlreadyInstalledError):
        installer.install(artifact, b"replacement")

    assert installer.installed_payload(artifact.coordinate) == original
    assert installer.list_installed() == (artifact,)


def test_v1_acquirer_copies_payload_mapping_at_construction() -> None:
    """Keep later caller mapping mutation from changing acquisition behavior."""
    payload = b"original"
    artifact = _artifact("1.0.0", payload)
    payloads = {artifact.coordinate: payload}
    acquirer = InMemoryArtifactAcquirer(payloads)

    payloads[artifact.coordinate] = b"changed"

    assert acquirer.acquire(artifact) == payload


def test_v1_installation_list_order_is_deterministic() -> None:
    """Sort installed artifacts by namespace, name, and semantic version."""
    first = _artifact("1.10.0", b"first", name="alpha")
    second = _artifact("1.2.0", b"second", name="alpha")
    third = _artifact("1.0.0", b"third", name="beta")
    installer = InMemoryArtifactInstaller()

    installer.install(third, b"third")
    installer.install(first, b"first")
    installer.install(second, b"second")

    assert installer.list_installed() == (
        second,
        first,
        third,
    )


def test_v1_repeated_repository_version_listing_is_deterministic() -> None:
    """Return the same ordered versions across repeated equivalent lookups."""
    identity = ArtifactIdentity(
        namespace="openprojectlab",
        name="course-template",
    )
    artifacts = (
        _artifact("1.10.0", b"a"),
        _artifact("1.2.0", b"b"),
        _artifact("1.0.0", b"c"),
    )
    repository = InMemoryMarketplaceRepository(artifacts)

    first = repository.available_versions(identity)
    second = repository.available_versions(identity)

    assert (
        first
        == second
        == (
            ArtifactVersion("1.0.0"),
            ArtifactVersion("1.2.0"),
            ArtifactVersion("1.10.0"),
        )
    )
