"""Fail-closed v1.1 formal acceptance contract."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]

RECORD = ROOT / "docs" / "releases" / "v1.1-formal-acceptance.md"
ROADMAP = ROOT / "docs" / "roadmap.md"
HISTORY = ROOT / "docs" / "HISTORY.md"

DOC_PARITY = ROOT / "docs" / "releases" / "v1.1-documentation-parity.md"
ARTIFACT_ACCEPTANCE = (
    ROOT / "docs" / "releases" / "v1.1-reliability-artifact-backed-verification.md"
)

EXPECTED_PREDECESSOR_MERGE = "87dc6de198dd83816ece2856dbb192bf337d5dbe"


def _read(path: Path) -> str:
    if not path.is_file():
        pytest.fail(f"Missing required v1.1 acceptance authority: {path}")
    return path.read_text(encoding="utf-8")


def test_formal_acceptance_record_exists_and_is_not_preaccepted() -> None:
    text = _read(RECORD)

    assert "v1.1.9 --- Formal v1.1 Acceptance" in text
    assert "> **Formal v1.1 Acceptance:** Accepted" in text
    assert "v1.1.9 Formal v1.1 Acceptance --- Accepted" in text


def test_v1_1_8_predecessor_is_terminally_accepted() -> None:
    text = _read(ARTIFACT_ACCEPTANCE)

    assert "v1.1.8 Reliability / Artifact-backed Verification --- Accepted" in text
    assert "Formal v1.1 Acceptance --- Not Accepted" in text


def test_v1_1_8_terminal_alignment_merge_is_bound_into_formal_acceptance() -> None:
    text = _read(RECORD)

    assert "Predecessor Terminal PR:** #217" in text
    assert f"Predecessor Merge:** {EXPECTED_PREDECESSOR_MERGE}" in text


def test_documentation_parity_predecessor_remains_accepted() -> None:
    text = _read(DOC_PARITY)

    assert "v1.1.7 Documentation / EN-zh-TW Parity --- Accepted" in text


def test_formal_acceptance_preserves_release_identity_boundary() -> None:
    text = _read(RECORD)

    assert "repository canonical historical identity" in text
    assert "1.0.0" in text
    assert "temporary v1.1 candidate build identity" in text
    assert "1.1.0rc1" in text
    assert "v1.1.0-rc.1" in text


def test_formal_acceptance_declares_local_passed_and_remote_pending_gates() -> None:
    text = _read(RECORD)

    local_passed = (
        "Focused formal-acceptance verification ---",
        "Full regression --- 2312 passed, 53 skipped, 1 deselected",
        "Total coverage --- 91.17%",
        "Required coverage threshold --- 67.0% --- Passed",
        "git diff --check --- Passed",
        "pre-commit --- Passed",
    )

    remote_pending = (
        "Acceptance PR required CI --- Pending",
        "Acceptance squash merge --- Pending",
        "main synchronization --- Pending",
        "Post-merge consistency verification --- Pending",
        "Terminal acceptance alignment --- Pending",
        "Formal v1.1 Acceptance --- Not Accepted",
    )

    for gate in local_passed:
        assert gate in text

    for gate in remote_pending:
        assert gate in text


def test_formal_acceptance_is_terminally_closed() -> None:
    text = _read(RECORD)

    assert "v1.1.9 Formal v1.1 Acceptance --- Accepted" in text
    assert "Formal v1.1 Acceptance --- Accepted" in text
    assert "> **Formal v1.1 Acceptance:** Accepted" in text
    assert "Acceptance PR #218 --- Merged" in text
    assert ("Acceptance merge --- c740613f5ac29d696962545afb2ee0f5b0c8c630") in text
    assert "Post-merge consistency verification --- Passed" in text
    assert "Terminal acceptance alignment --- Completed" in text
    assert "v1.1 --- Terminally Accepted" in text


def test_roadmap_and_history_record_terminal_v1_1_acceptance() -> None:
    for path in (ROADMAP, HISTORY):
        text = _read(path)
        assert "Formal v1.1 Acceptance --- Accepted" in text
        assert "v1.1 --- Terminally Accepted" in text


def test_formal_acceptance_terminal_closure_evidence() -> None:
    text = _read(RECORD)

    assert "Acceptance PR #218 --- Merged" in text
    assert "Acceptance merge --- c740613f5ac29d696962545afb2ee0f5b0c8c630" in text
    assert "Acceptance PR required CI --- Passed" in text
    assert "main synchronization --- Completed" in text
    assert "Post-merge consistency verification --- Passed" in text
    assert "Terminal acceptance alignment --- Completed" in text
    assert "v1.1 --- Terminally Accepted" in text
