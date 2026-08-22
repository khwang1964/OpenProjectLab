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


def test_review_handler_is_registered_after_slice_acceptance() -> None:
    parser = build_parser()
    choices = next(
        action.choices
        for action in parser._actions
        if isinstance(getattr(action, "choices", None), dict) and "list" in action.choices
    )
    assert "ai" in choices


_REVIEW_TERMINAL_ROOT = Path(__file__).resolve().parents[2]
_REVIEW_TERMINAL_SOURCES = (
    _REVIEW_TERMINAL_ROOT / "CHANGELOG.md",
    _REVIEW_TERMINAL_ROOT / "docs" / "HISTORY.md",
    _REVIEW_TERMINAL_ROOT / "docs" / "roadmap.md",
    _REVIEW_TERMINAL_ROOT / "docs" / "releases" / "v1.1-ai-cli-implementation.md",
)


def test_review_handler_terminal_alignment_is_closed() -> None:
    for source in _REVIEW_TERMINAL_SOURCES:
        prose = " ".join(source.read_text(encoding="utf-8").split()).lower()
        assert "v1.1.6.4 review handler --- accepted" in prose
        assert "implementation pr #198 --- merged" in prose
        assert "b78d68b86f7829c48c4bdc696d09a721bdcb35c5" in prose
        assert "post-merge verification --- 113 passed" in prose
        assert "v1.1.6 ai cli implementation --- in progress" in prose
        assert "ai cli document handler --- not started" in prose
        assert "ai cli production registration --- not started" in prose
        assert "formal v1.1 acceptance --- not accepted" in prose
        assert "next --- v1.1.6.5 document handler" in prose
