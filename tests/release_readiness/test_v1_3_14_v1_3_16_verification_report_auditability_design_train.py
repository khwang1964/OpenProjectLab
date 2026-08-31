from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/verification-report-auditability.md"
RELEASE = ROOT / ("docs/releases/v1.3.14-v1.3.16-verification-report-auditability-design-train.md")


def test_design_composes_three_non_overlapping_slices() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "v1.3.14 — Canonical report fingerprint" in text
    assert "v1.3.15 — Offline semantic report comparison" in text
    assert "v1.3.16 — Stable audit CLI" in text


def test_fingerprint_has_explicit_security_non_claims() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "lowercase SHA-256 hexadecimal fingerprint" in text
    assert "not a signature, identity, trust, or authenticity claim" in text
    assert "no digital signature, key, certificate" in text


def test_comparison_is_semantic_deterministic_and_offline() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "stable field path" in text
    assert "owns no runtime, repository adapter, network, cache" in text
    assert "immutable comparison" in text


def test_cli_preserves_stable_result_categories_and_existing_behavior() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "exit 0 for success/equality" in text
    assert "1 for a valid semantic difference" in text
    assert "2 for" in text
    assert "report validate` behavior" in text


def test_release_baseline_remains_pending_and_unimplemented() -> None:
    text = RELEASE.read_text(encoding="utf-8")
    assert text.count("> Status: Proposed / Pending Design Acceptance") == 1
    assert "Production implementation remains Not Started" in text
    assert "Separate terminal Design Acceptance PR" in text


def test_governance_surfaces_use_distinct_exact_markers() -> None:
    suffixes = {
        "CHANGELOG.md": "changelog",
        "docs/HISTORY.md": "history",
        "docs/roadmap.md": "roadmap",
    }
    base = "v1.3.14-v1.3.16-verification-report-auditability-design-train"
    for relative, suffix in suffixes.items():
        marker = f"<!-- {base}-{suffix} -->"
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Production implementation — Not Started" in text
