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


def test_acceptance_record_exists_and_is_not_preaccepted() -> None:
    text = _read(ACCEPTANCE)
    assert "v1.1.6.11 --- Full Regression / AI CLI Implementation Acceptance" in text
    assert "AI CLI Implementation Acceptance:** Not Accepted" in text
    assert "Formal v1.1 Acceptance:** Not Accepted" in text


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


def test_acceptance_record_declares_fail_closed_closure_gates() -> None:
    text = _read(ACCEPTANCE)
    for gate in (
        "Acceptance PR required CI --- Pending",
        "Acceptance squash merge --- Pending",
        "main synchronization after acceptance merge --- Pending",
        "Post-merge consistency verification --- Pending",
        "Terminal documentation alignment --- Pending",
        "AI CLI Implementation Acceptance --- Not Accepted",
        "Formal v1.1 Acceptance --- Not Accepted",
    ):
        assert gate in text


def test_roadmap_keeps_formal_v1_1_unaccepted() -> None:
    text = _read(ROADMAP)
    assert "Formal v1.1 Acceptance --- Not Accepted" in text
    assert "Formal v1.1 Acceptance --- Accepted" not in text
