from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = ROOT / (
    "docs/releases/v1.4.3-deterministic-readiness-decision-record-design-acceptance.md"
)
MERGE_SHA = "ce7feac4e7f47760624852bd382216e634bcbfb5"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_acceptance_uses_exact_post_merge_evidence() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "Design PR #347 merged",
        MERGE_SHA,
        "Required GitHub Actions / CI completed successfully",
        "focused Design First verification completed with 6 passed",
        "post-merge working tree remained clean",
    ):
        assert fragment in text


def test_design_is_accepted_without_implementation_claim() -> None:
    text = normalized(ACCEPTANCE)
    assert "Status: Accepted / Completed" in text
    assert "Design — Accepted / Completed" in text
    assert "Production implementation — Not Started" in text


def test_accepted_scope_preserves_decision_record_contract() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "repository- and revision-bound",
        "REVIEWABLE",
        "BLOCKED",
        "INDETERMINATE",
        "accepted evaluation and optional comparison evidence",
        "Bounded offline read-only decision CLI",
    ):
        assert fragment in text


def test_authority_and_finish_line_boundaries_remain_explicit() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "No input discovery",
        "ancestry inference",
        "release approval",
        "credential or network access",
        "publication",
        "final planned v1.4 feature slice",
        "finish-line review",
    ):
        assert fragment in text


def test_governance_surfaces_have_exact_acceptance_markers() -> None:
    base = "v1.4.3-deterministic-readiness-decision-record-design-acceptance"
    for relative, suffix in (
        ("CHANGELOG.md", "changelog"),
        ("docs/HISTORY.md", "history"),
        ("docs/roadmap.md", "roadmap"),
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        marker = f"<!-- {base}-{suffix} -->"
        assert text.count(marker) == 1
        block = text.split(marker, 1)[1]
        assert "Design — Accepted / Completed" in block
        assert "Production implementation — Not Started" in block
