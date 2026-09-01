from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_implementation_record_awaits_terminal_alignment_merge() -> None:
    text = (
        ROOT
        / "docs/releases/v1.3.17-v1.3.19-verification-audit-bundle-portability-implementation.md"
    ).read_text(encoding="utf-8")
    assert "Accepted / Completed" in text


def test_production_and_cli_symbols_exist() -> None:
    module = (ROOT / "generator/release_audit_bundle.py").read_text(encoding="utf-8")
    cli = (ROOT / "generator/cli/release_evidence.py").read_text(encoding="utf-8")
    for symbol in (
        "VerificationAuditBundle",
        "VerificationAuditBundleCodec",
        "VerificationAuditBundleValidator",
    ):
        assert f"class {symbol}" in module
    for handler in ("_handle_bundle_create", "_handle_bundle_inspect", "_handle_bundle_validate"):
        assert handler in cli


def test_governance_markers_are_exact_and_unique() -> None:
    base = "v1.3.17-v1.3.19-verification-audit-bundle-portability-implementation"
    for relative, suffix in (
        ("CHANGELOG.md", "changelog"),
        ("docs/HISTORY.md", "history"),
        ("docs/roadmap.md", "roadmap"),
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(f"<!-- {base}-{suffix} -->") == 1
