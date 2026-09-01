from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/audit-bundle-schema-evolution.md"
RELEASES = ROOT / "docs/releases"
BASELINE = RELEASES / "v1.3.20-v1.3.22-audit-bundle-schema-evolution-design-train.md"
ACCEPTANCE = RELEASES / ("v1.3.20-v1.3.22-audit-bundle-schema-evolution-design-acceptance.md")


def test_design_surfaces_are_terminally_accepted() -> None:
    architecture = ARCHITECTURE.read_text(encoding="utf-8")
    baseline = BASELINE.read_text(encoding="utf-8")
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Design First baseline — Accepted / Completed" in architecture
    assert "Status: Accepted / Completed" in baseline
    assert "Status: Accepted / Completed" in acceptance


def test_acceptance_records_exact_design_evidence() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Design PR: [#315]" in text
    assert "dae7fa499b7576717b3fa5b5b40afb4af8c711f8" in text
    assert "Synchronized-main Design First verification: 7 passed" in text


def test_accepted_scope_remains_explicit() -> None:
    text = " ".join(ACCEPTANCE.read_text(encoding="utf-8").split())
    for fragment in (
        "fail-closed schema compatibility",
        "deterministic offline migration planning",
        "Unknown schemas are never guessed",
        "Migration execution",
        "repository mutation",
    ):
        assert fragment in text


def test_production_implementation_remains_not_started() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Production implementation — Not Started" in text


def test_governance_surfaces_use_exact_unique_acceptance_markers() -> None:
    base = "v1.3.20-v1.3.22-audit-bundle-schema-evolution-design-acceptance"
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
