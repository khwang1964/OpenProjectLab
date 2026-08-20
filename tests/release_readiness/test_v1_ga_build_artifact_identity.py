"""Contract tests for GA.3 — GA Version / Artifact Identity."""

from __future__ import annotations

import hashlib
import re
import tomllib
from pathlib import Path

from generator.release.github_release import build_github_release_spec
from generator.release.identity import ReleaseIdentity, expected_release_tag

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
DESIGN = REPO_ROOT / "docs" / "releases" / "v1.0-ga-build-artifact-identity.md"
GA_REVIEW = REPO_ROOT / "docs" / "releases" / "v1.0-ga-rc-evidence-review.md"

EXPECTED_VERSION = "1.0.0"
EXPECTED_GA_TAG = "v1.0.0"
EXPECTED_RC_VERSION = "1.0.0rc1"
EXPECTED_RC_TAG = "v1.0.0-rc.1"

EXPECTED_WHEEL = "openprojectlab-1.0.0-py3-none-any.whl"
EXPECTED_SDIST = "openprojectlab-1.0.0.tar.gz"
RC_WHEEL = "openprojectlab-1.0.0rc1-py3-none-any.whl"
RC_SDIST = "openprojectlab-1.0.0rc1.tar.gz"

FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _read(path: Path) -> str:
    assert path.is_file(), f"Required GA.3 file is missing: {path}"
    return path.read_text(encoding="utf-8")


def _normalized(path: Path) -> str:
    return " ".join(_read(path).split())


def _project_version() -> str:
    parsed = tomllib.loads(_read(PYPROJECT))
    project = parsed["project"]
    assert isinstance(project, dict)
    version = project["version"]
    assert isinstance(version, str)
    return version


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _parse_manifest(path: Path) -> dict[str, str]:
    raw = path.read_text(encoding="utf-8")
    assert not raw.startswith("\ufeff"), "SHA256 manifest must not contain a BOM"

    result: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip():
            continue
        digest, filename = line.split(maxsplit=1)
        result[filename.strip()] = digest.lower()
    return result


def test_ga_3_design_exists() -> None:
    assert DESIGN.is_file()
    assert GA_REVIEW.is_file()


def test_ga_3_requires_stable_project_version() -> None:
    assert _project_version() == EXPECTED_VERSION


def test_ga_3_current_stable_version_is_distinct_from_historical_rc_version() -> None:
    """GA.3 current repository identity must not rewrite the accepted RC identity."""
    assert EXPECTED_VERSION != EXPECTED_RC_VERSION
    assert expected_release_tag(EXPECTED_RC_VERSION) == EXPECTED_RC_TAG


def test_ga_and_rc_tag_mappings_are_both_supported() -> None:
    assert expected_release_tag(EXPECTED_VERSION) == EXPECTED_GA_TAG
    assert expected_release_tag(EXPECTED_RC_VERSION) == EXPECTED_RC_TAG


def test_ga_release_identity_is_stable_not_prerelease(tmp_path: Path) -> None:
    wheel = tmp_path / EXPECTED_WHEEL
    sdist = tmp_path / EXPECTED_SDIST
    wheel.write_bytes(b"wheel")
    sdist.write_bytes(b"sdist")

    from generator.release.artifacts import ReleaseArtifact, ReleaseArtifactSet

    artifact_set = ReleaseArtifactSet(
        artifacts=(
            ReleaseArtifact.from_path(wheel),
            ReleaseArtifact.from_path(sdist),
        )
    )

    identity = ReleaseIdentity(
        version=EXPECTED_VERSION,
        commit_sha="a" * 40,
        tag=EXPECTED_GA_TAG,
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

    assert spec.tag == EXPECTED_GA_TAG
    assert spec.prerelease is False
    assert spec.draft is True


def test_ga_3_contract_fixes_exact_distribution_filenames() -> None:
    normalized = _normalized(DESIGN)

    assert EXPECTED_WHEEL in normalized
    assert EXPECTED_SDIST in normalized
    assert RC_WHEEL in normalized
    assert RC_SDIST in normalized
    assert "No RC artifact may satisfy GA.3" in normalized


def test_ga_3_requires_exact_artifact_set() -> None:
    normalized = _normalized(DESIGN)

    assert "exactly one wheel and exactly one sdist" in normalized
    assert "No duplicate, stale, or unrelated distribution may be accepted" in normalized


def test_ga_3_requires_exact_checksum_coverage_without_bom() -> None:
    normalized = _normalized(DESIGN)

    assert "contain one entry for the wheel" in normalized
    assert "contain one entry for the sdist" in normalized
    assert "match recomputed SHA-256 digests exactly" in normalized
    assert "written without a UTF-8 BOM" in normalized


def test_manifest_parser_rejects_bom_and_verifies_exact_bytes(tmp_path: Path) -> None:
    wheel = tmp_path / EXPECTED_WHEEL
    sdist = tmp_path / EXPECTED_SDIST
    manifest = tmp_path / "SHA256SUMS.txt"

    wheel.write_bytes(b"wheel-bytes")
    sdist.write_bytes(b"sdist-bytes")

    manifest.write_text(
        f"{_sha256(wheel)}  {wheel.name}\n{_sha256(sdist)}  {sdist.name}\n",
        encoding="utf-8",
        newline="\n",
    )

    parsed = _parse_manifest(manifest)

    assert parsed == {
        wheel.name: _sha256(wheel),
        sdist.name: _sha256(sdist),
    }


def test_ga_3_requires_release_source_commit_binding() -> None:
    normalized = _normalized(DESIGN)

    assert "approved GA source commit must" in normalized
    assert "full Git SHA" in normalized
    assert "be the source of the GA wheel and sdist" in normalized
    assert "later become the exact target of `v1.0.0`" in normalized


def test_ga_3_does_not_create_ga_tag_or_formally_accept_ga() -> None:
    normalized = _normalized(DESIGN)

    assert "v1.0.0 tag --- Not Created / Not Authorized in GA.3" in normalized
    assert "GA GitHub Release --- Not Created" in normalized
    assert "Formal v1.0.0 GA Acceptance --- Not Accepted" in normalized


def test_ga_3_preserves_rc_publication_identity() -> None:
    normalized = _normalized(DESIGN)

    assert "1.0.0rc1" in normalized
    assert "v1.0.0-rc.1" in normalized
    assert "b5958edbbf0e3279ed74fa0e3aee13e893c5dfc8" in normalized


def test_ga_3_rejects_rc_artifact_identity_semantically() -> None:
    normalized = _normalized(DESIGN)

    assert "No RC artifact may satisfy GA.3" in normalized
    assert "RC artifact reuse" in normalized
