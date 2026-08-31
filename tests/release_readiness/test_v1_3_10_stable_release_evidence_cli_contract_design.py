from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/stable-release-evidence-cli-contract.md"
RELEASE = ROOT / "docs/releases/v1.3.10-stable-release-evidence-cli-contract.md"


def test_design_defines_both_exact_stable_commands() -> None:
    text = " ".join(ARCHITECTURE.read_text(encoding="utf-8").split())
    assert "opl release-evidence verify --request <path> --format json|text" in text
    assert "opl release-evidence request validate --request <path> --format json|text" in text


def test_design_preserves_stream_exit_and_installation_contracts() -> None:
    text = " ".join(ARCHITECTURE.read_text(encoding="utf-8").split())
    assert "installed-package and source-tree invocation" in text
    assert "exit `1` remains exclusive" in text
    assert "English and zh-TW manuals" in text


def test_design_preserves_read_only_and_offline_authority() -> None:
    text = " ".join(ARCHITECTURE.read_text(encoding="utf-8").split())
    assert "retains the v1.3.4" in text
    assert "request validate` remains fully offline" in text
    assert "No mutation, discovery, retry, persistence, or publication" in text


def test_release_keeps_implementation_not_started() -> None:
    text = " ".join(RELEASE.read_text(encoding="utf-8").split())
    assert "Design First / Proposed / Pending design review" in text
    assert "Production implementation — Not Started" in text
