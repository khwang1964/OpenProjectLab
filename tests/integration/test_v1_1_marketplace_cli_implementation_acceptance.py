"""Keep Formal v1.1 Marketplace CLI acceptance fail closed."""

from __future__ import annotations

from pathlib import Path

from generator.cli.main import build_parser

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "docs" / "releases" / "v1.1-marketplace-cli-implementation-acceptance.md"
BASELINE = ROOT / "docs" / "releases" / "v1.1-marketplace-cli-implementation.md"
ROADMAP = ROOT / "docs" / "roadmap.md"
HISTORY = ROOT / "docs" / "HISTORY.md"
CHANGELOG = ROOT / "CHANGELOG.md"

BASELINE_SHA = "f7910d51c49c74614381491458414739c47d5d74"
ACCEPTANCE_MERGE = "a89d0d4e7b8fd068c1c4e2b841489bf211efbf28"


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


def test_marketplace_implementation_record_is_terminally_accepted() -> None:
    record = _read(RECORD)

    assert "# OpenProjectLab v1.1 Marketplace CLI Implementation Acceptance" in record
    assert "**Status:** Accepted" in record
    assert "v1.1.4.9 --- Full Regression / CI / Implementation Acceptance" in record
    assert f"**Acceptance Baseline Commit:** `{BASELINE_SHA}`" in record
    assert "**Acceptance PR:** #188 --- Merged" in record
    assert f"**Acceptance Merge Commit:** `{ACCEPTANCE_MERGE}`" in record
    assert "**Marketplace CLI Implementation Acceptance:** Accepted" in record
    assert "**Formal v1.1 Acceptance:** Not Accepted" in record


def test_candidate_records_fresh_regression_and_coverage_evidence() -> None:
    record = _read(RECORD)

    assert "Full regression --- 2150 passed, 33 skipped, 1 deselected" in record
    assert "Full regression execution time --- 23.77s" in record
    assert "Total coverage --- 90.74%" in record
    assert "Required coverage threshold --- 67.0%" in record
    assert "Marketplace-focused regression --- 160 passed, 1 skipped" in record
    assert "Marketplace-focused execution time --- 1.07s" in record
    assert "failures / errors --- 0" in record


def test_candidate_preserves_exact_production_command_inventory() -> None:
    record = _read(RECORD)

    assert "marketplace" in _top_level_commands()
    for subcommand in ("versions", "inspect", "verify", "install"):
        assert f"opl marketplace {subcommand} " in record
    assert "There is no `opl marketplace list` command" in record


def test_candidate_preserves_safety_and_side_effect_boundaries() -> None:
    prose = _normalized(RECORD)

    assert "payload-root containment" in prose
    assert "SHA-256 integrity" in prose
    assert "verification before installation" in prose
    assert "no partial installer state" in prose
    assert "process-local, non-persistent, non-activating" in prose
    assert "remote catalog or payload access" in prose
    assert "AI CLI commands" in prose


def test_every_post_candidate_closure_gate_is_complete() -> None:
    record = _read(RECORD)

    for gate in (
        "Acceptance PR #188 --- Merged",
        "Acceptance PR required CI --- Passed",
        "Acceptance squash merge --- Completed",
        "main synchronization after acceptance merge --- Completed",
        "Post-merge focused verification --- 56 passed in 0.30s",
        "Post-merge full regression --- 2158 passed, 33 skipped, 1 deselected",
        "Post-merge local quality gates --- Passed",
        "Terminal documentation alignment --- Completed",
    ):
        assert gate in record
    assert "must remain `Not Accepted`" in record
    assert "v1.1.5 AI CLI Contract --- Not Started" in record
    assert "v1.1.9 Formal v1.1 Acceptance --- Not Accepted" in record


def test_trackers_accept_marketplace_without_overclaiming_v1_1() -> None:
    for tracker in (ROADMAP, HISTORY, CHANGELOG, BASELINE):
        prose = _normalized(tracker)
        lower_prose = prose.lower()
        assert BASELINE_SHA in prose
        assert "v1.1.4.9 full regression / ci / formal acceptance" in lower_prose
        assert "2150 passed, 33 skipped, 1 deselected" in lower_prose
        assert "90.74%" in prose
        assert "160 passed, 1 skipped" in lower_prose
        assert "marketplace cli implementation acceptance" in lower_prose
        assert "accepted" in lower_prose
        assert "formal v1.1 acceptance" in lower_prose
        assert "not accepted" in lower_prose
        assert ACCEPTANCE_MERGE in prose


def test_next_action_is_ai_cli_contract() -> None:
    record = _read(RECORD)
    prose = _normalized(RECORD)

    assert "Next --- v1.1.5 AI CLI Contract" in record
    assert "under the existing v1.1 governing sequence" in prose
    assert "does not replace the remaining v1.1 acceptance stages" in prose
