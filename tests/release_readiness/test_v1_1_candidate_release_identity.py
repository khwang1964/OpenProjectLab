"""v1.1 candidate build-boundary identity contract."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

import pytest

from generator.release.identity import expected_release_tag

ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = ROOT / "pyproject.toml"
DIST = ROOT / "dist-v1.1.8"
EVIDENCE = DIST / "candidate-build-evidence.json"
DESIGN = ROOT / "docs" / "releases" / "v1.1-reliability-artifact-backed-verification.md"

REPOSITORY_VERSION = "1.0.0"
CANDIDATE_VERSION = "1.1.0rc1"
CANDIDATE_TAG = "v1.1.0-rc.1"


def _project_version() -> str:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]
    return str(project["version"])


def _evidence() -> dict[str, object]:
    if not EVIDENCE.is_file():
        pytest.skip(
            "candidate build evidence is not present; run scripts/build_v1_1_candidate.py first"
        )
    data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_repository_canonical_version_remains_v1_0_ga_identity() -> None:
    assert _project_version() == REPOSITORY_VERSION


def test_v1_1_candidate_tag_is_derived_from_candidate_version() -> None:
    assert expected_release_tag(CANDIDATE_VERSION) == CANDIDATE_TAG


def test_candidate_build_evidence_separates_repository_and_candidate_identity() -> None:
    evidence = _evidence()

    assert evidence["repository_version"] == REPOSITORY_VERSION
    assert evidence["candidate_version"] == CANDIDATE_VERSION
    assert evidence["candidate_tag"] == CANDIDATE_TAG

    transform = evidence["build_transform"]
    assert isinstance(transform, dict)
    assert transform["from"] == REPOSITORY_VERSION
    assert transform["to"] == CANDIDATE_VERSION
    assert transform["repository_mutated"] is False


def test_candidate_build_evidence_names_only_v1_1_rc_artifacts() -> None:
    evidence = _evidence()
    artifacts = evidence["artifacts"]
    assert isinstance(artifacts, list)
    assert len(artifacts) == 2

    names = {str(item["filename"]) for item in artifacts}
    assert any(name.endswith(".whl") for name in names)
    assert any(name.endswith(".tar.gz") for name in names)
    assert all(name.startswith("openprojectlab-1.1.0rc1") for name in names)
    assert all("1.0.0" not in name for name in names)


def test_candidate_build_evidence_records_full_source_commit_sha() -> None:
    evidence = _evidence()
    sha = str(evidence["source_commit_sha"])

    assert len(sha) == 40
    assert all(character in "0123456789abcdef" for character in sha)


def test_v1_1_8_design_keeps_formal_v1_1_unaccepted() -> None:
    text = DESIGN.read_text(encoding="utf-8")

    assert "> **Formal v1.1 Acceptance:** Not Accepted" in text
