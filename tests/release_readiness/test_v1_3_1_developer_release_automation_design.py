from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs/releases/v1.3.1-developer-release-automation-design.md"
ARCHITECTURE = ROOT / "docs/architecture/developer-release-automation.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_design_is_pending_and_predecessor_is_closed() -> None:
    text = read(DESIGN)
    assert "Proposed — Pending design review" in text
    assert "v1.3.0 Bootstrap SDK Serialization — Accepted / Completed" in text
    assert "Production implementation — Not Started" in text


def test_evidence_identity_and_fail_closed_rules_are_explicit() -> None:
    text = read(DESIGN) + read(ARCHITECTURE)
    for marker in (
        "candidate commit SHA",
        "pull request number and state",
        "required CI check names and conclusions",
        "coverage percentage and configured threshold",
        "Missing, ambiguous, stale, or contradictory evidence fails closed",
        "Unknown state is not success",
    ):
        assert marker in text


def test_two_pr_acceptance_boundary_is_preserved() -> None:
    text = read(DESIGN)
    assert "PR 1 may create a Pending acceptance record" in text
    assert "separate PR 2" in text
    assert "Accepted / Completed closure evidence" in text


def test_destructive_and_public_surfaces_are_deferred() -> None:
    text = read(DESIGN) + read(ARCHITECTURE)
    for marker in (
        "automatic pull-request merge",
        "tag, GitHub Release, or package publication",
        "no accidental public SDK expansion",
        "checkpoint/resume for Bootstrap execution",
        "serialization schema migration",
    ):
        assert marker in text


def test_lifecycle_documents_are_aligned_to_pending_design() -> None:
    paths = (ROOT / "docs/roadmap.md", ROOT / "docs/HISTORY.md", ROOT / "CHANGELOG.md")
    for path in paths:
        text = read(path)
        assert "v1.3.1 Developer / Release Automation" in text
        assert "Design review — Pending" in text
        assert "Production implementation — Not Started" in text
