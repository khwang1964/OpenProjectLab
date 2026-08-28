from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs/releases/v1.3.1-developer-release-automation-design.md"
ARCHITECTURE = ROOT / "docs/architecture/developer-release-automation.md"
ACCEPTANCE = ROOT / "docs/releases/v1.3.1-developer-release-automation-design-acceptance.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_design_is_terminally_accepted_and_predecessor_is_closed() -> None:
    text = read(DESIGN)
    assert "Accepted — Terminally Closed" in text
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


def test_lifecycle_documents_are_aligned_to_terminal_design() -> None:
    paths = (ROOT / "docs/roadmap.md", ROOT / "docs/HISTORY.md", ROOT / "CHANGELOG.md")
    for path in paths:
        text = read(path)
        assert "v1.3.1 Developer / Release Automation" in text
        assert "Design review — Passed / Completed" in text
        assert "Production implementation — Not Started" in text


def test_design_acceptance_records_terminal_evidence() -> None:
    text = read(ACCEPTANCE)
    for marker in (
        "Accepted — Completed",
        "Design PR — #269",
        "53cda269e2077e20941bfc2e64ed1cba59972b1d",
        "Required CI — Passed",
        "Post-merge focused verification — 5 passed",
        "Closure gates — Passed / Completed",
        "Production implementation — Not Started",
    ):
        assert marker in text


def test_minimum_implementation_alignment_is_terminally_accepted() -> None:
    alignment = (
        ROOT / "docs/releases/v1.3.1-developer-release-automation-implementation-alignment.md"
    )
    text = read(alignment)
    for marker in (
        "Accepted — Completed",
        "Implementation PR — #271",
        "0c8f615c72dd6cd023761f88a9e0a9d1e1eb6b6f",
        "Focused implementation tests — 4 passed, no warnings",
        "2564 passed, 56 skipped, 1 deselected",
        "Coverage — 90.88%",
        "Formal implementation acceptance — Accepted / Completed",
    ):
        assert marker in text
    assert (ROOT / "generator/release_automation.py").is_file()


def test_minimum_implementation_acceptance_records_terminal_evidence() -> None:
    acceptance = (
        ROOT / "docs/releases/v1.3.1-developer-release-automation-implementation-acceptance.md"
    )
    text = read(acceptance)
    for marker in (
        "Accepted — Completed",
        "Implementation PR — #271",
        "0c8f615c72dd6cd023761f88a9e0a9d1e1eb6b6f",
        "Alignment PR — #272",
        "ea0e7dc25b8d4c5ed60e0fb673d48ff4230e64b4",
        "Alignment post-merge verification — 11 passed",
        "2565 passed, 56 skipped, 1 deselected",
        "Coverage — 90.88%",
        "Closure gates — Passed / Completed",
        "Next roadmap slice — Pending explicit Design First definition",
    ):
        assert marker in text
