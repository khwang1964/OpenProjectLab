from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ACCEPTANCE = ROOT / (
    "docs/releases/v1.3.14-v1.3.16-verification-report-auditability-design-acceptance.md"
)


def test_design_acceptance_is_terminally_complete() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert text.count("> Status: Accepted / Completed") == 1
    assert "Design PR #305 merged" in text
    assert "Synchronized-main focused Design verification" in text
    assert "Production implementation remains Not Started" in text


def test_security_non_claims_remain_explicit() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "No signature, key, certificate, identity, trust" in text
    assert "authenticity, or attestation claim" in text
    assert "No runtime, repository discovery, network" in text


def test_governance_surfaces_use_exact_unique_acceptance_markers() -> None:
    suffixes = {
        "CHANGELOG.md": "changelog",
        "docs/HISTORY.md": "history",
        "docs/roadmap.md": "roadmap",
    }
    base = "v1.3.14-v1.3.16-verification-report-auditability-design-acceptance"
    for relative, suffix in suffixes.items():
        marker = f"<!-- {base}-{suffix} -->"
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Production implementation — Not Started" in text
