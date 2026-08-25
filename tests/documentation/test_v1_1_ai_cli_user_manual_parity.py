"""Executable EN / zh-TW AI CLI user-manual parity tests."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
EN_CLI = ROOT / "docs" / "user-guide" / "en" / "cli.md"
ZH_TW_CLI = ROOT / "docs" / "user-guide" / "zh-TW" / "cli.md"

AI_COMMANDS = (
    "course",
    "review",
    "document",
    "template",
)

AI_COMMAND_SHAPES = tuple(f"opl ai {command}" for command in AI_COMMANDS)

SHARED_PARITY_TERMS = (
    "AI CLI",
    "Stable",
    "Experimental",
    "local-response",
    "provider",
    "client factory",
    "exit code 2",
    "stderr",
    "non-mutating",
)

FORBIDDEN_CAPABILITY_TERMS = (
    "automatic SDK import",
    "automatic credential lookup",
    "implicit provider selection",
    "network fallback",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("path", (EN_CLI, ZH_TW_CLI))
def test_bilingual_cli_manuals_document_ai_cli_section(path: Path) -> None:
    text = _read(path)

    assert "AI CLI" in text


@pytest.mark.parametrize("path", (EN_CLI, ZH_TW_CLI))
def test_bilingual_cli_manuals_document_exact_ai_command_inventory(
    path: Path,
) -> None:
    text = _read(path)

    for command in AI_COMMAND_SHAPES:
        assert command in text

    documented = {command for command in AI_COMMANDS if f"opl ai {command}" in text}
    assert documented == set(AI_COMMANDS)


@pytest.mark.parametrize("path", (EN_CLI, ZH_TW_CLI))
def test_bilingual_cli_manuals_have_ai_functional_parity(path: Path) -> None:
    text = _read(path)

    for term in SHARED_PARITY_TERMS:
        assert term in text


@pytest.mark.parametrize("path", (EN_CLI, ZH_TW_CLI))
def test_bilingual_cli_manuals_document_stable_local_response_boundary(
    path: Path,
) -> None:
    text = _read(path)
    lowered = text.lower()

    assert "stable" in lowered
    assert "local-response" in lowered
    assert "deterministic" in lowered


@pytest.mark.parametrize("path", (EN_CLI, ZH_TW_CLI))
def test_bilingual_cli_manuals_document_experimental_provider_boundary(
    path: Path,
) -> None:
    text = _read(path)
    lowered = text.lower()

    assert "experimental" in lowered
    assert "provider" in lowered
    assert "explicit" in lowered
    assert "client factory" in lowered
    assert "fail-closed" in lowered or "fail closed" in lowered


@pytest.mark.parametrize("path", (EN_CLI, ZH_TW_CLI))
def test_bilingual_cli_manuals_document_failure_semantics(path: Path) -> None:
    text = _read(path)
    lowered = text.lower()

    assert "exit code 2" in lowered
    assert "stderr" in lowered
    assert "stdout" in lowered
    assert "no success" in lowered or "不輸出成功" in text or "不產生成功" in text


@pytest.mark.parametrize("path", (EN_CLI, ZH_TW_CLI))
def test_bilingual_cli_manuals_document_non_mutating_boundary(path: Path) -> None:
    text = _read(path)
    lowered = text.lower()

    assert "non-mutating" in lowered
    assert "filesystem" in lowered
    assert "repository" in lowered


@pytest.mark.parametrize("path", (EN_CLI, ZH_TW_CLI))
def test_bilingual_cli_manuals_reject_implicit_provider_capabilities(
    path: Path,
) -> None:
    text = _read(path)
    lowered = text.lower()

    for capability in FORBIDDEN_CAPABILITY_TERMS:
        assert capability.lower() in lowered

    rejection_markers = (
        "does not",
        "no ",
        "never",
        "不會",
        "不 ",
        "不得",
        "沒有",
    )

    for capability in FORBIDDEN_CAPABILITY_TERMS:
        capability_lower = capability.lower()
        lines = [line.lower() for line in text.splitlines() if capability_lower in line.lower()]
        assert lines, f"Missing documented boundary: {capability}"
        assert any(marker in line for line in lines for marker in rejection_markers), (
            f"Boundary must be explicitly rejected: {capability}"
        )


def test_en_and_zh_tw_ai_command_inventory_matches_exactly() -> None:
    documents = {
        "en": _read(EN_CLI),
        "zh-TW": _read(ZH_TW_CLI),
    }

    inventories = {
        locale: tuple(command for command in AI_COMMANDS if f"opl ai {command}" in text)
        for locale, text in documents.items()
    }

    assert inventories["en"] == AI_COMMANDS
    assert inventories["zh-TW"] == AI_COMMANDS
    assert inventories["en"] == inventories["zh-TW"]


def test_ai_cli_manual_parity_does_not_preaccept_implementation_or_v1_1() -> None:
    for path in (EN_CLI, ZH_TW_CLI):
        text = _read(path)

        assert "AI CLI Implementation Acceptance --- Accepted" not in text
        assert "Formal v1.1 Acceptance --- Accepted" not in text
