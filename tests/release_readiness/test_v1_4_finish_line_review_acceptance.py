from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = ROOT / "docs/releases/v1.4-finish-line-review-acceptance.md"
MERGE_SHA = "4382f14d3e2c1e6f562fcfa14a5e11dbfb607845"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_acceptance_uses_exact_post_merge_evidence() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "PR #351 merged",
        MERGE_SHA,
        "Required GitHub Actions / CI completed successfully",
        "Seventeen v1.4 focused files",
        "119 passed and 1 skipped",
        "post-merge working tree remained clean",
    ):
        assert fragment in text


def test_finish_line_and_train_are_completed() -> None:
    text = normalized(ACCEPTANCE)
    assert "Status: Accepted / Completed" in text
    assert "v1.4 finish-line review — Accepted / Completed" in text
    assert "v1.4 development train — Accepted / Completed" in text


def test_enough_to_stop_is_accepted() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "v1.4.0 through v1.4.3",
        "full regression",
        "configured coverage",
        "No verified release blocker",
        "Feature expansion is frozen",
        "Additional v1.4 feature slice — Not required",
    ):
        assert fragment in text


def test_release_mutations_remain_separate_and_unauthorized() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "does not change package versions",
        "create a tag",
        "publish artifacts",
        "create a GitHub Release",
        "authorize publication",
        "Release mutation — Not authorized",
    ):
        assert fragment in text


def test_next_gate_allows_project_stop_without_scope_expansion() -> None:
    text = normalized(ACCEPTANCE)
    assert "Next gate — Explicitly authorized release planning or project stop" in text
    assert "Additional v1.4 feature slice — Not required" in text


def test_governance_surfaces_have_exact_acceptance_markers() -> None:
    for relative, suffix in (
        ("CHANGELOG.md", "changelog"),
        ("docs/HISTORY.md", "history"),
        ("docs/roadmap.md", "roadmap"),
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        marker = f"<!-- v1.4-finish-line-review-acceptance-{suffix} -->"
        assert text.count(marker) == 1
        block = text.split(marker, 1)[1]
        assert "v1.4 development train — Accepted / Completed" in block
        assert "Next gate — Explicitly authorized release planning or project stop" in block
        assert "Release mutation — Not authorized" in block
