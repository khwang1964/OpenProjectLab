"""Contract tests for Milestone 8 Step 8.10 RC Acceptance."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RELEASES_DIR = REPO_ROOT / "docs" / "releases"
ROADMAP_PATH = REPO_ROOT / "docs" / "roadmap.md"

RC_CONTRACT_PATH = RELEASES_DIR / "v1.0-rc-acceptance.md"
STEP_8_9_ACCEPTANCE_PATH = RELEASES_DIR / "v1.0-full-release-readiness-verification-acceptance.md"

EXPECTED_RC_TAG = "v1.0.0-rc.1"


def _read(path: Path) -> str:
    """Read one required UTF-8 repository document."""
    assert path.is_file(), f"Required release-readiness document is missing: {path}"
    return path.read_text(encoding="utf-8")


def _metadata_value(document: str, label: str) -> str:
    """Return one blockquote metadata value."""
    pattern = re.compile(
        rf"^>\s*\*\*{re.escape(label)}:\*\*\s*(?P<value>.+?)\\?\s*$",
        re.MULTILINE,
    )
    match = pattern.search(document)
    assert match is not None, f"Missing required metadata field: {label}"
    return match.group("value").strip()


def _roadmap_step_section(roadmap: str, step: str) -> str:
    """Return one Step 8.x roadmap section through the next Step heading."""
    heading = re.compile(rf"^## Step {re.escape(step)}\b.*$", re.MULTILINE)
    match = heading.search(roadmap)
    assert match is not None, f"Roadmap section for Step {step} is missing"

    next_heading = re.compile(r"^## Step 8\.\d+\b.*$", re.MULTILINE)
    next_match = next_heading.search(roadmap, match.end())
    end = next_match.start() if next_match is not None else len(roadmap)
    return roadmap[match.start() : end]


def _roadmap_status(roadmap: str, step: str) -> str:
    """Return the explicit status from one Step 8.x roadmap section."""
    section = _roadmap_step_section(roadmap, step)
    match = re.search(r"^\*\*Status:\*\*\s*(?P<status>.+?)\s*$", section, re.MULTILINE)
    assert match is not None, f"Roadmap Step {step} has no explicit status"
    return match.group("status").strip()


def test_rc_acceptance_governing_document_exists() -> None:
    """Step 8.10 must have an explicit governing RC contract."""
    assert RC_CONTRACT_PATH.is_file()


def test_rc_contract_metadata_identifies_step_8_10() -> None:
    """The governing record must identify the correct Milestone 8 slice."""
    document = _read(RC_CONTRACT_PATH)

    assert _metadata_value(document, "Milestone").startswith("8 ")
    assert _metadata_value(document, "Step").startswith("8.10")
    assert _metadata_value(document, "Status").startswith("Design / Contract Definition")


def test_rc_contract_requires_accepted_step_8_9_predecessor() -> None:
    """RC Acceptance must depend on the already-accepted Step 8.9 state."""
    document = _read(RC_CONTRACT_PATH)
    predecessor = _metadata_value(document, "Predecessor")

    assert predecessor.startswith("Step 8.9")
    assert predecessor.endswith("Accepted")

    step_8_9_acceptance = _read(STEP_8_9_ACCEPTANCE_PATH)
    assert _metadata_value(step_8_9_acceptance, "Status") == "Accepted"


def test_first_rc_identity_is_fixed() -> None:
    """The first v1.0 RC identity must be stable and unambiguous."""
    document = _read(RC_CONTRACT_PATH)

    assert _metadata_value(document, "Target RC") == f"`{EXPECTED_RC_TAG}`"
    assert f"canonical RC tag is:\n\n```text\n{EXPECTED_RC_TAG}\n```" in document


def test_rc_and_ga_acceptance_are_explicitly_separate() -> None:
    """Accepting an RC must never pre-approve the v1.0 GA release."""
    document = _read(RC_CONTRACT_PATH)

    assert "RC Acceptance and GA Acceptance are separate decisions." in document
    assert "RC Acceptance does not mean:" in document
    assert "`v1.0.0` is GA Accepted." in document
    assert "GA requires a later independent decision" in document


def test_rc_contract_is_fail_closed() -> None:
    """Missing or contradictory evidence must block RC Acceptance."""
    document = _read(RC_CONTRACT_PATH)

    assert "RC Acceptance is fail-closed." in document
    assert "No individual passing gate compensates" in document
    assert "Until all required evidence exists, the RC remains unaccepted." in document


def test_rc_contract_requires_complete_release_identity() -> None:
    """Source, artifact, checksum, tag, and release identity must agree."""
    document = _read(RC_CONTRACT_PATH)

    required_phrases = (
        "Approved source commit",
        "Tag target commit",
        "Wheel metadata version",
        "Source-distribution metadata version",
        "Artifact checksum manifest",
        "Installed-user test artifact",
        "GitHub Release tag",
        "GitHub Release artifacts",
    )

    missing = [phrase for phrase in required_phrases if phrase not in document]
    assert missing == [], f"RC identity contract is missing: {missing}"


def test_rc_contract_requires_artifact_backed_evidence() -> None:
    """Source-checkout-only success cannot satisfy the final RC gate."""
    document = _read(RC_CONTRACT_PATH)

    assert "source-checkout-only success as installed-user evidence" in document
    assert "Required artifact-backed tests must not be accepted as skipped" in document
    assert "wheel-backed First 15 Minutes" in document
    assert "artifact-backed installed-user E2E" in document


def test_rc_contract_rejects_stale_and_mutated_release_identity() -> None:
    """The same RC identity cannot be silently reused for different bytes/source."""
    document = _read(RC_CONTRACT_PATH)

    assert "silently reuse stale artifacts" in document
    assert "rewrite an existing release tag to point at another commit" in document
    assert "replace an already-published RC artifact under the same identity" in document
    assert "do not retarget `v1.0.0-rc.1`" in document


def test_rc_contract_limits_allowed_rc_changes() -> None:
    """RC-period work must remain inside the frozen stabilization boundary."""
    document = _read(RC_CONTRACT_PATH)

    required_change_classes = (
        "release blockers",
        "correctness defects",
        "compatibility defects",
        "installation / packaging defects",
        "security defects",
        "documentation correctness fixes",
        "release/test automation defects",
    )

    missing = [item for item in required_change_classes if item not in document]
    assert missing == [], f"RC allowed-change policy is incomplete: {missing}"

    assert "should normally move to v1.1+" in document


def test_rc_contract_requires_real_evidence_not_placeholders() -> None:
    """Future result values must be recorded only from actual execution."""
    document = _read(RC_CONTRACT_PATH)
    normalized = " ".join(document.split())

    assert "must be recorded from real evidence" in normalized
    assert "must not be pre-filled" in normalized
    assert "No tag, GitHub Release, checksum, artifact, test count" in normalized


def test_roadmap_keeps_step_8_9_accepted() -> None:
    """Entering RC Acceptance must not reopen Step 8.9."""
    roadmap = _read(ROADMAP_PATH)

    assert _roadmap_status(roadmap, "8.9") == "Accepted"


def test_roadmap_does_not_preaccept_step_8_10() -> None:
    """The governing-contract slice may start, but RC Acceptance is not complete."""
    roadmap = _read(ROADMAP_PATH)
    status = _roadmap_status(roadmap, "8.10")

    assert status == "Planned" or status.startswith("In Progress")
    assert status != "Accepted"


def test_current_governing_record_does_not_claim_rc_is_accepted() -> None:
    """Creating the Step 8.10 design must not fabricate the terminal decision."""
    document = _read(RC_CONTRACT_PATH)

    assert "v1.0.0-rc.1                     Not yet accepted" in document
    assert "v1.0.0 GA                       Not accepted" in document
    assert _metadata_value(document, "Status") != "Accepted"
