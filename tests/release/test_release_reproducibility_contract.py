"""Contract tests for semantic release reproducibility."""

from __future__ import annotations

from pathlib import Path

import pytest

from generator.release.artifacts import ReleaseArtifact, ReleaseArtifactSet
from generator.release.reproducibility import (
    ReleaseBuildSnapshot,
    ReleaseReproducibilityError,
    build_release_snapshot,
    compare_release_snapshots,
    verify_semantic_reproducibility,
    verify_wheel_for_clean_install,
)


def _artifact_set(
    tmp_path: Path,
    *,
    version: str = "1.0.0",
) -> ReleaseArtifactSet:
    """Create one deterministic wheel/sdist artifact set."""
    wheel = tmp_path / f"openprojectlab-{version}-py3-none-any.whl"
    sdist = tmp_path / f"openprojectlab-{version}.tar.gz"
    wheel.write_bytes(b"wheel-bytes")
    sdist.write_bytes(b"sdist-bytes")

    return ReleaseArtifactSet(
        artifacts=(
            ReleaseArtifact.from_path(wheel),
            ReleaseArtifact.from_path(sdist),
        )
    )


def _snapshot(
    *,
    version: str = "1.0.0",
    project_name: str = "openprojectlab",
    artifact_names: tuple[str, ...] | None = None,
    artifact_kinds: tuple[str, ...] = ("sdist", "wheel"),
    wheel_project: str = "openprojectlab",
    wheel_version: str = "1.0.0",
    checksums: tuple[tuple[str, str], ...] | None = None,
) -> ReleaseBuildSnapshot:
    """Create a snapshot with explicit semantic and byte-level fields."""
    if artifact_names is None:
        artifact_names = (
            "openprojectlab-1.0.0-py3-none-any.whl",
            "openprojectlab-1.0.0.tar.gz",
        )

    if checksums is None:
        checksums = (
            ("openprojectlab-1.0.0-py3-none-any.whl", "1" * 64),
            ("openprojectlab-1.0.0.tar.gz", "2" * 64),
        )

    return ReleaseBuildSnapshot(
        project_name=project_name,
        version=version,
        artifact_names=artifact_names,
        artifact_kinds=artifact_kinds,
        wheel_project=wheel_project,
        wheel_version=wheel_version,
        checksums=checksums,
    )


def test_release_build_snapshot_is_immutable() -> None:
    """Reproducibility evidence must not mutate after capture."""
    snapshot = _snapshot()

    with pytest.raises((AttributeError, TypeError)):
        snapshot.version = "1.0.1"


def test_build_release_snapshot_records_semantic_identity(
    tmp_path: Path,
) -> None:
    """Snapshot must capture the release's semantic artifact identity."""
    artifacts = _artifact_set(tmp_path)
    snapshot = build_release_snapshot(
        project_name="openprojectlab",
        version="1.0.0",
        artifact_set=artifacts,
        wheel_project="openprojectlab",
        wheel_version="1.0.0",
        checksums={
            "openprojectlab-1.0.0-py3-none-any.whl": "1" * 64,
            "openprojectlab-1.0.0.tar.gz": "2" * 64,
        },
    )

    assert snapshot.project_name == "openprojectlab"
    assert snapshot.version == "1.0.0"
    assert snapshot.wheel_project == "openprojectlab"
    assert snapshot.wheel_version == "1.0.0"
    assert snapshot.artifact_kinds == ("sdist", "wheel")


def test_build_release_snapshot_sorts_artifact_names(
    tmp_path: Path,
) -> None:
    """Snapshot ordering must be deterministic."""
    artifacts = _artifact_set(tmp_path)
    snapshot = build_release_snapshot(
        project_name="openprojectlab",
        version="1.0.0",
        artifact_set=artifacts,
        wheel_project="openprojectlab",
        wheel_version="1.0.0",
        checksums={
            "openprojectlab-1.0.0.tar.gz": "2" * 64,
            "openprojectlab-1.0.0-py3-none-any.whl": "1" * 64,
        },
    )

    assert snapshot.artifact_names == tuple(sorted(snapshot.artifact_names))
    assert snapshot.checksums == tuple(sorted(snapshot.checksums))


def test_build_release_snapshot_requires_exact_checksum_coverage(
    tmp_path: Path,
) -> None:
    """Snapshot checksum evidence must cover the exact artifact set."""
    artifacts = _artifact_set(tmp_path)

    with pytest.raises(ReleaseReproducibilityError):
        build_release_snapshot(
            project_name="openprojectlab",
            version="1.0.0",
            artifact_set=artifacts,
            wheel_project="openprojectlab",
            wheel_version="1.0.0",
            checksums={
                "openprojectlab-1.0.0-py3-none-any.whl": "1" * 64,
            },
        )


def test_compare_release_snapshots_accepts_semantically_equivalent_builds() -> None:
    """Equivalent metadata and artifact classes satisfy semantic reproducibility."""
    baseline = _snapshot()
    rebuilt = _snapshot()

    assert compare_release_snapshots(baseline, rebuilt) == ()


def test_compare_release_snapshots_reports_version_difference() -> None:
    """Different release version is a semantic reproducibility failure."""
    differences = compare_release_snapshots(
        _snapshot(),
        _snapshot(version="1.0.1", wheel_version="1.0.1"),
    )

    assert "version" in differences


def test_compare_release_snapshots_reports_project_difference() -> None:
    """Different project identity is a semantic reproducibility failure."""
    differences = compare_release_snapshots(
        _snapshot(),
        _snapshot(
            project_name="other-project",
            wheel_project="other-project",
        ),
    )

    assert "project_name" in differences


def test_compare_release_snapshots_reports_artifact_kind_difference() -> None:
    """Missing artifact type is a semantic reproducibility failure."""
    differences = compare_release_snapshots(
        _snapshot(),
        _snapshot(artifact_kinds=("wheel",)),
    )

    assert "artifact_kinds" in differences


def test_compare_release_snapshots_reports_wheel_metadata_difference() -> None:
    """Wheel metadata identity must remain contract-equivalent."""
    differences = compare_release_snapshots(
        _snapshot(),
        _snapshot(wheel_version="1.0.1"),
    )

    assert "wheel_version" in differences


def test_compare_release_snapshots_does_not_require_same_checksums() -> None:
    """Semantic reproducibility must not imply byte-for-byte reproducibility."""
    baseline = _snapshot()
    rebuilt = _snapshot(
        checksums=(
            ("openprojectlab-1.0.0-py3-none-any.whl", "a" * 64),
            ("openprojectlab-1.0.0.tar.gz", "b" * 64),
        )
    )

    assert compare_release_snapshots(baseline, rebuilt) == ()


def test_verify_semantic_reproducibility_accepts_equivalent_snapshots() -> None:
    """Equivalent snapshots satisfy the Step 8.8 semantic contract."""
    baseline = _snapshot()
    rebuilt = _snapshot()

    assert verify_semantic_reproducibility(baseline, rebuilt) is rebuilt


def test_verify_semantic_reproducibility_rejects_semantic_difference() -> None:
    """Any semantic release-identity drift must fail closed."""
    with pytest.raises(ReleaseReproducibilityError):
        verify_semantic_reproducibility(
            _snapshot(),
            _snapshot(version="1.0.1", wheel_version="1.0.1"),
        )


def test_verify_wheel_for_clean_install_accepts_exact_current_wheel(
    tmp_path: Path,
) -> None:
    """Clean-install verification must use the exact current release wheel."""
    artifacts = _artifact_set(tmp_path)
    wheel = next(artifact.path for artifact in artifacts.artifacts if artifact.kind == "wheel")

    verified = verify_wheel_for_clean_install(
        wheel,
        expected_project="openprojectlab",
        expected_version="1.0.0",
    )

    assert verified == wheel.resolve()


def test_verify_wheel_for_clean_install_rejects_missing_wheel(
    tmp_path: Path,
) -> None:
    """Missing release wheel must fail before clean-install execution."""
    missing = tmp_path / "openprojectlab-1.0.0-py3-none-any.whl"

    with pytest.raises(ReleaseReproducibilityError):
        verify_wheel_for_clean_install(
            missing,
            expected_project="openprojectlab",
            expected_version="1.0.0",
        )


def test_verify_wheel_for_clean_install_rejects_wrong_version(
    tmp_path: Path,
) -> None:
    """An older or newer wheel must not back the current release verification."""
    wheel = tmp_path / "openprojectlab-0.6.0-py3-none-any.whl"
    wheel.write_bytes(b"old-wheel")

    with pytest.raises(ReleaseReproducibilityError):
        verify_wheel_for_clean_install(
            wheel,
            expected_project="openprojectlab",
            expected_version="1.0.0",
        )


def test_verify_wheel_for_clean_install_rejects_non_wheel(
    tmp_path: Path,
) -> None:
    """Clean-install release verification requires a wheel artifact."""
    sdist = tmp_path / "openprojectlab-1.0.0.tar.gz"
    sdist.write_bytes(b"sdist")

    with pytest.raises(ReleaseReproducibilityError):
        verify_wheel_for_clean_install(
            sdist,
            expected_project="openprojectlab",
            expected_version="1.0.0",
        )


def test_semantic_reproducibility_does_not_claim_byte_reproducibility() -> None:
    """Checksum equality is evidence, not a required semantic invariant."""
    baseline = _snapshot()
    rebuilt = _snapshot(
        checksums=(
            ("openprojectlab-1.0.0-py3-none-any.whl", "c" * 64),
            ("openprojectlab-1.0.0.tar.gz", "d" * 64),
        )
    )

    assert verify_semantic_reproducibility(baseline, rebuilt) is rebuilt
