"""Verify the unregistered v1.1 AI CLI template handler."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pytest

from generator.ai.errors import AIResponseValidationError
from generator.cli.ai import _handle_ai_template
from generator.cli.main import build_parser


def _write(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def _args(tmp_path: Path, *, as_json: bool) -> argparse.Namespace:
    request = _write(
        tmp_path / "request.json",
        {
            "schema_version": 1,
            "instructions": "Complete the template.",
            "context": {"course_name": "Modern Java"},
            "response_contract": "template.completion.v1",
        },
    )
    response = _write(
        tmp_path / "response.json",
        {
            "template_name": "course-readme",
            "content": "# {{ course_name }}",
            "context_keys": ["course_name", "language"],
        },
    )
    return argparse.Namespace(request=request, response=response, json=as_json)


def test_template_handler_emits_deterministic_json(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _handle_ai_template(_args(tmp_path, as_json=True)) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    assert json.loads(captured.out) == {
        "schema_version": 1,
        "command": "template",
        "source": "local-response",
        "result": {
            "template_name": "course-readme",
            "content": "# {{ course_name }}",
            "context_keys": ["course_name", "language"],
        },
    }


def test_template_handler_emits_ordered_human_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert _handle_ai_template(_args(tmp_path, as_json=False)) == 0
    captured = capsys.readouterr()
    assert captured.err == ""
    assert captured.out.splitlines() == [
        "模板：course-readme",
        "內容：",
        "# {{ course_name }}",
        "Context keys：",
        "  - course_name",
        "  - language",
    ]


def test_template_handler_fails_before_success_output(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    args = _args(tmp_path, as_json=True)
    args.response.write_text(
        '{"template_name":"x","content":"y","context_keys":[""]}',
        encoding="utf-8",
    )
    with pytest.raises(AIResponseValidationError):
        _handle_ai_template(args)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_template_handler_is_registered_after_slice_acceptance() -> None:
    parser = build_parser()
    choices = next(
        action.choices
        for action in parser._actions
        if isinstance(getattr(action, "choices", None), dict) and "list" in action.choices
    )
    assert "ai" in choices


def test_template_handler_terminal_alignment_records_post_merge_evidence() -> None:
    root = Path(__file__).parents[2]
    expected = (
        "v1.1.6.6 Template Handler --- Accepted",
        "Implementation PR #202 --- Merged",
        "1ecf3c0b843385c2deee3e849e8f1b9fbd6463bf",
        "Post-merge focused verification --- 123 passed",
        "v1.1.6 AI CLI Implementation --- In Progress",
        "Experimental Provider Opt-in Boundary --- Not Started",
        "AI CLI Production Registration --- Not Started",
        "Formal v1.1 Acceptance --- Not Accepted",
        "Next --- v1.1.6.7 Experimental Provider Opt-in Boundary",
    )
    trackers = (
        root / "CHANGELOG.md",
        root / "docs" / "HISTORY.md",
        root / "docs" / "roadmap.md",
        root / "docs" / "releases" / "v1.1-ai-cli-implementation.md",
    )

    for tracker in trackers:
        prose = tracker.read_text(encoding="utf-8")
        for statement in expected:
            assert statement in prose
