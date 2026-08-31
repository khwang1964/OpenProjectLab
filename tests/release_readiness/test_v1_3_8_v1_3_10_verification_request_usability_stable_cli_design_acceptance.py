from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = (
    ROOT
    / "docs/releases"
    / ("v1.3.8-v1.3.10-verification-request-usability-stable-cli-design-acceptance.md")
)
TRAIN = (
    ROOT
    / "docs/releases"
    / ("v1.3.8-v1.3.10-verification-request-usability-stable-cli-design-train.md")
)


def test_all_design_records_are_terminally_accepted() -> None:
    assert "Design Accepted / Completed" in TRAIN.read_text(encoding="utf-8")
    for relative in (
        "docs/releases/v1.3.8-canonical-verification-request-serialization.md",
        "docs/releases/v1.3.9-offline-verification-request-inspection.md",
        "docs/releases/v1.3.10-stable-release-evidence-cli-contract.md",
    ):
        assert "Design Accepted / Completed" in (ROOT / relative).read_text(encoding="utf-8")


def test_acceptance_records_exact_pr_and_post_merge_evidence() -> None:
    text = " ".join(ACCEPTANCE.read_text(encoding="utf-8").split())
    assert "Design Train PR #294 merged" in text
    assert "required CI completed successfully" in text
    assert "verification completed with 14 passed" in text


def test_acceptance_keeps_production_not_started() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Production implementation remains Not Started" in text
    assert "automatic discovery, tests, arbitrary subprocesses, mutation" in text


def test_architectures_are_terminally_closed() -> None:
    for relative in (
        "docs/architecture/canonical-verification-request-serialization.md",
        "docs/architecture/offline-verification-request-inspection.md",
        "docs/architecture/stable-release-evidence-cli-contract.md",
    ):
        assert "Accepted / Terminally Closed" in (ROOT / relative).read_text(encoding="utf-8")


def test_governance_surfaces_share_one_exact_acceptance_marker() -> None:
    marker = "v1.3.8-v1.3.10-verification-request-usability-stable-cli-design-acceptance"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Production implementation" in text
