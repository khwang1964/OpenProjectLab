from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_implementation_record_is_pending_terminal_alignment() -> None:
    text = (
        ROOT / "docs/releases/v1.3.14-v1.3.16-verification-report-auditability-implementation.md"
    ).read_text(encoding="utf-8")
    assert "Accepted / Completed" in text
    assert "not a signature" in text


def test_production_symbols_and_cli_commands_exist() -> None:
    module = (ROOT / "generator/release_automation.py").read_text(encoding="utf-8")
    cli = (ROOT / "generator/cli/release_evidence.py").read_text(encoding="utf-8")
    for symbol in ("VerificationReportFingerprinter", "VerificationReportComparator"):
        assert f"class {symbol}" in module
    assert "_handle_report_fingerprint" in cli
    assert "_handle_report_compare" in cli


def test_governance_markers_are_exact_and_unique() -> None:
    base = "v1.3.14-v1.3.16-verification-report-auditability-implementation"
    for path, suffix in (
        ("CHANGELOG.md", "changelog"),
        ("docs/HISTORY.md", "history"),
        ("docs/roadmap.md", "roadmap"),
    ):
        text = (ROOT / path).read_text(encoding="utf-8")
        assert text.count(f"<!-- {base}-{suffix} -->") == 1
