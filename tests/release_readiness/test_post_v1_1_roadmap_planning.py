"""Fail-closed Post-v1.1 roadmap planning contract."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "docs" / "releases" / "post-v1.1-roadmap-planning.md"
FORMAL_V1_1 = ROOT / "docs" / "releases" / "v1.1-formal-acceptance.md"
ROADMAP = ROOT / "docs" / "roadmap.md"
HISTORY = ROOT / "docs" / "HISTORY.md"

V1_1_TERMINAL_MERGE = "9997e9d85ed3672451c6c538d464d07a93d3d9cb"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_post_v1_1_planning_document_exists_and_is_not_preaccepted() -> None:
    text = _read(PLAN)

    assert "Post-v1.1 Roadmap Planning" in text
    assert "**Status:** Design / Planning Baseline --- In Progress" in text
    assert "**Next Version Decision:** Not Yet Accepted" in text
    assert "**Implementation:** Not Started" in text


def test_v1_1_predecessor_remains_terminally_accepted() -> None:
    text = _read(FORMAL_V1_1)

    assert "Formal v1.1 Acceptance --- Accepted" in text
    assert "v1.1 --- Terminally Accepted" in text


def test_planning_is_bound_to_exact_v1_1_terminal_merge() -> None:
    text = _read(PLAN)

    assert f"**Predecessor Merge:** {V1_1_TERMINAL_MERGE}" in text


def test_next_version_selection_rules_are_explicit() -> None:
    text = _read(PLAN)

    for marker in (
        "v1.1.x maintenance release",
        "Use v1.2",
        "Use v2.0 only",
        "this is not accepted until the planning baseline passes review",
        "v2.0 must not be selected merely because a feature is large",
    ):
        assert marker in text


def test_candidate_workstreams_are_declared() -> None:
    text = _read(PLAN)

    for heading in (
        "Bootstrap Framework maturity",
        "AI-assisted project and course generation",
        "Marketplace production workflow",
        "Developer and release automation",
    ):
        assert heading in text


def test_non_goals_keep_high_risk_scope_closed() -> None:
    text = _read(PLAN)

    for marker in (
        "remote Marketplace service",
        "automatic plugin or generator activation",
        "artifact signing / trust infrastructure",
        "silent network access",
        "implicit AI provider selection",
        "automatic credential discovery",
        "v2.0 without an explicit breaking-change justification",
        "implementation before planning acceptance",
    ):
        assert marker in text


def test_architecture_requirements_are_documentation_first() -> None:
    text = _read(PLAN)

    required = (
        "public contract boundary",
        "compatibility impact",
        "failure and rollback behavior",
        "state / mutation model",
        "test strategy",
        "acceptance gates",
        "documentation impact",
    )

    for marker in required:
        assert marker in text


def test_planning_closure_gates_are_fail_closed() -> None:
    text = _read(PLAN)

    for marker in (
        "Next-version decision --- Pending",
        "Roadmap alignment --- Pending",
        "HISTORY alignment --- Pending",
        "CHANGELOG alignment --- Pending",
        "Focused planning tests --- Pending",
        "Full regression / coverage --- Pending",
        "Planning PR required CI --- Pending",
        "Post-merge consistency verification --- Pending",
        "Terminal planning acceptance --- Pending",
        "Next Version Decision --- Not Yet Accepted",
        "Implementation --- Not Started",
    ):
        assert marker in text


def test_post_v1_1_planning_does_not_reopen_v1_1_acceptance() -> None:
    planning = _read(PLAN)
    roadmap = _read(ROADMAP)
    history = _read(HISTORY)

    assert "v1.1 --- Terminally Accepted" in planning
    assert "Formal v1.1 Acceptance --- Accepted" in roadmap
    assert "Formal v1.1 Acceptance --- Accepted" in history

    assert "v1.1 --- Reopened" not in planning
    assert "Formal v1.1 Acceptance --- Not Accepted" not in planning


def test_lifecycle_documents_select_v1_2_without_preaccepting_it() -> None:
    for path in (ROADMAP, HISTORY):
        text = _read(path)

        assert "Next Version Boundary --- v1.2" in text
        assert "v1.2 Implementation --- Not Started" in text

    planning = _read(PLAN)

    assert "Next Version Decision --- Not Yet Accepted" in planning
    assert "Implementation --- Not Started" in planning
    assert "v1.2 --- Accepted" not in planning
