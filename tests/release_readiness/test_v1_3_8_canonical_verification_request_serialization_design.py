from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/canonical-verification-request-serialization.md"
RELEASE = ROOT / "docs/releases/v1.3.8-canonical-verification-request-serialization.md"


def test_design_defines_exact_canonical_round_trip() -> None:
    text = " ".join(ARCHITECTURE.read_text(encoding="utf-8").split())
    for phrase in (
        "existing schema-version-1 field set",
        "canonical compact UTF-8-compatible JSON",
        "round-trips through the accepted strict decoder",
    ):
        assert phrase in text


def test_design_forbids_discovery_and_io_authority() -> None:
    text = " ".join(ARCHITECTURE.read_text(encoding="utf-8").split())
    assert "performs no discovery, inference, correction, command execution" in text
    assert "file access, persistence, logging, telemetry, or publication" in text


def test_release_keeps_implementation_not_started() -> None:
    text = " ".join(RELEASE.read_text(encoding="utf-8").split())
    assert "Design First / Proposed / Pending design review" in text
    assert "Production implementation — Not Started" in text
