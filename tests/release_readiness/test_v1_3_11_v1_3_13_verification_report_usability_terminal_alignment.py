from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALIGNMENT = ROOT / (
    "docs/releases/v1.3.11-v1.3.13-verification-report-usability-terminal-alignment.md"
)
IMPLEMENTATION = ROOT / (
    "docs/releases/v1.3.11-v1.3.13-verification-report-usability-implementation.md"
)


def test_alignment_has_exact_pending_status() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    status = "> Status: Pending / Awaiting terminal-alignment merge and verification"
    assert text.count(status) == 1
    assert "A separate implementation-acceptance closure PR remains required" in text


def test_implementation_record_tracks_completed_evidence_and_pending_closure() -> None:
    text = IMPLEMENTATION.read_text(encoding="utf-8")
    assert "Implementation PR #302 merge and required CI — Completed" in text
    assert "Synchronized-main focused post-merge verification — Completed" in text
    assert "acceptance closure — Pending" in text


def test_governance_surfaces_use_exact_unique_alignment_markers() -> None:
    suffixes = {
        "CHANGELOG.md": "changelog",
        "docs/HISTORY.md": "history",
        "docs/roadmap.md": "roadmap",
    }
    base = "v1.3.11-v1.3.13-verification-report-usability-terminal-alignment"
    for relative, suffix in suffixes.items():
        marker = f"<!-- {base}-{suffix} -->"
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "terminal-alignment merge and verification remain pending" in text


def test_alignment_preserves_deferred_authority() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    assert "runtime-free" in text
    assert "Stable report-result exit categories remain 0, 1, and 2" in text
