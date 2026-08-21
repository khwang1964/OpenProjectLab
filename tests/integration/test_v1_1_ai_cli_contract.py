"""Govern the v1.1 AI CLI contract before implementation."""

from __future__ import annotations

from pathlib import Path

from generator.cli.main import build_parser

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs" / "releases" / "v1.1-ai-cli-contract.md"
ROADMAP = ROOT / "docs" / "roadmap.md"
HISTORY = ROOT / "docs" / "HISTORY.md"
CHANGELOG = ROOT / "CHANGELOG.md"

EXPECTED_COMMANDS = ("course", "review", "document", "template")


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


def test_contract_is_proposed_without_production_registration() -> None:
    contract = _read(CONTRACT)

    assert "# OpenProjectLab v1.1 AI CLI Contract" in contract
    assert "**Status:** Proposed --- Contract In Progress" in contract
    assert "v1.1.5 --- AI CLI Contract" in contract
    assert "**AI CLI Production Registration:** Not Started" in contract
    assert "**AI CLI Implementation:** Not Started" in contract
    assert "**Formal v1.1 Acceptance:** Not Accepted" in contract
    assert "ai" not in _top_level_commands()


def test_contract_defines_exact_proposed_command_inventory() -> None:
    contract = _read(CONTRACT)

    for command in EXPECTED_COMMANDS:
        assert f"opl ai {command} --request FILE" in contract
    for excluded in ("chat", "providers", "refactor", "apply", "agent"):
        assert f"`opl ai {excluded}`" in contract
    assert "No aliases, short options" in contract


def test_each_command_requires_exactly_one_execution_source() -> None:
    prose = _normalized(CONTRACT)

    assert "(--response FILE | --provider NAME)" in prose
    assert "mutually exclusive, and exactly one is required" in prose
    assert "There is no implicit provider" in prose
    assert "network fallback" in prose


def test_request_schema_is_explicit_and_secret_free() -> None:
    contract = _read(CONTRACT)
    prose = _normalized(CONTRACT)

    assert '"schema_version": 1' in contract
    assert '"instructions"' in contract
    assert '"context"' in contract
    assert '"response_contract"' in contract
    assert "unknown root fields are rejected" in prose
    assert "secrets must not be embedded" in prose


def test_local_response_source_is_stable_deterministic_core() -> None:
    prose = _normalized(CONTRACT)

    assert "`--response FILE` is the Stable core execution source" in prose
    assert "performs no network access" in prose
    assert "reads no credentials" in prose
    assert "suitable for normal tests and required CI" in prose
    assert "does not bypass structured response or domain validation" in prose


def test_live_provider_is_experimental_and_credential_isolated() -> None:
    prose = _normalized(CONTRACT)

    assert "`--provider NAME` is Experimental and opt-in" in prose
    assert "does not stabilize" in prose
    assert "credential storage or acquisition" in prose
    assert "provider SDK request/response types" in prose
    assert "There is no fallback from a failed live provider" in prose


def test_contract_reuses_existing_application_services() -> None:
    contract = _read(CONTRACT)

    for service in (
        "AICourseGenerationService",
        "AIReviewService",
        "AIDocumentationService",
        "AITemplateCompletionService",
    ):
        assert service in contract
    assert "FakeAIProvider" in contract


def test_output_stream_exit_and_side_effect_boundaries_are_explicit() -> None:
    prose = _normalized(CONTRACT)

    assert "Successful human-readable output goes to stdout" in prose
    assert "Diagnostics go to stderr" in prose
    assert "success emits exactly one UTF-8 JSON object" in prose
    assert "| `0` | Successful validated AI CLI operation |" in prose
    assert "| `2` | Usage, file, JSON" in prose
    assert "the filesystem unchanged" in prose
    assert "no success JSON document on stdout" in prose


def test_deferred_capabilities_do_not_leak_into_v1_1_contract() -> None:
    prose = _normalized(CONTRACT)

    for boundary in (
        "chat or conversational session state",
        "AI Refactoring Assistant",
        "streaming, tool calling, agents",
        "repository mutation, Git operations",
        "credential persistence",
    ):
        assert boundary in prose


def test_trackers_start_ai_contract_without_claiming_implementation() -> None:
    for tracker in (ROADMAP, HISTORY, CHANGELOG):
        prose = _normalized(tracker).lower()
        assert "v1.1.5 ai cli contract" in prose
        assert "in progress" in prose
        assert "ai cli implementation" in prose
        assert "not started" in prose
        assert "formal v1.1 acceptance" in prose
        assert "not accepted" in prose
