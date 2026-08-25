"""Fail-closed acceptance tests for the v1.1 planning baseline."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
BASELINE = REPO_ROOT / "docs" / "releases" / "v1.1-planning-baseline.md"
ACCEPTANCE = REPO_ROOT / "docs" / "releases" / "v1.1-planning-baseline-acceptance.md"
ROADMAP = REPO_ROOT / "docs" / "roadmap.md"
HISTORY = REPO_ROOT / "docs" / "HISTORY.md"
CHANGELOG = REPO_ROOT / "CHANGELOG.md"

GOVERNING_PR = "#164"
GOVERNING_MERGE = "33c367b989014c34c162f326ee825f3fe8f4c8e6"
ACCEPTANCE_PR = "#165"
ACCEPTANCE_MERGE = "97dac1eca516e7b91e2f5bdfbe6da84b7a32215c"


def _read(path: Path) -> str:
    """Read one acceptance document as UTF-8 text."""
    return path.read_text(encoding="utf-8")


def _normalized(path: Path) -> str:
    """Normalize Markdown whitespace for wrapped contract markers."""
    return " ".join(_read(path).split())


def test_acceptance_record_has_exact_governing_identity() -> None:
    """Bind terminal acceptance to both reviewed merge identities."""
    document = _read(ACCEPTANCE)

    assert "**Status:** Accepted" in document
    assert f"**Governing PR:** {GOVERNING_PR}" in document
    assert f"**Governing Merge Commit:** `{GOVERNING_MERGE}`" in document
    assert f"**Acceptance PR:** {ACCEPTANCE_PR}" in document
    assert f"**Acceptance Merge Commit:** `{ACCEPTANCE_MERGE}`" in document
    assert "Formal v1.1 Planning Baseline Acceptance:** Accepted" in document


def test_acceptance_retains_verified_governing_evidence() -> None:
    """Retain the exact governing baseline verification evidence."""
    document = _read(ACCEPTANCE)

    required = (
        "Focused planning-contract suite --- 7 passed, 0 skipped",
        "Full regression --- 1983 passed, 32 skipped, 1 deselected",
        "Coverage --- 90.90%",
        "Required coverage --- 67.0% --- Passed",
        "Quality checks --- Passed",
        "Packaging artifact verification --- Passed",
    )
    for marker in required:
        assert marker in document


def test_acceptance_records_all_completed_closure_gates() -> None:
    """Require complete closure evidence before terminal acceptance."""
    document = _read(ACCEPTANCE)

    completed = (
        "Focused acceptance suite --- 15 passed",
        "Full regression --- 1991 passed, 32 skipped, 1 deselected",
        "Coverage --- 90.90% (required 67.0%) --- Passed",
        "Local quality gates --- Passed",
        "Acceptance PR #165 required CI --- Passed",
        "Acceptance squash merge --- Completed",
        "main synchronization --- Passed",
        "Post-merge consistency --- Passed",
        "Terminal documentation alignment --- Completed",
    )
    for marker in completed:
        assert marker in document

    assert "Formal v1.1 Planning Baseline Acceptance --- Accepted" in document


def test_product_work_and_release_acceptance_remain_unaccepted() -> None:
    """Keep product work unstarted and release acceptance unaccepted."""
    for path in (BASELINE, ACCEPTANCE, ROADMAP, HISTORY, CHANGELOG):
        document = _normalized(path)
        assert "Marketplace CLI --- Not Started" in document
        assert "AI CLI --- Not Started" in document
        assert "Formal v1.1 Acceptance --- Not Accepted" in document


def test_acceptance_preserves_deferred_and_compatibility_boundaries() -> None:
    """Preserve v1 compatibility and Deferred capability boundaries."""
    document = _read(ACCEPTANCE)

    assert "v1.0 Stable contracts remain compatible" in document
    assert "live provider behavior remains Experimental and opt-in" in document
    assert "remote Marketplace" in document
    assert "signing/trust" in document
    assert "dependency resolution" in document
    assert "remain Deferred" in document


def test_terminal_documentation_scope_is_explicit() -> None:
    """Require every terminal-alignment document explicitly."""
    document = _read(ACCEPTANCE)

    required_paths = (
        "docs/releases/v1.1-planning-baseline.md",
        "docs/releases/v1.1-planning-baseline-acceptance.md",
        "docs/roadmap.md",
        "docs/HISTORY.md",
        "CHANGELOG.md",
    )
    for path in required_paths:
        assert path in document


def test_documents_align_to_terminal_planning_acceptance() -> None:
    """Align all governing documents to terminal planning acceptance."""
    for path in (BASELINE, ACCEPTANCE, ROADMAP, HISTORY, CHANGELOG):
        document = _normalized(path)
        assert "v1.1.1 Planning Baseline --- Accepted" in document
        assert "Formal v1.1 Planning Baseline Acceptance --- Accepted" in document


def test_planning_acceptance_history_remains_pre_release() -> None:
    """Keep the immutable planning acceptance record at its historical state."""
    historical_sections = (
        _read(BASELINE).split("## 15. Current State", maxsplit=1)[1],
        _read(ACCEPTANCE).split("## 10. Current State", maxsplit=1)[1],
    )

    for document in historical_sections:
        assert "Formal v1.1 Acceptance --- Not Accepted" in document
        assert "Formal v1.1 Acceptance --- Accepted" not in document


def test_lifecycle_documents_record_terminal_v1_1_acceptance() -> None:
    """Later lifecycle records may now contain verified terminal acceptance."""
    for path in (ROADMAP, HISTORY):
        document = _read(path)

        assert "Formal v1.1 Acceptance --- Accepted" in document
        assert "v1.1 --- Terminally Accepted" in document

    changelog = _read(CHANGELOG)

    assert "Terminally accepted OpenProjectLab v1.1" in changelog
    assert "Formal Acceptance PR #218" in changelog
    assert "c740613f5ac29d696962545afb2ee0f5b0c8c630" in changelog
