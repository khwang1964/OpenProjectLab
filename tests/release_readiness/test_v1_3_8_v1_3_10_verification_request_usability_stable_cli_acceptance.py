from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = (
    ROOT
    / "docs/releases"
    / "v1.3.8-v1.3.10-verification-request-usability-stable-cli-acceptance.md"
)


def test_acceptance_records_exact_delivery_train_evidence() -> None:
    text = " ".join(ACCEPTANCE.read_text(encoding="utf-8").split())
    assert "Implementation PR #296 merged" in text
    assert "Terminal Alignment PR #297 merged" in text
    assert "5168298743b3686ebc625588a87c1d2bc509578e" in text
    assert "2742 passed, 56 skipped, 1 deselected" in text
    assert "90.51%" in text


def test_acceptance_is_terminally_completed() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Status: Accepted / Completed" in text
    assert "PR #297 required CI completed successfully" in text
    assert "post-merge terminal-alignment verification passed" in text


def test_acceptance_preserves_read_only_authority() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "No automatic request discovery or arbitrary subprocess execution" in text
    assert "Merge authorization remains explicit" in text


def test_governance_surfaces_share_one_exact_acceptance_marker() -> None:
    marker = "v1.3.8-v1.3.10-verification-request-usability-stable-cli-acceptance"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Accepted / Completed" in text


def test_implementation_and_alignment_records_are_closed() -> None:
    implementation = (
        ROOT
        / "docs/releases"
        / "v1.3.8-v1.3.10-verification-request-usability-stable-cli-implementation.md"
    ).read_text(encoding="utf-8")
    alignment = (
        ROOT
        / "docs/releases"
        / ("v1.3.8-v1.3.10-verification-request-usability-stable-cli-terminal-alignment.md")
    ).read_text(encoding="utf-8")
    assert "Status: Accepted / Completed" in implementation
    assert "Status: Aligned / Completed" in alignment
