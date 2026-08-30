from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/opt-in-verification-cli-preview.md"
RELEASE = ROOT / "docs/releases/v1.3.7-opt-in-verification-cli-preview.md"


def test_cli_design_is_accepted_and_unimplemented() -> None:
    architecture = ARCHITECTURE.read_text(encoding="utf-8")
    release = RELEASE.read_text(encoding="utf-8")
    assert "Accepted / Terminally Closed" in architecture
    assert "Status: Accepted / Completed" in release
    assert "Production implementation — Not Started" in release


def test_cli_design_defines_one_explicit_command() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "opl release-evidence verify" in text
    assert "--request <path>" in text
    assert "--format json|text" in text
    assert "No output file" in text


def test_cli_design_reuses_train_contracts_once() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "v1.3.6 strict request contract" in text
    assert "v1.3.5 service exactly once" in text
    assert "requested v1.3.6 format" in text


def test_cli_design_defines_stable_exit_statuses() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "Exit status `0`" in text
    assert "Exit status `1`" in text
    assert "Exit status `2`" in text
    assert "Output and exit status must agree" in text


def test_cli_design_preserves_read_only_authority() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "only the v1.3.4 accepted read commands" in text
    assert "cannot execute" in text
    assert "tests or arbitrary commands" in text
    assert "cannot commit, push, merge, tag, release, publish" in text
    assert "prompt for credentials" in text


def test_cli_governance_surfaces_share_exact_markers() -> None:
    marker = "v1.3.7-opt-in-verification-cli-preview-design"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Production implementation — Not Started" in text
