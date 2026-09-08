from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / "docs/releases/v1.4-finish-line-review.md"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_review_preserves_pending_two_pr_boundary() -> None:
    text = normalized(REVIEW)
    assert "Status: Pending / Awaiting post-merge verification" in text
    assert "Finish-line acceptance closure — Pending / Separate PR" in text


def test_all_planned_v1_4_slices_are_confirmed_accepted() -> None:
    text = normalized(REVIEW)
    for version in ("v1.4.0", "v1.4.1", "v1.4.2", "v1.4.3"):
        assert version in text
    assert text.count("Accepted / Completed") == 4


def test_exact_terminal_evidence_is_recorded() -> None:
    text = normalized(REVIEW)
    assert "PR #350 merged" in text
    assert "7bfea727199843b0932ea92a001dc83df8964a99" in text
    assert "34 passed" in text
    assert "clean tree" in text


def test_enough_to_stop_is_explicit() -> None:
    text = normalized(REVIEW)
    for fragment in (
        "focused v1.4 contract suite",
        "full regression",
        "configured coverage threshold",
        "No verified release blocker",
        "silent v1.4.4 expansion",
        "Optional improvements remain deferred",
    ):
        assert fragment in text


def test_release_mutations_remain_unauthorized() -> None:
    text = normalized(REVIEW)
    for fragment in (
        "does not change package versions",
        "create a tag",
        "publish artifacts",
        "create a GitHub Release",
        "authorize publication",
        "v1.4 release mutation — Not authorized",
    ):
        assert fragment in text


def test_governance_surfaces_have_exact_pending_markers() -> None:
    for relative, suffix in (
        ("CHANGELOG.md", "changelog"),
        ("docs/HISTORY.md", "history"),
        ("docs/roadmap.md", "roadmap"),
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        marker = f"<!-- v1.4-finish-line-review-{suffix} -->"
        assert text.count(marker) == 1
        block = text.split(marker, 1)[1]
        assert "Pending / Awaiting post-merge verification" in block
        assert "Finish-line acceptance closure — Pending / Separate PR" in block
