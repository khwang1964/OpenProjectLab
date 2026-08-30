from __future__ import annotations

import json

from generator.cli.main import build_parser
from generator.cli.release_evidence import _handle_verify
from generator.release_automation import (
    VerificationFinding,
    VerificationFindingStage,
    VerificationReport,
)


def test_parser_requires_explicit_request_and_format() -> None:
    args = build_parser().parse_args(
        ["release-evidence", "verify", "--request", "request.json", "--format", "json"]
    )
    assert args.release_evidence_command == "verify"
    assert args.command_handler is _handle_verify


def test_handler_emits_report_and_stable_exit_status(tmp_path, monkeypatch, capsys) -> None:
    request_path = tmp_path / "request.json"
    request_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "expected_repository": "khwang1964/OpenProjectLab",
                "expected_branch": "main",
                "expected_sha": "a" * 40,
                "pull_request_number": 290,
                "focused_tests": {"passed": 28, "failed": 0, "skipped": 0, "deselected": 0},
            }
        ),
        encoding="utf-8",
    )
    report = VerificationReport(
        None,
        None,
        None,
        (VerificationFinding(VerificationFindingStage.COLLECTION, "failed", "no report"),),
    )

    class FakeInvoker:
        def __init__(self, runtime) -> None:
            self.runtime = runtime

        def invoke(self, request):
            return report

    import generator.cli.release_evidence as cli

    monkeypatch.setattr(cli, "build_verification_runtime", lambda configuration: object())
    monkeypatch.setattr(cli, "ReadOnlyVerificationInvoker", FakeInvoker)
    args = build_parser().parse_args(
        ["release-evidence", "verify", "--request", str(request_path), "--format", "json"]
    )
    args.project_root = tmp_path
    assert _handle_verify(args) == 1
    captured = capsys.readouterr()
    assert json.loads(captured.out)["status"] == "failed"
    assert captured.err == ""


def test_handler_rejects_invalid_request_without_stdout(tmp_path, capsys) -> None:
    request_path = tmp_path / "request.json"
    request_path.write_text("{}", encoding="utf-8")
    args = build_parser().parse_args(
        ["release-evidence", "verify", "--request", str(request_path), "--format", "text"]
    )
    args.project_root = tmp_path
    assert _handle_verify(args) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err.startswith("error: ")
