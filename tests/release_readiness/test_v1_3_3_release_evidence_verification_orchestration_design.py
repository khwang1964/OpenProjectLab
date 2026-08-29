from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/release-evidence-verification-orchestration.md"
RELEASE = ROOT / "docs/releases/v1.3.3-release-evidence-verification-orchestration.md"


def test_design_surfaces_exist_and_remain_pending() -> None:
    architecture = ARCHITECTURE.read_text(encoding="utf-8")
    release = RELEASE.read_text(encoding="utf-8")

    assert "Proposed / Pending design review" in architecture
    assert "Status: Proposed / Pending design review" in release
    assert "Production implementation — Not Started" in release


def test_design_composes_existing_accepted_boundaries() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")

    assert "v1.3.1" in text
    assert "v1.3.2" in text
    assert "ReleaseEvidenceValidator" in text
    assert "Repository observation + GitHub PR observation" in text


def test_design_is_explicit_deterministic_and_fail_closed() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")

    assert "explicit expected repository" in text
    assert "explicit expected branch" in text
    assert "explicit expected candidate SHA" in text
    assert "fails closed" in text
    assert "stably ordered" in text


def test_design_preserves_side_effect_boundaries() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")

    assert "does not run" in text
    assert "No filesystem write" in text
    assert "Git mutation" in text
    assert "GitHub mutation" in text
    assert "CLI" in text
    assert "public SDK" in text


def test_design_includes_code_review_checklist() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")

    assert "## Code Review Checklist" in text
    assert "Finding order is deterministic" in text
    assert "Focused-test evidence remains caller supplied" in text


def test_governance_surfaces_share_one_design_marker() -> None:
    marker = "v1.3.3-release-evidence-verification-orchestration-design"

    for relative_path in ("CHANGELOG.md", "docs/HISTORY.md", "docs/roadmap.md"):
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Production implementation — Not Started" in text
