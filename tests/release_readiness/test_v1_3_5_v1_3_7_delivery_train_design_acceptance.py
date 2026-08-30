from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = ROOT / (
    "docs/releases/v1.3.5-v1.3.7-read-only-verification-delivery-train-design-acceptance.md"
)


def test_train_design_is_formally_accepted() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert text.count("> Status: Accepted / Completed") == 1


def test_acceptance_cites_exact_design_train_evidence() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "PR #289" in text
    assert "aada1068cd4452b264ba612deff7deab455cfb31" in text
    assert "Required CI checks completed successfully" in text
    assert "22 passed" in text


def test_acceptance_covers_all_three_capabilities() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "v1.3.5 — stateless" in text
    assert "v1.3.6 — strict deterministic" in text
    assert "v1.3.7 — explicit opt-in" in text


def test_acceptance_preserves_read_only_boundaries() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "No arbitrary subprocess or test execution" in text
    assert "No Git/GitHub mutation" in text
    assert "No retry, polling, queue, cache" in text
    assert "Production implementation — Not Started" in text


def test_every_design_surface_is_terminally_accepted() -> None:
    surfaces = (
        "docs/architecture/read-only-verification-invocation.md",
        "docs/architecture/deterministic-verification-io-contracts.md",
        "docs/architecture/opt-in-verification-cli-preview.md",
        "docs/releases/v1.3.5-read-only-verification-invocation.md",
        "docs/releases/v1.3.6-deterministic-verification-io-contracts.md",
        "docs/releases/v1.3.7-opt-in-verification-cli-preview.md",
    )
    for relative in surfaces:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "Accepted" in text


def test_governance_surfaces_share_exact_acceptance_markers() -> None:
    marker = "v1.3.5-v1.3.7-delivery-train-design-acceptance"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Accepted / Completed" in text
