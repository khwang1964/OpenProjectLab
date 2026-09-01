from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASES = ROOT / "docs/releases"
ACCEPTANCE = (
    RELEASES / "v1.3.14-v1.3.16-verification-report-auditability-implementation-acceptance.md"
)
IMPLEMENTATION = RELEASES / "v1.3.14-v1.3.16-verification-report-auditability-implementation.md"
ALIGNMENT = RELEASES / "v1.3.14-v1.3.16-verification-report-auditability-terminal-alignment.md"


def test_acceptance_records_terminal_evidence() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "Status: Accepted / Completed" in text
    assert "Terminal-alignment PR: [#308]" in text
    assert "14564eba784b1d34f04387863039934822fa3729" in text
    assert "Synchronized-main focused verification" in text
    assert "============================== 7 passed in 0.07s ==============================" in text


def test_prior_records_have_terminal_states() -> None:
    implementation = IMPLEMENTATION.read_text(encoding="utf-8")
    alignment = ALIGNMENT.read_text(encoding="utf-8")
    assert "Accepted / Completed" in implementation
    assert "Completed / Verified after merge" in alignment


def test_security_boundary_remains_explicit() -> None:
    text = ACCEPTANCE.read_text(encoding="utf-8")
    assert "do not provide signatures" in text
    assert "authentication" in text
    assert "authorization" in text
    assert "provenance" in text
    assert "Network access" in text
    assert "repository mutation" in text


def test_governance_surfaces_use_exact_unique_acceptance_markers() -> None:
    base = "v1.3.14-v1.3.16-verification-report-auditability-implementation-acceptance"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, exact_marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Implementation acceptance — Accepted / Completed" in text
