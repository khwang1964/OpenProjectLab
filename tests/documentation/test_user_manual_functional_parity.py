"""Functional parity tests for the bilingual v1.0 User Manual."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from generator.cli.main import build_parser
from generator.generators.assignment_generator import AssignmentGenerator
from generator.generators.bootstrap_generator import BootstrapGenerator
from generator.generators.course_generator import CourseGenerator
from generator.generators.lab_generator import LabGenerator
from generator.generators.quiz_generator import QuizGenerator
from generator.generators.slides_generator import SlidesGenerator
from generator.generators.website_generator import WebsiteGenerator
from generator.generators.week_generator import WeekGenerator

REPO_ROOT = Path(__file__).resolve().parents[2]
USER_GUIDE_ROOT = REPO_ROOT / "docs" / "user-guide"

EN_ROOT = USER_GUIDE_ROOT / "en"
ZH_TW_ROOT = USER_GUIDE_ROOT / "zh-TW"

MAJOR_CLI_COMMANDS = frozenset(
    {
        "list",
        "bootstrap",
        "course",
        "week",
        "lab",
        "assignment",
        "quiz",
        "slides",
        "website",
        "upgrade",
    }
)

GENERATOR_IDENTITIES = frozenset(
    {
        "assignment",
        "bootstrap",
        "course",
        "lab",
        "quiz",
        "slides",
        "website",
        "week",
    }
)

GLOBAL_OPTIONS = frozenset(
    {
        "--config",
        "--template-root",
        "--output-root",
    }
)

SHARED_WRITE_OPTIONS = frozenset(
    {
        "--dry-run",
        "--force",
        "--no-manifest",
    }
)

GENERATOR_CLASSES = (
    AssignmentGenerator,
    BootstrapGenerator,
    CourseGenerator,
    LabGenerator,
    QuizGenerator,
    SlidesGenerator,
    WebsiteGenerator,
    WeekGenerator,
)


def _read_manual(language_root: Path, chapter: str) -> str:
    """Read one required User Manual chapter as UTF-8 text."""
    path = language_root / chapter
    if not path.is_file():
        pytest.fail(f"Missing required User Manual chapter: {path.relative_to(REPO_ROOT)}")
    return path.read_text(encoding="utf-8")


def _subparser_choices(
    parser: argparse.ArgumentParser,
) -> dict[str, argparse.ArgumentParser]:
    """Return the production CLI subparser mapping."""
    for action in parser._actions:
        choices = getattr(action, "choices", None)
        if action.dest == "command" and isinstance(choices, dict):
            return choices
    pytest.fail("Production CLI parser does not expose the expected command subparsers")


def _public_global_options(parser: argparse.ArgumentParser) -> frozenset[str]:
    """Return documented global long options, excluding help and legacy aliases."""
    options = {
        option
        for action in parser._actions
        for option in action.option_strings
        if option.startswith("--")
    }
    return frozenset(options - {"--help", "--list"})


def _long_options(parser: argparse.ArgumentParser) -> frozenset[str]:
    """Return all long options exposed by one command parser."""
    return frozenset(
        option
        for action in parser._actions
        for option in action.option_strings
        if option.startswith("--") and option != "--help"
    )


def _assert_terms_present(
    text: str,
    terms: frozenset[str],
    *,
    language: str,
    chapter: str,
    contract_name: str,
) -> None:
    """Assert that canonical public identifiers appear in a manual chapter."""
    missing = sorted(term for term in terms if term not in text)
    assert missing == [], f"{language} {chapter} is missing {contract_name}: {missing}"


def test_production_cli_major_command_contract_matches_v1_manual_contract() -> None:
    """The documented major command set must equal the production CLI surface."""
    parser = build_parser()
    actual_commands = frozenset(_subparser_choices(parser))

    assert actual_commands == MAJOR_CLI_COMMANDS


@pytest.mark.parametrize(
    ("language", "language_root"),
    (
        ("EN", EN_ROOT),
        ("zh-TW", ZH_TW_ROOT),
    ),
)
def test_bilingual_cli_manual_documents_all_major_commands(
    language: str,
    language_root: Path,
) -> None:
    """Both CLI manuals must document every major production command."""
    text = _read_manual(language_root, "cli.md")

    _assert_terms_present(
        text,
        MAJOR_CLI_COMMANDS,
        language=language,
        chapter="cli.md",
        contract_name="major CLI commands",
    )


def test_production_generator_identity_contract_matches_v1_manual_contract() -> None:
    """The frozen Generator identity set must match production classes."""
    actual_identities = frozenset(generator.name for generator in GENERATOR_CLASSES)

    assert actual_identities == GENERATOR_IDENTITIES


@pytest.mark.parametrize(
    ("language", "language_root"),
    (
        ("EN", EN_ROOT),
        ("zh-TW", ZH_TW_ROOT),
    ),
)
def test_bilingual_generator_manual_documents_all_generator_identities(
    language: str,
    language_root: Path,
) -> None:
    """Both Generator manuals must document the same built-in identities."""
    text = _read_manual(language_root, "generators.md")

    _assert_terms_present(
        text,
        GENERATOR_IDENTITIES,
        language=language,
        chapter="generators.md",
        contract_name="Generator identities",
    )


def test_production_global_option_contract_matches_v1_manual_contract() -> None:
    """Public global CLI options must remain aligned with the manual contract."""
    parser = build_parser()

    assert _public_global_options(parser) == GLOBAL_OPTIONS


@pytest.mark.parametrize(
    ("language", "language_root"),
    (
        ("EN", EN_ROOT),
        ("zh-TW", ZH_TW_ROOT),
    ),
)
def test_bilingual_configuration_and_cli_manuals_document_global_options(
    language: str,
    language_root: Path,
) -> None:
    """Both languages must expose the same global path/configuration options."""
    configuration_text = _read_manual(language_root, "configuration.md")
    cli_text = _read_manual(language_root, "cli.md")

    _assert_terms_present(
        configuration_text,
        GLOBAL_OPTIONS,
        language=language,
        chapter="configuration.md",
        contract_name="global CLI options",
    )
    _assert_terms_present(
        cli_text,
        GLOBAL_OPTIONS,
        language=language,
        chapter="cli.md",
        contract_name="global CLI options",
    )


@pytest.mark.parametrize("command", sorted(GENERATOR_IDENTITIES))
def test_all_generation_commands_expose_shared_write_options(command: str) -> None:
    """Every built-in generation command must expose the shared write controls."""
    parser = build_parser()
    command_parser = _subparser_choices(parser)[command]

    assert SHARED_WRITE_OPTIONS <= _long_options(command_parser)


@pytest.mark.parametrize(
    ("language", "language_root"),
    (
        ("EN", EN_ROOT),
        ("zh-TW", ZH_TW_ROOT),
    ),
)
def test_bilingual_cli_and_generator_manuals_document_shared_write_options(
    language: str,
    language_root: Path,
) -> None:
    """Both languages must document dry-run, overwrite, and manifest controls."""
    cli_text = _read_manual(language_root, "cli.md")
    generator_text = _read_manual(language_root, "generators.md")

    _assert_terms_present(
        cli_text,
        SHARED_WRITE_OPTIONS,
        language=language,
        chapter="cli.md",
        contract_name="shared write options",
    )
    _assert_terms_present(
        generator_text,
        SHARED_WRITE_OPTIONS,
        language=language,
        chapter="generators.md",
        contract_name="shared write options",
    )


def test_en_and_zh_tw_cli_contract_terms_are_functionally_symmetric() -> None:
    """Canonical CLI contract identifiers must be present in both languages."""
    english = _read_manual(EN_ROOT, "cli.md")
    zh_tw = _read_manual(ZH_TW_ROOT, "cli.md")

    contract_terms = MAJOR_CLI_COMMANDS | GLOBAL_OPTIONS | SHARED_WRITE_OPTIONS

    english_terms = frozenset(term for term in contract_terms if term in english)
    zh_tw_terms = frozenset(term for term in contract_terms if term in zh_tw)

    assert english_terms == contract_terms
    assert zh_tw_terms == contract_terms
    assert english_terms == zh_tw_terms


def test_en_and_zh_tw_generator_contract_terms_are_functionally_symmetric() -> None:
    """Canonical Generator identifiers must be present in both languages."""
    english = _read_manual(EN_ROOT, "generators.md")
    zh_tw = _read_manual(ZH_TW_ROOT, "generators.md")

    contract_terms = GENERATOR_IDENTITIES | SHARED_WRITE_OPTIONS

    english_terms = frozenset(term for term in contract_terms if term in english)
    zh_tw_terms = frozenset(term for term in contract_terms if term in zh_tw)

    assert english_terms == contract_terms
    assert zh_tw_terms == contract_terms
    assert english_terms == zh_tw_terms
