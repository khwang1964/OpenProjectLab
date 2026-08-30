from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = ROOT / (
    "docs/releases/v1.3.3-release-evidence-verification-orchestration-implementation-acceptance.md"
)


def test_implementation_is_formally_accepted() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert text.count("> Status: Accepted / Completed") == 1


def test_acceptance_cites_implementation_evidence() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "PR #281" in text
    assert "1441c362923f16d704f817e302ef22fbb829782a" in text
    assert "workflow run #576 completed successfully" in text
    assert "2610 passed, 56 skipped, 1 deselected" in text
    assert "90.64%" in text
    assert "36 passed" in text


def test_acceptance_cites_alignment_evidence() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "PR #282" in text
    assert "86ad4406107e90fbec5dcfb2fe57dae407695eec" in text
    assert "workflow run #578 completed successfully" in text
    assert "41 passed" in text


def test_acceptance_preserves_deferred_authority() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Focused-test evidence remains caller supplied" in text
    assert "No test execution, CLI, public SDK, Git/GitHub mutation" in text
    assert "No retry, polling, persistence, caching, credential" in text


def test_governance_surfaces_share_one_closure_marker() -> None:
    marker = "v1.3.3-release-evidence-verification-orchestration-implementation-closure"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Accepted / Completed" in text
