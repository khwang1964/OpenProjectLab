from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / (
    "docs/releases/v1.3.4-read-only-verification-runtime-wiring-implementation.md"
)
ALIGNMENT = ROOT / (
    "docs/releases/v1.3.4-read-only-verification-runtime-wiring-implementation-alignment.md"
)


def test_alignment_is_verified_after_merge() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    assert text.count("> Status: Verified / Completed") == 1
    assert "Post-merge focused verification — 42 passed" in text


def test_alignment_cites_exact_implementation_evidence() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    assert "PR #286" in text
    assert "8e944d73f241523f8e82c4cb5792501d76ad7ae1" in text
    assert "CI/Packaging artifact verification" in text
    assert "CI/Quality checks (pull_request)" in text
    assert "2646 passed, 56 skipped" in text
    assert "1 deselected" in text
    assert "90.60%" in text
    assert "37 passed" in text


def test_implementation_record_is_accepted() -> None:
    text = IMPLEMENTATION.read_text(encoding="utf-8")
    assert "> Status: Accepted / Completed" in text
    assert "Separate implementation acceptance closure — Recorded" in text


def test_alignment_preserves_deferred_authority() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    assert "Only the accepted Git and GitHub read commands are allowed" in text
    assert "No CLI, public SDK, arbitrary subprocess, mutation" in text
    assert "Runtime construction performs no command or verification" in text


def test_governance_surfaces_share_exact_alignment_markers() -> None:
    marker = "v1.3.4-read-only-verification-runtime-wiring-implementation-alignment"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Awaiting implementation acceptance" in text
