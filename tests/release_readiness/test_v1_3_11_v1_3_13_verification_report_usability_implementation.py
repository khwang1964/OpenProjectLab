from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "generator/release_automation.py"
CLI = ROOT / "generator/cli/release_evidence.py"
RELEASE = ROOT / ("docs/releases/v1.3.11-v1.3.13-verification-report-usability-implementation.md")


def test_production_contract_is_present() -> None:
    module = MODULE.read_text(encoding="utf-8")
    for symbol in (
        "class VerificationReportCodec",
        "class VerificationReportEncoder",
        "class VerificationReportInspector",
        "class VerificationReportInspectionRenderer",
    ):
        assert symbol in module


def test_cli_exposes_offline_report_validation() -> None:
    text = CLI.read_text(encoding="utf-8")
    assert 'commands.add_parser("report"' in text
    assert "_handle_report_validate" in text
    assert "build_verification_runtime" not in text.split("def _handle_report_validate", 1)[1]


def test_release_record_remains_pending() -> None:
    text = RELEASE.read_text(encoding="utf-8")
    assert "Implemented / Terminal alignment pending merge verification" in text
    assert "Synchronized-main focused post-merge verification" in text


def test_governance_markers_are_exact_and_unique() -> None:
    suffixes = {
        "CHANGELOG.md": "changelog",
        "docs/HISTORY.md": "history",
        "docs/roadmap.md": "roadmap",
    }
    base = "v1.3.11-v1.3.13-verification-report-usability-implementation"
    for relative, suffix in suffixes.items():
        marker = f"<!-- {base}-{suffix} -->"
        assert (ROOT / relative).read_text(encoding="utf-8").count(marker) == 1


def test_bilingual_manual_markers_are_distinct() -> None:
    pairs = {
        "docs/user-guide/en/cli.md": "en",
        "docs/user-guide/zh-TW/cli.md": "zh-tw",
    }
    for relative, suffix in pairs.items():
        marker = f"<!-- v1.3.13-verification-report-validation-cli-{suffix} -->"
        assert (ROOT / relative).read_text(encoding="utf-8").count(marker) == 1
