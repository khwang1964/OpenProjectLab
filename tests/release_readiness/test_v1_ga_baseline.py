"""Fail-closed tests for GA.1 — GA Acceptance Baseline."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PYPROJECT = REPO_ROOT / "pyproject.toml"
ROADMAP = REPO_ROOT / "docs" / "roadmap.md"
GA_CONTRACT = REPO_ROOT / "docs" / "releases" / "v1.0-ga-acceptance.md"
GA_BASELINE = REPO_ROOT / "docs" / "releases" / "v1.0-ga-baseline.md"
RC_CONTRACT = REPO_ROOT / "docs" / "releases" / "v1.0-rc-acceptance.md"
RC_RECORD = REPO_ROOT / "docs" / "releases" / "v1.0-rc-acceptance-record.md"

EXPECTED_RC = "v1.0.0-rc.1"
EXPECTED_VERSION = "1.0.0rc1"

RC_PUBLICATION_SHA = "b5958edbbf0e3279ed74fa0e3aee13e893c5dfc8"
RC_TERMINAL_ACCEPTANCE_SHA = "0e3b31cb410fde3ebb85251e668a0c424bcfc60c"
GA_CONTRACT_MERGE_SHA = "d6f2ecf45c42e439d9ca172fa74919488fd6b14b"

FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")


def _read(path: Path) -> str:
    assert path.is_file(), f"Required GA.1 file is missing: {path}"
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


def test_ga_baseline_exists() -> None:
    assert GA_BASELINE.is_file()
    assert GA_CONTRACT.is_file()


def test_ga_baseline_metadata_identifies_ga_1() -> None:
    document = _read(GA_BASELINE)

    assert _metadata_value(document, "Status") == "In Progress"
    assert _metadata_value(document, "Milestone") == "v1.0 GA Acceptance"
    assert _metadata_value(document, "Step").startswith("GA.1")
    assert _metadata_value(document, "Accepted RC") == f"`{EXPECTED_RC}`"


def test_step_8_10_remains_formally_accepted() -> None:
    roadmap = _read(ROADMAP)
    rc_contract = _read(RC_CONTRACT)
    rc_record = _read(RC_RECORD)

    assert _roadmap_status(roadmap, "8.10") == "Accepted"
    assert _metadata_value(rc_contract, "Status") == "Accepted"
    assert _metadata_value(rc_record, "Status") == "Accepted"


def test_repository_remains_on_rc_version_during_ga_1() -> None:
    assert _project_version() == EXPECTED_VERSION


def test_ga_baseline_records_all_three_provenance_shas() -> None:
    baseline = _read(GA_BASELINE)

    for sha in (
        RC_PUBLICATION_SHA,
        RC_TERMINAL_ACCEPTANCE_SHA,
        GA_CONTRACT_MERGE_SHA,
    ):
        assert FULL_SHA_RE.fullmatch(sha)
        assert sha in baseline


def test_ga_provenance_shas_are_not_conflated() -> None:
    assert RC_PUBLICATION_SHA != RC_TERMINAL_ACCEPTANCE_SHA
    assert RC_PUBLICATION_SHA != GA_CONTRACT_MERGE_SHA
    assert RC_TERMINAL_ACCEPTANCE_SHA != GA_CONTRACT_MERGE_SHA

    normalized = _normalized(GA_BASELINE)
    assert "These values are intentionally different" in normalized
    assert "governance provenance only" in normalized


def test_ga_1_requires_actual_rc_evidence_review() -> None:
    normalized = _normalized(GA_BASELINE)

    assert "RC validation / observation review --- In Progress" in normalized
    assert "actual evidence gathered after RC publication" in normalized
    assert "produced zero blockers" in normalized
    assert "absence of recorded evidence" in normalized


def test_ga_1_keeps_blocker_disposition_pending() -> None:
    normalized = _normalized(GA_BASELINE)

    assert "GA blocker disposition --- Pending evidence review" in normalized
    assert "GA blockers resolved --- Not yet established" in normalized
    assert "GA corrections required --- Not yet established" in normalized


def test_ga_1_does_not_invent_zero_blockers() -> None:
    normalized = _normalized(GA_BASELINE).lower()

    assert "zero blockers" in normalized
    assert "absence of recorded evidence" in normalized
    assert "proof that zero ga blockers exist" in normalized
    assert "ga blockers --- 0" not in normalized
    assert "ga blockers: 0" not in normalized


def test_ga_1_defines_required_finding_classifications() -> None:
    normalized = _normalized(GA_BASELINE)

    for classification in (
        "GA blocker",
        "GA correction",
        "Post-GA patch candidate",
        "v1.1+ deferred improvement",
    ):
        assert classification in normalized


def test_ga_version_transition_and_publication_remain_unauthorized() -> None:
    normalized = _normalized(GA_BASELINE)

    for required in (
        "GA version transition to 1.0.0 --- Not Authorized",
        "v1.0.0 tag creation --- Not Authorized",
        "GA artifact publication --- Not Authorized",
        "GA GitHub Release creation --- Not Authorized",
        "Formal v1.0.0 GA Acceptance --- Not Accepted",
    ):
        assert required in normalized


def test_ga_1_current_decision_is_not_complete() -> None:
    normalized = _normalized(GA_BASELINE)

    assert "Status --- In Progress" in normalized
    assert "GA.1 is therefore not yet complete" in normalized


def test_ga_1_does_not_authorize_ga_source_commit() -> None:
    normalized = _normalized(GA_BASELINE)

    assert "No GA source commit is invented" in normalized
