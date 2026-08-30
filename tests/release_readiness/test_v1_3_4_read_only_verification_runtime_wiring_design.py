from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/read-only-verification-runtime-wiring.md"
RELEASE = ROOT / "docs/releases/v1.3.4-read-only-verification-runtime-wiring.md"


def test_design_surfaces_exist_and_remain_pending() -> None:
    architecture = ARCHITECTURE.read_text(encoding="utf-8")
    release = RELEASE.read_text(encoding="utf-8")
    assert "Proposed / Pending design review" in architecture
    assert "Status: Proposed / Pending design review" in release
    assert "Production implementation — Not Started" in release


def test_design_defines_explicit_runtime_configuration() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "repository working directory" in text
    assert "command timeout" in text
    assert "environment mapping" in text
    assert "copied immutably" in text


def test_design_allows_only_accepted_read_commands() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    for command in (
        "git config --get remote.origin.url",
        "git branch --show-current",
        "git rev-parse HEAD",
        "git rev-parse origin/main",
        "git status --porcelain",
        "gh pr view <positive-number> --json <accepted-fields>",
    ):
        assert command in text
    assert "fail closed before process execution" in text


def test_design_factory_reuses_components_without_execution() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    for component in (
        "RepositoryEvidenceAdapter",
        "GitHubEvidenceAdapter",
        "ReleaseEvidenceValidator",
        "ReleaseEvidenceVerificationOrchestrator",
    ):
        assert component in text
    assert "does not run verification" in text


def test_design_preserves_deferred_authority() -> None:
    text = ARCHITECTURE.read_text(encoding="utf-8")
    assert "production implementation" in text
    assert "CLI and public SDK exposure" in text
    assert "pytest, coverage, or arbitrary subprocess execution" in text
    assert "commit, push, merge, tag, release, publication" in text
    assert "credential management" in text


def test_governance_surfaces_share_one_design_marker() -> None:
    marker = "v1.3.4-read-only-verification-runtime-wiring-design"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Production implementation — Not Started" in text
