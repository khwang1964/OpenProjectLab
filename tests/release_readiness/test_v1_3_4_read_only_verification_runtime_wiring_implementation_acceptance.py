from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = ROOT / (
    "docs/releases/v1.3.4-read-only-verification-runtime-wiring-implementation-acceptance.md"
)


def test_implementation_is_formally_accepted() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert text.count("> Status: Accepted / Completed") == 1


def test_acceptance_cites_implementation_evidence() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "PR #286" in text
    assert "8e944d73f241523f8e82c4cb5792501d76ad7ae1" in text
    assert "2646 passed, 56 skipped, 1 deselected" in text
    assert "90.60%" in text
    assert "37 passed" in text


def test_acceptance_cites_alignment_evidence() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "PR #287" in text
    assert "89d16d61f5be0559faf0e87f8740a19378ac0717" in text
    assert "2651 passed, 56 skipped, 1 deselected" in text
    assert "42 passed" in text


def test_acceptance_preserves_deferred_authority() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "No CLI, public SDK, arbitrary subprocess, mutation" in text
    assert "No retry, polling, persistence, caching, telemetry" in text
    assert "No authority to execute verification" in text


def test_governance_surfaces_share_exact_closure_markers() -> None:
    marker = "v1.3.4-read-only-verification-runtime-wiring-implementation-closure"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Accepted / Completed" in text
