"""Freeze the OpenProjectLab v1 Marketplace public contract."""

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
    ArtifactInstallationStatus,
    InMemoryArtifactInstaller,
)
from generator.marketplace.integrity import (
    ArtifactIntegrityError,
    sha256_digest,
    verify_integrity,
)
from generator.marketplace.repository import (
    ArtifactAlreadyExistsError,
    ArtifactNotFoundError,
    InMemoryMarketplaceRepository,
)
from generator.marketplace.template_package import (
    TemplateEntry,
    TemplatePackageManifest,
    TemplatePackageValidationError,
)


def _artifact(
    version: str,
    payload: bytes,
    *,
    name: str = "course-template",
) -> MarketplaceArtifact:
    """Build one deterministic Marketplace artifact for v1 contract tests."""
    return MarketplaceArtifact(
        schema_version=1,
        identity=ArtifactIdentity(
            namespace="openprojectlab",
            name=name,
        ),
        version=ArtifactVersion(version),
        artifact_type=ArtifactType.TEMPLATE,
        description="Representative v1 template package",
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


def test_v1_marketplace_artifact_coordinate_is_identity_plus_version() -> None:
    """Keep exact immutable identity/version coordinates as Marketplace identity."""
    artifact = _artifact("1.2.3", b"payload")

    assert str(artifact.identity) == "openprojectlab/course-template"
    assert artifact.version.parts == (1, 2, 3)
    assert str(artifact.coordinate) == "openprojectlab/course-template@1.2.3"


def test_v1_marketplace_version_ordering_is_semantic_and_deterministic() -> None:
    """Order canonical MAJOR.MINOR.PATCH versions numerically."""
    versions = (
        ArtifactVersion("1.10.0"),
        ArtifactVersion("1.2.0"),
        ArtifactVersion("1.0.9"),
    )

    assert tuple(sorted(versions)) == (
        ArtifactVersion("1.0.9"),
        ArtifactVersion("1.2.0"),
        ArtifactVersion("1.10.0"),
    )


def test_v1_repository_uses_exact_coordinate_lookup_and_version_ordering() -> None:
    """Freeze exact lookup and deterministic ascending available versions."""
    identity = ArtifactIdentity(
        namespace="openprojectlab",
        name="course-template",
    )
    first = _artifact("1.2.0", b"first")
    second = _artifact("1.0.0", b"second")
    repository = InMemoryMarketplaceRepository((first, second))

    assert repository.find(identity, ArtifactVersion("1.2.0")) is first
    assert repository.available_versions(identity) == (
        ArtifactVersion("1.0.0"),
        ArtifactVersion("1.2.0"),
    )

    with pytest.raises(ArtifactNotFoundError):
        repository.find(identity, ArtifactVersion("9.9.9"))


def test_v1_repository_rejects_duplicate_coordinates() -> None:
    """Reject multiple artifacts claiming the same exact coordinate."""
    artifact = _artifact("1.0.0", b"payload")

    with pytest.raises(ArtifactAlreadyExistsError):
        InMemoryMarketplaceRepository((artifact, artifact))


def test_v1_acquisition_returns_exact_bytes_without_installing() -> None:
    """Keep acquisition as a bytes-only boundary separate from installation."""
    payload = b"marketplace payload"
    artifact = _artifact("1.0.0", payload)
    acquirer = InMemoryArtifactAcquirer(
        {artifact.coordinate: payload},
    )
    installer = InMemoryArtifactInstaller()

    assert acquirer.acquire(artifact) == payload
    assert not installer.is_installed(artifact.coordinate)


def test_v1_acquisition_reports_missing_payload() -> None:
    """Keep missing exact-coordinate payloads explicit."""
    artifact = _artifact("1.0.0", b"payload")
    acquirer = InMemoryArtifactAcquirer()

    with pytest.raises(ArtifactPayloadNotFoundError):
        acquirer.acquire(artifact)


def test_v1_sha256_integrity_contract_is_deterministic() -> None:
    """Freeze SHA-256 digest and verification behavior."""
    payload = b"integrity payload"
    artifact = _artifact("1.0.0", payload)

    assert sha256_digest(payload) == sha256(payload).hexdigest()
    assert verify_integrity(payload, artifact.integrity) is None


def test_v1_integrity_mismatch_fails_before_installation_state() -> None:
    """Keep integrity verification before installation in the composed flow."""
    expected_payload = b"expected"
    corrupt_payload = b"corrupt"
    artifact = _artifact("1.0.0", expected_payload)
    installer = InMemoryArtifactInstaller()

    with pytest.raises(ArtifactIntegrityError):
        verify_integrity(corrupt_payload, artifact.integrity)

    assert not installer.is_installed(artifact.coordinate)
    assert installer.list_installed() == ()


def test_v1_installation_is_separate_from_activation() -> None:
    """Freeze deterministic installation as stored artifact bytes only."""
    payload = b"install payload"
    artifact = _artifact("1.0.0", payload)
    installer = InMemoryArtifactInstaller()

    result = installer.install(artifact, payload)

    assert result.artifact is artifact
    assert result.status is ArtifactInstallationStatus.INSTALLED
    assert result.payload_size == len(payload)
    assert installer.is_installed(artifact.coordinate)
    assert installer.installed_payload(artifact.coordinate) == payload
    assert installer.list_installed() == (artifact,)


def test_v1_duplicate_install_does_not_replace_installed_payload() -> None:
    """Reject duplicate exact-coordinate installation without silent replacement."""
    original = b"original"
    artifact = _artifact("1.0.0", original)
    installer = InMemoryArtifactInstaller()
    installer.install(artifact, original)

    with pytest.raises(ArtifactAlreadyInstalledError):
        installer.install(artifact, b"replacement")

    assert installer.installed_payload(artifact.coordinate) == original


@pytest.mark.parametrize(
    "relative_path",
    [
        "../secret.txt",
        "/absolute.txt",
        "C:/absolute.txt",
    ],
)
def test_v1_template_entry_rejects_unsafe_relative_paths(
    relative_path: str,
) -> None:
    """Reject absolute, drive-prefixed, and traversal package paths."""
    with pytest.raises(ValueError):
        TemplateEntry(
            name="unsafe",
            relative_path=relative_path,
            media_type="text/plain",
        )


def test_v1_template_entry_normalizes_dot_prefixed_relative_path() -> None:
    """Normalize a safe dot-prefixed package path."""
    entry = TemplateEntry(
        name="template",
        relative_path="./template.md.j2",
        media_type="text/plain",
    )

    assert entry.relative_path == "template.md.j2"


def test_v1_template_manifest_rejects_duplicate_names_and_paths() -> None:
    """Keep Template Package entry identity/path uniqueness deterministic."""
    duplicate_name = (
        TemplateEntry(
            name="readme",
            relative_path="templates/a.md.j2",
            media_type="text/plain",
        ),
        TemplateEntry(
            name="readme",
            relative_path="templates/b.md.j2",
            media_type="text/plain",
        ),
    )

    with pytest.raises(TemplatePackageValidationError):
        TemplatePackageManifest(
            schema_version=1,
            templates=duplicate_name,
            resources=(),
        )

    duplicate_path = (
        TemplateEntry(
            name="first",
            relative_path="templates/a.md.j2",
            media_type="text/plain",
        ),
        TemplateEntry(
            name="second",
            relative_path="templates/a.md.j2",
            media_type="text/plain",
        ),
    )

    with pytest.raises(TemplatePackageValidationError):
        TemplatePackageManifest(
            schema_version=1,
            templates=duplicate_path,
            resources=(),
        )


def test_v1_template_manifest_orders_entries_deterministically() -> None:
    """Normalize template entries into deterministic name/path/media ordering."""
    later = TemplateEntry(
        name="z-template",
        relative_path="templates/z.md.j2",
        media_type="text/plain",
    )
    earlier = TemplateEntry(
        name="a-template",
        relative_path="templates/a.md.j2",
        media_type="text/plain",
    )

    manifest = TemplatePackageManifest(
        schema_version=1,
        templates=(later, earlier),
        resources=(),
    )

    assert manifest.templates == (earlier, later)
