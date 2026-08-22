"""Freeze the OpenProjectLab v1 command-line public contract."""

from __future__ import annotations

from collections.abc import Sequence

import pytest

from generator.cli.main import build_parser, main

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
EXPECTED_ADDITIVE_COMMANDS = frozenset({"ai", "marketplace"})

VALID_V1_COMMAND_LINES: tuple[tuple[str, ...], ...] = (
    ("list",),
    ("bootstrap", "demo", "--name", "Demo"),
    ("course", "demo", "--name", "Demo"),
    ("week", "demo", "--week", "1", "--title", "Week 01"),
    (
        "lab",
        "demo",
        "--week",
        "1",
        "--lab-id",
        "lab-01",
        "--title",
        "Lab 01",
    ),
    (
        "assignment",
        "demo",
        "--week",
        "1",
        "--assignment-id",
        "assignment-01",
        "--title",
        "Assignment 01",
        "--content-file",
        "assignment.json",
    ),
    (
        "quiz",
        "demo",
        "--week",
        "1",
        "--quiz-id",
        "quiz-01",
        "--title",
        "Quiz 01",
        "--questions-file",
        "questions.json",
    ),
    (
        "slides",
        "demo",
        "--title",
        "Slides",
        "--slides-file",
        "slides.json",
    ),
    (
        "website",
        "demo",
        "--title",
        "Website",
        "--pages-file",
        "pages.json",
    ),
    ("upgrade", "update.zip"),
)

WRITE_COMMAND_LINES: tuple[tuple[str, ...], ...] = (
    ("bootstrap", "demo", "--name", "Demo"),
    ("course", "demo", "--name", "Demo"),
    ("week", "demo", "--week", "1", "--title", "Week 01"),
    (
        "lab",
        "demo",
        "--week",
        "1",
        "--lab-id",
        "lab-01",
        "--title",
        "Lab 01",
    ),
    (
        "assignment",
        "demo",
        "--week",
        "1",
        "--assignment-id",
        "assignment-01",
        "--title",
        "Assignment 01",
        "--content-file",
        "assignment.json",
    ),
    (
        "quiz",
        "demo",
        "--week",
        "1",
        "--quiz-id",
        "quiz-01",
        "--title",
        "Quiz 01",
        "--questions-file",
        "questions.json",
    ),
    (
        "slides",
        "demo",
        "--title",
        "Slides",
        "--slides-file",
        "slides.json",
    ),
    (
        "website",
        "demo",
        "--title",
        "Website",
        "--pages-file",
        "pages.json",
    ),
)


def _command_choices() -> frozenset[str]:
    """Return command names declared by the production parser."""
    parser = build_parser()

    for action in parser._actions:
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict) and choices:
            if EXPECTED_V1_COMMANDS.intersection(choices):
                return frozenset(choices)

    raise AssertionError("CLI subcommand registry was not found")


def _parse(argv: Sequence[str]):
    """Parse one reviewed v1 command line without executing its handler."""
    return build_parser().parse_args(argv)


def test_v1_cli_command_inventory_is_preserved_with_reviewed_additions() -> None:
    """Preserve every v1 command while allowing reviewed additive families."""
    assert _command_choices() == EXPECTED_V1_COMMANDS | EXPECTED_ADDITIVE_COMMANDS


@pytest.mark.parametrize("argv", VALID_V1_COMMAND_LINES)
def test_v1_cli_accepts_reviewed_command_shapes(
    argv: tuple[str, ...],
) -> None:
    """Keep each reviewed v1 command syntax parseable."""
    args = _parse(argv)

    assert args.command == argv[0]


@pytest.mark.parametrize("argv", WRITE_COMMAND_LINES)
def test_v1_generation_commands_share_write_options(
    argv: tuple[str, ...],
) -> None:
    """Keep dry-run, force, and manifest controls on generation commands."""
    args = _parse((*argv, "--dry-run", "--force", "--no-manifest"))

    assert args.dry_run is True
    assert args.force is True
    assert args.no_manifest is True


def test_v1_list_command_and_legacy_list_are_compatible(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Keep the canonical list command and compatibility --list path aligned."""
    assert main(["list"]) == 0
    canonical = capsys.readouterr()

    assert main(["--list"]) == 0
    legacy = capsys.readouterr()

    assert legacy.out == canonical.out
    assert legacy.err == canonical.err == ""


def test_v1_list_output_contains_reviewed_builtin_generators(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Expose every reviewed built-in Generator through the list command."""
    assert main(["list"]) == 0
    output = capsys.readouterr().out

    for name in (
        "assignment",
        "bootstrap",
        "course",
        "lab",
        "quiz",
        "slides",
        "website",
        "week",
    ):
        assert name in output


def test_v1_legacy_list_cannot_be_combined_with_subcommand() -> None:
    """Reject ambiguous legacy --list plus subcommand invocation."""
    with pytest.raises(SystemExit) as exc_info:
        main(["--list", "list"])

    assert exc_info.value.code == 2


def test_v1_cli_requires_a_command_without_legacy_list() -> None:
    """Reject an invocation that provides neither a command nor --list."""
    with pytest.raises(SystemExit) as exc_info:
        main([])

    assert exc_info.value.code == 2


def test_v1_cli_rejects_unknown_command() -> None:
    """Reject command names outside the reviewed v1 command surface."""
    with pytest.raises(SystemExit) as exc_info:
        _parse(("unknown-v1-command",))

    assert exc_info.value.code == 2


@pytest.mark.parametrize(
    "argv",
    [
        (
            "assignment",
            "demo",
            "--week",
            "1",
            "--assignment-id",
            "assignment-01",
            "--title",
            "Assignment 01",
        ),
        (
            "quiz",
            "demo",
            "--week",
            "1",
            "--quiz-id",
            "quiz-01",
            "--title",
            "Quiz 01",
        ),
        ("slides", "demo", "--title", "Slides"),
        ("website", "demo", "--title", "Website"),
    ],
)
def test_v1_structured_input_commands_require_input_files(
    argv: tuple[str, ...],
) -> None:
    """Require the established structured JSON input option for each command."""
    with pytest.raises(SystemExit) as exc_info:
        _parse(argv)

    assert exc_info.value.code == 2


@pytest.mark.parametrize(
    "argv",
    [
        ("week", "demo", "--week", "0", "--title", "Week"),
        ("week", "demo", "--week", "-1", "--title", "Week"),
        ("week", "demo", "--week", "not-an-int", "--title", "Week"),
    ],
)
def test_v1_positive_integer_cli_validation_returns_parse_error(
    argv: tuple[str, ...],
) -> None:
    """Keep positive-integer CLI validation at argparse exit code 2."""
    with pytest.raises(SystemExit) as exc_info:
        _parse(argv)

    assert exc_info.value.code == 2
