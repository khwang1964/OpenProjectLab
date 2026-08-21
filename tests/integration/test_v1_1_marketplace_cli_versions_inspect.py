"""v1.1.4.3 internal Marketplace versions and inspect service tests."""

from __future__ import annotations

import hashlib

import pytest

from generator.cli.main import build_parser
from generator.cli.marketplace import (
    MarketplaceCoordinateParseError,
    MarketplaceIdentityParseError,
    get_marketplace_versions,
    inspect_marketplace_artifact,
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
from generator.marketplace.repository import (
    ArtifactNotFoundError,
    InMemoryMarketplaceRepository,
)


def _artifact(version: str, *, name: str = "course-template") -> MarketplaceArtifact:
    return MarketplaceArtifact(
        schema_version=1,
        identity=ArtifactIdentity("community", name),
        version=ArtifactVersion(version),
        artifact_type=ArtifactType.TEMPLATE,
        description=f"Template {version}",
        compatibility=CompatibilityRequirement(">=1.0,<2.0"),
        distribution=DistributionMetadata(
            kind="file",
            reference=f"community/{name}-{version}.opl",
        ),
        integrity=IntegrityMetadata(
            algorithm="sha256",
            digest=hashlib.sha256(version.encode()).hexdigest(),
        ),
    )


def _top_level_commands() -> frozenset[str]:
    for action in build_parser()._actions:
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict) and "list" in choices:
            return frozenset(choices)
    raise AssertionError("CLI subcommand registry was not found")


class _RecordingRepository(InMemoryMarketplaceRepository):
    def __init__(self, artifacts: tuple[MarketplaceArtifact, ...]) -> None:
        super().__init__(artifacts)
        self.calls: list[tuple[str, object]] = []

    def available_versions(self, identity: ArtifactIdentity) -> tuple[ArtifactVersion, ...]:
        self.calls.append(("available_versions", identity))
        return super().available_versions(identity)

    def find(self, identity: ArtifactIdentity, version: ArtifactVersion) -> MarketplaceArtifact:
        self.calls.append(("find", (identity, version)))
        return super().find(identity, version)

    def list_artifacts(self) -> tuple[MarketplaceArtifact, ...]:
        self.calls.append(("list_artifacts", None))
        return super().list_artifacts()


def test_versions_returns_semantic_versions_in_deterministic_ascending_order() -> None:
    repository = _RecordingRepository((_artifact("10.0.0"), _artifact("2.0.0"), _artifact("1.9.0")))

    versions = get_marketplace_versions(repository, "community/course-template")

    assert versions == (
        ArtifactVersion("1.9.0"),
        ArtifactVersion("2.0.0"),
        ArtifactVersion("10.0.0"),
    )
    assert repository.calls == [
        ("available_versions", ArtifactIdentity("community", "course-template"))
    ]


def test_versions_returns_empty_tuple_for_unknown_identity() -> None:
    repository = _RecordingRepository((_artifact("1.0.0"),))

    assert get_marketplace_versions(repository, "community/unknown") == ()
    assert repository.calls == [("available_versions", ArtifactIdentity("community", "unknown"))]


def test_versions_rejects_invalid_identity_before_repository_access() -> None:
    repository = _RecordingRepository((_artifact("1.0.0"),))

    with pytest.raises(MarketplaceIdentityParseError):
        get_marketplace_versions(repository, "community/course-template/extra")

    assert repository.calls == []


def test_inspect_returns_the_exact_immutable_artifact() -> None:
    expected = _artifact("1.2.3")
    repository = _RecordingRepository((expected, _artifact("2.0.0")))

    artifact = inspect_marketplace_artifact(repository, "community/course-template@1.2.3")

    assert artifact is expected
    assert repository.calls == [
        (
            "find",
            (
                ArtifactIdentity("community", "course-template"),
                ArtifactVersion("1.2.3"),
            ),
        )
    ]


def test_inspect_preserves_exact_not_found_failure() -> None:
    repository = _RecordingRepository((_artifact("1.2.3"),))

    with pytest.raises(ArtifactNotFoundError):
        inspect_marketplace_artifact(repository, "community/course-template@9.9.9")

    assert repository.calls == [
        (
            "find",
            (
                ArtifactIdentity("community", "course-template"),
                ArtifactVersion("9.9.9"),
            ),
        )
    ]


def test_inspect_rejects_invalid_coordinate_before_repository_access() -> None:
    repository = _RecordingRepository((_artifact("1.2.3"),))

    with pytest.raises(MarketplaceCoordinateParseError):
        inspect_marketplace_artifact(repository, "community/course-template@1.2")

    assert repository.calls == []


def test_versions_and_inspect_do_not_use_internal_global_enumeration() -> None:
    artifact = _artifact("1.2.3")
    repository = _RecordingRepository((artifact,))

    get_marketplace_versions(repository, "community/course-template")
    inspect_marketplace_artifact(repository, "community/course-template@1.2.3")

    assert all(call[0] != "list_artifacts" for call in repository.calls)


def test_internal_query_services_remain_available_after_registration() -> None:
    assert "marketplace" in _top_level_commands()
