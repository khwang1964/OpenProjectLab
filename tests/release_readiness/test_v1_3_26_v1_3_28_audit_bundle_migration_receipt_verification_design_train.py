from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/audit-bundle-migration-receipt-verification.md"
RELEASE = ROOT / (
    "docs/releases/v1.3.26-v1.3.28-audit-bundle-migration-receipt-verification-design-train.md"
)


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_design_is_accepted_and_implementation_not_started() -> None:
    architecture = normalized(ARCHITECTURE)
    release = normalized(RELEASE)
    assert "Accepted / Completed" in architecture
    assert "Accepted / Completed" in release
    assert "Production implementation is Not Started" in release


def test_receipt_contract_is_strict_canonical_and_non_trusting() -> None:
    text = normalized(ARCHITECTURE)
    assert "AuditBundleMigrationReceipt" in text
    for phrase in (
        "duplicate keys",
        "unknown fields",
        "malformed digests",
        "canonical rendering is byte-stable",
        "equality evidence only",
        "not a signature",
    ):
        assert phrase in text


def test_verifier_binds_every_accepted_identity() -> None:
    text = normalized(ARCHITECTURE)
    assert "AuditBundleMigrationReceiptVerifier" in text
    for phrase in (
        "recomputes both document digests",
        "exact migration plan",
        "schemas, steps, plan fingerprint, and output identity",
        "stable field path",
        "fail closed",
    ):
        assert phrase in text


def test_cli_is_bounded_read_only_and_has_stable_exit_classes() -> None:
    text = normalized(ARCHITECTURE)
    assert "bundle verify-migration --bundle SOURCE --output TARGET" in text
    assert "--receipt RECEIPT --format json|text" in text
    assert "Exit 0" in text
    assert "exit 1" in text
    assert "exit 2" in text
    assert "reads bounded local files only" in text
    assert "never writes, replaces, deletes" in text


def test_security_non_claims_remain_explicit() -> None:
    text = normalized(ARCHITECTURE)
    for phrase in (
        "No migration execution",
        "network access",
        "repository mutation",
        "No signing",
        "trust",
        "provenance",
        "attestation",
    ):
        assert phrase in text


def test_governance_surfaces_use_exact_unique_markers() -> None:
    base = "v1.3.26-v1.3.28-audit-bundle-migration-receipt-verification-design-train"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Production implementation — Not Started" in text
