from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IMPLEMENTATION = ROOT / (
    "docs/releases/v1.3.3-release-evidence-verification-orchestration-implementation.md"
)
ALIGNMENT = ROOT / (
    "docs/releases/v1.3.3-release-evidence-verification-orchestration-implementation-alignment.md"
)


def test_alignment_is_verified_after_merge() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    assert text.count("> Status: Verified / Completed") == 1
    assert "Post-merge focused verification — 41 passed" in text


def test_alignment_cites_exact_implementation_evidence() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    assert "PR #281" in text
    assert "1441c362923f16d704f817e302ef22fbb829782a" in text
    assert "workflow run #576 completed successfully" in text
    assert "2610 passed, 56 skipped, 1 deselected" in text
    assert "90.64%" in text
    assert "36 passed" in text


def test_implementation_record_is_accepted() -> None:
    text = IMPLEMENTATION.read_text(encoding="utf-8")
    assert "Status: Accepted / Completed" in text
    assert "Separate implementation acceptance closure — Recorded" in text


def test_alignment_preserves_deferred_authority() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    assert "Focused-test evidence remains caller supplied" in text
    assert "No test execution, CLI, public SDK, Git/GitHub mutation" in text


def test_governance_surfaces_share_one_alignment_marker() -> None:
    marker = "v1.3.3-release-evidence-verification-orchestration-implementation-alignment"
    surfaces = {
        "CHANGELOG.md": (
            f"<!-- {marker}-changelog -->",
            "Status — Implemented / Awaiting implementation acceptance.",
        ),
        "docs/HISTORY.md": (
            f"<!-- {marker}-history -->",
            "Implementation acceptance — Awaiting terminal-alignment merge",
        ),
        "docs/roadmap.md": (
            f"<!-- {marker}-roadmap -->",
            "Status — Implemented / Awaiting implementation acceptance.",
        ),
    }

    for relative, (exact_marker, expected_state) in surfaces.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert expected_state in text
