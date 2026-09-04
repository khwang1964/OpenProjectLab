from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = ROOT / (
    "docs/releases/v1.4.0-release-readiness-stability-baseline-design-acceptance.md"
)


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_acceptance_uses_exact_post_merge_evidence() -> None:
    text = normalized(ACCEPTANCE)
    assert "Design PR #335 merged" in text
    assert "a7667bff5b8009189f2f6d798b50f584946ab90a" in text
    assert "Required GitHub Actions / CI completed successfully" in text
    assert "focused Design First verification completed with 6 passed" in text
    assert "post-merge working tree remained clean" in text


def test_design_is_accepted_without_implementation_claim() -> None:
    text = normalized(ACCEPTANCE)
    assert "Status: Accepted / Completed" in text
    assert "Design — Accepted / Completed" in text
    assert "Production implementation — Not Started" in text


def test_accepted_scope_remains_fail_closed_and_revision_bound() -> None:
    text = normalized(ACCEPTANCE)
    for phrase in (
        "revision-bound",
        "READY",
        "BLOCKED",
        "INDETERMINATE",
        "bounded offline read-only",
        "v1.3 compatibility boundaries",
        "readiness evidence from release authorization",
    ):
        assert phrase in text


def test_release_and_mutation_boundaries_remain_deferred() -> None:
    text = normalized(ACCEPTANCE)
    for phrase in (
        "version mutation",
        "tag",
        "GitHub Release",
        "package publication",
        "compatibility promotion",
        "network access",
        "repository mutation",
    ):
        assert phrase in text


def test_governance_surfaces_have_exact_acceptance_markers() -> None:
    base = "v1.4.0-release-readiness-stability-baseline-design-acceptance"
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
