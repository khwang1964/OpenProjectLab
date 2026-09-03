from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/audit-bundle-migration-chain-verification.md"
RELEASE = ROOT / (
    "docs/releases/v1.3.29-v1.3.31-audit-bundle-migration-chain-verification-design-train.md"
)


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_design_is_pending_and_implementation_not_started() -> None:
    architecture = normalized(ARCHITECTURE)
    release = normalized(RELEASE)
    assert "Proposed / Pending design review" in architecture
    assert "Proposed / Pending design review" in release
    assert "Production implementation is Not Started" in release


def test_chain_manifest_is_strict_canonical_and_non_trusting() -> None:
    text = normalized(ARCHITECTURE)
    assert "AuditBundleMigrationChainManifest" in text
    for phrase in (
        "duplicate keys",
        "unknown fields",
        "malformed digests",
        "empty chains",
        "Receipt order is significant",
        "canonical rendering is byte-stable",
        "equality and continuity evidence only",
    ):
        assert phrase in text


def test_verifier_binds_every_edge_and_terminal_identity() -> None:
    text = normalized(ARCHITECTURE)
    assert "AuditBundleMigrationChainVerifier" in text
    for phrase in (
        "N receipts requires exactly N+1 bundles",
        "accepted single-receipt verifier",
        "bundle adjacency",
        "schema continuity",
        "initial/final bindings",
        "stable indexed field paths",
        "fail closed",
    ):
        assert phrase in text


def test_cli_is_bounded_read_only_and_has_stable_exit_classes() -> None:
    text = normalized(ARCHITECTURE)
    assert "bundle verify-migration-chain --manifest MANIFEST" in text
    assert "--bundle BUNDLE [--bundle BUNDLE ...]" in text
    assert "--receipt RECEIPT [--receipt RECEIPT ...]" in text
    assert "Exit 0" in text
    assert "exit 1" in text
    assert "exit 2" in text
    assert "aggregate-byte limits" in text
    assert "reads only explicitly named local files" in text
    assert "never discovers, writes, replaces, deletes" in text


def test_security_non_claims_remain_explicit() -> None:
    text = normalized(ARCHITECTURE)
    for phrase in (
        "No migration execution",
        "glob discovery",
        "network access",
        "repository mutation",
        "No signing",
        "trust",
        "provenance",
        "attestation",
    ):
        assert phrase in text


def test_governance_surfaces_use_exact_unique_markers() -> None:
    base = "v1.3.29-v1.3.31-audit-bundle-migration-chain-verification-design-train"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Production implementation — Not Started" in text
