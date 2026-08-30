from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "generator/release_automation.py"
RELEASE = ROOT / ("docs/releases/v1.3.4-read-only-verification-runtime-wiring-implementation.md")


def test_runtime_wiring_production_contract_exists() -> None:
    text = MODULE.read_text(encoding="utf-8")
    for name in (
        "VerificationRuntimeConfiguration",
        "ReadOnlyVerificationCommandExecutor",
        "VerificationRuntime",
        "build_verification_runtime",
    ):
        assert name in text


def test_implementation_reuses_accepted_components() -> None:
    text = MODULE.read_text(encoding="utf-8")
    for name in (
        "RepositoryEvidenceAdapter",
        "GitHubEvidenceAdapter",
        "ReleaseEvidenceValidator",
        "ReleaseEvidenceVerificationOrchestrator",
    ):
        assert name in text


def test_release_record_preserves_deferred_authority() -> None:
    text = RELEASE.read_text(encoding="utf-8")
    assert "Implemented / Awaiting implementation acceptance" in text
    assert "No CLI, public SDK, arbitrary subprocess, mutation" in text
    assert "No retry, polling, persistence, caching" in text
    assert "Code Review Checklist" in text
