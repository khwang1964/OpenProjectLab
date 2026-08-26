"""Fail-closed v1.2.3 Dry-run Execution Preview design contract."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs" / "releases" / "v1.2.3-dry-run-execution-preview.md"
ARCHITECTURE = ROOT / "docs" / "architecture" / "bootstrap-dry-run-execution-preview.md"
PREDECESSOR = ROOT / "docs" / "releases" / "v1.2.2-bootstrap-planning-core.md"
ACCEPTANCE = ROOT / "docs" / "releases" / "v1.2.3-dry-run-execution-preview-acceptance.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v1_2_3_design_is_terminally_accepted() -> None:
    text = _read(DESIGN)
    assert "OpenProjectLab v1.2.3 Dry-run Execution Preview" in text
    assert "**Status:** Accepted --- Terminally Closed" in text
    assert "Production Implementation --- Not Started" in text
    assert "v1.2.3 Acceptance --- Accepted" in text


def test_v1_2_3_is_bound_to_implemented_planning_core() -> None:
    text = _read(DESIGN)
    predecessor = _read(PREDECESSOR)
    assert "v1.2.2 Bootstrap Planning Core --- Accepted / Implemented" in text
    assert "BootstrapPlanner implementation --- Completed" in predecessor
    assert "Implementation PR #228 --- Merged" in predecessor


def test_dry_run_preview_contracts_are_explicit() -> None:
    text = _read(DESIGN)
    for marker in (
        "### 3.1 BootstrapDryRunStep",
        "### 3.2 BootstrapDryRunPreview",
        "### 3.3 BootstrapDryRunExecutor",
        "BootstrapDryRunExecutor.preview(plan)",
    ):
        assert marker in text


def test_existing_bootstrap_plan_is_authoritative() -> None:
    text = _read(DESIGN)
    for marker in (
        "Authoritative Input Boundary",
        "Input BootstrapPlan --- Immutable / Authoritative",
        "must not:",
        "reconstruct or silently re-plan bootstrap intent",
        "introduce an alternative planning model",
    ):
        assert marker in text


def test_preview_determinism_and_equivalence_are_required() -> None:
    text = _read(DESIGN)
    for marker in (
        "Preview Ordering --- Deterministic",
        "Equivalent Preview Behavior --- Required",
        "plan step order is preserved",
        "expected-effect order is preserved",
        "repeated preview of the same plan is reproducible",
    ):
        assert marker in text


def test_expected_effects_remain_descriptive_only() -> None:
    text = _read(DESIGN)
    assert "Expected effects remain descriptive data only" in text
    assert "must not translate them into executable mutation commands" in text


def test_all_execution_and_mutation_surfaces_are_forbidden() -> None:
    combined = _read(DESIGN) + _read(ARCHITECTURE)
    for marker in (
        "Generator Instantiation --- Forbidden",
        "Generator Execution --- Forbidden",
        "Filesystem Mutation --- Forbidden",
        "Manifest / Backup / Checkpoint Writes --- Forbidden",
        "Network Access --- Forbidden",
        "Plugin Activation --- Forbidden",
    ):
        assert marker in combined


def test_preview_failure_has_zero_partial_state() -> None:
    text = _read(DESIGN)
    for marker in (
        "Preview is fail closed",
        "Failure Partial State --- Forbidden",
        "no persisted preview artifact",
        "no partially committed state",
        "no success-shaped partial preview",
    ):
        assert marker in text


def test_future_surfaces_remain_closed() -> None:
    text = _read(DESIGN)
    for marker in (
        "apply execution --- Not Started",
        "validation runtime --- Not Started",
        "checkpoint / resume --- Deferred",
        "generalized rollback --- Deferred",
        "CLI Boundary --- Not Accepted",
        "Production Implementation --- Not Started",
    ):
        assert marker in text


def test_acceptance_gates_are_terminally_closed() -> None:
    text = _read(DESIGN)
    for marker in (
        "Focused tests --- Passed",
        "Full regression / coverage --- Passed",
        "Design PR #230 required CI --- Passed",
        "Design PR #230 squash merge --- Completed",
        "Post-merge consistency verification --- Passed",
        "Terminal design acceptance --- Completed",
        "v1.2.3 Acceptance --- Accepted",
    ):
        assert marker in text


def test_architecture_preserves_existing_boundaries() -> None:
    text = _read(ARCHITECTURE)
    for marker in (
        "BootstrapPlan (authoritative)",
        "Pure projection boundary",
        "no second registry, planner, filesystem, or mutation pipeline",
        "Production Implementation --- Not Started",
    ):
        assert marker in text


def test_v1_2_3_acceptance_record_preserves_runtime_boundary() -> None:
    text = _read(ACCEPTANCE)
    for marker in (
        "**Status:** Accepted --- Terminally Closed",
        "Design PR #230",
        "5f26cf2526ff39de381129d76791d0c28d06c91a",
        "Post-merge focused verification --- 11 passed",
        "v1.2.3 Design Contract --- Accepted",
        "Production Implementation --- Not Started",
        "Next --- v1.2.3 Dry-run Execution Preview implementation slice",
    ):
        assert marker in text
