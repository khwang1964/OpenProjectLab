"""Contract tests for release artifact metadata and checksums."""

from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

import pytest

from generator.release.artifacts import (
    ReleaseArtifact,
    ReleaseArtifactError,
    ReleaseArtifactSet,
    ReleaseChecksumMismatchError,
    enumerate_release_artifacts,
    generate_sha256_manifest,
    select_current_wheel,
    verify_checksum_manifest,
    verify_release_artifact_set,
)


def _write_fake_wheel(
    path: Path,
    *,
    project_name: str = "openprojectlab",
    version: str = "1.0.0",
) -> None:
    """Write a minimal wheel-shaped zip containing METADATA."""
    dist_info = f"{project_name.replace('-', '_')}-{version}.dist-info"
    metadata = f"Metadata-Version: 2.4\nName: {project_name}\nVersion: {version}\n"

    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(f"{dist_info}/METADATA", metadata)


def _write_fake_sdist(
    path: Path,
    *,
    project_name: str = "openprojectlab",
    version: str = "1.0.0",
) -> None:
    """Write a minimal source-distribution-shaped file."""
    path.write_bytes(f"{project_name}-{version}\n".encode())


def test_enumerate_release_artifacts_requires_explicit_dist_directory(
    tmp_path: Path,
) -> None:
    """Missing artifact directory must fail closed."""
    missing = tmp_path / "dist"

    with pytest.raises(ReleaseArtifactError):
        enumerate_release_artifacts(missing)


def test_enumerate_release_artifacts_returns_only_wheel_and_sdist(
    tmp_path: Path,
) -> None:
    """Only canonical release artifact types belong to the release set."""
    dist = tmp_path / "dist"
    dist.mkdir()

    wheel = dist / "openprojectlab-1.0.0-py3-none-any.whl"
    sdist = dist / "openprojectlab-1.0.0.tar.gz"
    wheel.write_bytes(b"wheel")
    sdist.write_bytes(b"sdist")
    (dist / "notes.txt").write_text("not a release artifact", encoding="utf-8")

    artifacts = enumerate_release_artifacts(dist)

    assert [artifact.path.name for artifact in artifacts] == [
        wheel.name,
        sdist.name,
    ]


def test_release_artifact_records_kind_from_filename(tmp_path: Path) -> None:
    """Artifact kind must be explicit and deterministic."""
    wheel = tmp_path / "openprojectlab-1.0.0-py3-none-any.whl"
    sdist = tmp_path / "openprojectlab-1.0.0.tar.gz"
    wheel.write_bytes(b"wheel")
    sdist.write_bytes(b"sdist")

    assert ReleaseArtifact.from_path(wheel).kind == "wheel"
    assert ReleaseArtifact.from_path(sdist).kind == "sdist"


def test_release_artifact_rejects_unknown_extension(tmp_path: Path) -> None:
    """Unrecognized files must not silently enter the release set."""
    unknown = tmp_path / "openprojectlab-1.0.0.zip"
    unknown.write_bytes(b"unknown")

    with pytest.raises(ReleaseArtifactError):
        ReleaseArtifact.from_path(unknown)


def test_verify_release_artifact_set_requires_one_wheel_and_one_sdist(
    tmp_path: Path,
) -> None:
    """The v1 release set must contain exactly one wheel and one sdist."""
    wheel = tmp_path / "openprojectlab-1.0.0-py3-none-any.whl"
    wheel.write_bytes(b"wheel")

    with pytest.raises(ReleaseArtifactError):
        verify_release_artifact_set(
            ReleaseArtifactSet(
                artifacts=(ReleaseArtifact.from_path(wheel),),
            ),
            expected_project="openprojectlab",
            expected_version="1.0.0",
        )


def test_verify_release_artifact_set_rejects_duplicate_wheels(
    tmp_path: Path,
) -> None:
    """Stale or duplicate wheels must fail closed."""
    wheel1 = tmp_path / "openprojectlab-1.0.0-py3-none-any.whl"
    wheel2 = tmp_path / "openprojectlab-1.0.0-1-py3-none-any.whl"
    sdist = tmp_path / "openprojectlab-1.0.0.tar.gz"

    for path in (wheel1, wheel2, sdist):
        path.write_bytes(path.name.encode())

    artifact_set = ReleaseArtifactSet(
        artifacts=tuple(ReleaseArtifact.from_path(path) for path in (wheel1, wheel2, sdist))
    )

    with pytest.raises(ReleaseArtifactError):
        verify_release_artifact_set(
            artifact_set,
            expected_project="openprojectlab",
            expected_version="1.0.0",
        )


def test_verify_release_artifact_set_rejects_version_mismatch(
    tmp_path: Path,
) -> None:
    """Artifact filenames must match the expected release version."""
    wheel = tmp_path / "openprojectlab-1.0.1-py3-none-any.whl"
    sdist = tmp_path / "openprojectlab-1.0.0.tar.gz"
    wheel.write_bytes(b"wheel")
    sdist.write_bytes(b"sdist")

    artifact_set = ReleaseArtifactSet(
        artifacts=(
            ReleaseArtifact.from_path(wheel),
            ReleaseArtifact.from_path(sdist),
        )
    )

    with pytest.raises(ReleaseArtifactError):
        verify_release_artifact_set(
            artifact_set,
            expected_project="openprojectlab",
            expected_version="1.0.0",
        )


def test_verify_release_artifact_set_accepts_expected_files(
    tmp_path: Path,
) -> None:
    """One matching wheel and one matching sdist form a valid set."""
    wheel = tmp_path / "openprojectlab-1.0.0-py3-none-any.whl"
    sdist = tmp_path / "openprojectlab-1.0.0.tar.gz"
    wheel.write_bytes(b"wheel")
    sdist.write_bytes(b"sdist")

    artifact_set = ReleaseArtifactSet(
        artifacts=(
            ReleaseArtifact.from_path(wheel),
            ReleaseArtifact.from_path(sdist),
        )
    )

    verified = verify_release_artifact_set(
        artifact_set,
        expected_project="openprojectlab",
        expected_version="1.0.0",
    )

    assert verified is artifact_set


def test_wheel_metadata_matches_expected_identity(tmp_path: Path) -> None:
    """Wheel METADATA must agree with the release identity."""
    wheel = tmp_path / "openprojectlab-1.0.0-py3-none-any.whl"
    sdist = tmp_path / "openprojectlab-1.0.0.tar.gz"

    _write_fake_wheel(wheel)
    _write_fake_sdist(sdist)

    artifact_set = ReleaseArtifactSet(
        artifacts=(
            ReleaseArtifact.from_path(wheel),
            ReleaseArtifact.from_path(sdist),
        )
    )

    verify_release_artifact_set(
        artifact_set,
        expected_project="openprojectlab",
        expected_version="1.0.0",
        inspect_wheel_metadata=True,
    )


def test_wheel_metadata_mismatch_is_rejected(tmp_path: Path) -> None:
    """Filename agreement alone is insufficient when metadata disagrees."""
    wheel = tmp_path / "openprojectlab-1.0.0-py3-none-any.whl"
    sdist = tmp_path / "openprojectlab-1.0.0.tar.gz"

    _write_fake_wheel(wheel, version="1.0.1")
    _write_fake_sdist(sdist)

    artifact_set = ReleaseArtifactSet(
        artifacts=(
            ReleaseArtifact.from_path(wheel),
            ReleaseArtifact.from_path(sdist),
        )
    )

    with pytest.raises(ReleaseArtifactError):
        verify_release_artifact_set(
            artifact_set,
            expected_project="openprojectlab",
            expected_version="1.0.0",
            inspect_wheel_metadata=True,
        )


def test_select_current_wheel_requires_single_matching_wheel(
    tmp_path: Path,
) -> None:
    """Current release wheel selection must reject ambiguous dist state."""
    dist = tmp_path / "dist"
    dist.mkdir()

    for name in (
        "openprojectlab-1.0.0-py3-none-any.whl",
        "openprojectlab-1.0.1-py3-none-any.whl",
    ):
        (dist / name).write_bytes(name.encode())

    selected = select_current_wheel(
        dist,
        expected_project="openprojectlab",
        expected_version="1.0.0",
    )

    assert selected.name == "openprojectlab-1.0.0-py3-none-any.whl"


def test_select_current_wheel_fails_when_expected_wheel_is_missing(
    tmp_path: Path,
) -> None:
    """Release verification must never fall back to an older wheel."""
    dist = tmp_path / "dist"
    dist.mkdir()
    (dist / "openprojectlab-0.6.0-py3-none-any.whl").write_bytes(b"old")

    with pytest.raises(ReleaseArtifactError):
        select_current_wheel(
            dist,
            expected_project="openprojectlab",
            expected_version="1.0.0",
        )


def test_generate_sha256_manifest_covers_every_artifact(
    tmp_path: Path,
) -> None:
    """Checksum manifest must contain every exact release artifact."""
    wheel = tmp_path / "openprojectlab-1.0.0-py3-none-any.whl"
    sdist = tmp_path / "openprojectlab-1.0.0.tar.gz"
    wheel.write_bytes(b"wheel-bytes")
    sdist.write_bytes(b"sdist-bytes")

    artifacts = (
        ReleaseArtifact.from_path(wheel),
        ReleaseArtifact.from_path(sdist),
    )

    manifest = generate_sha256_manifest(artifacts)

    assert set(manifest) == {wheel.name, sdist.name}
    assert manifest[wheel.name] == hashlib.sha256(b"wheel-bytes").hexdigest()
    assert manifest[sdist.name] == hashlib.sha256(b"sdist-bytes").hexdigest()


def test_generate_sha256_manifest_is_deterministic(tmp_path: Path) -> None:
    """Manifest output must not depend on input tuple ordering."""
    first = tmp_path / "openprojectlab-1.0.0.tar.gz"
    second = tmp_path / "openprojectlab-1.0.0-py3-none-any.whl"
    first.write_bytes(b"a")
    second.write_bytes(b"b")

    a = generate_sha256_manifest(
        (
            ReleaseArtifact.from_path(first),
            ReleaseArtifact.from_path(second),
        )
    )
    b = generate_sha256_manifest(
        (
            ReleaseArtifact.from_path(second),
            ReleaseArtifact.from_path(first),
        )
    )

    assert a == b
    assert list(a) == sorted(a)


def test_verify_checksum_manifest_accepts_unchanged_artifacts(
    tmp_path: Path,
) -> None:
    """Verified bytes must match their recorded checksums."""
    wheel = tmp_path / "openprojectlab-1.0.0-py3-none-any.whl"
    wheel.write_bytes(b"release-bytes")
    artifacts = (ReleaseArtifact.from_path(wheel),)

    manifest = generate_sha256_manifest(artifacts)

    verify_checksum_manifest(artifacts, manifest)


def test_verify_checksum_manifest_detects_mutation(tmp_path: Path) -> None:
    """Artifact mutation after checksum generation must fail."""
    wheel = tmp_path / "openprojectlab-1.0.0-py3-none-any.whl"
    wheel.write_bytes(b"release-bytes")
    artifacts = (ReleaseArtifact.from_path(wheel),)

    manifest = generate_sha256_manifest(artifacts)
    wheel.write_bytes(b"tampered-bytes")

    with pytest.raises(ReleaseChecksumMismatchError):
        verify_checksum_manifest(artifacts, manifest)


def test_verify_checksum_manifest_rejects_missing_entry(
    tmp_path: Path,
) -> None:
    """Every release artifact must have a checksum entry."""
    wheel = tmp_path / "openprojectlab-1.0.0-py3-none-any.whl"
    wheel.write_bytes(b"release-bytes")
    artifacts = (ReleaseArtifact.from_path(wheel),)

    with pytest.raises(ReleaseArtifactError):
        verify_checksum_manifest(artifacts, {})


def test_release_artifact_model_is_immutable(tmp_path: Path) -> None:
    """Artifact identity must not mutate after release verification."""
    wheel = tmp_path / "openprojectlab-1.0.0-py3-none-any.whl"
    wheel.write_bytes(b"release")

    artifact = ReleaseArtifact.from_path(wheel)

    with pytest.raises((AttributeError, TypeError)):
        artifact.kind = "sdist"
