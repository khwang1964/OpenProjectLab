"""Keep v1.1 Marketplace CLI contract acceptance fail closed."""

from __future__ import annotations

from pathlib import Path

from generator.cli.main import build_parser

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs" / "releases" / "v1.1-marketplace-cli-contract.md"
ACCEPTANCE = ROOT / "docs" / "releases" / "v1.1-marketplace-cli-contract-acceptance.md"
ROADMAP = ROOT / "docs" / "roadmap.md"
HISTORY = ROOT / "docs" / "HISTORY.md"
CHANGELOG = ROOT / "CHANGELOG.md"

GOVERNING_PR = "#170"
GOVERNING_MERGE = "5f63bd3dc438ba1ea5e10b8225c761964c1819bc"
ACCEPTANCE_PR = "#171"
ACCEPTANCE_MERGE = "02ed8569bbd5a6c12632783186220954b2b99f12"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(path: Path) -> str:
    return " ".join(_read(path).split())


def _top_level_commands() -> frozenset[str]:
    parser = build_parser()

    for action in parser._actions:
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict) and "list" in choices:
            return frozenset(choices)

    raise AssertionError("CLI subcommand registry was not found")


def test_acceptance_record_exists_and_is_accepted() -> None:
    record = _read(ACCEPTANCE)

    assert "# OpenProjectLab v1.1 Marketplace CLI Contract Acceptance" in record
    assert "**Status:** Accepted" in record
    assert "v1.1.3 --- Marketplace CLI Contract Acceptance" in record
    assert "**Acceptance PR:** #171 --- Merged" in record
    assert f"**Acceptance Merge Commit:** `{ACCEPTANCE_MERGE}`" in record
    assert "**Marketplace CLI Contract Acceptance:** Accepted" in record
    assert "**Marketplace CLI Implementation:** Not Started" in record
    assert "**Formal v1.1 Acceptance:** Not Accepted" in record


def test_governing_contract_records_reviewed_merge_identity() -> None:
    contract = _read(CONTRACT)
    record = _read(ACCEPTANCE)

    for document in (contract, record):
        assert GOVERNING_PR in document
        assert GOVERNING_MERGE in document

    assert "**Status:** Accepted" in contract
    assert "**Marketplace CLI Contract:** Accepted" in contract
    assert "Governing PR #170 --- Merged" in contract


def test_fresh_acceptance_state_evidence_and_closure_are_recorded() -> None:
    record = _read(ACCEPTANCE)
    prose = _normalized(ACCEPTANCE)

    assert "Focused Marketplace contract suite --- 35 passed" in record
    assert "2018 passed, 32 skipped, 1 deselected" in record
    assert "fresh acceptance-state execution" in prose
    assert "Governing required CI evidence --- Passed" in record
    assert "Acceptance-state focused suite --- 84 passed" in record
    assert "Acceptance-state full regression --- 1533 passed, 11 skipped, 1 deselected" in record
    assert "Acceptance-state full regression execution time --- 11.00s" in record
    assert "Acceptance-state failures / errors --- 0" in record
    assert "Acceptance-state pre-commit --- Passed" in record
    assert "Acceptance-state required coverage evidence --- Passed" in record
    assert "Acceptance-state git diff --check --- Passed" in record


def test_historical_acceptance_record_precedes_later_registration() -> None:
    record = _read(ACCEPTANCE)

    assert "marketplace" in _top_level_commands()
    assert "`marketplace` remains absent from the production parser" in record
    assert "v1.1.4 Marketplace CLI Implementation remains Not Started" in record
    assert "Marketplace CLI Implementation remains Not Started" in record


def test_acceptance_scope_matches_the_governing_command_inventory() -> None:
    record = _read(ACCEPTANCE)

    for subcommand in ("versions", "inspect", "verify", "install"):
        assert f"opl marketplace {subcommand} " in record

    assert "does not invent `opl marketplace list`" in record
    assert "namespace/name@MAJOR.MINOR.PATCH" in record
    assert "UTF-8 local catalog schema version 1" in record


def test_acceptance_preserves_local_safety_and_side_effect_boundaries() -> None:
    prose = _normalized(ACCEPTANCE)

    assert "safe payload-root containment and file-only acquisition" in prose
    assert "exact lookup, SHA-256 verification" in prose
    assert "failure-before-installation" in prose
    assert "in-memory, non-activating, non-persistent" in prose
    assert "implicit network fallback remain Deferred" in prose
    assert "dependency resolution, signing/trust" in prose


def test_acceptance_records_every_completed_closure_gate() -> None:
    record = _read(ACCEPTANCE)

    for gate in (
        "Acceptance PR required CI --- Passed",
        "Acceptance squash merge --- Completed",
        "main synchronization after acceptance merge --- Completed",
        "Post-merge focused suite --- Passed",
        "Post-merge local quality gates --- Passed",
        "Terminal documentation alignment --- Completed",
    ):
        assert gate in record

    assert "No earlier result or governing merge skips a later gate" in record
    assert "must remain `Not Accepted`" in record


def test_trackers_align_with_accepted_contract_without_overclaiming() -> None:
    for tracker in (ROADMAP, HISTORY, CHANGELOG):
        text = _read(tracker)
        assert GOVERNING_PR in text
        assert GOVERNING_MERGE in text
        assert ACCEPTANCE_PR in text
        assert ACCEPTANCE_MERGE in text
        assert "Marketplace CLI Contract" in text
        assert "Marketplace CLI Contract Acceptance --- Accepted" in text
        assert "Marketplace CLI Implementation" in text
        assert "Not Started" in text


def test_terminal_state_is_documented_and_claimed_currently() -> None:
    record = _read(ACCEPTANCE)

    assert "Only after every closure gate passes" in record
    assert "v1.1.3 Marketplace CLI Contract --- Accepted" in record
    assert "Next --- v1.1.4 Marketplace CLI Implementation" in record
    assert "Marketplace CLI Contract Acceptance --- Accepted" in record
    assert "Formal v1.1 Acceptance --- Not Accepted" in record
