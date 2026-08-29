from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / (
    "docs/releases/v1.3.2-repository-github-evidence-adapters-implementation-acceptance.md"
)


def test_implementation_acceptance_is_terminally_completed() -> None:
    text = RECORD.read_text(encoding="utf-8")

    assert "> Status: Accepted / Completed" in text
    assert "Status: Pending" not in text
    assert "## Completed closure gates" in text


def test_record_cites_implementation_and_alignment_merges() -> None:
    text = RECORD.read_text(encoding="utf-8")

    assert "a87251ed7714f6516ca19023d585bb3043744661" in text
    assert "ec52e25dfbe911033e0b049701fb1df3171c1268" in text
    assert "24 focused tests" in text


def test_record_cites_successful_required_ci() -> None:
    text = RECORD.read_text(encoding="utf-8")

    assert "CI workflow run #568 completed successfully" in text
    assert "Terminal-alignment PR required CI — Passed" in text


def test_record_preserves_read_only_and_fail_closed_boundaries() -> None:
    text = RECORD.read_text(encoding="utf-8")

    assert "remains read-only" in text
    assert "fails closed" in text
    assert "Merge authorization remains explicit" in text
    assert "mutation remains deferred" in text


def test_governance_surfaces_share_the_completed_state() -> None:
    marker = "v1.3.2-repository-github-evidence-adapters-implementation-closure"

    for relative_path in ("CHANGELOG.md", "docs/HISTORY.md", "docs/roadmap.md"):
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Implementation acceptance — Accepted / Completed" in text
