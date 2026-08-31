from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TRAIN = (
    ROOT
    / "docs/releases"
    / ("v1.3.8-v1.3.10-verification-request-usability-stable-cli-design-train.md")
)


def test_train_composes_three_adjacent_slices() -> None:
    text = " ".join(TRAIN.read_text(encoding="utf-8").split())
    assert "v1.3.8 — canonical serialization" in text
    assert "v1.3.9 — deterministic offline request validation" in text
    assert "v1.3.10 — stable `release-evidence` CLI" in text


def test_train_uses_accelerated_five_pr_delivery() -> None:
    text = " ".join(TRAIN.read_text(encoding="utf-8").split())
    for phrase in (
        "one Design PR",
        "one terminal Design Acceptance",
        "one implementation PR",
        "one pending terminal-alignment PR",
        "one separate final acceptance closure PR",
    ):
        assert phrase in text


def test_train_keeps_every_production_capability_not_started() -> None:
    text = " ".join(TRAIN.read_text(encoding="utf-8").split())
    assert "no production implementation in the Design Train" in text
    for relative in (
        "docs/releases/v1.3.8-canonical-verification-request-serialization.md",
        "docs/releases/v1.3.9-offline-verification-request-inspection.md",
        "docs/releases/v1.3.10-stable-release-evidence-cli-contract.md",
    ):
        assert "Production implementation — Not Started" in (ROOT / relative).read_text(
            encoding="utf-8"
        )


def test_governance_surfaces_share_one_exact_train_marker() -> None:
    marker = "v1.3.8-v1.3.10-verification-request-usability-stable-cli-design-train"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Production implementation — Not Started" in text
