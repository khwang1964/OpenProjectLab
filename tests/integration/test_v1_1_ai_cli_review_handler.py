"""Verify the unregistered v1.1 AI CLI review handler."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from generator.ai.errors import AIResponseValidationError
from generator.cli.ai import _handle_ai_review
from generator.cli.main import build_parser


def _write(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def _args(tmp_path: Path, *, as_json: bool) -> argparse.Namespace:
    request = _write(
        tmp_path / "request.json",
        {
            "schema_version": 1,
            "instructions": "Review the supplied course.",
            "context": {"course_id": "modern-java"},
            "response_contract": "courseware.review.v1",
        },
    )
    response = _write(
        tmp_path / "response.json",
        {
            "findings": [
                {
                    "category": "structure",
                    "severity": "warning",
                    "message": "Missing prerequisites.",
                    "recommendation": "Add a prerequisites section.",
                },
                {
                    "category": "style",
                    "severity": "info",
                    "message": "Examples are concise.",
                    "recommendation": "Keep the current style.",
                },
            ]
        },
    )
    return argparse.Namespace(request=request, response=response, json=as_json)


def test_review_handler_emits_deterministic_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _handle_ai_review(_args(tmp_path, as_json=True)) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    document = json.loads(captured.out)
    assert document["schema_version"] == 1
    assert document["command"] == "review"
    assert document["source"] == "local-response"
    assert [finding["severity"] for finding in document["result"]["findings"]] == [
        "warning",
        "info",
    ]


def test_review_handler_emits_ordered_human_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _handle_ai_review(_args(tmp_path, as_json=False)) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.splitlines() == [
        "檢閱發現：2",
        "  1. [warning] structure",
        "     訊息：Missing prerequisites.",
        "     建議：Add a prerequisites section.",
        "  2. [info] style",
        "     訊息：Examples are concise.",
        "     建議：Keep the current style.",
    ]


def test_review_handler_fails_before_success_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    args = _args(tmp_path, as_json=True)
    args.response.write_text('{"findings":[{"severity":"critical"}]}', encoding="utf-8")
    with pytest.raises(AIResponseValidationError):
        _handle_ai_review(args)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_review_handler_remains_unregistered() -> None:
    parser = build_parser()
    choices = next(
        action.choices
        for action in parser._actions
        if isinstance(getattr(action, "choices", None), dict) and "list" in action.choices
    )
    assert "ai" not in choices
