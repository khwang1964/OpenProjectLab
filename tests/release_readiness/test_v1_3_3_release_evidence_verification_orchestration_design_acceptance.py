from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/release-evidence-verification-orchestration.md"
RELEASE = ROOT / "docs/releases/v1.3.3-release-evidence-verification-orchestration.md"
ACCEPTANCE = ROOT / (
    "docs/releases/v1.3.3-release-evidence-verification-orchestration-design-acceptance.md"
)


def test_design_is_terminally_accepted() -> None:
    architecture = ARCHITECTURE.read_text(encoding="utf-8")
    release = RELEASE.read_text(encoding="utf-8")
    acceptance = ACCEPTANCE.read_text(encoding="utf-8")

    assert "Accepted / Terminally Closed" in architecture
    assert "Status: Accepted / Completed" in release
    assert "Status: Accepted / Completed" in acceptance


def test_acceptance_cites_current_merge_ci_and_test_evidence() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")

    assert "PR #279" in text
    assert "1b3c2e732cf13f384d87efdfc5cc85ff1fdc52aa" in text
    assert "workflow run #572 completed successfully" in text
    assert "2592 passed, 56 skipped, 1 deselected" in text
    assert "90.62%" in text
    assert "6 passed" in text


def test_acceptance_preserves_deferred_boundaries() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")

    assert "Production implementation — Not Started" in text
    assert "remain read-only" in text
    assert "No Git/GitHub mutation" in text
    assert "public SDK" in text
    assert "test-execution authority" in text


def test_acceptance_authorizes_only_minimum_implementation() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")

    assert "minimum v1.3.3 production implementation slice" in text
    assert "new explicit Design First decision" in text


def test_governance_surfaces_share_terminal_design_acceptance() -> None:
    marker = "v1.3.3-release-evidence-verification-orchestration-design-acceptance"

    for relative_path in ("CHANGELOG.md", "docs/HISTORY.md", "docs/roadmap.md"):
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Production implementation — Not Started" in text
