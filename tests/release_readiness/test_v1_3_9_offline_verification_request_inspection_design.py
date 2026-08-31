from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/offline-verification-request-inspection.md"
RELEASE = ROOT / "docs/releases/v1.3.9-offline-verification-request-inspection.md"


def test_design_defines_exact_offline_command() -> None:
    text = " ".join(ARCHITECTURE.read_text(encoding="utf-8").split())
    command = "opl release-evidence request validate --request <path> --format json|text"
    assert command in text
    assert "return exit status `0` for valid input or `2`" in text


def test_design_cannot_reach_runtime_or_commands() -> None:
    text = " ".join(ARCHITECTURE.read_text(encoding="utf-8").split())
    assert "never builds a verification runtime" in text
    assert "never invokes Git, GitHub, pytest" in text
    assert "cannot write an output file" in text


def test_release_keeps_implementation_not_started() -> None:
    text = " ".join(RELEASE.read_text(encoding="utf-8").split())
    assert "Design First / Proposed / Pending design review" in text
    assert "Production implementation — Not Started" in text
