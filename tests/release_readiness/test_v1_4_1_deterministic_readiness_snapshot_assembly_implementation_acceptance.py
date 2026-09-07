from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = (
    ROOT
    / "docs/releases/v1.4.1-deterministic-readiness-snapshot-assembly-implementation-acceptance.md"
)
SHA = "4e02b11ec2386c0991e70fd5e25c09f00b078779"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_acceptance_records_exact_evidence_and_platform_skip() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "PR #341",
        SHA,
        "17 passed",
        "1 skipped",
        "Windows no-symlink",
        "working tree remained clean",
    ):
        assert fragment in text


def test_scope_and_authority_remain_explicit() -> None:
    text = normalized(ACCEPTANCE)
    for fragment in (
        "canonical evidence manifest",
        "bounded evidence reader",
        "safe path containment",
        "revision-bound assembler",
        "fail-closed findings",
        "offline read-only CLI",
        "evaluation and release authorization remain separate",
    ):
        assert fragment in text


def test_governance_markers_are_exact_and_unique() -> None:
    base = "v1.4.1-deterministic-readiness-snapshot-assembly-implementation-acceptance"
    for relative, suffix in (
        ("CHANGELOG.md", "changelog"),
        ("docs/HISTORY.md", "history"),
        ("docs/roadmap.md", "roadmap"),
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        marker = f"<!-- {base}-{suffix} -->"
        assert text.count(marker) == 1
        assert "Implementation acceptance — Accepted / Completed" in text.split(marker, 1)[1]
