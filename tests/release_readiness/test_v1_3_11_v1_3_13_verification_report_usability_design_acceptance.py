from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/verification-report-usability.md"
RELEASE = ROOT / ("docs/releases/v1.3.11-v1.3.13-verification-report-usability-design-train.md")
ACCEPTANCE = ROOT / (
    "docs/releases/v1.3.11-v1.3.13-verification-report-usability-design-acceptance.md"
)


def test_design_surfaces_are_terminally_accepted() -> None:
    architecture = ARCHITECTURE.read_text(encoding="utf-8")
    release = RELEASE.read_text(encoding="utf-8")
    assert "Design Accepted / Completed" in architecture
    assert "Status: Design Accepted / Completed" in release


def test_acceptance_records_exact_design_pr_evidence() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Design PR #300 merged" in text
    assert "742ce77c701acfeb8358e37785730072b09302ae" in text
    assert "focused Design verification completed with 7 passed" in text


def test_acceptance_preserves_deferred_authority() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Production implementation remains Not Started" in text
    assert "Runtime mutation, arbitrary subprocess" in text
    assert "release, and publication authority remain" in text


def test_governance_surfaces_use_exact_acceptance_markers() -> None:
    marker = "v1.3.11-v1.3.13-verification-report-usability-design-acceptance"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative_path, exact_marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Production implementation — Not Started" in text


def test_design_markers_remain_distinct_and_unique() -> None:
    marker = "v1.3.11-v1.3.13-verification-report-usability-design-train"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative_path, exact_marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
