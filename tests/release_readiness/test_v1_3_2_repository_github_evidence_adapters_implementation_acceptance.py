from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / (
    "docs/releases/v1.3.2-repository-github-evidence-adapters-implementation-acceptance.md"
)


def test_pending_implementation_acceptance_record_exists() -> None:
    text = RECORD.read_text(encoding="utf-8")

    assert "Status: Pending" in text
    assert "Awaiting terminal-alignment merge and post-merge verification" in text
    assert "> Status: Accepted / Completed" not in text


def test_record_cites_current_implementation_evidence() -> None:
    text = RECORD.read_text(encoding="utf-8")

    assert "PR #276" in text
    assert "a87251ed7714f6516ca19023d585bb3043744661" in text
    assert "7 focused tests" in text


def test_record_preserves_read_only_and_fail_closed_boundaries() -> None:
    text = RECORD.read_text(encoding="utf-8")

    assert "remains read-only" in text
    assert "fails closed" in text
    assert "Merge authorization remains explicit" in text
    assert "mutation remains deferred" in text


def test_record_keeps_post_merge_gates_pending() -> None:
    text = RECORD.read_text(encoding="utf-8")

    assert "Terminal-alignment PR required CI — Pending" in text
    assert "Terminal-alignment PR merge identity — Pending" in text
    assert "Synchronized-main post-merge focused verification — Pending" in text
    assert "Separate acceptance-closure PR — Pending" in text


def test_governance_surfaces_share_the_pending_alignment_state() -> None:
    marker = "v1.3.2-repository-github-evidence-adapters-implementation-alignment"

    for relative_path in ("CHANGELOG.md", "docs/HISTORY.md", "docs/roadmap.md"):
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Implementation acceptance — Pending" in text
