"""Verify fail-closed provider selection and handler wiring."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from generator.cli.ai import ExperimentalProviderOptions, _handle_ai_course
from generator.cli.main import build_parser


class _Responses:
    def __init__(self, output: object) -> None:
        self.output = output
        self.calls: list[dict[str, object]] = []

    def create(self, **kwargs: object) -> object:
        self.calls.append(kwargs)
        return SimpleNamespace(
            output_text=json.dumps(self.output),
            model="gpt-test",
            id="response-1",
            status="completed",
            usage=None,
        )


class _Client:
    def __init__(self, output: object) -> None:
        self.responses = _Responses(output)


def _request(tmp_path: Path) -> Path:
    path = tmp_path / "request.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "instructions": "Generate a course.",
                "context": {"audience": "developers"},
                "response_contract": "courseware.course.v1",
            }
        ),
        encoding="utf-8",
    )
    return path


def _options(output: object) -> tuple[ExperimentalProviderOptions, _Client]:
    client = _Client(output)
    options = ExperimentalProviderOptions(
        client_factory=lambda *, api_key: client,
        api_key="secret",
        model="gpt-test",
        timeout_seconds=10.0,
    )
    return options, client


def test_course_handler_uses_explicit_provider_and_projects_source(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    options, client = _options(
        {
            "course_id": "modern-java",
            "title": "Modern Java",
            "language": "zh-TW",
            "weeks": [],
        }
    )
    args = argparse.Namespace(
        request=_request(tmp_path), response=None, provider="openai", json=True
    )

    assert _handle_ai_course(args, experimental_options=options) == 0

    assert json.loads(capsys.readouterr().out)["source"] == "provider:openai"
    assert len(client.responses.calls) == 1


@pytest.mark.parametrize(
    ("response", "provider"),
    [(None, None), (Path("response.json"), "openai")],
)
def test_handler_requires_exactly_one_source(
    tmp_path: Path, response: Path | None, provider: str | None
) -> None:
    args = argparse.Namespace(
        request=_request(tmp_path), response=response, provider=provider, json=True
    )
    with pytest.raises(ValueError, match="exactly one"):
        _handle_ai_course(args)


def test_provider_requires_explicit_injected_options(tmp_path: Path) -> None:
    args = argparse.Namespace(
        request=_request(tmp_path), response=None, provider="openai", json=True
    )
    with pytest.raises(ValueError, match="options"):
        _handle_ai_course(args)


@pytest.mark.parametrize("output", ["not an object", ["not", "an", "object"]])
def test_provider_output_fails_before_success_output(
    tmp_path: Path, output: object, capsys: pytest.CaptureFixture[str]
) -> None:
    options, _ = _options(output)
    args = argparse.Namespace(
        request=_request(tmp_path), response=None, provider="openai", json=True
    )
    with pytest.raises(ValueError):
        _handle_ai_course(args, experimental_options=options)
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_ai_parser_remains_unregistered() -> None:
    parser = build_parser()
    choices = parser._subparsers._group_actions[0].choices
    assert "ai" not in choices
