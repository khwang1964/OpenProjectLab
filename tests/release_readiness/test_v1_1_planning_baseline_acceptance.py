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


def _read(path: Path) -> str:
    """Read one acceptance document as UTF-8 text."""
    return path.read_text(encoding="utf-8")


def _normalized(path: Path) -> str:
    """Normalize Markdown whitespace for wrapped contract markers."""
    return " ".join(_read(path).split())


def test_acceptance_record_has_exact_governing_identity() -> None:
    """Bind acceptance to the reviewed governing PR and merge commit."""
    document = _read(ACCEPTANCE)

    assert "**Status:** Acceptance Closure --- In Progress" in document
    assert f"**Governing PR:** {GOVERNING_PR}" in document
    assert f"**Governing Merge Commit:** `{GOVERNING_MERGE}`" in document
    assert "Formal v1.1 Planning Baseline Acceptance:** Not Accepted" in document


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


def test_acceptance_is_fail_closed_until_all_gates_pass() -> None:
    """Keep formal planning acceptance closed while gates are pending."""
    document = _read(ACCEPTANCE)

    pending = (
        "Focused acceptance suite --- Pending local execution",
        "Full regression / coverage --- Pending acceptance-state execution",
        "Local quality gates --- Pending acceptance-state execution",
        "Acceptance PR required CI --- Pending",
        "Acceptance squash merge --- Pending",
        "main synchronization --- Pending",
        "Post-merge consistency --- Pending",
        "Terminal documentation alignment --- Pending",
    )
    for marker in pending:
        assert marker in document

    assert "Formal v1.1 Planning Baseline Acceptance --- Not Accepted" in document


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


def test_documents_align_to_pre_acceptance_state() -> None:
    """Align all governing documents to the pre-acceptance state."""
    for path in (BASELINE, ACCEPTANCE, ROADMAP, HISTORY, CHANGELOG):
        document = _read(path)
        assert "v1.1.1 Acceptance Closure --- In Progress" in document
        assert "Formal v1.1 Planning Baseline Acceptance --- Not Accepted" in document


def test_candidate_does_not_fabricate_acceptance_evidence() -> None:
    """Reject terminal evidence in current candidate-state sections."""
    current_sections = (
        _read(BASELINE).split("## 15. Current State", maxsplit=1)[1],
        _read(ACCEPTANCE).split("## 10. Current State", maxsplit=1)[1],
        _read(ROADMAP).split("Current release boundary", maxsplit=1)[1],
        _read(HISTORY).split("# v1.1 Planning Baseline", maxsplit=1)[1],
        _read(CHANGELOG)
        .split("#### v1.1 Planning Baseline", maxsplit=1)[1]
        .split("#### Milestone 8", maxsplit=1)[0],
    )
    forbidden = (
        "Acceptance PR required CI --- Passed",
        "Acceptance squash merge --- Completed",
        "Formal v1.1 Planning Baseline Acceptance --- Accepted",
    )
    for document in current_sections:
        for marker in forbidden:
            assert marker not in document
