"""Fail closed until v1.1 CLI public-contract acceptance is complete."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs" / "releases" / "v1.1-cli-public-contract.md"
ACCEPTANCE = ROOT / "docs" / "releases" / "v1.1-cli-public-contract-acceptance.md"
ROADMAP = ROOT / "docs" / "roadmap.md"
HISTORY = ROOT / "docs" / "HISTORY.md"
CHANGELOG = ROOT / "CHANGELOG.md"

GOVERNING_PR = "#167"
GOVERNING_MERGE = "2727bba27a1438b949870f9dee7df4aa16d43244"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(path: Path) -> str:
    return " ".join(_read(path).split())


def test_acceptance_record_exists_and_remains_fail_closed() -> None:
    record = _read(ACCEPTANCE)

    assert "# OpenProjectLab v1.1 CLI Public Contract Acceptance" in record
    assert "**Status:** Acceptance Closure --- In Progress" in record
    assert "**Formal v1.1 CLI Public Contract Acceptance:** Not Accepted" in record
    assert "**Formal v1.1 Acceptance:** Not Accepted" in record


def test_acceptance_keeps_canonical_governing_identity() -> None:
    design = _read(DESIGN)
    record = _read(ACCEPTANCE)

    for text in (GOVERNING_PR, GOVERNING_MERGE):
        assert text in design
        assert text in record
    assert "Workflow run --- 32360278259" in record


def test_acceptance_records_only_available_local_evidence() -> None:
    record = _read(ACCEPTANCE)

    assert "Focused v1/v1.1 CLI public-contract suite --- 40 passed" in record
    assert "Failures / errors --- 0" in record
    assert "exact metrics not recorded" in record
    assert "pre-commit --- Passed" in record


def test_acceptance_keeps_unresolved_closure_gates_pending() -> None:
    record = _read(ACCEPTANCE)

    for gate in (
        "Acceptance-state focused suite --- Pending local execution",
        "Acceptance-state full regression / coverage --- Pending local execution",
        "Acceptance-state local quality gates --- Pending local execution",
        "Acceptance PR required CI --- Pending",
        "Acceptance squash merge --- Pending",
        "main synchronization --- Pending",
        "Post-merge consistency --- Pending",
        "Terminal documentation alignment --- Pending",
    ):
        assert gate in record


def test_acceptance_does_not_implement_reserved_command_families() -> None:
    record = _read(ACCEPTANCE)

    assert "`marketplace` and `ai` remain absent from the production parser" in record
    assert "Marketplace CLI Contract and implementation remain Not Started" in record
    assert "AI CLI Contract and implementation remain Not Started" in record


def test_acceptance_preserves_deferred_and_experimental_boundaries() -> None:
    prose = _normalized(ACCEPTANCE)

    assert "remote Marketplace and automatic activation remain Deferred" in prose
    assert "live AI remains Experimental and opt-in" in prose
    assert "no production `--json` schema or finer Stable exit taxonomy" in prose


def test_trackers_agree_on_acceptance_closure_state() -> None:
    for tracker in (ROADMAP, HISTORY, CHANGELOG):
        prose = _normalized(tracker)
        assert "#167" in prose
        assert GOVERNING_MERGE in prose
        assert "acceptance closure" in prose.lower()
        assert "Not Accepted" in prose


def test_terminal_state_remains_future_only() -> None:
    record = _read(ACCEPTANCE)

    assert "Only after every closure gate passes" in record
    assert "Next --- v1.1.3 Marketplace CLI Contract" in record
    assert "No earlier passing result substitutes" in record
