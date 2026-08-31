from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALIGNMENT = (
    ROOT
    / "docs/releases"
    / ("v1.3.5-v1.3.7-read-only-verification-delivery-train-terminal-alignment.md")
)
IMPLEMENTATION = (
    ROOT
    / "docs/releases"
    / ("v1.3.5-v1.3.7-read-only-verification-delivery-train-implementation.md")
)


def test_alignment_records_exact_implementation_merge_evidence() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    assert "PR #291 merged" in text
    assert "0c8ac6886ad3c21e74ea1c934b0ce5374882729b" in text
    assert "required CI completed successfully" in text
    assert "completed with 134 passed" in text


def test_alignment_is_accepted_after_merge_verification() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    assert "Accepted / Completed" in text
    assert "Implementation acceptance completed after PR #292" in text


def test_implementation_record_is_terminally_accepted() -> None:
    text = IMPLEMENTATION.read_text(encoding="utf-8")
    assert "Accepted / Completed" in text
    assert "implementation acceptance — Accepted / Completed" in text


def test_alignment_preserves_deferred_authority_boundaries() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    for phrase in (
        "no test execution, mutation, arbitrary subprocess",
        "no commit, push, merge, tag, release, publication",
        "no stable public SDK, HTTP, RPC, plugin",
    ):
        assert phrase in text


def test_governance_surfaces_share_one_exact_alignment_marker() -> None:
    marker = "v1.3.5-v1.3.7-read-only-verification-delivery-train-terminal-alignment"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Implementation acceptance" in text or "implementation acceptance" in text
