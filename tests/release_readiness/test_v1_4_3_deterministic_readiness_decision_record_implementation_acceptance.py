from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = ROOT / (
    "docs/releases/v1.4.3-deterministic-readiness-decision-record-implementation-acceptance.md"
)
MERGE_SHA = "542cec89151641cd61a4d0781fa916d7945b4e76"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_acceptance_uses_exact_post_merge_evidence() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "Implementation PR #349 merged",
        MERGE_SHA,
        "Required GitHub Actions / CI completed successfully",
        "focused verification completed with 29 passed",
        "post-merge working tree remained clean",
    ):
        assert fragment in text


def test_implementation_and_acceptance_are_completed() -> None:
    text = normalized(ACCEPTANCE)
    assert "Status: Accepted / Completed" in text
    assert "Production implementation — Accepted / Completed" in text
    assert "Implementation acceptance — Accepted / Completed" in text
    assert "v1.4 feature expansion — Completed" in text


def test_accepted_scope_matches_implementation_contract() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "optional-baseline-bound decision record",
        "REVIEWABLE",
        "Fail-closed composition",
        "Stable source findings",
        "bounded offline read-only decision CLI",
        "Exit outcomes 0",
    ):
        assert fragment in text


def test_authority_and_mutation_boundaries_remain_explicit() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "does not discover inputs",
        "infer ancestry",
        "establish provenance or authenticity",
        "authorize release",
        "access networks or credentials",
        "publication state",
    ):
        assert fragment in text


def test_governance_surfaces_close_at_finish_line_without_v1_4_4() -> None:
    base = "v1.4.3-deterministic-readiness-decision-record-implementation-acceptance"
    for relative, suffix in (
        ("CHANGELOG.md", "changelog"),
        ("docs/HISTORY.md", "history"),
        ("docs/roadmap.md", "roadmap"),
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        marker = f"<!-- {base}-{suffix} -->"
        assert text.count(marker) == 1
        block = text.split(marker, 1)[1]
        assert "Implementation acceptance — Accepted / Completed" in block
        assert "Next gate — v1.4 finish-line review" in block
        assert "No v1.4.4 feature slice" in block
