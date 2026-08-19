"""Contract tests for Step 8.10.4 RC build / artifact identity."""

from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path

import pytest

from generator.release.artifacts import (
    ReleaseArtifact,
    ReleaseArtifactError,
    ReleaseArtifactSet,
    ReleaseChecksumMismatchError,
    generate_sha256_manifest,
    verify_checksum_manifest,
    verify_release_artifact_set,
)
from generator.release.identity import (
    ReleaseIdentity,
    expected_release_tag,
    read_canonical_version,
    validate_release_identity,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"
DESIGN_PATH = REPO_ROOT / "docs" / "releases" / "v1.0-rc-build-artifact-identity.md"

EXPECTED_PROJECT = "openprojectlab"
EXPECTED_PACKAGE_VERSION = "1.0.0rc1"
EXPECTED_RC_TAG = "v1.0.0-rc.1"


def _git(*args: str) -> str:
    """Run one read-only Git command against the repository."""
    completed = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _write_fake_wheel(path: Path, *, version: str) -> None:
    """Write minimal wheel-shaped metadata for identity verification."""
    dist_info = f"openprojectlab-{version}.dist-info"
    metadata = f"Metadata-Version: 2.4\nName: {EXPECTED_PROJECT}\nVersion: {version}\n"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(f"{dist_info}/METADATA", metadata)


def test_rc_build_artifact_identity_design_exists() -> None:
    """Step 8.10.4 must have an explicit governing design/contract."""
    assert DESIGN_PATH.is_file()


def test_canonical_repository_version_is_first_rc_package_version() -> None:
    """The reviewable repository version must identify the first RC."""
    assert read_canonical_version(PYPROJECT_PATH) == EXPECTED_PACKAGE_VERSION


def test_first_rc_package_version_maps_to_human_facing_rc_tag() -> None:
    """PEP 440 RC syntax must map to the accepted human-facing tag."""
    assert expected_release_tag(EXPECTED_PACKAGE_VERSION) == EXPECTED_RC_TAG


@pytest.mark.parametrize(
    ("version", "expected_tag"),
    [
        ("1.0.0", "v1.0.0"),
        ("1.0.1", "v1.0.1"),
    ],
)
def test_stable_release_tag_mapping_remains_unchanged(
    version: str,
    expected_tag: str,
) -> None:
    """RC support must not alter stable-release tag identity."""
    assert expected_release_tag(version) == expected_tag


def test_release_identity_accepts_first_rc_mapping() -> None:
    """The RC package version, approved SHA, and RC tag form one identity."""
    identity = ReleaseIdentity(
        version=EXPECTED_PACKAGE_VERSION,
        commit_sha="a" * 40,
        tag=EXPECTED_RC_TAG,
    )

    assert identity.version == EXPECTED_PACKAGE_VERSION
    assert identity.tag == EXPECTED_RC_TAG


def test_rc_identity_validation_is_pre_tag_and_side_effect_free() -> None:
    """Step 8.10.4 verifies identity without creating or moving a tag."""
    before = _git("status", "--porcelain")
    identity = ReleaseIdentity(
        version=EXPECTED_PACKAGE_VERSION,
        commit_sha="a" * 40,
        tag=EXPECTED_RC_TAG,
    )

    assert validate_release_identity(identity, tag_target_sha=None) is identity

    after = _git("status", "--porcelain")
    assert after == before


def test_rc_artifact_set_accepts_pep440_version_filenames(tmp_path: Path) -> None:
    """RC wheel/sdist filenames use the canonical package version."""
    wheel = tmp_path / "openprojectlab-1.0.0rc1-py3-none-any.whl"
    sdist = tmp_path / "openprojectlab-1.0.0rc1.tar.gz"
    wheel.write_bytes(b"wheel")
    sdist.write_bytes(b"sdist")

    artifact_set = ReleaseArtifactSet(
        artifacts=(
            ReleaseArtifact.from_path(wheel),
            ReleaseArtifact.from_path(sdist),
        )
    )

    assert (
        verify_release_artifact_set(
            artifact_set,
            expected_project=EXPECTED_PROJECT,
            expected_version=EXPECTED_PACKAGE_VERSION,
        )
        is artifact_set
    )


def test_rc_wheel_metadata_matches_pep440_package_identity(tmp_path: Path) -> None:
    """Wheel METADATA must identify the canonical RC package version."""
    wheel = tmp_path / "openprojectlab-1.0.0rc1-py3-none-any.whl"
    sdist = tmp_path / "openprojectlab-1.0.0rc1.tar.gz"

    _write_fake_wheel(wheel, version=EXPECTED_PACKAGE_VERSION)
    sdist.write_bytes(b"sdist")

    artifact_set = ReleaseArtifactSet(
        artifacts=(
            ReleaseArtifact.from_path(wheel),
            ReleaseArtifact.from_path(sdist),
        )
    )

    verify_release_artifact_set(
        artifact_set,
        expected_project=EXPECTED_PROJECT,
        expected_version=EXPECTED_PACKAGE_VERSION,
        inspect_wheel_metadata=True,
    )


def test_stale_pre_rc_artifacts_are_rejected(tmp_path: Path) -> None:
    """The RC gate must not silently accept the historical 0.6.0 build."""
    wheel = tmp_path / "openprojectlab-0.6.0-py3-none-any.whl"
    sdist = tmp_path / "openprojectlab-0.6.0.tar.gz"
    wheel.write_bytes(b"stale-wheel")
    sdist.write_bytes(b"stale-sdist")

    artifact_set = ReleaseArtifactSet(
        artifacts=(
            ReleaseArtifact.from_path(wheel),
            ReleaseArtifact.from_path(sdist),
        )
    )

    with pytest.raises(ReleaseArtifactError):
        verify_release_artifact_set(
            artifact_set,
            expected_project=EXPECTED_PROJECT,
            expected_version=EXPECTED_PACKAGE_VERSION,
        )


def test_rc_checksum_manifest_binds_exact_artifact_bytes(tmp_path: Path) -> None:
    """Checksums must cover the exact verified RC artifact set."""
    wheel = tmp_path / "openprojectlab-1.0.0rc1-py3-none-any.whl"
    sdist = tmp_path / "openprojectlab-1.0.0rc1.tar.gz"
    wheel.write_bytes(b"rc-wheel")
    sdist.write_bytes(b"rc-sdist")

    artifacts = (
        ReleaseArtifact.from_path(wheel),
        ReleaseArtifact.from_path(sdist),
    )

    manifest = generate_sha256_manifest(artifacts)

    assert list(manifest) == sorted(manifest)
    assert set(manifest) == {wheel.name, sdist.name}
    verify_checksum_manifest(artifacts, manifest)


def test_rc_checksum_verification_detects_post_manifest_mutation(
    tmp_path: Path,
) -> None:
    """Artifact bytes cannot change after checksum identity is recorded."""
    wheel = tmp_path / "openprojectlab-1.0.0rc1-py3-none-any.whl"
    wheel.write_bytes(b"verified-rc-wheel")
    artifacts = (ReleaseArtifact.from_path(wheel),)

    manifest = generate_sha256_manifest(artifacts)
    wheel.write_bytes(b"mutated-rc-wheel")

    with pytest.raises(ReleaseChecksumMismatchError):
        verify_checksum_manifest(artifacts, manifest)
