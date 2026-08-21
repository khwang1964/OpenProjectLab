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


def test_acceptance_record_is_a_fail_closed_candidate() -> None:
    record = _read(RECORD)

    assert "# OpenProjectLab v1.1 Marketplace CLI Implementation Acceptance" in record
    assert "**Status:** Proposed --- Acceptance Candidate In Progress" in record
    assert "v1.1.4.9 --- Full Regression / CI / Formal Acceptance" in record
    assert f"**Acceptance Baseline Commit:** `{BASELINE_SHA}`" in record
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


def test_every_post_candidate_closure_gate_remains_pending() -> None:
    record = _read(RECORD)

    for gate in (
        "Acceptance PR --- Pending",
        "Acceptance PR required CI --- Pending",
        "Acceptance squash merge --- Pending",
        "main synchronization after acceptance merge --- Pending",
        "Post-merge full regression / focused verification --- Pending",
        "Post-merge local quality gates --- Pending",
        "Terminal documentation alignment --- Pending",
    ):
        assert gate in record
    assert "must remain `Not Accepted`" in record


def test_trackers_align_without_claiming_formal_acceptance() -> None:
    for tracker in (ROADMAP, HISTORY, CHANGELOG, BASELINE):
        prose = _normalized(tracker)
        lower_prose = prose.lower()
        assert BASELINE_SHA in prose
        assert "v1.1.4.9 full regression / ci / formal acceptance" in lower_prose
        assert "2150 passed, 33 skipped, 1 deselected" in lower_prose
        assert "90.74%" in prose
        assert "160 passed, 1 skipped" in lower_prose
        assert "formal v1.1 acceptance" in lower_prose
        assert "not accepted" in lower_prose


def test_next_action_is_acceptance_pr_required_ci() -> None:
    record = _read(RECORD)
    prose = _normalized(RECORD)

    assert "Next --- acceptance PR / required CI" in record
    assert "Only after required CI, squash merge, synchronized `main`," in prose
    assert "terminal documentation alignment may Formal v1.1 Acceptance become Accepted" in prose
