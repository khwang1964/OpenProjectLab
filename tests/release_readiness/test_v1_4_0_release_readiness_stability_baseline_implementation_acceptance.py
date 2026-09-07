from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = (
    ROOT / "docs/releases/v1.4.0-release-readiness-stability-baseline-implementation.md"
)
ACCEPTANCE = (
    ROOT / "docs/releases/v1.4.0-release-readiness-stability-baseline-implementation-acceptance.md"
)
MERGE_SHA = "1f1684b3cc1f60f7f14d6c7cefc8f4e0c42f0ad6"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_implementation_and_acceptance_are_closed_with_exact_evidence() -> None:
    for text in (normalized(IMPLEMENTATION), normalized(ACCEPTANCE)):
        assert "Accepted / Completed" in text
        assert "PR #337" in text
        assert MERGE_SHA in text
        assert "20 passed" in text


def test_accepted_runtime_contract_remains_explicit() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "Strict canonical snapshots",
        "deterministic fail-closed evaluation",
        "bounded offline read-only CLI",
        "accepted production behavior",
    ):
        assert fragment in text


def test_readiness_does_not_become_release_authorization() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "evidence rather than release authorization",
        "Version mutation",
        "GitHub Releases",
        "publication",
        "network access",
        "repository mutation",
        "outside this acceptance",
    ):
        assert fragment in text


def test_governance_surfaces_have_distinct_exact_acceptance_markers() -> None:
    base = "v1.4.0-release-readiness-stability-baseline-implementation-acceptance"
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
