"""Verify the unregistered v1.1 AI CLI shared infrastructure."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from generator.ai.models import AIRequest, AIResponse
from generator.ai.protocols import AIProvider
from generator.cli.ai import (
    _load_ai_request,
    _load_local_response,
    _LocalResponseProvider,
)
from generator.cli.main import build_parser


def _write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def _request() -> dict[str, object]:
    return {
        "schema_version": 1,
        "instructions": "Produce a structured result.",
        "context": {"course": "modern-java"},
        "response_contract": "courseware.course.v1",
    }


@pytest.mark.parametrize(
    ("command", "task"),
    [
        ("course", "courseware.generate"),
        ("review", "courseware.review"),
        ("document", "documentation.generate"),
        ("template", "template.complete"),
    ],
)
def test_request_loader_assigns_command_owned_task(tmp_path: Path, command: str, task: str) -> None:
    request = _load_ai_request(_write_json(tmp_path / "request.json", _request()), command=command)
    assert request.task == task
    assert request.instructions == "Produce a structured result."
    assert request.context == {"course": "modern-java"}


@pytest.mark.parametrize(
    "mutation",
    [
        {"schema_version": True},
        {"schema_version": 2},
        {"instructions": ""},
        {"context": []},
        {"response_contract": ""},
        {"unknown": "value"},
    ],
)
def test_request_loader_rejects_invalid_contract_fields(
    tmp_path: Path, mutation: dict[str, object]
) -> None:
    value = _request()
    value.update(mutation)
    with pytest.raises(ValueError):
        _load_ai_request(_write_json(tmp_path / "request.json", value), command="course")


def test_request_loader_rejects_caller_task_and_unknown_command(tmp_path: Path) -> None:
    value = _request()
    value["task"] = "caller.controlled"
    path = _write_json(tmp_path / "request.json", value)
    with pytest.raises(ValueError):
        _load_ai_request(path, command="course")
    value.pop("task")
    _write_json(path, value)
    with pytest.raises(ValueError):
        _load_ai_request(path, command="chat")


@pytest.mark.parametrize("name", ["missing.json", "directory"])
def test_loaders_reject_non_files(tmp_path: Path, name: str) -> None:
    path = tmp_path / name
    if name == "directory":
        path.mkdir()
    with pytest.raises(ValueError):
        _load_ai_request(path, command="course")
    with pytest.raises(ValueError):
        _load_local_response(path)


def test_loaders_reject_invalid_utf8_json_and_non_object(tmp_path: Path) -> None:
    invalid_utf8 = tmp_path / "invalid-utf8.json"
    invalid_utf8.write_bytes(b"\xff")
    malformed = tmp_path / "malformed.json"
    malformed.write_text("{", encoding="utf-8")
    scalar = _write_json(tmp_path / "scalar.json", [])
    for path in (invalid_utf8, malformed, scalar):
        with pytest.raises(ValueError):
            _load_local_response(path)


def test_local_response_provider_is_deterministic_and_protocol_compatible(
    tmp_path: Path,
) -> None:
    response = _load_local_response(_write_json(tmp_path / "response.json", {"title": "Course"}))
    provider = _LocalResponseProvider(response=response)
    request = AIRequest(task="courseware.generate", instructions="x", context={})
    assert isinstance(provider, AIProvider)
    assert provider.generate(request) is response
    assert provider.generate(request) is response
    assert provider.requests == (request, request)
    assert response.metadata == {"source": "local-response"}


def test_shared_infrastructure_remains_unregistered() -> None:
    parser = build_parser()
    choices = next(
        action.choices
        for action in parser._actions
        if isinstance(getattr(action, "choices", None), dict) and "list" in action.choices
    )
    assert "ai" not in choices
    assert AIResponse is not None


_TERMINAL_ROOT = Path(__file__).resolve().parents[2]
_TERMINAL_SOURCES = (
    _TERMINAL_ROOT / "CHANGELOG.md",
    _TERMINAL_ROOT / "docs" / "HISTORY.md",
    _TERMINAL_ROOT / "docs" / "roadmap.md",
    _TERMINAL_ROOT / "docs" / "releases" / "v1.1-ai-cli-implementation.md",
)


def test_shared_infrastructure_terminal_alignment_is_closed() -> None:
    for source in _TERMINAL_SOURCES:
        prose = " ".join(source.read_text(encoding="utf-8").split()).lower()
        assert "v1.1.6.2 shared request / local-response infrastructure --- accepted" in prose
        assert "implementation pr #194 --- merged" in prose
        assert "746bff69df824a6fa56051ccd80beb43acf93e73" in prose
        assert "post-merge verification --- 91 passed" in prose
        assert "v1.1.6 ai cli implementation --- in progress" in prose
        assert "ai cli course handler --- not started" in prose
        assert "ai cli production registration --- not started" in prose
        assert "formal v1.1 acceptance --- not accepted" in prose
        assert "next --- v1.1.6.3 course handler" in prose
