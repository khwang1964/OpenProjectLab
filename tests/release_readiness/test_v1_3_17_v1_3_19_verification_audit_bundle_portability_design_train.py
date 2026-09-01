from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/verification-audit-bundle-portability.md"
RELEASE = (
    ROOT / "docs/releases/v1.3.17-v1.3.19-verification-audit-bundle-portability-design-train.md"
)


def test_design_defines_three_integrated_slices() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "v1.3.17 — Immutable bundle and canonical codec" in text
    assert "v1.3.18 — Offline consistency validation" in text
    assert "v1.3.19 — Stable CLI boundary" in text


def test_bundle_contract_is_canonical_and_fail_closed() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "UTF-8" in text
    assert "sorted keys" in text
    assert "rejects duplicate or unknown fields" in text
    assert "lowercase SHA-256 digest" in text
    assert "fail-closed" in text


def test_validation_is_offline_and_recomputes_evidence() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "Every embedded fingerprint is recomputed" in text
    assert "performs no network" in text
    assert "repository mutation" in text


def test_cli_contract_has_stable_commands_and_exit_classes() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "release-evidence bundle create" in text
    assert "release-evidence bundle inspect" in text
    assert "release-evidence bundle validate" in text
    assert "returns 0 for a valid bundle" in text
    assert "1 for recorded semantic inconsistency" in text
    assert "2 for input, document, or usage errors" in text


def test_security_non_claims_are_explicit() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    for fragment in (
        "No archive extraction",
        "No signing",
        "authentication",
        "provenance",
        "attestation",
        "encryption",
    ):
        assert fragment in text


def test_production_implementation_remains_not_started() -> None:
    release = RELEASE.read_text(encoding="utf-8")
    assert "Status: Proposed / Pending design review" in release
    assert "Production implementation — Not Started" in release


def test_governance_surfaces_use_exact_unique_markers() -> None:
    base = "v1.3.17-v1.3.19-verification-audit-bundle-portability-design-train"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, exact_marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Production implementation — Not Started" in text
