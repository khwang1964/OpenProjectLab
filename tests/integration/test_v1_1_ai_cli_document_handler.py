"""Verify the unregistered v1.1 AI CLI document handler."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from generator.ai.errors import AIResponseValidationError
from generator.cli.ai import _handle_ai_document
from generator.cli.main import build_parser


def _write(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def _args(tmp_path: Path, *, as_json: bool) -> argparse.Namespace:
    request = _write(
        tmp_path / "request.json",
        {
            "schema_version": 1,
            "instructions": "Draft documentation.",
            "context": {"topic": "streams"},
            "response_contract": "documentation.draft.v1",
        },
    )
    response = _write(
        tmp_path / "response.json",
        {
            "title": "Streams Guide",
            "format": "markdown",
            "content": "# Streams\n\nUse streams deliberately.",
        },
    )
    return argparse.Namespace(request=request, response=response, json=as_json)


def test_document_handler_emits_deterministic_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _handle_ai_document(_args(tmp_path, as_json=True)) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    assert json.loads(captured.out) == {
        "schema_version": 1,
        "command": "document",
        "source": "local-response",
        "result": {
            "title": "Streams Guide",
            "format": "markdown",
            "content": "# Streams\n\nUse streams deliberately.",
        },
    }


def test_document_handler_emits_human_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _handle_ai_document(_args(tmp_path, as_json=False)) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.splitlines() == [
        "文件：Streams Guide",
        "格式：markdown",
        "內容：",
        "# Streams",
        "",
        "Use streams deliberately.",
    ]


def test_document_handler_fails_before_success_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    args = _args(tmp_path, as_json=True)
    args.response.write_text('{"title":"Draft","format":"html","content":"x"}', encoding="utf-8")
    with pytest.raises(AIResponseValidationError):
        _handle_ai_document(args)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_document_handler_remains_unregistered() -> None:
    parser = build_parser()
    choices = next(
        action.choices
        for action in parser._actions
        if isinstance(getattr(action, "choices", None), dict) and "list" in action.choices
    )
    assert "ai" not in choices
