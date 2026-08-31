from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASE = (
    ROOT
    / "docs/releases"
    / ("v1.3.8-v1.3.10-verification-request-usability-stable-cli-implementation.md")
)


def test_implementation_record_identifies_terminal_acceptance() -> None:
    text = RELEASE.read_text(encoding="utf-8")
    assert "Status: Accepted / Completed" in text
    assert "Design Acceptance PR #295" in text
    assert "Terminal Alignment PR #297" in text


def test_production_symbols_and_cli_exist() -> None:
    core = (ROOT / "generator/release_automation.py").read_text(encoding="utf-8")
    cli = (ROOT / "generator/cli/release_evidence.py").read_text(encoding="utf-8")
    assert "class VerificationRequestEncoder" in core
    assert "class VerificationRequestInspector" in core
    assert "request_commands" in cli and "_handle_request_validate" in cli


def test_governance_markers_are_exact() -> None:
    marker = "v1.3.8-v1.3.10-verification-request-usability-stable-cli-implementation"
    surfaces = (
        ("CHANGELOG.md", "changelog"),
        ("docs/HISTORY.md", "history"),
        ("docs/roadmap.md", "roadmap"),
    )
    for relative, suffix in surfaces:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(f"<!-- {marker}-{suffix} -->") == 1
