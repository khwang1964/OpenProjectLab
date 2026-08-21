"""v1.1.4.4 safe local Marketplace verification tests."""

from __future__ import annotations

import hashlib
import os
from pathlib import Path

import pytest

from generator.cli.main import build_parser
from generator.cli.marketplace import (
    MarketplaceCoordinateParseError,
    MarketplacePayloadError,
    verify_marketplace_artifact,
)
from generator.marketplace.installation import InMemoryArtifactInstaller
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


def _artifact(
    payload: bytes,
    *,
    reference: str = "packages/demo.opl",
    kind: str = "file",
    digest: str | None = None,
) -> MarketplaceArtifact:
    return MarketplaceArtifact(
        schema_version=1,
        identity=ArtifactIdentity("community", "demo"),
        version=ArtifactVersion("1.2.3"),
        artifact_type=ArtifactType.TEMPLATE,
        description="Safe local verification fixture",
        compatibility=CompatibilityRequirement(">=1.0,<2.0"),
        distribution=DistributionMetadata(kind=kind, reference=reference),
        integrity=IntegrityMetadata(
            algorithm="sha256",
            digest=digest or hashlib.sha256(payload).hexdigest(),
        ),
    )


def _repository(artifact: MarketplaceArtifact) -> InMemoryMarketplaceRepository:
    return InMemoryMarketplaceRepository((artifact,))


def _write_payload(root: Path, payload: bytes) -> Path:
    path = root / "packages" / "demo.opl"
    path.parent.mkdir(parents=True)
    path.write_bytes(payload)
    return path


def _top_level_commands() -> frozenset[str]:
    for action in build_parser()._actions:
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict) and "list" in choices:
            return frozenset(choices)
    raise AssertionError("CLI subcommand registry was not found")


def test_verify_returns_exact_verified_payload_metadata(tmp_path: Path) -> None:
    payload = b"deterministic marketplace payload"
    _write_payload(tmp_path, payload)
    artifact = _artifact(payload)

    result = verify_marketplace_artifact(
        _repository(artifact),
        "community/demo@1.2.3",
        tmp_path,
    )

    assert result.artifact is artifact
    assert result.payload == payload
    assert result.digest == hashlib.sha256(payload).hexdigest()
    assert result.payload_size == len(payload)


def test_verify_accepts_safe_backslash_separated_reference(tmp_path: Path) -> None:
    payload = b"portable local reference"
    _write_payload(tmp_path, payload)
    artifact = _artifact(payload, reference=r"packages\demo.opl")

    result = verify_marketplace_artifact(_repository(artifact), "community/demo@1.2.3", tmp_path)

    assert result.payload == payload


@pytest.mark.parametrize(
    "reference",
    (
        "/absolute/demo.opl",
        r"C:\payloads\demo.opl",
        r"C:payloads\demo.opl",
        r"\\server\share\demo.opl",
        "../demo.opl",
        "packages/../../demo.opl",
        r"packages\..\..\demo.opl",
    ),
)
def test_verify_rejects_unsafe_reference_before_reading(tmp_path: Path, reference: str) -> None:
    artifact = _artifact(b"payload", reference=reference)

    with pytest.raises(MarketplacePayloadError):
        verify_marketplace_artifact(_repository(artifact), "community/demo@1.2.3", tmp_path)


def test_verify_rejects_unsupported_distribution_kind(tmp_path: Path) -> None:
    artifact = _artifact(b"payload", kind="remote")

    with pytest.raises(MarketplacePayloadError, match="file distribution"):
        verify_marketplace_artifact(_repository(artifact), "community/demo@1.2.3", tmp_path)


def test_verify_rejects_missing_payload_root(tmp_path: Path) -> None:
    artifact = _artifact(b"payload")

    with pytest.raises(MarketplacePayloadError, match="root"):
        verify_marketplace_artifact(
            _repository(artifact), "community/demo@1.2.3", tmp_path / "missing"
        )


def test_verify_rejects_missing_payload(tmp_path: Path) -> None:
    artifact = _artifact(b"payload")

    with pytest.raises(MarketplacePayloadError, match="missing or escapes"):
        verify_marketplace_artifact(_repository(artifact), "community/demo@1.2.3", tmp_path)


def test_verify_rejects_directory_payload(tmp_path: Path) -> None:
    (tmp_path / "packages" / "demo.opl").mkdir(parents=True)
    artifact = _artifact(b"payload")

    with pytest.raises(MarketplacePayloadError, match="regular file"):
        verify_marketplace_artifact(_repository(artifact), "community/demo@1.2.3", tmp_path)


def test_verify_rejects_symlink_escaping_payload_root(tmp_path: Path) -> None:
    payload_root = tmp_path / "root"
    payload_root.mkdir()
    outside = tmp_path / "outside.opl"
    outside.write_bytes(b"outside")
    link = payload_root / "escape.opl"
    try:
        os.symlink(outside, link)
    except (OSError, NotImplementedError):
        pytest.skip("symlink creation is unavailable")
    artifact = _artifact(b"outside", reference="escape.opl")

    with pytest.raises(MarketplacePayloadError, match="missing or escapes"):
        verify_marketplace_artifact(_repository(artifact), "community/demo@1.2.3", payload_root)


def test_verify_rejects_integrity_mismatch_without_installation(tmp_path: Path) -> None:
    payload = b"actual"
    _write_payload(tmp_path, payload)
    artifact = _artifact(payload, digest=hashlib.sha256(b"expected").hexdigest())
    installer = InMemoryArtifactInstaller()

    with pytest.raises(ArtifactIntegrityError):
        verify_marketplace_artifact(_repository(artifact), "community/demo@1.2.3", tmp_path)

    assert installer.list_installed() == ()


def test_verify_rejects_invalid_coordinate_before_payload_access(tmp_path: Path) -> None:
    payload = b"payload"
    payload_path = _write_payload(tmp_path, payload)
    artifact = _artifact(payload)

    with pytest.raises(MarketplaceCoordinateParseError):
        verify_marketplace_artifact(_repository(artifact), "community/demo@1.2", tmp_path)

    assert payload_path.read_bytes() == payload


def test_safe_verify_does_not_register_production_parser() -> None:
    assert "marketplace" not in _top_level_commands()
