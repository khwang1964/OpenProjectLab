from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "generator/release_audit_bundle.py"
CLI = ROOT / "generator/cli/release_evidence.py"
RELEASE = ROOT / (
    "docs/releases/v1.3.23-v1.3.25-audit-bundle-migration-execution-implementation.md"
)


def test_implementation_defines_accepted_execution_symbols() -> None:
    text = MODULE.read_text(encoding="utf-8")
    for symbol in (
        "AuditBundleMigrationRequest",
        "AuditBundleMigrationResult",
        "AuditBundleMigrationExecutor",
    ):
        assert f"class {symbol}" in text
    assert "DEFAULT_MIGRATION_STEP_REGISTRY" in text


def test_cli_exposes_explicit_execution_and_distinct_output() -> None:
    text = CLI.read_text(encoding="utf-8")
    assert 'migration_mode.add_argument("--execute", action="store_true")' in text
    assert 'bundle_migrate.add_argument("--output")' in text
    assert "input and output must be distinct" in text
    assert "migration output already exists" in text


def test_implementation_record_preserves_pending_acceptance() -> None:
    text = RELEASE.read_text(encoding="utf-8")
    assert "Status: Implemented / Pending terminal alignment" in text
    assert "Terminal alignment and implementation acceptance — Pending" in text
    assert "Source rewriting" in text
    assert "trust" in text


def test_governance_surfaces_use_exact_unique_markers() -> None:
    base = "v1.3.23-v1.3.25-audit-bundle-migration-execution-implementation"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Terminal alignment and implementation acceptance — Pending" in text
