from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = ROOT / (
    "docs/releases/v1.4.2-deterministic-readiness-snapshot-comparison-implementation-acceptance.md"
)
MERGE_SHA = "1775e597ab220f118c656a5fc7b711cd2c091d95"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_acceptance_uses_exact_post_merge_evidence() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "Implementation PR #345 merged",
        MERGE_SHA,
        "Required GitHub Actions / CI completed successfully",
        "focused verification completed with 30 passed",
        "post-merge working tree remained clean",
    ):
        assert fragment in text


def test_implementation_and_acceptance_are_completed() -> None:
    text = normalized(ACCEPTANCE)
    assert "Status: Accepted / Completed" in text
    assert "Production implementation — Accepted / Completed" in text
    assert "Implementation acceptance — Accepted / Completed" in text
    assert "Next roadmap slice — Pending explicit Design First definition" in text


def test_accepted_scope_matches_implementation_contract() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "comparison categories",
        "Gate-level comparison",
        "Fail-closed repository mismatch",
        "Stable JSON/text rendering",
        "bounded offline read-only comparison CLI",
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


def test_governance_surfaces_have_exact_acceptance_markers() -> None:
    base = "v1.4.2-deterministic-readiness-snapshot-comparison-implementation-acceptance"
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
        assert "Next roadmap slice — Pending explicit Design First definition" in block
