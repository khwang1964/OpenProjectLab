from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/deterministic-readiness-snapshot-assembly.md"
RELEASE = ROOT / "docs/releases/v1.4.1-deterministic-readiness-snapshot-assembly-design.md"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_design_is_pending_and_implementation_not_started() -> None:
    for text in (normalized(ARCHITECTURE), normalized(RELEASE)):
        assert "Proposed / Pending design review" in text
    assert "Production implementation is Not Started" in normalized(RELEASE)


def test_manifest_and_assembler_are_strict_revision_bound_and_deterministic() -> None:
    text = normalized(ARCHITECTURE)
    for phrase in (
        "ReadinessEvidenceManifest",
        "ReleaseReadinessSnapshotAssembler",
        "duplicate or unknown fields",
        "same repository revision",
        "stable ordered findings",
        "Canonical snapshot bytes",
    ):
        assert phrase in text


def test_paths_and_inputs_fail_closed() -> None:
    text = normalized(ARCHITECTURE)
    for phrase in (
        "explicit input root",
        "absolute paths",
        "traversal",
        "symlinks",
        "implicit discovery fail closed",
        "per-document",
        "aggregate-byte limits",
    ):
        assert phrase in text


def test_cli_is_bounded_offline_and_read_only() -> None:
    text = normalized(ARCHITECTURE)
    assert "readiness assemble --manifest MANIFEST --input-root ROOT" in text
    assert "--format json|text" in text
    assert "Exit 0" in text and "exit 2" in text
    assert "never writes, discovers, repairs, stages, commits, pushes" in text


def test_authority_boundaries_remain_separate() -> None:
    architecture = normalized(ARCHITECTURE)
    release = normalized(RELEASE)
    for phrase in (
        "does not evaluate readiness or authorize release",
        "Evaluation remains a separate v1.4.0 operation",
        "remote collection",
        "GitHub Releases",
        "repository mutation",
    ):
        assert phrase in architecture
    assert "v1.4.0 evaluation and release authorization remain separate" in release


def test_governance_surfaces_have_exact_unique_markers() -> None:
    base = "v1.4.1-deterministic-readiness-snapshot-assembly-design"
    for relative, suffix in (
        ("CHANGELOG.md", "changelog"),
        ("docs/HISTORY.md", "history"),
        ("docs/roadmap.md", "roadmap"),
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert text.count(f"<!-- {base}-{suffix} -->") == 1
        assert "Production implementation — Not Started" in text
