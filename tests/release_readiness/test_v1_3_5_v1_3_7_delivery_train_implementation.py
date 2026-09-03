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
    for forbidden in ("subprocess", "git push", "pr merge"):
        assert forbidden not in text

    before_create, create_and_after = text.split(
        "def _handle_bundle_create",
        maxsplit=1,
    )
    create_handler, read_only_and_migrate = create_and_after.split(
        "def _handle_bundle_inspect",
        maxsplit=1,
    )
    read_only_handlers, migrate_handler = read_only_and_migrate.split(
        "def _handle_bundle_migrate",
        maxsplit=1,
    )

    assert "write_text(" not in before_create
    assert "write_text(" not in read_only_handlers
    assert create_handler.count("temporary.write_text(") == 1
    assert "if output.exists() or temporary.exists():" in create_handler
    assert "temporary.replace(output)" in create_handler
    assert migrate_handler.count("temporary.write_text(") == 1
    assert "if output.exists() or temporary.exists():" in migrate_handler
    assert "temporary.replace(output)" in migrate_handler


def test_release_record_is_accepted_after_alignment_verification() -> None:
    text = RELEASE.read_text(encoding="utf-8")
    assert "Accepted / Completed" in text
    assert "implementation acceptance — Accepted / Completed" in text


def test_governance_surfaces_share_exact_implementation_marker() -> None:
    marker = "v1.3.5-v1.3.7-read-only-verification-delivery-train-implementation"
    surfaces = {
        "CHANGELOG.md": f"<!-- {marker}-changelog -->",
        "docs/HISTORY.md": f"<!-- {marker}-history -->",
        "docs/roadmap.md": f"<!-- {marker}-roadmap -->",
    }
    for relative, exact_marker in surfaces.items():
        assert (ROOT / relative).read_text(encoding="utf-8").count(exact_marker) == 1
