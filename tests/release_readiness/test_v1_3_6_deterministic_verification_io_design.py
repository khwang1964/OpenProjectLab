from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/deterministic-verification-io-contracts.md"
RELEASE = ROOT / "docs/releases/v1.3.6-deterministic-verification-io-contracts.md"


def test_io_design_remains_pending_and_unimplemented() -> None:
    architecture = ARCHITECTURE.read_text(encoding="utf-8")
    release = RELEASE.read_text(encoding="utf-8")
    assert "Proposed / Pending design review" in architecture
    assert "Status: Proposed / Pending design review" in release
    assert "Production implementation — Not Started" in release


def test_io_design_requires_strict_versioned_schemas() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "one explicit schema version" in text
    assert "exact required keys" in text
    assert "rejection of unknown keys" in text
    assert "native JSON types" in text


def test_io_design_requires_deterministic_output() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "stable field names" in text
    assert "canonical compact JSON" in text
    assert "exactly one newline" in text
    assert "stable text rendering" in text


def test_io_design_preserves_failure_categories() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "Collection, contradiction, and validation findings" in text
    assert "retain separate categories" in text
    assert "same status" in text


def test_io_design_preserves_deferred_authority() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "production implementation" in text
    assert "CLI, public SDK, HTTP, RPC, plugin" in text
    assert "file writes, persistence, caching" in text
    assert "arbitrary subprocess execution" in text


def test_io_governance_surfaces_share_exact_markers() -> None:
    marker = "v1.3.6-deterministic-verification-io-contracts-design"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Production implementation — Not Started" in text
