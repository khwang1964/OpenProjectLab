from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "generator/release_audit_bundle.py"
CLI = ROOT / "generator/cli/release_evidence.py"
RELEASE = ROOT / ("docs/releases/v1.3.20-v1.3.22-audit-bundle-schema-evolution-implementation.md")


def test_implementation_defines_accepted_production_symbols() -> None:
    text = MODULE.read_text(encoding="utf-8")
    for symbol in (
        "AuditBundleSchemaCompatibility",
        "AuditBundleMigrationPlan",
        "AuditBundleSchemaRegistry",
    ):
        assert f"class {symbol}" in text


def test_cli_exposes_accepted_preview_only_commands() -> None:
    text = CLI.read_text(encoding="utf-8")
    assert 'add_parser("compatibility")' in text
    assert 'add_parser("migrate")' in text
    assert '"--preview", action="store_true", required=True' in text


def test_release_record_remains_pending_before_alignment() -> None:
    text = RELEASE.read_text(encoding="utf-8")
    assert "Implemented / Terminal alignment pending merge verification" in text
    assert "Terminal alignment and implementation acceptance — Pending" in text
