"""Contract tests for Marketplace installation integration.

Step 7.6 scope:
- deterministic in-memory installation
- structured immutable installation result
- explicit duplicate-install semantics
- explicit installation failures
- installation is separate from activation

Out of scope:
- package-manager integration
- remote/network installation
- plugin registration
- entry-point discovery
- generator execution
- Courseware filesystem output
- Marketplace CLI
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from generator.marketplace.installation import (
    ArtifactAlreadyInstalledError,
    ArtifactInstallationError,
    ArtifactInstallationResult,
    ArtifactInstallationStatus,
    InMemoryArtifactInstaller,
)
from generator.marketplace.models import (
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
    artifact_type: ArtifactType = ArtifactType.TEMPLATE,
) -> MarketplaceArtifact:
    return MarketplaceArtifact(
        schema_version=1,
        identity=ArtifactIdentity(
            namespace=namespace,
            name=name,
        ),
        version=ArtifactVersion(version),
        artifact_type=artifact_type,
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


class TestArtifactInstallationResult:
    def test_contains_artifact_status_and_payload_size(self) -> None:
        artifact = _artifact()
        result = ArtifactInstallationResult(
            artifact=artifact,
            status=ArtifactInstallationStatus.INSTALLED,
            payload_size=7,
        )

        assert result.artifact == artifact
        assert result.status is ArtifactInstallationStatus.INSTALLED
        assert result.payload_size == 7

    def test_is_immutable(self) -> None:
        result = ArtifactInstallationResult(
            artifact=_artifact(),
            status=ArtifactInstallationStatus.INSTALLED,
            payload_size=7,
        )

        with pytest.raises(FrozenInstanceError):
            result.payload_size = 8  # type: ignore[misc]


class TestInMemoryArtifactInstaller:
    def test_installs_artifact_payload(self) -> None:
        artifact = _artifact()
        payload = b"payload"
        installer = InMemoryArtifactInstaller()

        result = installer.install(
            artifact,
            payload,
        )

        assert result == ArtifactInstallationResult(
            artifact=artifact,
            status=ArtifactInstallationStatus.INSTALLED,
            payload_size=len(payload),
        )

    def test_reports_installed_artifact(self) -> None:
        artifact = _artifact()
        installer = InMemoryArtifactInstaller()

        installer.install(
            artifact,
            b"payload",
        )

        assert installer.is_installed(artifact.coordinate) is True

    def test_returns_installed_payload_by_coordinate(self) -> None:
        artifact = _artifact()
        payload = b"payload"
        installer = InMemoryArtifactInstaller()

        installer.install(
            artifact,
            payload,
        )

        assert installer.installed_payload(artifact.coordinate) == payload

    def test_rejects_duplicate_installation(self) -> None:
        artifact = _artifact()
        installer = InMemoryArtifactInstaller()

        installer.install(
            artifact,
            b"payload",
        )

        with pytest.raises(ArtifactAlreadyInstalledError):
            installer.install(
                artifact,
                b"payload",
            )

    def test_different_versions_install_independently(self) -> None:
        first = _artifact(version="1.0.0")
        second = _artifact(version="2.0.0")
        installer = InMemoryArtifactInstaller()

        first_result = installer.install(
            first,
            b"v1",
        )
        second_result = installer.install(
            second,
            b"v2",
        )

        assert first_result.artifact == first
        assert second_result.artifact == second
        assert installer.is_installed(first.coordinate)
        assert installer.is_installed(second.coordinate)

    def test_rejects_non_artifact_input(self) -> None:
        installer = InMemoryArtifactInstaller()

        with pytest.raises(TypeError):
            installer.install(
                object(),  # type: ignore[arg-type]
                b"payload",
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
    def test_requires_bytes_payload(
        self,
        payload: object,
    ) -> None:
        installer = InMemoryArtifactInstaller()

        with pytest.raises(TypeError):
            installer.install(
                _artifact(),
                payload,  # type: ignore[arg-type]
            )

    def test_copies_payload_value(self) -> None:
        artifact = _artifact()
        payload = b"payload"
        installer = InMemoryArtifactInstaller()

        installer.install(
            artifact,
            payload,
        )

        assert installer.installed_payload(artifact.coordinate) == b"payload"

    def test_installation_does_not_mutate_artifact(self) -> None:
        artifact = _artifact()
        original = artifact
        installer = InMemoryArtifactInstaller()

        installer.install(
            artifact,
            b"payload",
        )

        assert artifact == original

    def test_installation_does_not_verify_integrity(self) -> None:
        artifact = _artifact()
        payload = b"payload whose digest does not match artifact metadata"
        installer = InMemoryArtifactInstaller()

        result = installer.install(
            artifact,
            payload,
        )

        assert result.status is ArtifactInstallationStatus.INSTALLED

    def test_installation_has_no_filesystem_side_effect_contract(
        self,
        tmp_path,
    ) -> None:
        installer = InMemoryArtifactInstaller()
        before = tuple(tmp_path.iterdir())

        installer.install(
            _artifact(),
            b"payload",
        )

        assert tuple(tmp_path.iterdir()) == before

    def test_listing_installed_artifacts_is_deterministic(self) -> None:
        installer = InMemoryArtifactInstaller()
        first = _artifact(
            namespace="zeta",
            name="plugin",
            version="1.0.0",
            artifact_type=ArtifactType.PLUGIN,
        )
        second = _artifact(
            namespace="community",
            name="templates",
            version="2.0.0",
        )
        third = _artifact(
            namespace="community",
            name="templates",
            version="1.0.0",
        )

        installer.install(first, b"first")
        installer.install(second, b"second")
        installer.install(third, b"third")

        coordinates = tuple(str(artifact.coordinate) for artifact in installer.list_installed())

        assert coordinates == (
            "community/templates@1.0.0",
            "community/templates@2.0.0",
            "zeta/plugin@1.0.0",
        )

    def test_empty_installer_has_no_installed_artifacts(self) -> None:
        installer = InMemoryArtifactInstaller()

        assert installer.list_installed() == ()


class TestInstallationErrors:
    def test_duplicate_install_error_is_installation_error(self) -> None:
        assert issubclass(
            ArtifactAlreadyInstalledError,
            ArtifactInstallationError,
        )

    def test_duplicate_error_identifies_coordinate(self) -> None:
        artifact = _artifact()
        installer = InMemoryArtifactInstaller()

        installer.install(
            artifact,
            b"payload",
        )

        with pytest.raises(ArtifactAlreadyInstalledError) as exc_info:
            installer.install(
                artifact,
                b"payload",
            )

        assert str(artifact.coordinate) in str(exc_info.value)
