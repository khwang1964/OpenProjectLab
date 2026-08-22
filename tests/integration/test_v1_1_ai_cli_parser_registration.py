"""Verify v1.1.6.9 AI CLI production parser registration."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from generator.cli.ai import (
    _handle_ai_course,
    _handle_ai_document,
    _handle_ai_review,
    _handle_ai_template,
)
from generator.cli.main import build_parser

EXPECTED = {
    "course": _handle_ai_course,
    "review": _handle_ai_review,
    "document": _handle_ai_document,
    "template": _handle_ai_template,
}


def _ai_parser() -> argparse.ArgumentParser:
    parser = build_parser()
    return parser._subparsers._group_actions[0].choices["ai"]


def test_ai_is_registered_with_exact_command_inventory() -> None:
    choices = _ai_parser()._subparsers._group_actions[0].choices
    assert tuple(choices) == tuple(EXPECTED)


@pytest.mark.parametrize(("command", "handler"), EXPECTED.items())
def test_each_command_registers_request_local_response_and_handler(
    command: str, handler: object
) -> None:
    args = build_parser().parse_args(
        [
            "ai",
            command,
            "--request",
            "request.json",
            "--response",
            "response.json",
            "--json",
        ]
    )
    assert args.ai_command == command
    assert args.request == Path("request.json")
    assert args.response == Path("response.json")
    assert args.provider is None
    assert args.json is True
    assert args.handler is handler


@pytest.mark.parametrize("command", EXPECTED)
def test_each_command_registers_explicit_provider_source(command: str) -> None:
    args = build_parser().parse_args(
        ["ai", command, "--request", "request.json", "--provider", "openai"]
    )
    assert args.response is None
    assert args.provider == "openai"


@pytest.mark.parametrize("command", EXPECTED)
@pytest.mark.parametrize(
    "source",
    [[], ["--response", "response.json", "--provider", "openai"]],
)
def test_each_command_requires_exactly_one_source(command: str, source: list[str]) -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(["ai", command, "--request", "request.json", *source])
    assert exc_info.value.code == 2


def test_ai_requires_one_subcommand() -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(["ai"])
    assert exc_info.value.code == 2


def test_registration_does_not_import_sdk_or_read_environment() -> None:
    root = Path(__file__).parents[2]
    production = "\n".join(
        (root / path).read_text(encoding="utf-8")
        for path in ("generator/cli/ai.py", "generator/cli/ai_provider.py")
    )
    forbidden = (
        "import openai",
        "from openai",
        "OPENAI_API_KEY",
        "os.environ",
        "FakeAIProvider",
    )
    for statement in forbidden:
        assert statement not in production
