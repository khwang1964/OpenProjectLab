from __future__ import annotations

from argparse import Namespace

from generator.cli.main import build_parser
from generator.cli.release_evidence import _handle_report_validate
from generator.release_automation import (
    VerificationFinding,
    VerificationFindingStage,
    VerificationReport,
    VerificationReportEncoder,
)


def test_report_validate_parser_is_additive() -> None:
    args = build_parser().parse_args(
        ["release-evidence", "report", "validate", "--report", "r.json", "--format", "json"]
    )
    assert args.command_handler is _handle_report_validate


def test_report_validate_returns_one_for_recorded_failure(tmp_path, capsys) -> None:
    report = VerificationReport(
        None,
        None,
        None,
        (VerificationFinding(VerificationFindingStage.COLLECTION, "failed", "offline"),),
    )
    path = tmp_path / "report.json"
    path.write_text(VerificationReportEncoder.encode(report), encoding="utf-8")
    assert _handle_report_validate(Namespace(report=path, format="json")) == 1
    assert '"status":"failed"' in capsys.readouterr().out


def test_report_validate_returns_two_for_bad_input(tmp_path, capsys) -> None:
    path = tmp_path / "report.json"
    path.write_text("{}", encoding="utf-8")
    assert _handle_report_validate(Namespace(report=path, format="text")) == 2
    assert capsys.readouterr().err.startswith("error: ")
