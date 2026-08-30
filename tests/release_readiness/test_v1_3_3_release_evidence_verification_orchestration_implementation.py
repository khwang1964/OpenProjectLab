from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "generator/release_automation.py"
RELEASE = (
    ROOT / "docs/releases/v1.3.3-release-evidence-verification-orchestration-implementation.md"
)


def test_production_orchestration_contract_exists() -> None:
    text = MODULE.read_text(encoding="utf-8")
    for name in (
        "VerificationRequest",
        "VerificationReport",
        "VerificationFinding",
        "ReleaseEvidenceVerificationOrchestrator",
    ):
        assert f"class {name}" in text


def test_implementation_reuses_accepted_boundaries() -> None:
    text = MODULE.read_text(encoding="utf-8")
    assert "RepositoryEvidenceAdapter" in text
    assert "GitHubEvidenceAdapter" in text
    assert "ReleaseEvidenceValidator" in text


def test_release_record_preserves_deferred_authority() -> None:
    text = RELEASE.read_text(encoding="utf-8")
    assert "Implemented / Awaiting implementation acceptance" in text
    assert "No pytest execution, CLI, SDK, Git/GitHub mutation" in text
    assert "Code Review Checklist" in text
