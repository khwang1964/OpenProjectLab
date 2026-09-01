from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/verification-audit-bundle-portability.md"
RELEASES = ROOT / "docs/releases"
BASELINE = RELEASES / "v1.3.17-v1.3.19-verification-audit-bundle-portability-design-train.md"
ACCEPTANCE = RELEASES / "v1.3.17-v1.3.19-verification-audit-bundle-portability-design-acceptance.md"


def test_design_surfaces_are_terminally_accepted() -> None:
    architecture = ARCHITECTURE.read_text(encoding="utf-8")
    baseline = BASELINE.read_text(encoding="utf-8")
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Design First baseline — Accepted / Completed" in architecture
    assert "Status: Accepted / Completed" in baseline
    assert "Status: Accepted / Completed" in acceptance


def test_acceptance_records_exact_design_evidence() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Design PR: [#310]" in text
    assert "9f41d4ae5c20bcd499e22c44d84477cfbae756d9" in text
    assert "Synchronized-main Design First verification: 7 passed" in text


def test_accepted_scope_and_security_boundaries_remain_explicit() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    for fragment in (
        "immutable canonical audit bundle",
        "offline, stateless, deterministic, fail-closed",
        "Archive extraction",
        "signing",
        "provenance",
        "repository mutation",
    ):
        assert fragment in text


def test_production_implementation_remains_not_started() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Production implementation — Not Started" in text


def test_governance_surfaces_use_exact_unique_acceptance_markers() -> None:
    base = "v1.3.17-v1.3.19-verification-audit-bundle-portability-design-acceptance"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, exact_marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Design — Accepted / Completed" in text
        assert "Production implementation — Not Started" in text
