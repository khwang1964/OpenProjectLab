from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/audit-bundle-migration-execution.md"
RELEASE = ROOT / ("docs/releases/v1.3.23-v1.3.25-audit-bundle-migration-execution-design-train.md")


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_design_is_pending_and_implementation_not_started() -> None:
    architecture = ARCHITECTURE.read_text(encoding="utf-8")
    release = RELEASE.read_text(encoding="utf-8")
    assert "Proposed / Pending design review" in architecture
    assert "Status: Proposed / Pending design review" in release
    assert "Production implementation — Not Started" in release


def test_accepted_predecessor_remains_explicit() -> None:
    architecture = normalized(ARCHITECTURE)
    release = normalized(RELEASE)
    assert "accepted v1.3.20-v1.3.22" in architecture
    assert "terminally accepted v1.3.20-v1.3.22" in release
    assert "preview-only behavior remain accepted and unchanged" in release


def test_execution_requires_exact_plan_and_explicit_intent() -> None:
    text = normalized(ARCHITECTURE)
    assert "AuditBundleMigrationRequest" in text
    assert "accepted migration-plan fingerprint" in text
    assert "preview fingerprint matches the request" in text
    assert "--execute" in text
    assert "mandatory for mutation" in text


def test_source_preservation_and_fail_closed_output_are_required() -> None:
    text = normalized(ARCHITECTURE)
    assert "source bundle is never rewritten or deleted" in text
    assert "Input and output must resolve to distinct paths" in text
    assert "leaves no published partial output" in text
    assert "Existing outputs are never silently overwritten" in text
    assert "published atomically" in text


def test_receipts_and_digests_are_not_trust_evidence() -> None:
    text = normalized(ARCHITECTURE)
    for phrase in (
        "not trust",
        "provenance",
        "authentication",
        "authorization",
        "signing",
        "attestation",
    ):
        assert phrase in text


def test_deferred_security_and_remote_boundaries_remain_explicit() -> None:
    text = normalized(RELEASE)
    for phrase in (
        "network",
        "repository",
        "publishes remotely",
        "Signing",
        "encryption",
        "tags",
        "releases",
    ):
        assert phrase in text


def test_governance_surfaces_use_exact_unique_markers() -> None:
    base = "v1.3.23-v1.3.25-audit-bundle-migration-execution-design-train"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Production implementation — Not Started" in text
