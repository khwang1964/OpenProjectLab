from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/read-only-verification-runtime-wiring.md"
RELEASE = ROOT / "docs/releases/v1.3.4-read-only-verification-runtime-wiring.md"
ACCEPTANCE = ROOT / (
    "docs/releases/v1.3.4-read-only-verification-runtime-wiring-design-acceptance.md"
)


def test_design_is_terminally_accepted() -> None:
    assert "Accepted / Terminally Closed" in ARCHITECTURE.read_text(encoding="utf-8")
    assert "Status: Accepted / Completed" in RELEASE.read_text(encoding="utf-8")
    assert "Status: Accepted / Completed" in ACCEPTANCE.read_text(encoding="utf-8")


def test_acceptance_cites_exact_design_evidence() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "PR #284" in text
    assert "247e899f6034e7159a843056c40290b3c42b7dce" in text
    assert "workflow run #582 completed successfully" in text
    assert "2626 passed, 56 skipped, 1 deselected" in text
    assert "90.64%" in text
    assert "6 passed" in text


def test_acceptance_preserves_deferred_authority() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Production implementation — Not Started" in text
    assert "No automatic verification, pytest, coverage" in text
    assert "No CLI, public SDK, Git/GitHub mutation" in text
    assert "credential management" in text


def test_acceptance_authorizes_only_minimum_implementation() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "minimum v1.3.4 production implementation" in text
    assert "new explicit Design First decision" in text


def test_governance_surfaces_share_one_acceptance_marker() -> None:
    marker = "v1.3.4-read-only-verification-runtime-wiring-design-acceptance"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Production implementation — Not Started" in text
