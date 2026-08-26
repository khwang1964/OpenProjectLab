"""Fail-closed v1.2.4 Bootstrap Apply Execution design contract."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs" / "releases" / "v1.2.4-bootstrap-apply-execution.md"
ARCHITECTURE = ROOT / "docs" / "architecture" / "bootstrap-apply-execution.md"
PREDECESSOR = ROOT / "docs" / "releases" / "v1.2.3-dry-run-execution-preview.md"
PRODUCTION = ROOT / "generator" / "core" / "bootstrap_apply.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v1_2_4_design_is_fail_closed_and_unaccepted() -> None:
    text = _read(DESIGN)
    assert "OpenProjectLab v1.2.4 Bootstrap Apply Execution" in text
    assert "**Status:** Design / Contract Definition --- In Progress" in text
    assert "Production Implementation --- Not Started" in text
    assert "v1.2.4 Acceptance --- Not Accepted" in text
    assert not PRODUCTION.exists()


def test_v1_2_4_is_bound_to_terminal_v1_2_3() -> None:
    text = _read(DESIGN)
    predecessor = _read(PREDECESSOR)
    assert "v1.2.3 Dry-run Execution Preview --- Accepted / Implemented" in text
    assert "Implementation PR #232 --- Merged" in predecessor
    assert "Production Implementation Slice --- Completed" in predecessor


def test_apply_contracts_are_explicit() -> None:
    text = _read(DESIGN)
    for marker in (
        "### 3.1 BootstrapApplyStepResult",
        "### 3.2 BootstrapApplyResult",
        "### 3.3 BootstrapApplyExecutor",
        "### 3.4 Bootstrap Step Execution Adapter",
        "BootstrapApplyExecutor.apply(plan)",
    ):
        assert marker in text


def test_authoritative_plan_and_existing_lifecycle_are_reused() -> None:
    combined = _read(DESIGN) + _read(ARCHITECTURE)
    for marker in (
        "Input BootstrapPlan --- Immutable / Authoritative",
        "Generator Lifecycle --- Reused",
        "Filesystem Abstraction --- Reused",
        "BaseGenerator.run(GenerateRequest)",
        "Parallel Mutation Pipeline --- Forbidden",
    ):
        assert marker in combined


def test_expected_effects_are_not_executed_directly() -> None:
    text = _read(DESIGN)
    assert "`ExpectedEffect` remains descriptive preview/planning data" in text
    assert "ExpectedEffect Direct Execution --- Forbidden" in text
    assert "must not translate expected-effect kinds" in text


def test_apply_is_deterministic_and_sequential() -> None:
    text = _read(DESIGN)
    for marker in (
        "Apply is explicit, ordered, and sequential",
        "each step starts only after the previous step succeeds",
        "each generator executes at most once",
        "completed result ordering matches",
        "no parallel execution is introduced",
    ):
        assert marker in text


def test_failure_semantics_expose_partial_state_and_stop() -> None:
    combined = _read(DESIGN) + _read(ARCHITECTURE)
    for marker in (
        "Fail-fast --- Required",
        "Later-step Execution after Failure --- Forbidden",
        "Automatic Rollback --- Not Guaranteed",
        "Transaction-wide Atomicity --- Not Claimed",
        "completed step results in order",
        "failed step identity",
    ):
        assert marker in combined


def test_future_surfaces_remain_closed() -> None:
    combined = _read(DESIGN) + _read(ARCHITECTURE)
    for marker in (
        "validation runtime --- Not Started",
        "checkpoint / resume --- Deferred",
        "generalized rollback --- Deferred",
        "parallel apply --- Deferred",
        "Implicit Network Access --- Forbidden",
        "Implicit Plugin Activation --- Forbidden",
        "CLI Boundary --- Not Accepted",
        "Public SDK Expansion --- Forbidden",
        "Production Implementation --- Not Started",
    ):
        assert marker in combined


def test_acceptance_gates_remain_pending() -> None:
    text = _read(DESIGN)
    for marker in (
        "Focused tests --- Pending",
        "Full regression / coverage --- Pending",
        "Design PR required CI --- Pending",
        "Design PR squash merge --- Pending",
        "Post-merge consistency verification --- Pending",
        "Terminal design acceptance --- Pending",
        "v1.2.4 Acceptance --- Not Accepted",
    ):
        assert marker in text
