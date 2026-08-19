"""Contract tests for Step 8.10.8 RC creation / publication identity."""

from __future__ import annotations

from pathlib import Path

import pytest

from generator.release.artifacts import ReleaseArtifact, ReleaseArtifactSet
from generator.release.github_release import (
    GitHubReleaseConflictError,
    build_github_release_spec,
    validate_existing_github_release,
)
from generator.release.identity import ReleaseIdentity, expected_release_tag

REPO_ROOT = Path(__file__).resolve().parents[2]
DESIGN = REPO_ROOT / "docs" / "releases" / "v1.0-rc-creation-publication-identity.md"

EXPECTED_VERSION = "1.0.0rc1"
EXPECTED_TAG = "v1.0.0-rc.1"
EXPECTED_ASSETS = (
    "SHA256SUMS.txt",
    "openprojectlab-1.0.0rc1-py3-none-any.whl",
    "openprojectlab-1.0.0rc1.tar.gz",
)


def _artifact_set(tmp_path: Path) -> ReleaseArtifactSet:
    wheel = tmp_path / "openprojectlab-1.0.0rc1-py3-none-any.whl"
    sdist = tmp_path / "openprojectlab-1.0.0rc1.tar.gz"
    wheel.write_bytes(b"wheel")
    sdist.write_bytes(b"sdist")

    return ReleaseArtifactSet(
        artifacts=(
            ReleaseArtifact.from_path(wheel),
            ReleaseArtifact.from_path(sdist),
        )
    )


def _identity() -> ReleaseIdentity:
    return ReleaseIdentity(
        version=EXPECTED_VERSION,
        commit_sha="a" * 40,
        tag=EXPECTED_TAG,
    )


def _checksums() -> dict[str, str]:
    return {
        "openprojectlab-1.0.0rc1-py3-none-any.whl": "1" * 64,
        "openprojectlab-1.0.0rc1.tar.gz": "2" * 64,
    }


def _spec(tmp_path: Path):
    return build_github_release_spec(
        identity=_identity(),
        artifact_set=_artifact_set(tmp_path),
        checksums=_checksums(),
    )


def test_rc_creation_publication_design_exists() -> None:
    assert DESIGN.is_file()


def test_rc_publication_contract_keeps_canonical_tag_mapping() -> None:
    assert expected_release_tag(EXPECTED_VERSION) == EXPECTED_TAG


def test_rc_github_release_is_draft_first_and_prerelease(
    tmp_path: Path,
) -> None:
    spec = _spec(tmp_path)

    assert spec.version == EXPECTED_VERSION
    assert spec.tag == EXPECTED_TAG
    assert spec.commit_sha == "a" * 40
    assert spec.draft is True
    assert spec.prerelease is True


def test_rc_github_release_has_exact_verified_asset_names(
    tmp_path: Path,
) -> None:
    spec = _spec(tmp_path)

    assert spec.asset_names == EXPECTED_ASSETS


def test_matching_rc_draft_state_can_be_validated(
    tmp_path: Path,
) -> None:
    spec = _spec(tmp_path)

    assert (
        validate_existing_github_release(
            spec,
            existing_tag=EXPECTED_TAG,
            existing_commit_sha="a" * 40,
            existing_asset_names=EXPECTED_ASSETS,
            existing_draft=True,
            existing_prerelease=True,
        )
        is spec
    )


@pytest.mark.parametrize(
    ("tag", "sha", "assets", "draft", "prerelease"),
    [
        (
            "v1.0.0-rc.2",
            "a" * 40,
            EXPECTED_ASSETS,
            True,
            True,
        ),
        (
            EXPECTED_TAG,
            "b" * 40,
            EXPECTED_ASSETS,
            True,
            True,
        ),
        (
            EXPECTED_TAG,
            "a" * 40,
            ("stale.whl",),
            True,
            True,
        ),
        (
            EXPECTED_TAG,
            "a" * 40,
            EXPECTED_ASSETS,
            True,
            False,
        ),
        (
            EXPECTED_TAG,
            "a" * 40,
            EXPECTED_ASSETS,
            False,
            True,
        ),
    ],
)
def test_conflicting_or_already_published_rc_state_fails_closed(
    tmp_path: Path,
    tag: str,
    sha: str,
    assets: tuple[str, ...],
    draft: bool,
    prerelease: bool,
) -> None:
    spec = _spec(tmp_path)

    with pytest.raises(GitHubReleaseConflictError):
        validate_existing_github_release(
            spec,
            existing_tag=tag,
            existing_commit_sha=sha,
            existing_asset_names=assets,
            existing_draft=draft,
            existing_prerelease=prerelease,
        )


def test_publication_contract_prohibits_retarget_and_replacement() -> None:
    normalized = " ".join(DESIGN.read_text(encoding="utf-8").lower().split())

    assert "do not force-move `v1.0.0-rc.1`" in normalized
    assert "do not replace wheel bytes" in normalized
    assert "do not replace sdist bytes" in normalized
    assert "v1.0.0-rc.2" in normalized


def test_publication_contract_requires_draft_validation_before_publish() -> None:
    normalized = " ".join(DESIGN.read_text(encoding="utf-8").lower().split())

    assert "create github release draft" in normalized
    assert "validate draft identity" in normalized
    assert "publish as prerelease" in normalized


def test_publication_contract_requires_postpublication_reread() -> None:
    normalized = " ".join(DESIGN.read_text(encoding="utf-8").lower().split())

    assert "re-read published github state" in normalized
    assert "post-publication identity verification" in normalized


def test_step_8_10_8_does_not_preaccept_rc_or_ga() -> None:
    normalized = " ".join(DESIGN.read_text(encoding="utf-8").lower().split())

    assert "formal acceptance remains step 8.10.9" in normalized
    assert "does not authorize `v1.0.0` ga" in normalized
