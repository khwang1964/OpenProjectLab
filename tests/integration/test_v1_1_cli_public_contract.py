"""Govern the v1.1 CLI public-contract design before implementation."""

from __future__ import annotations

from pathlib import Path

from generator.cli.main import build_parser

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs" / "releases" / "v1.1-cli-public-contract.md"
V1_TEST = ROOT / "tests" / "integration" / "test_v1_cli_public_contract.py"

EXPECTED_V1_COMMANDS = frozenset(
    {
        "assignment",
        "bootstrap",
        "course",
        "lab",
        "list",
        "quiz",
        "slides",
        "upgrade",
        "website",
        "week",
    }
)
IMPLEMENTED_V1_1_COMMANDS = frozenset({"ai", "marketplace"})
RESERVED_V1_1_COMMANDS = frozenset()


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(text: str) -> str:
    """Collapse Markdown wrapping so contract checks remain semantic."""
    return " ".join(text.split())


def _command_choices() -> frozenset[str]:
    parser = build_parser()

    for action in parser._actions:
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict) and EXPECTED_V1_COMMANDS.intersection(choices):
            return frozenset(choices)

    raise AssertionError("CLI subcommand registry was not found")


def test_v1_1_cli_design_is_formally_accepted() -> None:
    design = _read(DESIGN)

    assert "# OpenProjectLab v1.1 CLI Public Contract Design" in design
    assert "**Status:** Accepted" in design
    assert "v1.1.2 --- CLI Public Contract Design" in design
    assert "**Marketplace CLI:** Not Started" in design
    assert "**AI CLI:** Not Started" in design
    assert "**Formal v1.1 CLI Public Contract Acceptance:** Accepted" in design
    assert "**Formal v1.1 Acceptance:** Not Accepted" in design


def test_v1_1_design_preserves_the_exact_reviewed_v1_command_inventory() -> None:
    design = _read(DESIGN)

    assert _command_choices() == EXPECTED_V1_COMMANDS | IMPLEMENTED_V1_1_COMMANDS
    assert V1_TEST.is_file()
    for command in EXPECTED_V1_COMMANDS:
        assert f"\n{command}\n" in design


def test_v1_1_registration_follows_the_reviewed_delivery_sequence() -> None:
    design = _read(DESIGN)
    production_commands = _command_choices()

    assert RESERVED_V1_1_COMMANDS.isdisjoint(production_commands)
    assert IMPLEMENTED_V1_1_COMMANDS.issubset(production_commands)
    assert "opl marketplace ..." in design
    assert "opl ai ..." in design
    assert "Production registration is prohibited during v1.1.2" in design
    assert "v1.1.3 --- Marketplace CLI Contract" in design
    assert "v1.1.5 --- AI CLI Contract" in design


def test_v1_1_design_keeps_cli_evolution_additive_and_deprecation_governed() -> None:
    design = _read(DESIGN)

    assert "must not remove, rename, silently" in design
    assert "make an existing valid v1 command line invalid" in design
    assert "`opl --list`" in design
    assert "`--dry-run`, `--force`, and `--no-manifest`" in design
    assert "compatibility and deprecation policy" in design


def test_v1_1_design_does_not_overclaim_exit_or_json_contracts() -> None:
    design = _read(DESIGN)
    prose = _normalized(design)

    assert "| `0` | Successful reviewed operation | Stable |" in design
    assert "| `2` | argparse usage failure" in design
    assert "No finer taxonomy is claimed" in prose
    assert "does not claim a production `--json` option" in prose
    assert "Exact human-readable error text is not Stable" in prose


def test_v1_1_design_defines_stream_and_failure_before_side_effect_rules() -> None:
    design = _read(DESIGN)
    prose = _normalized(design)

    assert "successful human-readable results are written to stdout" in prose
    assert "diagnostics and handled operational errors are written to stderr" in prose
    assert "before irreversible side effects" in prose
    assert "must not leave partial Marketplace installation" in prose
    assert "without production filesystem mutation" in prose


def test_v1_1_marketplace_boundary_remains_local_and_non_activating() -> None:
    design = _read(DESIGN)

    for required in (
        "exact-coordinate lookup",
        "SHA-256 integrity verification",
        "deterministic installation results",
        "remote Marketplace or Community Repository service",
        "automatic Plugin or Generator activation",
        "Marketplace-driven execution",
    ):
        assert required in design


def test_v1_1_ai_boundary_remains_provider_independent_and_offline_testable() -> None:
    design = _read(DESIGN)
    prose = _normalized(design)

    assert "provider-independent request" in prose
    assert "credential-free" in prose
    assert "network-independent" in prose
    assert "fake-provider boundary" in prose
    assert "Live-provider use remains Experimental and opt-in" in prose
    assert "streaming, and tool calling must not leak" in prose


def test_v1_1_design_requires_bilingual_and_artifact_backed_acceptance() -> None:
    design = _read(DESIGN)

    assert "English and Traditional Chinese (Taiwan) functional documentation parity" in design
    assert "representative installed-wheel behavior" in design
    assert "deterministic core CI without network or credentials" in design
    assert "Test counts, coverage, PR numbers, commit identities, and CI outcomes" in design
    assert "only after the corresponding evidence exists" in design
