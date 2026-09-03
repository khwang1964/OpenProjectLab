from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/audit-bundle-migration-receipt-verification.md"
RELEASES = ROOT / "docs/releases"
BASELINE = RELEASES / (
    "v1.3.26-v1.3.28-audit-bundle-migration-receipt-verification-design-train.md"
)
ACCEPTANCE = RELEASES / (
    "v1.3.26-v1.3.28-audit-bundle-migration-receipt-verification-design-acceptance.md"
)


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_design_surfaces_are_terminally_accepted() -> None:
    assert "Design First baseline — Accepted / Completed" in normalized(ARCHITECTURE)
    assert "Status: Accepted / Completed" in normalized(BASELINE)
    assert "Status: Accepted / Completed" in normalized(ACCEPTANCE)


def test_acceptance_records_exact_design_evidence() -> None:
    text = normalized(ACCEPTANCE)
    assert "Design PR: [#325]" in text
    assert "d27018cd6e71437a33d45e3f41ab73f48be6f7f3" in text
    assert "Synchronized-main Design First verification: 6 passed" in text


def test_accepted_scope_remains_explicit() -> None:
    text = normalized(ACCEPTANCE)
    for phrase in (
        "canonical migration-receipt contract",
        "deterministic offline verification",
        "stable bounded read-only verification CLI",
        "Unknown schemas, steps, fields, and ambiguous plans fail closed",
        "Migration execution",
        "repository mutation",
    ):
        assert phrase in text


def test_production_implementation_remains_not_started() -> None:
    assert "Production implementation — Not Started" in normalized(ACCEPTANCE)


def test_governance_surfaces_use_exact_unique_acceptance_markers() -> None:
    base = "v1.3.26-v1.3.28-audit-bundle-migration-receipt-verification-design-acceptance"
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
