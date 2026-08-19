"""Fail-closed contract tests for Step 8.10.9 formal RC acceptance."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PYPROJECT = REPO_ROOT / "pyproject.toml"
ROADMAP = REPO_ROOT / "docs" / "roadmap.md"
HISTORY = REPO_ROOT / "docs" / "HISTORY.md"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"

GOVERNING = REPO_ROOT / "docs" / "releases" / "v1.0-rc-acceptance.md"
PUBLICATION = REPO_ROOT / "docs" / "releases" / "v1.0-rc-creation-publication-identity.md"
RECORD = REPO_ROOT / "docs" / "releases" / "v1.0-rc-acceptance-record.md"

EXPECTED_VERSION = "1.0.0rc1"
EXPECTED_TAG = "v1.0.0-rc.1"
EXPECTED_PUBLICATION_SHA = "b5958edbbf0e3279ed74fa0e3aee13e893c5dfc8"
EXPECTED_WHEEL = "openprojectlab-1.0.0rc1-py3-none-any.whl"
EXPECTED_SDIST = "openprojectlab-1.0.0rc1.tar.gz"
EXPECTED_CHECKSUM = "SHA256SUMS.txt"

EXPECTED_WHEEL_SHA256 = "0dbea1bdbf972a91c25aeb84e5441cb308df866b269ab8f7feea8d099d93d337"
EXPECTED_SDIST_SHA256 = "37e2593a4693b7f038da1b9f0b3ae83643fff2d989992a185a3cdc9022098ea2"
EXPECTED_CHECKSUM_ASSET_SHA256 = "0b56ca72ab9aec34afabcf3fb00d170522a923d4e0120df3bca6234061bb3c4f"

FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")

PENDING_CLOSURE_MARKERS = (
    "Acceptance PR --- Pending",
    "Acceptance PR CI --- Pending",
    "Acceptance squash merge --- Pending",
    "main synchronization --- Pending",
    "post-merge consistency verification --- Pending",
    "cross-document terminal-state alignment --- Pending",
    "Formal RC Acceptance --- Pending",
)


def _read(path: Path) -> str:
    assert path.is_file(), f"Required file is missing: {path}"
    return path.read_text(encoding="utf-8")


def _normalized(path: Path) -> str:
    return " ".join(_read(path).split())


def _project() -> dict[str, object]:
    parsed = tomllib.loads(_read(PYPROJECT))
    project = parsed["project"]
    assert isinstance(project, dict)
    return project


def test_formal_rc_acceptance_record_exists() -> None:
    assert GOVERNING.is_file()
    assert PUBLICATION.is_file()
    assert RECORD.is_file()


def test_formal_rc_acceptance_record_keeps_canonical_identity() -> None:
    record = _read(RECORD)

    assert _project()["version"] == EXPECTED_VERSION
    assert EXPECTED_VERSION in record
    assert EXPECTED_TAG in record


def test_formal_rc_acceptance_record_binds_published_source_identity() -> None:
    record = _read(RECORD)

    assert FULL_SHA_RE.fullmatch(EXPECTED_PUBLICATION_SHA)
    assert record.count(EXPECTED_PUBLICATION_SHA) >= 2
    assert "approved publication commit" in record.lower()
    assert "published rc tag target" in record.lower()


def test_formal_rc_acceptance_record_binds_exact_published_assets() -> None:
    record = _read(RECORD)

    assert EXPECTED_WHEEL in record
    assert EXPECTED_SDIST in record
    assert EXPECTED_CHECKSUM in record

    for digest in (
        EXPECTED_WHEEL_SHA256,
        EXPECTED_SDIST_SHA256,
        EXPECTED_CHECKSUM_ASSET_SHA256,
    ):
        assert SHA256_RE.fullmatch(digest)
        assert digest in record


def test_formal_rc_acceptance_record_requires_prerelease_not_draft() -> None:
    normalized = _normalized(RECORD).lower()

    assert "draft --- false" in normalized
    assert "prerelease --- true" in normalized


def test_formal_rc_acceptance_record_preserves_required_artifact_evidence() -> None:
    normalized = _normalized(RECORD).lower()

    assert "focused completion suite --- 59 passed" in normalized
    assert "required artifact-backed skips --- 0" in normalized
    assert "full regression --- 1881 passed, 1 deselected" in normalized
    assert "coverage --- 90.90%" in normalized


def test_formal_rc_acceptance_record_keeps_ga_unaccepted() -> None:
    normalized = _normalized(RECORD).lower()

    assert "v1.0.0 ga acceptance --- not accepted" in normalized
    assert "ga remains a later independent gate" in normalized


def test_acceptance_candidate_keeps_all_final_closure_gates_pending() -> None:
    record = _read(RECORD)

    assert "**Status:** Acceptance Candidate" in record
    assert "Formal RC Acceptance --- Pending" in record

    missing = [marker for marker in PENDING_CLOSURE_MARKERS if marker not in record]
    assert missing == []


def test_acceptance_candidate_must_not_claim_formal_acceptance() -> None:
    record = _read(RECORD)

    assert "**Status:** Accepted" not in record
    assert "Formal RC Acceptance --- Accepted" not in record


def test_step_8_10_1_through_8_are_complete_and_8_10_9_is_in_progress() -> None:
    record = _read(RECORD)

    for step in (
        "8.10.1 RC Acceptance Baseline                   Completed",
        "8.10.2 RC Acceptance Contract                   Completed",
        "8.10.3 RC Contract Automation                   Completed",
        "8.10.4 RC Build / Artifact Identity             Completed",
        "8.10.5 RC Artifact-backed Verification          Completed",
        "8.10.6 RC Full Regression / Local Quality Gates Completed",
        "8.10.7 RC GitHub Actions / CI                   Completed",
        "8.10.8 RC Creation / Publication Identity       Completed",
        "8.10.9 Formal RC Acceptance / Post-merge        In Progress",
    ):
        assert step in record


def test_acceptance_record_does_not_replace_governing_contract() -> None:
    normalized = _normalized(RECORD).lower()

    assert "acceptance record, not a governing design" in normalized
    assert "governing acceptance contract remains" in normalized


def test_current_roadmap_does_not_preaccept_rc_while_record_is_candidate() -> None:
    roadmap = _read(ROADMAP)

    # The precise formatting of the roadmap may evolve; the final-acceptance
    # test protects the semantic boundary while closure is still pending.
    assert "Step 8.10" in roadmap
    assert "**Status:** In Progress" in roadmap
    assert "8.10.9" in roadmap


def test_current_history_and_changelog_do_not_need_to_claim_rc_accepted_yet() -> None:
    history = _read(HISTORY)
    changelog = _read(CHANGELOG)

    assert "Step 8.10" in history
    assert "Step 8.10" in changelog

    # The candidate-phase test intentionally does not require terminal
    # acceptance wording before the acceptance PR/merge/post-merge gates.
    assert "v1.0.0 GA Acceptance --- Accepted" not in history
    assert "v1.0.0 GA Acceptance --- Accepted" not in changelog
