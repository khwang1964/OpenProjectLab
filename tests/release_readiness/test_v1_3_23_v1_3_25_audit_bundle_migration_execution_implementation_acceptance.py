from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASES = ROOT / "docs/releases"
ACCEPTANCE = RELEASES / (
    "v1.3.23-v1.3.25-audit-bundle-migration-execution-implementation-acceptance.md"
)
IMPLEMENTATION = RELEASES / ("v1.3.23-v1.3.25-audit-bundle-migration-execution-implementation.md")
ALIGNMENT = RELEASES / ("v1.3.23-v1.3.25-audit-bundle-migration-execution-terminal-alignment.md")


def test_acceptance_records_terminal_evidence() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Status: Accepted / Completed" in text
    assert "Terminal-alignment PR: [#323]" in text
    assert "541356262fa0aa5a3a861017e8ac8f9514871592" in text
    assert "39 passed" in text


def test_prior_records_have_terminal_states() -> None:
    assert "Status: Accepted / Completed" in IMPLEMENTATION.read_text(encoding="utf-8")
    assert "Completed / Verified after merge" in ALIGNMENT.read_text(encoding="utf-8")


def test_accepted_boundary_remains_explicit() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    text = " ".join(text.split())
    for phrase in (
        "explicit",
        "`--execute`",
        "distinct, non-existing output path",
        "Source rewriting",
        "signing",
        "trust",
        "provenance",
        "network access",
        "repository mutation",
    ):
        assert phrase in text


def test_governance_surfaces_use_exact_unique_acceptance_markers() -> None:
    base = "v1.3.23-v1.3.25-audit-bundle-migration-execution-implementation-acceptance"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Implementation acceptance — Accepted / Completed" in text
