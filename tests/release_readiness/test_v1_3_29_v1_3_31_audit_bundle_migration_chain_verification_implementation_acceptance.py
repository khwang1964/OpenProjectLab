from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASES = ROOT / "docs/releases"
ACCEPTANCE = RELEASES / (
    "v1.3.29-v1.3.31-audit-bundle-migration-chain-verification-implementation-acceptance.md"
)
IMPLEMENTATION = RELEASES / (
    "v1.3.29-v1.3.31-audit-bundle-migration-chain-verification-implementation.md"
)
ALIGNMENT = RELEASES / (
    "v1.3.29-v1.3.31-audit-bundle-migration-chain-verification-terminal-alignment.md"
)


def test_acceptance_records_terminal_evidence() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Status: Accepted / Completed" in text
    assert "Terminal-alignment PR: [#333]" in text
    assert "2a740cce476f8b0808b68cea3fd9493f4ef5b261" in text
    assert "46 passed" in text


def test_prior_records_have_terminal_states() -> None:
    assert "Status: Accepted / Completed" in IMPLEMENTATION.read_text(encoding="utf-8")
    assert "Completed / Verified after merge" in ALIGNMENT.read_text(encoding="utf-8")


def test_accepted_boundary_remains_explicit() -> None:
    text = " ".join(ACCEPTANCE.read_text(encoding="utf-8").split())
    for phrase in (
        "canonical chain manifest",
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
        "generalized N-edge structure",
        "Equality and continuity evidence",
        "signing",
        "trust",
        "provenance",
        "network access",
        "repository mutation",
    ):
        assert phrase in text


def test_governance_surfaces_use_exact_unique_acceptance_markers() -> None:
    base = "v1.3.29-v1.3.31-audit-bundle-migration-chain-verification-implementation-acceptance"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Implementation acceptance — Accepted / Completed" in text
