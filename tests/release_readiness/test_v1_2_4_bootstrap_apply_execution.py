"""Fail-closed v1.2.4 Bootstrap Apply Execution design contract."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs" / "releases" / "v1.2.4-bootstrap-apply-execution.md"
ARCHITECTURE = ROOT / "docs" / "architecture" / "bootstrap-apply-execution.md"
PREDECESSOR = ROOT / "docs" / "releases" / "v1.2.3-dry-run-execution-preview.md"
ACCEPTANCE = ROOT / "docs" / "releases" / "v1.2.4-bootstrap-apply-execution-acceptance.md"
PRODUCTION = ROOT / "generator" / "core" / "bootstrap_apply.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v1_2_4_design_is_terminally_accepted() -> None:
    text = _read(DESIGN)
    assert "OpenProjectLab v1.2.4 Bootstrap Apply Execution" in text
    assert "**Status:** Accepted --- Terminally Closed" in text
    assert "Production Implementation --- Not Started" in text
    assert "v1.2.4 Acceptance --- Accepted" in text


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


def test_acceptance_gates_are_terminally_closed() -> None:
    text = _read(DESIGN)
    for marker in (
        "Focused tests --- Passed",
        "Full regression / coverage --- Passed",
        "Design PR #234 required CI --- Passed",
        "Design PR #234 squash merge --- Completed",
        "Post-merge consistency verification --- Passed",
        "Terminal design acceptance --- Completed",
        "v1.2.4 Acceptance --- Accepted",
    ):
        assert marker in text


def test_v1_2_4_acceptance_record_preserves_runtime_boundary() -> None:
    text = _read(ACCEPTANCE)
    for marker in (
        "**Status:** Accepted --- Terminally Closed",
        "Design PR #234",
        "1e0f7ebba9b98dd1c6bfa5edad52efa1bae7f0b6",
        "Post-merge focused verification --- 9 passed",
        "v1.2.4 Design Contract --- Accepted",
        "Production Implementation --- Not Started",
        "Next --- v1.2.4 Bootstrap Apply Execution minimum implementation slice",
    ):
        assert marker in text


def test_v1_2_4_minimum_implementation_evidence() -> None:
    design = _read(DESIGN)
    production = _read(PRODUCTION)

    for expected in (
        "Implementation PR #236 --- Merged",
        "Implementation merge --- 1fbf799bd6bc687592a46788fc98f2dda1b79907",
        "Post-merge focused verification --- 30 passed",
        "Production Implementation Slice --- Completed",
        "validation runtime --- Not Started",
        "CLI Boundary --- Not Accepted",
    ):
        assert expected in design

    for expected in (
        "class BootstrapApplyStepResult",
        "class BootstrapApplyResult",
        "class BootstrapApplyError",
        "class BootstrapApplyExecutor",
        "def apply(self, plan: BootstrapPlan)",
        "class GeneratorBootstrapStepRunner",
    ):
        assert expected in production
