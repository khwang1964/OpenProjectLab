from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ALIGNMENT = (
    ROOT
    / "docs/releases/v1.3.17-v1.3.19-verification-audit-bundle-portability-terminal-alignment.md"
)
IMPLEMENTATION = (
    ROOT / "docs/releases/v1.3.17-v1.3.19-verification-audit-bundle-portability-implementation.md"
)


def test_alignment_remains_pending_before_merge_verification() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    assert "Completed / Verified after merge" in text
    assert "A separate implementation-acceptance closure" in text


def test_alignment_records_exact_implementation_evidence() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    assert "Implementation PR: [#312]" in text
    assert "b00c49874500a49f5975762f151440f7372a0338" in text
    assert "Synchronized-main focused verification: 11 passed" in text


def test_implementation_status_awaits_alignment_merge() -> None:
    text = IMPLEMENTATION.read_text(encoding="utf-8")
    assert "Accepted / Completed" in text


def test_governance_surfaces_use_exact_unique_markers() -> None:
    base = "v1.3.17-v1.3.19-verification-audit-bundle-portability-terminal-alignment"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, exact_marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Accepted / Completed" in text
