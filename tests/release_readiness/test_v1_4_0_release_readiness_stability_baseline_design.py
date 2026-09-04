from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE = ROOT / "docs/architecture/release-readiness-stability-baseline.md"
RELEASE = ROOT / "docs/releases/v1.4.0-release-readiness-stability-baseline-design.md"


def normalized(path: Path) -> str:
    return " ".join(path.read_text(encoding="utf-8").split())


def test_design_is_pending_and_implementation_not_started() -> None:
    architecture = normalized(ARCHITECTURE)
    release = normalized(RELEASE)
    assert "Proposed / Pending design review" in architecture
    assert "Proposed / Pending design review" in release
    assert "Production implementation is Not Started" in release


def test_snapshot_is_strict_revision_bound_and_non_authorizing() -> None:
    text = normalized(ARCHITECTURE)
    assert "ReleaseReadinessStabilitySnapshot" in text
    for phrase in (
        "duplicate keys",
        "unknown fields",
        "invalid counts",
        "contradictory evidence",
        "canonical rendering is byte-stable",
        "evaluated revision",
        "not a signature",
        "release approval",
    ):
        assert phrase in text


def test_evaluator_is_deterministic_and_fails_closed() -> None:
    text = normalized(ARCHITECTURE)
    assert "ReleaseReadinessStabilityEvaluator" in text
    for phrase in (
        "READY",
        "BLOCKED",
        "INDETERMINATE",
        "stable field paths",
        "documented reason codes",
        "revision-mismatched evidence",
        "can never produce `READY`",
        "no unresolved release blocker",
    ):
        assert phrase in text


def test_cli_is_bounded_read_only_and_has_stable_exit_classes() -> None:
    text = normalized(ARCHITECTURE)
    assert "readiness evaluate --snapshot SNAPSHOT --policy POLICY" in text
    assert "--format json|text" in text
    assert "aggregate-byte limits" in text
    assert "Exit 0" in text
    assert "exit 1" in text
    assert "exit 2" in text
    assert "reads only explicitly named local files" in text
    assert "never discovers, writes, repairs, stages, commits, pushes" in text


def test_release_authority_and_compatibility_boundaries_are_explicit() -> None:
    architecture = normalized(ARCHITECTURE)
    release = normalized(RELEASE)
    for phrase in (
        "accepted v1.3 public CLI, SDK, Bootstrap Framework",
        "without silently expanding their compatibility promises",
        "necessary evidence, not release authorization",
        "tags, artifacts, GitHub Releases, package publication",
        "No network access",
        "repository mutation",
    ):
        assert phrase in architecture
    assert "Existing v1.3 public and compatibility boundaries remain unchanged" in release
    assert "separate design and explicit authorization" in release


def test_governance_surfaces_use_exact_unique_markers() -> None:
    base = "v1.4.0-release-readiness-stability-baseline-design"
    surfaces = {
        "CHANGELOG.md": f"<!-- {base}-changelog -->",
        "docs/HISTORY.md": f"<!-- {base}-history -->",
        "docs/roadmap.md": f"<!-- {base}-roadmap -->",
    }
    for relative_path, marker in surfaces.items():
        text = (ROOT / relative_path).read_text(encoding="utf-8")
        assert text.count(marker) == 1
        assert "Production implementation — Not Started" in text
