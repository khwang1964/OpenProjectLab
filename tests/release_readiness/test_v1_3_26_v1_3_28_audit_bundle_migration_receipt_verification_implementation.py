from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "generator/release_audit_bundle.py"
CLI = ROOT / "generator/cli/release_evidence.py"
RELEASE = ROOT / (
    "docs/releases/v1.3.26-v1.3.28-audit-bundle-migration-receipt-verification-implementation.md"
)


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_implementation_defines_accepted_receipt_symbols() -> None:
    text = MODULE.read_text(encoding="utf-8")
    for symbol in (
        "AuditBundleMigrationReceipt",
        "AuditBundleMigrationReceiptCodec",
        "AuditBundleMigrationReceiptFinding",
        "AuditBundleMigrationReceiptVerification",
        "AuditBundleMigrationReceiptVerifier",
    ):
        assert f"class {symbol}" in text


def test_cli_exposes_bounded_read_only_verification() -> None:
    text = CLI.read_text(encoding="utf-8")
    assert 'add_parser("verify-migration")' in text
    for option in ('"--bundle"', '"--output"', '"--receipt"'):
        assert option in text
    handler = text.split("def _handle_bundle_verify_migration", 1)[1].split(
        "def _handle_bundle_migrate", 1
    )[0]
    assert "write_text(" not in handler
    assert "replace(" not in handler
    assert "unlink(" not in handler


def test_implementation_record_is_accepted_after_alignment() -> None:
    text = normalized(RELEASE)
    assert "Status: Accepted / Completed" in text
    assert "Terminal alignment and implementation acceptance — Accepted / Completed" in text
    assert "equality evidence only" in text
    assert "trust" in text


def test_governance_surfaces_use_exact_unique_markers() -> None:
    base = "v1.3.26-v1.3.28-audit-bundle-migration-receipt-verification-implementation"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Terminal alignment and implementation acceptance — Pending" in text
