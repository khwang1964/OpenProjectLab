"""v1.1.4.5 Marketplace install, dry-run, and no-partial-state tests."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from generator.cli.main import build_parser
from generator.cli.marketplace import (
    MarketplaceCoordinateParseError,
    MarketplacePayloadError,
    install_marketplace_artifact,
)
from generator.marketplace.installation import (
    ArtifactAlreadyInstalledError,
    ArtifactInstallationError,
    ArtifactInstallationResult,
    ArtifactInstallationStatus,
    InMemoryArtifactInstaller,
)
from generator.marketplace.integrity import ArtifactIntegrityError
from generator.marketplace.models import (
    ArtifactIdentity,
    ArtifactType,
    ArtifactVersion,
    CompatibilityRequirement,
    DistributionMetadata,
    IntegrityMetadata,
    MarketplaceArtifact,
)
from generator.marketplace.repository import InMemoryMarketplaceRepository


def _artifact(payload: bytes, *, digest: str | None = None) -> MarketplaceArtifact:
    return MarketplaceArtifact(
        schema_version=1,
        identity=ArtifactIdentity("community", "demo"),
        version=ArtifactVersion("1.2.3"),
        artifact_type=ArtifactType.TEMPLATE,
        description="Verified installation fixture",
        compatibility=CompatibilityRequirement(">=1.0,<2.0"),
        distribution=DistributionMetadata(kind="file", reference="packages/demo.opl"),
        integrity=IntegrityMetadata(
            algorithm="sha256",
            digest=digest or hashlib.sha256(payload).hexdigest(),
        ),
    )


def _fixture(tmp_path: Path, payload: bytes) -> tuple[MarketplaceArtifact, Path]:
    path = tmp_path / "packages" / "demo.opl"
    path.parent.mkdir(parents=True)
    path.write_bytes(payload)
    return _artifact(payload), path


def _repository(artifact: MarketplaceArtifact) -> InMemoryMarketplaceRepository:
    return InMemoryMarketplaceRepository((artifact,))


def _top_level_commands() -> frozenset[str]:
    for action in build_parser()._actions:
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict) and "list" in choices:
            return frozenset(choices)
    raise AssertionError("CLI subcommand registry was not found")


class _RecordingInstaller(InMemoryArtifactInstaller):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[tuple[MarketplaceArtifact, bytes]] = []

    def install(self, artifact: MarketplaceArtifact, payload: bytes) -> ArtifactInstallationResult:
        self.calls.append((artifact, payload))
        return super().install(artifact, payload)


class _FailingInstaller:
    def __init__(self) -> None:
        self.calls: list[tuple[MarketplaceArtifact, bytes]] = []

    def install(self, artifact: MarketplaceArtifact, payload: bytes) -> ArtifactInstallationResult:
        self.calls.append((artifact, payload))
        raise ArtifactInstallationError("controlled installation failure")


def test_install_runs_only_after_successful_verification(tmp_path: Path) -> None:
    payload = b"verified installation payload"
    artifact, _ = _fixture(tmp_path, payload)
    installer = _RecordingInstaller()

    outcome = install_marketplace_artifact(
        _repository(artifact),
        installer,
        "community/demo@1.2.3",
        tmp_path,
    )

    assert outcome.dry_run is False
    assert outcome.verified.artifact is artifact
    assert outcome.verified.payload == payload
    assert outcome.installation == ArtifactInstallationResult(
        artifact=artifact,
        status=ArtifactInstallationStatus.INSTALLED,
        payload_size=len(payload),
    )
    assert installer.calls == [(artifact, payload)]
    assert installer.installed_payload(artifact.coordinate) == payload


def test_dry_run_verifies_without_calling_installer(tmp_path: Path) -> None:
    payload = b"dry-run payload"
    artifact, _ = _fixture(tmp_path, payload)
    installer = _RecordingInstaller()

    outcome = install_marketplace_artifact(
        _repository(artifact),
        installer,
        "community/demo@1.2.3",
        tmp_path,
        dry_run=True,
    )

    assert outcome.dry_run is True
    assert outcome.installation is None
    assert outcome.verified.digest == hashlib.sha256(payload).hexdigest()
    assert installer.calls == []
    assert installer.list_installed() == ()


@pytest.mark.parametrize("dry_run", (False, True))
def test_integrity_failure_never_calls_installer(tmp_path: Path, dry_run: bool) -> None:
    payload = b"actual"
    artifact, _ = _fixture(tmp_path, payload)
    artifact = _artifact(payload, digest=hashlib.sha256(b"expected").hexdigest())
    installer = _RecordingInstaller()

    with pytest.raises(ArtifactIntegrityError):
        install_marketplace_artifact(
            _repository(artifact),
            installer,
            "community/demo@1.2.3",
            tmp_path,
            dry_run=dry_run,
        )

    assert installer.calls == []
    assert installer.list_installed() == ()


@pytest.mark.parametrize("dry_run", (False, True))
def test_lookup_and_payload_failures_never_call_installer(tmp_path: Path, dry_run: bool) -> None:
    artifact = _artifact(b"payload")
    installer = _RecordingInstaller()

    with pytest.raises(MarketplacePayloadError):
        install_marketplace_artifact(
            _repository(artifact),
            installer,
            "community/demo@1.2.3",
            tmp_path,
            dry_run=dry_run,
        )

    assert installer.calls == []
    assert installer.list_installed() == ()


def test_invalid_coordinate_fails_before_installer_access(tmp_path: Path) -> None:
    artifact, _ = _fixture(tmp_path, b"payload")
    installer = _RecordingInstaller()

    with pytest.raises(MarketplaceCoordinateParseError):
        install_marketplace_artifact(
            _repository(artifact), installer, "community/demo@1.2", tmp_path
        )

    assert installer.calls == []


def test_duplicate_installation_preserves_original_payload(tmp_path: Path) -> None:
    original = b"original payload"
    artifact, path = _fixture(tmp_path, original)
    installer = InMemoryArtifactInstaller()
    repository = _repository(artifact)
    install_marketplace_artifact(repository, installer, "community/demo@1.2.3", tmp_path)
    replacement = b"replacement bytes"
    path.write_bytes(replacement)
    replacement_repository = _repository(_artifact(replacement))

    with pytest.raises(ArtifactAlreadyInstalledError):
        install_marketplace_artifact(
            replacement_repository, installer, "community/demo@1.2.3", tmp_path
        )

    assert installer.installed_payload(artifact.coordinate) == original


def test_exact_duplicate_installation_is_rejected_without_replacement(
    tmp_path: Path,
) -> None:
    payload = b"same verified payload"
    artifact, _ = _fixture(tmp_path, payload)
    installer = InMemoryArtifactInstaller()
    repository = _repository(artifact)
    install_marketplace_artifact(repository, installer, "community/demo@1.2.3", tmp_path)

    with pytest.raises(ArtifactAlreadyInstalledError):
        install_marketplace_artifact(repository, installer, "community/demo@1.2.3", tmp_path)

    assert installer.installed_payload(artifact.coordinate) == payload
    assert installer.list_installed() == (artifact,)


def test_controlled_installer_failure_occurs_after_verified_payload(tmp_path: Path) -> None:
    payload = b"verified before installer failure"
    artifact, _ = _fixture(tmp_path, payload)
    installer = _FailingInstaller()

    with pytest.raises(ArtifactInstallationError):
        install_marketplace_artifact(
            _repository(artifact), installer, "community/demo@1.2.3", tmp_path
        )

    assert installer.calls == [(artifact, payload)]


def test_install_requires_boolean_dry_run_before_any_side_effect(tmp_path: Path) -> None:
    artifact, _ = _fixture(tmp_path, b"payload")
    installer = _RecordingInstaller()

    with pytest.raises(TypeError, match="dry_run"):
        install_marketplace_artifact(
            _repository(artifact),
            installer,
            "community/demo@1.2.3",
            tmp_path,
            dry_run=1,  # type: ignore[arg-type]
        )

    assert installer.calls == []


def test_install_service_does_not_register_production_parser() -> None:
    assert "marketplace" not in _top_level_commands()
