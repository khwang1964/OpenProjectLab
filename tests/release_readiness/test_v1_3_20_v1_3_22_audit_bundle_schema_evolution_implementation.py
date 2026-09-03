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


def test_cli_preserves_preview_and_exposes_explicit_execution() -> None:
    text = CLI.read_text(encoding="utf-8")
    assert 'add_parser("compatibility")' in text
    assert 'add_parser("migrate")' in text
    assert 'migration_mode.add_argument("--preview", action="store_true")' in text
    assert 'migration_mode.add_argument("--execute", action="store_true")' in text
    assert 'bundle_migrate.add_argument("--output")' in text


def test_release_record_is_accepted_after_alignment() -> None:
    text = RELEASE.read_text(encoding="utf-8")
    assert "Status: Accepted / Completed" in text
    assert "Terminal alignment and implementation acceptance — Accepted / Completed" in text
