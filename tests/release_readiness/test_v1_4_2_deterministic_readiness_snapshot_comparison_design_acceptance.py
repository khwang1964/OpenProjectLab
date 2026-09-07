from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = ROOT / (
    "docs/releases/v1.4.2-deterministic-readiness-snapshot-comparison-design-acceptance.md"
)
MERGE_SHA = "c0ea20f38daf283db340281888e0d9898bee1f43"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_acceptance_uses_exact_post_merge_evidence() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "Design PR #343 merged",
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


def test_accepted_scope_preserves_comparison_contract() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "baseline and candidate repository identities and revisions",
        "UNCHANGED",
        "IMPROVED",
        "REGRESSED",
        "INCOMPARABLE",
        "Fail-closed readiness-gate regression",
        "Bounded offline read-only comparison CLI",
    ):
        assert fragment in text


def test_deferred_authority_and_mutation_boundaries_remain_explicit() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "remote evidence collection",
        "Git/GitHub mutation",
        "credential or network access",
        "ancestry or authenticity proof",
        "gate waiver",
        "publication",
    ):
        assert fragment in text


def test_governance_surfaces_have_exact_acceptance_markers() -> None:
    base = "v1.4.2-deterministic-readiness-snapshot-comparison-design-acceptance"
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
