from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASES = ROOT / "docs/releases"
ALIGNMENT = RELEASES / (
    "v1.3.29-v1.3.31-audit-bundle-migration-chain-verification-terminal-alignment.md"
)
IMPLEMENTATION = RELEASES / (
    "v1.3.29-v1.3.31-audit-bundle-migration-chain-verification-implementation.md"
)


def test_alignment_remains_pending_before_merge_verification() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    assert "Pending / Awaiting terminal-alignment merge and verification" in text
    assert "A separate implementation-acceptance closure" in text


def test_alignment_records_exact_implementation_evidence() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    assert "Implementation PR: [#332]" in text
    assert "c239abd1c8f62249533b368a9212b49c4287eb62" in text
    assert "Synchronized-main focused verification: 41 passed" in text


def test_alignment_preserves_chain_boundary() -> None:
    text = " ".join(ALIGNMENT.read_text(encoding="utf-8").split())
    for phrase in (
        "ordered receipt identities",
        "initial/final bundle digests",
        "N+1 bundle count",
        "adjacency",
        "schema continuity",
        "terminal bindings",
        "verify-migration-chain",
        "aggregate-byte bounds",
        "without glob or directory discovery",
        "0 -> 1",
        "trust",
        "provenance",
        "repository mutation",
    ):
        assert phrase in text


def test_implementation_status_awaits_alignment_merge() -> None:
    text = IMPLEMENTATION.read_text(encoding="utf-8")
    assert "Implemented / Terminal alignment pending merge verification" in text


def test_governance_surfaces_use_exact_unique_markers() -> None:
    base = "v1.3.29-v1.3.31-audit-bundle-migration-chain-verification-terminal-alignment"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, exact_marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Awaiting terminal-alignment merge and verification" in text
