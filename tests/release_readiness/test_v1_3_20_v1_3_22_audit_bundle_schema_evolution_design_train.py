from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/audit-bundle-schema-evolution.md"
RELEASE = ROOT / "docs/releases/v1.3.20-v1.3.22-audit-bundle-schema-evolution-design-train.md"


def test_design_is_pending_and_implementation_not_started() -> None:
    architecture = ARCHITECTURE.read_text(encoding="utf-8")
    release = RELEASE.read_text(encoding="utf-8")
    assert "Accepted / Completed" in architecture
    assert "Accepted / Completed" in release
    assert "Production implementation is Not Started" in release


def test_compatibility_uses_explicit_fail_closed_classification() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    for category in ("CURRENT", "MIGRATABLE", "FUTURE", "UNSUPPORTED"):
        assert category in text
    assert "lexical or numeric guessing is forbidden" in text
    assert "never decode through the current codec" in text


def test_migration_planning_is_deterministic_and_non_executing() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "AuditBundleMigrationPlan" in text
    assert "deterministic preview fingerprint" in text
    assert "never executes a migration" in text
    for failure in ("Cycles", "missing edges", "ambiguous paths", "downgrades"):
        assert failure in text


def test_cli_is_preview_only_with_stable_exit_classes() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "bundle compatibility --bundle FILE" in text
    assert "bundle migrate --bundle FILE --target SCHEMA --preview" in text
    normalized = " ".join(text.split())
    assert "never writes output" in normalized
    assert "0 only" in text
    assert "1 for a" in text
    assert "2 for input" in text


def test_security_non_claims_remain_explicit() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    for phrase in (
        "No migration execution",
        "archive extraction",
        "network access",
        "repository mutation",
        "No signing",
        "trust",
        "provenance",
    ):
        assert phrase in text


def test_governance_surfaces_use_exact_unique_markers() -> None:
    base = "v1.3.20-v1.3.22-audit-bundle-schema-evolution-design-train"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Production implementation — Not Started" in text


def test_design_does_not_create_production_symbols() -> None:
    production = ROOT / "generator/release_audit_bundle.py"
    text = production.read_text(encoding="utf-8")
    for symbol in ("AuditBundleSchemaCompatibility", "AuditBundleMigrationPlan"):
        assert f"class {symbol}" not in text
