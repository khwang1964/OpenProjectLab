from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CLOSURE = (
    ROOT / "docs/releases" / ("v1.3.5-v1.3.7-read-only-verification-delivery-train-acceptance.md")
)
IMPLEMENTATION = (
    ROOT
    / "docs/releases"
    / ("v1.3.5-v1.3.7-read-only-verification-delivery-train-implementation.md")
)
ALIGNMENT = (
    ROOT
    / "docs/releases"
    / ("v1.3.5-v1.3.7-read-only-verification-delivery-train-terminal-alignment.md")
)


def test_all_delivery_train_records_are_terminally_accepted() -> None:
    for path in (CLOSURE, IMPLEMENTATION, ALIGNMENT):
        assert "Accepted / Completed" in path.read_text(encoding="utf-8")


def test_closure_records_exact_implementation_and_alignment_evidence() -> None:
    text = CLOSURE.read_text(encoding="utf-8")
    assert "PR #291 synchronized-main implementation verification: 134 passed" in text
    assert "0c8ac6886ad3c21e74ea1c934b0ce5374882729b" in text
    assert "PR #292 synchronized-main alignment verification: 9 passed" in text
    assert "fa4f043ba251abe91da8192bf83ee6101d2c08ba" in text


def test_closure_marks_every_required_gate_completed() -> None:
    text = CLOSURE.read_text(encoding="utf-8")
    for gate in (
        "Design Train",
        "Design Acceptance",
        "Implementation Train",
        "Terminal Alignment",
        "Required CI",
        "Synchronized-main verification",
    ):
        assert f"- {gate} — Passed / Completed" in text
    assert "Implementation Acceptance — Accepted / Completed" in text


def test_closure_preserves_deferred_authority() -> None:
    text = CLOSURE.read_text(encoding="utf-8")
    assert "stable public SDK, HTTP, RPC, plugin" in text
    assert "test execution, arbitrary subprocess, mutation" in text
    assert "automatic evidence discovery, repair, enrichment" in text


def test_governance_surfaces_share_one_exact_acceptance_marker() -> None:
    marker = "v1.3.5-v1.3.7-read-only-verification-delivery-train-acceptance"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Accepted / Completed" in text
