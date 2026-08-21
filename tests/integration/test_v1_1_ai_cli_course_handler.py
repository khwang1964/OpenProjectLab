"""Verify the unregistered v1.1 AI CLI course handler."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from generator.cli.ai import _handle_ai_course
from generator.cli.main import build_parser


def _write(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def _args(tmp_path: Path, *, as_json: bool) -> argparse.Namespace:
    request = _write(
        tmp_path / "request.json",
        {
            "schema_version": 1,
            "instructions": "Generate a course.",
            "context": {"audience": "developers"},
            "response_contract": "courseware.course.v1",
        },
    )
    response = _write(
        tmp_path / "response.json",
        {
            "course_id": "modern-java",
            "title": "Modern Java",
            "language": "zh-TW",
            "weeks": [
                {"number": 2, "title": "Streams"},
                {"number": 1, "title": "Lambdas"},
            ],
        },
    )
    return argparse.Namespace(request=request, response=response, json=as_json)


def test_course_handler_emits_deterministic_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _handle_ai_course(_args(tmp_path, as_json=True)) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    assert json.loads(captured.out) == {
        "schema_version": 1,
        "command": "course",
        "source": "local-response",
        "result": {
            "course_id": "modern-java",
            "title": "Modern Java",
            "language": "zh-TW",
            "weeks": [
                {"number": 1, "title": "Lambdas"},
                {"number": 2, "title": "Streams"},
            ],
        },
    }


def test_course_handler_emits_human_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _handle_ai_course(_args(tmp_path, as_json=False)) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.splitlines() == [
        "課程：Modern Java",
        "課程代號：modern-java",
        "語言：zh-TW",
        "週次：",
        "  1. Lambdas",
        "  2. Streams",
    ]


def test_course_handler_fails_before_success_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    args = _args(tmp_path, as_json=True)
    args.response.write_text("{}", encoding="utf-8")
    with pytest.raises(ValueError):
        _handle_ai_course(args)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_course_handler_remains_unregistered() -> None:
    parser = build_parser()
    choices = next(
        action.choices
        for action in parser._actions
        if isinstance(getattr(action, "choices", None), dict) and "list" in action.choices
    )
    assert "ai" not in choices
