from __future__ import annotations

from generator.cli.main import build_parser


def test_report_audit_commands_are_registered() -> None:
    parser = build_parser()
    fingerprint = parser.parse_args(
        ["release-evidence", "report", "fingerprint", "--report", "report.json"]
    )
    compare = parser.parse_args(
        [
            "release-evidence",
            "report",
            "compare",
            "--left",
            "left.json",
            "--right",
            "right.json",
        ]
    )
    assert fingerprint.command_handler.__name__ == "_handle_report_fingerprint"
    assert compare.command_handler.__name__ == "_handle_report_compare"
