"""Fail-closed v1.2 Planning Baseline contract."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PLAN = ROOT / "docs" / "releases" / "v1.2-planning-baseline.md"
POST_V1_1 = ROOT / "docs" / "releases" / "post-v1.1-roadmap-planning.md"
ROADMAP = ROOT / "docs" / "roadmap.md"
HISTORY = ROOT / "docs" / "HISTORY.md"

PREDECESSOR_MERGE = "55781b43f7b661a48338601cb22a4d69a120c584"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v1_2_planning_document_is_terminally_accepted() -> None:
    text = _read(PLAN)

    assert "OpenProjectLab v1.2 Planning Baseline" in text
    assert "**Status:** Accepted --- Terminally Closed" in text
    assert "**Implementation:** Not Started" in text
    assert "v1.2 Planning Baseline --- Accepted" in text


def test_predecessor_is_post_v1_1_accepted_boundary() -> None:
    text = _read(PLAN)

    assert "**Predecessor:** Post-v1.1 Roadmap Planning --- Accepted" in text
    assert f"**Predecessor Merge:** {PREDECESSOR_MERGE}" in text


def test_post_v1_1_acceptance_remains_immutable() -> None:
    text = _read(POST_V1_1)

    assert "Post-v1.1 Roadmap Planning --- Accepted" in text
    assert "Next Version Decision --- Accepted" in text
    assert "v1.2 Planning Baseline --- Accepted" in text


def test_workstream_priority_is_explicit() -> None:
    text = _read(PLAN)

    ordered = (
        "Priority 1 --- Bootstrap Framework maturity",
        "Priority 2 --- Developer / Release Automation",
        "Priority 3 --- AI-assisted Project / Course Generation",
        "Priority 4 --- Marketplace Production Workflow",
    )

    positions = [text.index(marker) for marker in ordered]
    assert positions == sorted(positions)


def test_first_slice_is_bootstrap_design_not_implementation() -> None:
    text = _read(PLAN)

    assert "v1.2.1 --- Bootstrap Framework Design Baseline" in text
    assert "This selection is not accepted until this planning baseline passes" in text
    assert "v1.2 Implementation --- Not Started" in text


def test_bootstrap_design_requirements_are_explicit() -> None:
    text = _read(PLAN)

    for marker in (
        "bootstrap public contract boundary",
        "orchestration responsibilities",
        "plan / dry-run / apply semantics",
        "mutation and failure boundaries",
        "generator composition rules",
        "compatibility constraints",
        "test strategy",
        "acceptance gates",
    ):
        assert marker in text


def test_non_goals_keep_scope_closed() -> None:
    text = _read(PLAN)

    for marker in (
        "v2.0 breaking Stable-contract changes",
        "remote Marketplace service",
        "silent network access",
        "implicit AI provider selection",
        "automatic plugin activation",
        "generalized dependency solving",
        "replacing existing generator lifecycle contracts",
        "implementation before Design First approval",
    ):
        assert marker in text


def test_architecture_guardrails_prevent_parallel_pipelines() -> None:
    text = _read(PLAN)

    for marker in (
        "reuse existing Stable public contracts",
        "preserve deterministic local / offline testability",
        "keep filesystem mutation explicit",
        "avoid parallel orchestration infrastructure",
        "provide executable acceptance evidence",
    ):
        assert marker in text


def test_planning_closure_gates_are_terminally_accepted() -> None:
    text = _read(PLAN)

    required = (
        "Workstream priority --- Accepted",
        "First implementation slice --- Accepted: v1.2.1 Bootstrap Framework Design Baseline",
        "Roadmap alignment --- Completed",
        "HISTORY alignment --- Completed",
        "CHANGELOG alignment --- Completed",
        "Focused planning tests --- Passed",
        "Full regression --- 2322 passed, 56 skipped, 1 deselected",
        "Total coverage --- 91.17%",
        "Required coverage --- 67.0% --- Passed",
        "git diff --check --- Passed",
        "pre-commit --- Passed",
        "Planning PR #222 required CI --- Passed",
        "Planning PR #222 squash merge --- Completed",
        "main synchronization --- Completed",
        "Post-merge consistency verification --- Passed",
        "Terminal planning acceptance --- Completed",
        "v1.2 Planning Baseline --- Accepted",
        "v1.2 Implementation --- Not Started",
    )

    for marker in required:
        assert marker in text


def test_lifecycle_docs_do_not_preaccept_v1_2_implementation() -> None:
    for path in (ROADMAP, HISTORY):
        text = _read(path)

        assert "v1.2 Planning Baseline --- Accepted" in text
        assert "v1.2 Implementation --- Not Started" in text
        assert "v1.2 Implementation --- Accepted" not in text


def test_v1_2_planning_acceptance_closure_evidence() -> None:
    text = _read(PLAN)

    assert "v1.2 Planning Baseline --- Accepted" in text
    assert "Planning PR #222 --- Merged" in text
    assert "Planning merge --- cc710f57141f7766acbb4e1ff3feb1884549ea2e" in text
    assert "Planning PR required CI --- Passed" in text
    assert "main synchronization --- Completed" in text
    assert "Post-merge consistency verification --- Passed" in text
    assert "Focused post-merge verification --- 10 passed" in text
    assert "Full regression --- 2322 passed, 56 skipped, 1 deselected" in text
    assert "Total coverage --- 91.17%" in text
    assert "Required coverage --- 67.0% --- Passed" in text
    assert "Workstream Priority --- Accepted" in text
    assert (
        "First Implementation Slice --- Accepted: v1.2.1 Bootstrap Framework Design Baseline"
        in text
    )
    assert "v1.2 Implementation --- Not Started" in text


def test_v1_2_acceptance_history_and_lifecycle_alignment() -> None:
    plan = _read(PLAN)
    roadmap = _read(ROADMAP)
    history = _read(HISTORY)

    assert "Planning PR #222 --- Merged" in plan
    assert "Planning merge --- cc710f57141f7766acbb4e1ff3feb1884549ea2e" in plan
    assert "v1.2 Planning Baseline --- Accepted" in roadmap
    assert "v1.2 Planning Baseline --- Accepted" in history
    assert "v1.2 Implementation --- Not Started" in roadmap
    assert "v1.2 Implementation --- Not Started" in history
