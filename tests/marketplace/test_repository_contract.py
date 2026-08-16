"""Contract tests for the Marketplace repository/index boundary.

Step 7.4 scope:
- deterministic in-memory artifact lookup
- exact coordinate lookup
- available-version lookup and ordering
- deterministic artifact listing
- duplicate-coordinate rejection
- explicit not-found semantics

Out of scope:
- remote repositories
- acquisition/download
- integrity verification
- installation/activation
- CLI
- filesystem side effects
- generator execution
"""

from __future__ import annotations

import pytest

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
    ArtifactAlreadyExistsError,
    ArtifactNotFoundError,
    InMemoryMarketplaceRepository,
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


class TestRepositoryRegistration:
    def test_accepts_unique_artifacts(self) -> None:
        first = _artifact(version="1.0.0")
        second = _artifact(version="1.1.0")

        repository = InMemoryMarketplaceRepository(
            [
                first,
                second,
            ]
        )

        assert (
            repository.find(
                first.identity,
                first.version,
            )
            == first
        )
        assert (
            repository.find(
                second.identity,
                second.version,
            )
            == second
        )

    def test_rejects_duplicate_coordinate(self) -> None:
        artifact = _artifact()

        with pytest.raises(ArtifactAlreadyExistsError):
            InMemoryMarketplaceRepository(
                [
                    artifact,
                    artifact,
                ]
            )

    def test_rejects_conflicting_duplicate_coordinate(self) -> None:
        first = _artifact()
        second = MarketplaceArtifact(
            schema_version=1,
            identity=first.identity,
            version=first.version,
            artifact_type=first.artifact_type,
            description="different metadata for the same coordinate",
            compatibility=first.compatibility,
            distribution=DistributionMetadata(
                kind="package",
                reference="different-reference",
            ),
            integrity=IntegrityMetadata(
                algorithm="sha256",
                digest="b" * 64,
            ),
        )

        with pytest.raises(ArtifactAlreadyExistsError):
            InMemoryMarketplaceRepository(
                [
                    first,
                    second,
                ]
            )


class TestExactLookup:
    def test_finds_artifact_by_identity_and_version(self) -> None:
        artifact = _artifact(
            namespace="community",
            name="course-generator",
            version="2.3.4",
            artifact_type=ArtifactType.GENERATOR,
        )
        repository = InMemoryMarketplaceRepository([artifact])

        result = repository.find(
            ArtifactIdentity(
                namespace="community",
                name="course-generator",
            ),
            ArtifactVersion("2.3.4"),
        )

        assert result == artifact

    def test_missing_version_raises_explicit_not_found_error(self) -> None:
        artifact = _artifact(version="1.0.0")
        repository = InMemoryMarketplaceRepository([artifact])

        with pytest.raises(ArtifactNotFoundError):
            repository.find(
                artifact.identity,
                ArtifactVersion("9.9.9"),
            )

    def test_missing_identity_raises_explicit_not_found_error(self) -> None:
        repository = InMemoryMarketplaceRepository(
            [
                _artifact(),
            ]
        )

        with pytest.raises(ArtifactNotFoundError):
            repository.find(
                ArtifactIdentity(
                    namespace="community",
                    name="missing",
                ),
                ArtifactVersion("1.0.0"),
            )


class TestAvailableVersions:
    def test_returns_versions_in_ascending_semantic_order(self) -> None:
        identity = ArtifactIdentity(
            namespace="community",
            name="modern-java-templates",
        )
        repository = InMemoryMarketplaceRepository(
            [
                _artifact(version="2.0.0"),
                _artifact(version="1.10.0"),
                _artifact(version="1.2.0"),
                _artifact(version="1.0.0"),
            ]
        )

        assert repository.available_versions(identity) == (
            ArtifactVersion("1.0.0"),
            ArtifactVersion("1.2.0"),
            ArtifactVersion("1.10.0"),
            ArtifactVersion("2.0.0"),
        )

    def test_missing_identity_returns_empty_tuple(self) -> None:
        repository = InMemoryMarketplaceRepository(
            [
                _artifact(),
            ]
        )

        assert (
            repository.available_versions(
                ArtifactIdentity(
                    namespace="community",
                    name="missing",
                )
            )
            == ()
        )

    def test_available_versions_are_immutable(self) -> None:
        artifact = _artifact()
        repository = InMemoryMarketplaceRepository([artifact])

        versions = repository.available_versions(
            artifact.identity,
        )

        assert isinstance(versions, tuple)


class TestArtifactListing:
    def test_lists_artifacts_deterministically_by_coordinate(self) -> None:
        repository = InMemoryMarketplaceRepository(
            [
                _artifact(
                    namespace="zeta",
                    name="plugin",
                    version="1.0.0",
                    artifact_type=ArtifactType.PLUGIN,
                ),
                _artifact(
                    namespace="community",
                    name="templates",
                    version="2.0.0",
                ),
                _artifact(
                    namespace="community",
                    name="templates",
                    version="1.0.0",
                ),
                _artifact(
                    namespace="community",
                    name="generator",
                    version="1.0.0",
                    artifact_type=ArtifactType.GENERATOR,
                ),
            ]
        )

        coordinates = tuple(str(artifact.coordinate) for artifact in repository.list_artifacts())

        assert coordinates == (
            "community/generator@1.0.0",
            "community/templates@1.0.0",
            "community/templates@2.0.0",
            "zeta/plugin@1.0.0",
        )

    def test_empty_repository_returns_empty_tuple(self) -> None:
        repository = InMemoryMarketplaceRepository()

        assert repository.list_artifacts() == ()

    def test_listing_is_immutable(self) -> None:
        repository = InMemoryMarketplaceRepository(
            [
                _artifact(),
            ]
        )

        assert isinstance(
            repository.list_artifacts(),
            tuple,
        )


class TestRepositoryDeterminism:
    def test_insertion_order_does_not_change_lookup_results(self) -> None:
        first = _artifact(version="1.0.0")
        second = _artifact(version="2.0.0")

        forward = InMemoryMarketplaceRepository(
            [
                first,
                second,
            ]
        )
        reverse = InMemoryMarketplaceRepository(
            [
                second,
                first,
            ]
        )

        assert forward.list_artifacts() == reverse.list_artifacts()
        assert forward.available_versions(first.identity) == (
            reverse.available_versions(first.identity)
        )

    def test_repository_does_not_mutate_source_collection(self) -> None:
        artifacts = [
            _artifact(version="1.0.0"),
            _artifact(version="2.0.0"),
        ]
        original = list(artifacts)

        InMemoryMarketplaceRepository(artifacts)

        assert artifacts == original
