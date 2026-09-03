from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/audit-bundle-migration-chain-verification.md"
RELEASES = ROOT / "docs/releases"
BASELINE = RELEASES / ("v1.3.29-v1.3.31-audit-bundle-migration-chain-verification-design-train.md")
ACCEPTANCE = RELEASES / (
    "v1.3.29-v1.3.31-audit-bundle-migration-chain-verification-design-acceptance.md"
)


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_design_surfaces_are_terminally_accepted() -> None:
    assert "Design First baseline — Accepted / Completed" in normalized(ARCHITECTURE)
    assert "Status: Accepted / Completed" in normalized(BASELINE)
    assert "Status: Accepted / Completed" in normalized(ACCEPTANCE)


def test_acceptance_records_exact_design_evidence() -> None:
    text = normalized(ACCEPTANCE)
    assert "Design PR: [#330]" in text
    assert "17e9fb3e149b027e98b32bc502f90679e89e2d41" in text
    assert "Synchronized-main Design First verification: 6 passed" in text


def test_accepted_scope_remains_explicit() -> None:
    text = normalized(ACCEPTANCE)
    for phrase in (
        "canonical migration-chain manifest",
        "ordered receipt identities",
        "explicit initial/final bundle digests",
        "deterministic offline verification",
        "adjacency",
        "schema continuity",
        "terminal bindings",
        "bounded read-only chain-verification CLI",
        "aggregate-byte limits",
        "no implicit discovery",
        "fail closed",
        "Migration execution",
        "trust",
        "provenance",
        "repository mutation",
    ):
        assert phrase in text


def test_production_implementation_remains_not_started() -> None:
    assert "Production implementation — Not Started" in normalized(ACCEPTANCE)


def test_governance_surfaces_use_exact_unique_acceptance_markers() -> None:
    base = "v1.3.29-v1.3.31-audit-bundle-migration-chain-verification-design-acceptance"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Design — Accepted / Completed" in text
        assert "Production implementation — Not Started" in text
