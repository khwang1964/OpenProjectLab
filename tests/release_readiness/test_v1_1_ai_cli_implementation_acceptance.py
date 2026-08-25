"""Fail-closed v1.1 AI CLI implementation acceptance contract."""

from __future__ import annotations

from pathlib import Path

import pytest

from generator.cli.main import main

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = ROOT / "docs" / "releases" / "v1.1-ai-cli-implementation-acceptance.md"
IMPLEMENTATION = ROOT / "docs" / "releases" / "v1.1-ai-cli-implementation.md"
ROADMAP = ROOT / "docs" / "roadmap.md"
EN_CLI = ROOT / "docs" / "user-guide" / "en" / "cli.md"
ZH_TW_CLI = ROOT / "docs" / "user-guide" / "zh-TW" / "cli.md"

EXPECTED_COMMANDS = ("course", "review", "document", "template")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_acceptance_record_is_terminally_accepted_without_accepting_v1_1() -> None:
    text = _read(ACCEPTANCE)

    assert "v1.1.6.11 --- Full Regression / AI CLI Implementation Acceptance" in text
    assert "> **Status:** Accepted --- Terminally Closed" in text
    assert "> **AI CLI Implementation Acceptance:** Accepted" in text
    assert "> **Formal v1.1 Acceptance:** Not Accepted" in text

    assert "v1.1.6.11 Full Regression / AI CLI Implementation Acceptance --- Accepted" in text
    assert "AI CLI Implementation Acceptance --- Accepted" in text
    assert "Formal v1.1 Acceptance --- Not Accepted" in text


def test_all_prior_ai_cli_slices_are_accepted() -> None:
    text = _read(IMPLEMENTATION)
    required = (
        "v1.1.6.1 Implementation Baseline --- Accepted",
        "v1.1.6.2 Shared Request / Local-response Infrastructure --- Accepted",
        "v1.1.6.3 course handler --- Accepted",
        "v1.1.6.4 review handler --- Accepted",
        "v1.1.6.5 document handler --- Accepted",
        "v1.1.6.6 Template Handler --- Accepted",
        "v1.1.6.7 Experimental Provider Opt-in Boundary --- Accepted",
        "v1.1.6.8 Provider Handler Wiring --- Accepted",
        "v1.1.6.9 Production Parser Registration --- Accepted",
        "v1.1.6.10 EN / zh-TW User Manual Parity --- Accepted",
    )
    for state in required:
        assert state in text


@pytest.mark.parametrize("path", (EN_CLI, ZH_TW_CLI))
def test_bilingual_manuals_preserve_exact_ai_command_inventory(path: Path) -> None:
    text = _read(path)
    for command in EXPECTED_COMMANDS:
        assert f"opl ai {command}" in text


@pytest.mark.parametrize("path", (EN_CLI, ZH_TW_CLI))
def test_bilingual_manuals_preserve_provider_and_failure_boundaries(path: Path) -> None:
    text = _read(path).lower()
    for term in (
        "stable",
        "local-response",
        "experimental",
        "fail-closed",
        "client factory",
        "exit code 2",
        "stderr",
        "non-mutating",
        "automatic sdk import",
        "automatic credential lookup",
        "implicit provider selection",
        "network fallback",
    ):
        assert term in text


def test_production_ai_parser_exposes_exact_four_commands(
    capsys: pytest.CaptureFixture[str],
) -> None:
    for command in EXPECTED_COMMANDS:
        with pytest.raises(SystemExit) as exc_info:
            main(("ai", command, "--help"))
        assert exc_info.value.code == 0
        captured = capsys.readouterr()
        assert captured.err == ""


def test_acceptance_record_declares_completed_terminal_closure_gates() -> None:
    text = _read(ACCEPTANCE)

    for gate in (
        "Acceptance PR #212 --- Merged",
        "Acceptance PR required CI --- Passed",
        "main synchronization after acceptance merge --- Completed",
        "Post-merge consistency verification --- Passed",
        "Terminal documentation alignment --- Completed",
        "AI CLI Implementation Acceptance --- Accepted",
        "Formal v1.1 Acceptance --- Not Accepted",
    ):
        assert gate in text


def test_ai_acceptance_history_remains_closed_and_roadmap_records_terminal_v1_1() -> None:
    acceptance = _read(ACCEPTANCE)
    roadmap = _read(ROADMAP)

    assert "Formal v1.1 Acceptance --- Not Accepted" in acceptance
    assert "Formal v1.1 Acceptance --- Accepted" in roadmap
    assert "v1.1 --- Terminally Accepted" in roadmap
