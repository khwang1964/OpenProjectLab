from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RELEASES = ROOT / "docs/releases"
ALIGNMENT = RELEASES / ("v1.3.23-v1.3.25-audit-bundle-migration-execution-terminal-alignment.md")
IMPLEMENTATION = RELEASES / ("v1.3.23-v1.3.25-audit-bundle-migration-execution-implementation.md")


def test_alignment_records_completed_merge_verification() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    assert "Completed / Verified after merge" in text
    assert "Terminal-alignment PR #323 merged with required CI successful" in text


def test_alignment_records_exact_implementation_evidence() -> None:
    text = ALIGNMENT.read_text(encoding="utf-8")
    assert "Implementation PR: [#322]" in text
    assert "6e9369643004caa45be2896d183611d0c7fc3df7" in text
    assert "Synchronized-main focused verification: 35 passed" in text


def test_implementation_status_is_accepted() -> None:
    text = IMPLEMENTATION.read_text(encoding="utf-8")
    assert "Status: Accepted / Completed" in text


def test_governance_surfaces_use_exact_unique_markers() -> None:
    base = "v1.3.23-v1.3.25-audit-bundle-migration-execution-terminal-alignment"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, exact_marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(exact_marker) == 1
        assert "Awaiting terminal-alignment merge and verification" in text
