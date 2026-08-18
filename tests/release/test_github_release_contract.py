"""Contract tests for GitHub Release consistency."""

from __future__ import annotations

from pathlib import Path

import pytest

from generator.release.artifacts import ReleaseArtifact, ReleaseArtifactSet
from generator.release.github_release import (
    GitHubReleaseConflictError,
    GitHubReleaseError,
    GitHubReleaseSpec,
    build_github_release_spec,
    validate_existing_github_release,
)
from generator.release.identity import ReleaseIdentity


def _artifact_set(tmp_path: Path) -> ReleaseArtifactSet:
    """Create one deterministic wheel/sdist release set."""
    wheel = tmp_path / "openprojectlab-1.0.0-py3-none-any.whl"
    sdist = tmp_path / "openprojectlab-1.0.0.tar.gz"
    wheel.write_bytes(b"wheel")
    sdist.write_bytes(b"sdist")

    return ReleaseArtifactSet(
        artifacts=(
            ReleaseArtifact.from_path(wheel),
            ReleaseArtifact.from_path(sdist),
        )
    )


def _identity() -> ReleaseIdentity:
    """Return a coherent v1 release identity."""
    return ReleaseIdentity(
        version="1.0.0",
        commit_sha="a" * 40,
        tag="v1.0.0",
    )


def _checksums() -> dict[str, str]:
    """Return deterministic placeholder checksums keyed by asset name."""
    return {
        "openprojectlab-1.0.0-py3-none-any.whl": "1" * 64,
        "openprojectlab-1.0.0.tar.gz": "2" * 64,
    }


def test_github_release_spec_is_immutable(tmp_path: Path) -> None:
    """Release publication specification must not mutate after validation."""
    spec = build_github_release_spec(
        identity=_identity(),
        artifact_set=_artifact_set(tmp_path),
        checksums=_checksums(),
    )

    with pytest.raises((AttributeError, TypeError)):
        spec.tag = "v1.0.1"


def test_build_github_release_spec_derives_title_from_version(
    tmp_path: Path,
) -> None:
    """GitHub Release title must describe the same canonical version."""
    spec = build_github_release_spec(
        identity=_identity(),
        artifact_set=_artifact_set(tmp_path),
        checksums=_checksums(),
    )

    assert spec.tag == "v1.0.0"
    assert spec.title == "OpenProjectLab v1.0.0"
    assert spec.version == "1.0.0"
    assert spec.commit_sha == "a" * 40


def test_build_github_release_spec_is_draft_first(tmp_path: Path) -> None:
    """Step 8.8 publication must remain draft-first."""
    spec = build_github_release_spec(
        identity=_identity(),
        artifact_set=_artifact_set(tmp_path),
        checksums=_checksums(),
    )

    assert spec.draft is True


def test_build_github_release_spec_marks_rc_as_prerelease(
    tmp_path: Path,
) -> None:
    """Release candidates must be published as GitHub prereleases."""
    identity = ReleaseIdentity(
        version="1.0.0rc1",
        commit_sha="a" * 40,
        tag="v1.0.0rc1",
    )
    artifacts = _artifact_set(tmp_path)

    renamed = []
    for artifact in artifacts.artifacts:
        if artifact.kind == "wheel":
            path = tmp_path / "openprojectlab-1.0.0rc1-py3-none-any.whl"
        else:
            path = tmp_path / "openprojectlab-1.0.0rc1.tar.gz"
        artifact.path.rename(path)
        renamed.append(ReleaseArtifact.from_path(path))

    spec = build_github_release_spec(
        identity=identity,
        artifact_set=ReleaseArtifactSet(artifacts=tuple(renamed)),
        checksums={
            "openprojectlab-1.0.0rc1-py3-none-any.whl": "1" * 64,
            "openprojectlab-1.0.0rc1.tar.gz": "2" * 64,
        },
    )

    assert spec.prerelease is True


def test_build_github_release_spec_marks_ga_as_not_prerelease(
    tmp_path: Path,
) -> None:
    """General-availability releases must not be marked prerelease."""
    spec = build_github_release_spec(
        identity=_identity(),
        artifact_set=_artifact_set(tmp_path),
        checksums=_checksums(),
    )

    assert spec.prerelease is False


def test_build_github_release_spec_requires_exact_checksum_coverage(
    tmp_path: Path,
) -> None:
    """Every artifact must have exactly one checksum entry."""
    with pytest.raises(GitHubReleaseError):
        build_github_release_spec(
            identity=_identity(),
            artifact_set=_artifact_set(tmp_path),
            checksums={
                "openprojectlab-1.0.0-py3-none-any.whl": "1" * 64,
            },
        )


def test_build_github_release_spec_rejects_extra_checksum_asset(
    tmp_path: Path,
) -> None:
    """Checksum manifest must not describe assets outside the release set."""
    checksums = _checksums()
    checksums["stale.whl"] = "3" * 64

    with pytest.raises(GitHubReleaseError):
        build_github_release_spec(
            identity=_identity(),
            artifact_set=_artifact_set(tmp_path),
            checksums=checksums,
        )


@pytest.mark.parametrize(
    "checksum",
    [
        "",
        "abc",
        "g" * 64,
        "1" * 63,
        "1" * 65,
    ],
)
def test_build_github_release_spec_rejects_invalid_sha256(
    tmp_path: Path,
    checksum: str,
) -> None:
    """Published checksum values must be canonical SHA-256 hex digests."""
    checksums = _checksums()
    checksums["openprojectlab-1.0.0-py3-none-any.whl"] = checksum

    with pytest.raises(GitHubReleaseError):
        build_github_release_spec(
            identity=_identity(),
            artifact_set=_artifact_set(tmp_path),
            checksums=checksums,
        )


def test_build_github_release_spec_asset_names_are_deterministic(
    tmp_path: Path,
) -> None:
    """GitHub Release assets must have deterministic sorted ordering."""
    spec = build_github_release_spec(
        identity=_identity(),
        artifact_set=_artifact_set(tmp_path),
        checksums=_checksums(),
    )

    assert spec.asset_names == tuple(sorted(spec.asset_names))


def test_build_github_release_spec_includes_checksum_manifest_asset(
    tmp_path: Path,
) -> None:
    """The checksum manifest itself must be part of release assets."""
    spec = build_github_release_spec(
        identity=_identity(),
        artifact_set=_artifact_set(tmp_path),
        checksums=_checksums(),
    )

    assert "SHA256SUMS.txt" in spec.asset_names


def test_validate_existing_github_release_accepts_matching_state(
    tmp_path: Path,
) -> None:
    """Existing draft state matching the expected identity may be reused."""
    spec = build_github_release_spec(
        identity=_identity(),
        artifact_set=_artifact_set(tmp_path),
        checksums=_checksums(),
    )

    validated = validate_existing_github_release(
        spec,
        existing_tag="v1.0.0",
        existing_commit_sha="a" * 40,
        existing_asset_names=spec.asset_names,
        existing_draft=True,
        existing_prerelease=False,
    )

    assert validated is spec


def test_validate_existing_github_release_rejects_tag_conflict(
    tmp_path: Path,
) -> None:
    """An existing release for another tag must fail closed."""
    spec = build_github_release_spec(
        identity=_identity(),
        artifact_set=_artifact_set(tmp_path),
        checksums=_checksums(),
    )

    with pytest.raises(GitHubReleaseConflictError):
        validate_existing_github_release(
            spec,
            existing_tag="v1.0.1",
            existing_commit_sha="a" * 40,
            existing_asset_names=spec.asset_names,
            existing_draft=True,
            existing_prerelease=False,
        )


def test_validate_existing_github_release_rejects_commit_conflict(
    tmp_path: Path,
) -> None:
    """GitHub Release state must bind to the approved release commit."""
    spec = build_github_release_spec(
        identity=_identity(),
        artifact_set=_artifact_set(tmp_path),
        checksums=_checksums(),
    )

    with pytest.raises(GitHubReleaseConflictError):
        validate_existing_github_release(
            spec,
            existing_tag=spec.tag,
            existing_commit_sha="b" * 40,
            existing_asset_names=spec.asset_names,
            existing_draft=True,
            existing_prerelease=False,
        )


def test_validate_existing_github_release_rejects_asset_conflict(
    tmp_path: Path,
) -> None:
    """Existing release assets must exactly match the verified asset set."""
    spec = build_github_release_spec(
        identity=_identity(),
        artifact_set=_artifact_set(tmp_path),
        checksums=_checksums(),
    )

    with pytest.raises(GitHubReleaseConflictError):
        validate_existing_github_release(
            spec,
            existing_tag=spec.tag,
            existing_commit_sha=spec.commit_sha,
            existing_asset_names=("stale.whl",),
            existing_draft=True,
            existing_prerelease=False,
        )


def test_validate_existing_github_release_rejects_published_state(
    tmp_path: Path,
) -> None:
    """Step 8.8.5 must not silently mutate an already-published release."""
    spec = build_github_release_spec(
        identity=_identity(),
        artifact_set=_artifact_set(tmp_path),
        checksums=_checksums(),
    )

    with pytest.raises(GitHubReleaseConflictError):
        validate_existing_github_release(
            spec,
            existing_tag=spec.tag,
            existing_commit_sha=spec.commit_sha,
            existing_asset_names=spec.asset_names,
            existing_draft=False,
            existing_prerelease=False,
        )


def test_validate_existing_github_release_rejects_prerelease_mismatch(
    tmp_path: Path,
) -> None:
    """Existing prerelease classification must agree with expected identity."""
    spec = build_github_release_spec(
        identity=_identity(),
        artifact_set=_artifact_set(tmp_path),
        checksums=_checksums(),
    )

    with pytest.raises(GitHubReleaseConflictError):
        validate_existing_github_release(
            spec,
            existing_tag=spec.tag,
            existing_commit_sha=spec.commit_sha,
            existing_asset_names=spec.asset_names,
            existing_draft=True,
            existing_prerelease=True,
        )


def test_github_release_consistency_layer_requires_no_network(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ordinary GitHub Release contract tests must remain offline."""

    def _unexpected_network(*args: object, **kwargs: object) -> None:
        raise AssertionError("GitHub Release consistency must not use network")

    monkeypatch.setattr("urllib.request.urlopen", _unexpected_network)

    spec = build_github_release_spec(
        identity=_identity(),
        artifact_set=_artifact_set(tmp_path),
        checksums=_checksums(),
    )

    assert isinstance(spec, GitHubReleaseSpec)
