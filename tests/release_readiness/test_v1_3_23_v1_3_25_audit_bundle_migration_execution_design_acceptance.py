from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/audit-bundle-migration-execution.md"
RELEASES = ROOT / "docs/releases"
BASELINE = RELEASES / ("v1.3.23-v1.3.25-audit-bundle-migration-execution-design-train.md")
ACCEPTANCE = RELEASES / ("v1.3.23-v1.3.25-audit-bundle-migration-execution-design-acceptance.md")


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_design_surfaces_are_terminally_accepted() -> None:
    assert "Accepted / Completed" in ARCHITECTURE.read_text(encoding="utf-8")
    assert "Status: Accepted / Completed" in BASELINE.read_text(encoding="utf-8")
    assert "Status: Accepted / Completed" in ACCEPTANCE.read_text(encoding="utf-8")


def test_acceptance_records_exact_design_evidence() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Design PR: [#320]" in text
    assert "0a7a24cde77afcd505111ca62c9c3f5f9846ebb3" in text
    assert "Synchronized-main Design First verification: 7 passed" in text


def test_accepted_execution_boundary_remains_explicit() -> None:
    text = normalized(ACCEPTANCE)
    for phrase in (
        "deterministic offline migration application",
        "accepted migration-plan fingerprint",
        "fail-closed target verification",
        "atomic distinct-output publication",
        "explicit `--execute` intent",
    ):
        assert phrase in text


def test_security_non_claims_and_deferred_work_remain_explicit() -> None:
    text = normalized(ACCEPTANCE)
    for phrase in (
        "network access",
        "repository mutation",
        "signing",
        "trust",
        "provenance",
        "attestation",
    ):
        assert phrase in text
    assert "Production implementation — Not Started" in text


def test_governance_surfaces_use_exact_unique_acceptance_markers() -> None:
    base = "v1.3.23-v1.3.25-audit-bundle-migration-execution-design-acceptance"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Design — Accepted / Completed" in text
        assert "Production implementation — Not Started" in text
