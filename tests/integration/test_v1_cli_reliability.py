"""Harden the OpenProjectLab v1 CLI input and failure reliability boundary."""

from __future__ import annotations

from pathlib import Path

import pytest

from generator.cli.main import build_parser, main


@pytest.mark.parametrize(
    "argv",
    [
        ("week", "demo", "--title", "Week"),
        ("lab", "demo", "--week", "1", "--title", "Lab"),
        ("assignment", "demo", "--week", "1", "--title", "Assignment"),
        ("quiz", "demo", "--week", "1", "--title", "Quiz"),
        ("slides", "demo", "--title", "Slides"),
        ("website", "demo", "--title", "Website"),
    ],
)
def test_v1_cli_missing_required_arguments_exit_with_parse_error(
    argv: tuple[str, ...],
) -> None:
    """Keep missing required CLI inputs at argparse exit code 2."""
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(argv)

    assert exc_info.value.code == 2


@pytest.mark.parametrize(
    "value",
    ["0", "-1", "not-an-int"],
)
def test_v1_cli_invalid_positive_integer_exits_with_parse_error(
    value: str,
) -> None:
    """Keep positive-integer validation deterministic."""
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(
            (
                "week",
                "demo",
                "--week",
                value,
                "--title",
                "Week",
            )
        )

    assert exc_info.value.code == 2


def test_v1_assignment_malformed_json_returns_operational_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Convert malformed structured input into the established CLI error code."""
    content_file = tmp_path / "assignment.json"
    content_file.write_text("{invalid-json", encoding="utf-8")

    result = main(
        [
            "--output-root",
            str(tmp_path / "output"),
            "assignment",
            "demo",
            "--week",
            "1",
            "--assignment-id",
            "assignment-01",
            "--title",
            "Assignment",
            "--content-file",
            str(content_file),
        ]
    )

    captured = capsys.readouterr()
    assert result == 2
    assert captured.err
    assert not (tmp_path / "output").exists()


def test_v1_assignment_non_object_json_returns_operational_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Reject the Assignment-specific wrong structured-input shape."""
    content_file = tmp_path / "assignment.json"
    content_file.write_text("[]", encoding="utf-8")

    result = main(
        [
            "--output-root",
            str(tmp_path / "output"),
            "assignment",
            "demo",
            "--week",
            "1",
            "--assignment-id",
            "assignment-01",
            "--title",
            "Assignment",
            "--content-file",
            str(content_file),
        ]
    )

    captured = capsys.readouterr()
    assert result == 2
    assert captured.err
    assert not (tmp_path / "output").exists()


@pytest.mark.parametrize(
    ("command", "file_option", "extra"),
    [
        (
            "assignment",
            "--content-file",
            (
                "--week",
                "1",
                "--assignment-id",
                "assignment-01",
                "--title",
                "Assignment",
            ),
        ),
        (
            "quiz",
            "--questions-file",
            (
                "--week",
                "1",
                "--quiz-id",
                "quiz-01",
                "--title",
                "Quiz",
            ),
        ),
        (
            "slides",
            "--slides-file",
            ("--title", "Slides"),
        ),
        (
            "website",
            "--pages-file",
            ("--title", "Website"),
        ),
    ],
)
def test_v1_cli_missing_structured_input_file_returns_operational_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    command: str,
    file_option: str,
    extra: tuple[str, ...],
) -> None:
    """Keep missing JSON files as expected operational failures without output."""
    missing = tmp_path / "missing.json"
    argv = [
        "--output-root",
        str(tmp_path / "output"),
        command,
        "demo",
        *extra,
        file_option,
        str(missing),
    ]

    result = main(argv)

    captured = capsys.readouterr()
    assert result == 2
    assert captured.err
    assert not (tmp_path / "output").exists()


def test_v1_cli_legacy_list_and_list_command_remain_repeatable(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Keep repeated read-only listing deterministic."""
    assert main(["list"]) == 0
    first = capsys.readouterr()

    assert main(["--list"]) == 0
    second = capsys.readouterr()

    assert first.out == second.out
    assert first.err == second.err == ""
