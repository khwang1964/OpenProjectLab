"""Representative Marketplace end-to-end integration tests.

Milestone 7 Step 7.8 composes the production Marketplace boundaries directly:

Repository
    -> Acquisition
    -> Integrity verification
    -> Installation

The representative flow is intentionally deterministic and local. It does not
use a public Marketplace, network access, an external package manager, plugin
activation, generator execution, or Courseware filesystem output.
"""

from __future__ import annotations

import hashlib

import pytest

from generator.marketplace.acquisition import (
    ArtifactPayloadNotFoundError,
    InMemoryArtifactAcquirer,
)
from generator.marketplace.installation import (
    ArtifactInstallationStatus,
    InMemoryArtifactInstaller,
)
from generator.marketplace.integrity import ArtifactIntegrityError, verify_integrity
from generator.marketplace.models import (
    ArtifactIdentity,
    ArtifactType,
    ArtifactVersion,
    CompatibilityRequirement,
    DistributionMetadata,
    IntegrityMetadata,
    MarketplaceArtifact,
)
from generator.marketplace.repository import (
    ArtifactNotFoundError,
    InMemoryMarketplaceRepository,
)
from generator.marketplace.template_package import (
    TemplateEntry,
    TemplatePackage,
    TemplatePackageManifest,
)


def _payload() -> bytes:
    return b"templates/week/README.md.j2\n# Week {{ week_number }}: {{ title }}\n"


def _artifact(
    *,
    digest: str | None = None,
) -> MarketplaceArtifact:
    payload = _payload()
    return MarketplaceArtifact(
        schema_version=1,
        identity=ArtifactIdentity(
            namespace="community",
            name="modern-java-templates",
        ),
        version=ArtifactVersion("1.0.0"),
        artifact_type=ArtifactType.TEMPLATE,
        description="Modern Java Marketplace template package",
        compatibility=CompatibilityRequirement(">=0.7,<1.0"),
        distribution=DistributionMetadata(
            kind="package",
            reference="community-modern-java-templates-1.0.0",
        ),
        integrity=IntegrityMetadata(
            algorithm="sha256",
            digest=(hashlib.sha256(payload).hexdigest() if digest is None else digest),
        ),
    )


def _template_package(
    artifact: MarketplaceArtifact,
) -> TemplatePackage:
    return TemplatePackage(
        artifact=artifact,
        manifest=TemplatePackageManifest(
            schema_version=1,
            templates=(
                TemplateEntry(
                    name="week-readme",
                    relative_path="templates/week/README.md.j2",
                    media_type="text/markdown+j2",
                ),
            ),
            resources=(),
        ),
    )


def _run_representative_flow(
    *,
    repository: InMemoryMarketplaceRepository,
    acquirer: InMemoryArtifactAcquirer,
    installer: InMemoryArtifactInstaller,
    identity: ArtifactIdentity,
    version: ArtifactVersion,
):
    artifact = repository.find(
        identity,
        version,
    )
    payload = acquirer.acquire(artifact)
    verify_integrity(
        payload,
        artifact.integrity,
    )
    return installer.install(
        artifact,
        payload,
    )


class TestMarketplaceRepresentativeE2E:
    def test_repository_to_verified_installation_happy_path(
        self,
    ) -> None:
        artifact = _artifact()
        package = _template_package(artifact)
        payload = _payload()

        repository = InMemoryMarketplaceRepository(
            [
                package.artifact,
            ]
        )
        acquirer = InMemoryArtifactAcquirer(
            {
                package.coordinate: payload,
            }
        )
        installer = InMemoryArtifactInstaller()

        result = _run_representative_flow(
            repository=repository,
            acquirer=acquirer,
            installer=installer,
            identity=artifact.identity,
            version=artifact.version,
        )

        assert result.artifact == artifact
        assert result.status is ArtifactInstallationStatus.INSTALLED
        assert result.payload_size == len(payload)
        assert installer.is_installed(artifact.coordinate)
        assert installer.installed_payload(artifact.coordinate) == payload

    def test_representative_template_package_contract_is_preserved(
        self,
    ) -> None:
        artifact = _artifact()
        package = _template_package(artifact)

        assert package.artifact.artifact_type is ArtifactType.TEMPLATE
        assert package.coordinate == artifact.coordinate
        assert package.manifest.templates == (
            TemplateEntry(
                name="week-readme",
                relative_path="templates/week/README.md.j2",
                media_type="text/markdown+j2",
            ),
        )
        assert package.manifest.resources == ()

    def test_same_inputs_produce_same_representative_results(
        self,
    ) -> None:
        artifact = _artifact()
        payload = _payload()

        first_repository = InMemoryMarketplaceRepository([artifact])
        second_repository = InMemoryMarketplaceRepository([artifact])

        first_acquirer = InMemoryArtifactAcquirer(
            {
                artifact.coordinate: payload,
            }
        )
        second_acquirer = InMemoryArtifactAcquirer(
            {
                artifact.coordinate: payload,
            }
        )

        first_installer = InMemoryArtifactInstaller()
        second_installer = InMemoryArtifactInstaller()

        first_result = _run_representative_flow(
            repository=first_repository,
            acquirer=first_acquirer,
            installer=first_installer,
            identity=artifact.identity,
            version=artifact.version,
        )
        second_result = _run_representative_flow(
            repository=second_repository,
            acquirer=second_acquirer,
            installer=second_installer,
            identity=artifact.identity,
            version=artifact.version,
        )

        assert first_result == second_result
        assert first_installer.list_installed() == second_installer.list_installed()
        assert first_installer.installed_payload(
            artifact.coordinate
        ) == second_installer.installed_payload(artifact.coordinate)

    def test_repository_not_found_fails_before_acquisition_or_installation(
        self,
    ) -> None:
        artifact = _artifact()
        repository = InMemoryMarketplaceRepository()
        acquirer = InMemoryArtifactAcquirer(
            {
                artifact.coordinate: _payload(),
            }
        )
        installer = InMemoryArtifactInstaller()

        with pytest.raises(ArtifactNotFoundError):
            _run_representative_flow(
                repository=repository,
                acquirer=acquirer,
                installer=installer,
                identity=artifact.identity,
                version=artifact.version,
            )

        assert installer.list_installed() == ()

    def test_missing_payload_fails_before_installation(
        self,
    ) -> None:
        artifact = _artifact()
        repository = InMemoryMarketplaceRepository([artifact])
        acquirer = InMemoryArtifactAcquirer()
        installer = InMemoryArtifactInstaller()

        with pytest.raises(ArtifactPayloadNotFoundError):
            _run_representative_flow(
                repository=repository,
                acquirer=acquirer,
                installer=installer,
                identity=artifact.identity,
                version=artifact.version,
            )

        assert installer.list_installed() == ()

    def test_integrity_mismatch_fails_before_installation(
        self,
    ) -> None:
        artifact = _artifact(
            digest="a" * 64,
        )
        repository = InMemoryMarketplaceRepository([artifact])
        acquirer = InMemoryArtifactAcquirer(
            {
                artifact.coordinate: _payload(),
            }
        )
        installer = InMemoryArtifactInstaller()

        with pytest.raises(ArtifactIntegrityError):
            _run_representative_flow(
                repository=repository,
                acquirer=acquirer,
                installer=installer,
                identity=artifact.identity,
                version=artifact.version,
            )

        assert installer.list_installed() == ()
        assert installer.is_installed(artifact.coordinate) is False

    def test_failed_flow_does_not_leave_partial_installation_state(
        self,
    ) -> None:
        artifact = _artifact(
            digest="b" * 64,
        )
        repository = InMemoryMarketplaceRepository([artifact])
        acquirer = InMemoryArtifactAcquirer(
            {
                artifact.coordinate: _payload(),
            }
        )
        installer = InMemoryArtifactInstaller()

        with pytest.raises(ArtifactIntegrityError):
            _run_representative_flow(
                repository=repository,
                acquirer=acquirer,
                installer=installer,
                identity=artifact.identity,
                version=artifact.version,
            )

        assert installer.list_installed() == ()

    def test_representative_flow_has_no_filesystem_persistence(
        self,
        tmp_path,
    ) -> None:
        artifact = _artifact()
        payload = _payload()

        repository = InMemoryMarketplaceRepository([artifact])
        acquirer = InMemoryArtifactAcquirer(
            {
                artifact.coordinate: payload,
            }
        )
        installer = InMemoryArtifactInstaller()

        before = tuple(tmp_path.iterdir())

        _run_representative_flow(
            repository=repository,
            acquirer=acquirer,
            installer=installer,
            identity=artifact.identity,
            version=artifact.version,
        )

        assert tuple(tmp_path.iterdir()) == before

    def test_representative_flow_uses_exact_coordinate(
        self,
    ) -> None:
        artifact = _artifact()
        repository = InMemoryMarketplaceRepository([artifact])
        acquirer = InMemoryArtifactAcquirer(
            {
                artifact.coordinate: _payload(),
            }
        )
        installer = InMemoryArtifactInstaller()

        with pytest.raises(ArtifactNotFoundError):
            _run_representative_flow(
                repository=repository,
                acquirer=acquirer,
                installer=installer,
                identity=artifact.identity,
                version=ArtifactVersion("2.0.0"),
            )

        assert installer.list_installed() == ()
