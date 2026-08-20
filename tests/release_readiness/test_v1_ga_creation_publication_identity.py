"""Contract tests for GA.7 — GA Creation / Publication Identity."""

from __future__ import annotations

from pathlib import Path

from generator.release.github_release import build_github_release_spec
from generator.release.identity import ReleaseIdentity, expected_release_tag

REPO_ROOT = Path(__file__).resolve().parents[2]
DESIGN = REPO_ROOT / "docs" / "releases" / "v1.0-ga-creation-publication-identity.md"

EXPECTED_VERSION = "1.0.0"
EXPECTED_TAG = "v1.0.0"
EXPECTED_RC_VERSION = "1.0.0rc1"
EXPECTED_RC_TAG = "v1.0.0-rc.1"

EXPECTED_WHEEL = "openprojectlab-1.0.0-py3-none-any.whl"
EXPECTED_SDIST = "openprojectlab-1.0.0.tar.gz"
EXPECTED_MANIFEST = "SHA256SUMS.txt"


def _read() -> str:
    assert DESIGN.is_file(), f"Required GA.7 governing design is missing: {DESIGN}"
    return DESIGN.read_text(encoding="utf-8")


def _normalized() -> str:
    return " ".join(_read().split())


def test_ga_7_governing_design_exists() -> None:
    assert DESIGN.is_file()


def test_ga_7_keeps_stable_and_rc_tag_mappings() -> None:
    assert expected_release_tag(EXPECTED_VERSION) == EXPECTED_TAG
    assert expected_release_tag(EXPECTED_RC_VERSION) == EXPECTED_RC_TAG


def test_ga_7_contract_fixes_exact_publication_filenames() -> None:
    normalized = _normalized()

    assert EXPECTED_WHEEL in normalized
    assert EXPECTED_SDIST in normalized
    assert EXPECTED_MANIFEST in normalized
    assert "No RC artifact may be present" in normalized


def test_ga_7_requires_annotated_stable_tag() -> None:
    normalized = _normalized().lower()

    assert "annotated git tag" in normalized
    assert "peeled v1.0.0 target == approved ga publication commit" in normalized
    assert "must never be retargeted" in normalized


def test_ga_7_requires_draft_first_stable_release() -> None:
    normalized = _normalized().lower()

    assert "created draft-first" in normalized
    assert "draft true" in normalized
    assert "prerelease false" in normalized
    assert (
        "only after draft identity verification passes may the release be published" in normalized
    )


def test_ga_7_requires_exact_asset_membership_and_checksum_identity() -> None:
    normalized = _normalized().lower()

    assert "exact published asset set" in normalized
    assert EXPECTED_WHEEL.lower() in normalized
    assert EXPECTED_SDIST.lower() in normalized
    assert EXPECTED_MANIFEST.lower() in normalized
    assert "match recomputed artifact bytes exactly" in normalized
    assert "no utf-8 bom" in normalized


def test_ga_7_requires_post_publication_identity_reread() -> None:
    normalized = _normalized().lower()

    assert "post-publication identity re-read" in normalized
    assert "local assumptions are insufficient after publication" in normalized
    assert "published artifact digests == verified digests" in normalized


def test_ga_7_preserves_rc_immutability() -> None:
    normalized = _normalized()

    assert EXPECTED_RC_VERSION in normalized
    assert EXPECTED_RC_TAG in normalized
    assert "GA creates a new stable identity" in normalized


def test_ga_7_does_not_formally_accept_ga() -> None:
    normalized = _normalized()

    assert "GA.7 does not own Formal GA Acceptance" in normalized
    assert "Formal v1.0.0 GA Acceptance --- Not Accepted" in normalized
    assert "GA.8 --- Planned" in normalized


def test_stable_github_release_spec_is_not_prerelease(tmp_path: Path) -> None:
    from generator.release.artifacts import ReleaseArtifact, ReleaseArtifactSet

    wheel = tmp_path / EXPECTED_WHEEL
    sdist = tmp_path / EXPECTED_SDIST
    wheel.write_bytes(b"wheel")
    sdist.write_bytes(b"sdist")

    artifact_set = ReleaseArtifactSet(
        artifacts=(
            ReleaseArtifact.from_path(wheel),
            ReleaseArtifact.from_path(sdist),
        )
    )
    identity = ReleaseIdentity(
        version=EXPECTED_VERSION,
        commit_sha="a" * 40,
        tag=EXPECTED_TAG,
    )
    checksums = {
        EXPECTED_WHEEL: "1" * 64,
        EXPECTED_SDIST: "2" * 64,
    }

    spec = build_github_release_spec(
        identity=identity,
        artifact_set=artifact_set,
        checksums=checksums,
    )

    assert spec.tag == EXPECTED_TAG
    assert spec.draft is True
    assert spec.prerelease is False
