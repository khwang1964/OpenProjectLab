from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = ROOT / (
    "docs/releases/v1.3.11-v1.3.13-verification-report-usability-implementation-acceptance.md"
)


def test_acceptance_record_is_terminally_complete() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert text.count("> Status: Accepted / Completed") == 1
    assert "Implementation PR #302 merged" in text
    assert "Terminal-alignment PR #303 merged" in text
    assert "Terminal-alignment post-merge verification" in text


def test_governance_surfaces_use_distinct_exact_acceptance_markers() -> None:
    suffixes = {
        "CHANGELOG.md": "changelog",
        "docs/HISTORY.md": "history",
        "docs/roadmap.md": "roadmap",
    }
    base = "v1.3.11-v1.3.13-verification-report-usability-implementation-acceptance"
    for relative, suffix in suffixes.items():
        marker = f"<!-- {base}-{suffix} -->"
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "v1.3.11-v1.3.13 implementation — Accepted / Completed" in text


def test_acceptance_preserves_deferred_authority() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "No runtime construction during offline inspection" in text
    assert "No repository mutation" in text
    assert "No stdin, persistence, batch, watch, retry, polling, or scheduling" in text
