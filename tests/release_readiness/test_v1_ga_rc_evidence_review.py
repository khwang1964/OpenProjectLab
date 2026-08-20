"""Fail-closed tests for GA.1 RC evidence review."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PYPROJECT = REPO_ROOT / "pyproject.toml"
ROADMAP = REPO_ROOT / "docs" / "roadmap.md"
GA_REVIEW = REPO_ROOT / "docs" / "releases" / "v1.0-ga-rc-evidence-review.md"
GA_BASELINE = REPO_ROOT / "docs" / "releases" / "v1.0-ga-baseline.md"
GA_CONTRACT = REPO_ROOT / "docs" / "releases" / "v1.0-ga-acceptance.md"
RC_CONTRACT = REPO_ROOT / "docs" / "releases" / "v1.0-rc-acceptance.md"
RC_RECORD = REPO_ROOT / "docs" / "releases" / "v1.0-rc-acceptance-record.md"

EXPECTED_RC = "v1.0.0-rc.1"
EXPECTED_VERSION = "1.0.0rc1"

RC_PUBLICATION_SHA = "b5958edbbf0e3279ed74fa0e3aee13e893c5dfc8"
RC_TERMINAL_ACCEPTANCE_SHA = "0e3b31cb410fde3ebb85251e668a0c424bcfc60c"
GA_CONTRACT_MERGE_SHA = "d6f2ecf45c42e439d9ca172fa74919488fd6b14b"


def _read(path: Path) -> str:
    assert path.is_file(), f"Required GA evidence-review file is missing: {path}"
    return path.read_text(encoding="utf-8")


def _normalized(path: Path) -> str:
    return " ".join(_read(path).split())


def _metadata_value(document: str, label: str) -> str:
    pattern = re.compile(
        rf"^>\s*\*\*{re.escape(label)}:\*\*\s*(?P<value>.+?)\\?\s*$",
        re.MULTILINE,
    )
    match = pattern.search(document)
    assert match is not None, f"Missing metadata field: {label}"
    return match.group("value").strip()


def _project_version() -> str:
    parsed = tomllib.loads(_read(PYPROJECT))
    project = parsed["project"]
    assert isinstance(project, dict)
    version = project["version"]
    assert isinstance(version, str)
    return version


def _roadmap_step_section(roadmap: str, step: str) -> str:
    heading = re.compile(rf"^## Step {re.escape(step)}\b.*$", re.MULTILINE)
    match = heading.search(roadmap)
    assert match is not None, f"Roadmap section for Step {step} is missing"

    next_heading = re.compile(r"^## Step 8\.\d+\b.*$", re.MULTILINE)
    next_match = next_heading.search(roadmap, match.end())
    end = next_match.start() if next_match is not None else len(roadmap)
    return roadmap[match.start() : end]


def _roadmap_status(roadmap: str, step: str) -> str:
    section = _roadmap_step_section(roadmap, step)
    match = re.search(
        r"^\*\*Status:\*\*\s*(?P<status>.+?)\s*$",
        section,
        re.MULTILINE,
    )
    assert match is not None, f"Roadmap Step {step} has no explicit status"
    return match.group("status").strip()


def test_ga_rc_evidence_review_exists() -> None:
    assert GA_REVIEW.is_file()
    assert GA_BASELINE.is_file()
    assert GA_CONTRACT.is_file()


def test_ga_rc_evidence_review_metadata_is_current() -> None:
    document = _read(GA_REVIEW)

    assert _metadata_value(document, "Status") == "In Progress"
    assert _metadata_value(document, "Milestone") == "v1.0 GA Acceptance"
    assert _metadata_value(document, "Step").startswith("GA.1")
    assert _metadata_value(document, "Accepted RC") == f"`{EXPECTED_RC}`"


def test_step_8_10_remains_accepted() -> None:
    roadmap = _read(ROADMAP)
    rc_contract = _read(RC_CONTRACT)
    rc_record = _read(RC_RECORD)

    assert _roadmap_status(roadmap, "8.10") == "Accepted"
    assert _metadata_value(rc_contract, "Status") == "Accepted"
    assert _metadata_value(rc_record, "Status") == "Accepted"


def test_repository_remains_on_rc_version() -> None:
    assert _project_version() == EXPECTED_VERSION


def test_review_records_release_and_governance_provenance() -> None:
    review = _read(GA_REVIEW)

    for value in (
        RC_PUBLICATION_SHA,
        RC_TERMINAL_ACCEPTANCE_SHA,
        GA_CONTRACT_MERGE_SHA,
    ):
        assert value in review

    assert RC_PUBLICATION_SHA != RC_TERMINAL_ACCEPTANCE_SHA
    assert RC_PUBLICATION_SHA != GA_CONTRACT_MERGE_SHA
    assert RC_TERMINAL_ACCEPTANCE_SHA != GA_CONTRACT_MERGE_SHA


def test_reviewed_evidence_sources_are_explicit() -> None:
    normalized = _normalized(GA_REVIEW)

    for source in (
        "Step 8.10 governing RC acceptance contract",
        "Step 8.10 formal RC acceptance record",
        "RC publication identity verification",
        "RC artifact-backed verification",
        "RC full regression / local quality-gate evidence",
        "RC GitHub Actions / CI evidence",
        "RC post-publication identity verification",
        "RC terminal acceptance / post-merge consistency evidence",
    ):
        assert source in normalized


def test_all_ga_finding_classifications_remain_defined() -> None:
    normalized = _normalized(GA_REVIEW)

    for classification in (
        "GA blocker",
        "GA correction",
        "Post-GA patch candidate",
        "v1.1+ deferred improvement",
    ):
        assert classification in normalized


def test_ga_blocker_result_is_scoped_to_reviewed_evidence() -> None:
    normalized = _normalized(GA_REVIEW)

    assert "Recorded GA blockers --- None found in reviewed evidence" in normalized
    assert "The statement is intentionally limited to the reviewed evidence set" in normalized
    assert "All possible GA blockers in existence --- 0" in normalized


def test_review_does_not_claim_universal_zero_blockers() -> None:
    normalized = _normalized(GA_REVIEW).lower()

    assert "not a universal statement that no defects exist" in normalized
    assert "universal zero-defect claim" in normalized
    assert "ga blockers --- 0" not in normalized
    assert "ga blockers: 0" not in normalized


def test_no_ga_correction_is_required_by_reviewed_evidence() -> None:
    normalized = _normalized(GA_REVIEW)

    assert "Recorded GA corrections --- None required by reviewed evidence" in normalized
    assert "GA correction required by reviewed evidence --- No" in normalized


def test_no_post_ga_patch_candidate_is_identified_in_reviewed_evidence() -> None:
    normalized = _normalized(GA_REVIEW)

    assert (
        "Recorded Post-GA patch candidates --- None identified in reviewed evidence" in normalized
    )


def test_deferred_backlog_remains_authoritative() -> None:
    normalized = _normalized(GA_REVIEW)

    assert (
        "v1.1+ deferred improvements --- Existing deferred backlog remains authoritative"
        in normalized
    )
    assert "does not promote deferred improvement work into v1.0 scope" in normalized


def test_ga_blocker_disposition_passes_for_current_reviewed_evidence() -> None:
    normalized = _normalized(GA_REVIEW)

    assert "RC evidence sources reviewed --- Completed" in normalized
    assert "RC validation / observation review --- Completed" in normalized
    assert "GA blocker disposition --- Passed" in normalized


def test_ga_release_mutation_remains_unauthorized() -> None:
    normalized = _normalized(GA_REVIEW)

    for required in (
        "Canonical repository version --- 1.0.0rc1",
        "GA version transition to 1.0.0 --- Not Authorized",
        "v1.0.0 tag creation --- Not Authorized",
        "GA artifact publication --- Not Authorized",
        "GA GitHub Release creation --- Not Authorized",
        "Formal v1.0.0 GA Acceptance --- Not Accepted",
    ):
        assert required in normalized


def test_ga_1_is_ready_for_closure_but_not_ga_acceptance() -> None:
    normalized = _normalized(GA_REVIEW)

    assert "GA.1 evidence review --- Ready for closure" in normalized
    assert "GA.1 is ready for reviewed closure" in normalized
    assert "Formal v1.0.0 GA Acceptance --- Not Accepted" in normalized


def test_new_contradictory_evidence_requires_reopen() -> None:
    normalized = _normalized(GA_REVIEW)

    assert "GA.1 must be reopened if new evidence before GA publication identifies" in normalized
    assert "The next gate must not rely on stale GA.1 evidence" in normalized
