from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALIGNMENT = (
    ROOT
    / "docs/releases"
    / ("v1.3.8-v1.3.10-verification-request-usability-stable-cli-terminal-alignment.md")
)


def test_alignment_records_exact_implementation_evidence() -> None:
    text = " ".join(ALIGNMENT.read_text(encoding="utf-8").split())
    assert "Implementation PR #296 merged" in text
    assert "verification completed with 65 passed" in text
    assert "2742 passed, 56 skipped, 1 deselected" in text
    assert "coverage 90.51%" in text


def test_alignment_records_completed_merge_verification() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    assert "Status: Aligned / Completed" in text
    assert "Terminal Alignment PR #297 merged" in text
    assert "Accepted / Completed" in text


def test_governance_alignment_markers_are_exact() -> None:
    marker = "v1.3.8-v1.3.10-verification-request-usability-stable-cli-terminal-alignment"
    surfaces = (
        ("CHANGELOG.md", "changelog"),
        ("docs/HISTORY.md", "history"),
        ("docs/roadmap.md", "roadmap"),
    )
    for relative, suffix in surfaces:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(f"<!-- {marker}-{suffix} -->") == 1
