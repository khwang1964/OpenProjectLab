from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "generator/release_automation.py"
CLI = ROOT / "generator/cli/release_evidence.py"
RELEASE = (
    ROOT
    / "docs/releases"
    / ("v1.3.5-v1.3.7-read-only-verification-delivery-train-implementation.md")
)


def test_delivery_train_implementation_symbols_exist() -> None:
    module = MODULE.read_text(encoding="utf-8")
    for symbol in (
        "class ReadOnlyVerificationInvoker",
        "class VerificationRequestCodec",
        "class VerificationReportRenderer",
        "class VerificationDocumentError",
    ):
        assert symbol in module


def test_cli_preserves_explicit_bounded_read_only_boundary() -> None:
    text = CLI.read_text(encoding="utf-8")
    assert "release-evidence" in text
    assert "MAX_REQUEST_BYTES" in text
    assert 'environment["GH_PROMPT_DISABLED"] = "1"' in text
    for forbidden in ("subprocess", "git push", "pr merge", "write_text("):
        assert forbidden not in text


def test_release_record_remains_pending_before_merge_verification() -> None:
    text = RELEASE.read_text(encoding="utf-8")
    assert "Implemented / Pending terminal alignment and acceptance" in text
    assert "implementation acceptance until implementation merge" in text


def test_governance_surfaces_share_exact_implementation_marker() -> None:
    marker = "v1.3.5-v1.3.7-read-only-verification-delivery-train-implementation"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        assert (ROOT / relative).read_text(encoding="utf-8").count(exact_marker) == 1
