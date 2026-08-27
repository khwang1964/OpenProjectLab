"""v1.2.6 Bootstrap Runtime Integration design contract."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs/releases/v1.2.6-bootstrap-runtime-integration.md"
ARCH = ROOT / "docs/architecture/bootstrap-runtime-integration.md"
PREVIOUS = ROOT / "docs/releases/v1.2.5-bootstrap-validation-runtime.md"
ACCEPTANCE = ROOT / "docs/releases/v1.2.6-bootstrap-runtime-integration-acceptance.md"
PRODUCTION = ROOT / "generator/core/bootstrap_runtime.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_design_is_terminally_accepted() -> None:
    text = read(DESIGN)
    assert "Accepted --- Terminally Closed" in text
    assert "Production Implementation --- Not Started" in text
    assert "v1.2.6 Acceptance --- Accepted" in text


def test_predecessor_is_implemented() -> None:
    text = read(DESIGN) + read(PREVIOUS)
    assert "v1.2.5 Bootstrap Validation Runtime --- Accepted / Implemented" in text
    assert "Implementation PR #240 --- Merged" in text
    assert "Production Implementation Slice --- Completed" in text


def test_core_contracts_are_explicit() -> None:
    text = read(DESIGN)
    for marker in (
        "BootstrapRuntimeMode",
        "BootstrapRuntimeRequest",
        "BootstrapRuntimeResult",
        "BootstrapRuntimeCoordinator.execute(request)",
    ):
        assert marker in text


def test_mode_matrix_is_closed() -> None:
    text = read(DESIGN)
    for marker in (
        "preview --- plan + preview; apply forbidden; validation not run",
        "apply --- plan + apply; validation not run",
        "apply-and-validate --- plan + apply + validation, in that order",
    ):
        assert marker in text


def test_authoritative_plan_is_reused() -> None:
    text = read(DESIGN) + read(ARCH)
    for marker in (
        "planner is invoked exactly once",
        "same `BootstrapPlan` identity",
        "Planning --- Exactly Once",
        "BootstrapPlan --- Authoritative / Reused",
    ):
        assert marker in text


def test_failure_is_fail_closed() -> None:
    text = read(DESIGN) + read(ARCH)
    for marker in (
        "Planning Failure --- Propagated / No Later Phase",
        "Apply Failure --- Propagated / Validation Not Run",
        "Validation Check Failure --- Propagated",
        "Success-shaped Partial Result --- Forbidden",
    ):
        assert marker in text


def test_invalid_result_is_not_execution_failure() -> None:
    text = read(DESIGN)
    assert "Invalid Validation Result --- Completed Result / is_valid False" in text
    assert "distinct from a validation execution failure" in text


def test_mutation_boundaries_remain_closed() -> None:
    text = read(DESIGN) + read(ARCH)
    for marker in (
        "Preview Mutation --- Forbidden",
        "Apply Mutation --- Explicit Mode Only",
        "Validation --- Inspection Only",
        "must not call apply in preview mode",
        "initiate automatic rollback",
    ):
        assert marker in text


def test_future_surfaces_remain_closed() -> None:
    text = read(DESIGN) + read(ARCH)
    for marker in (
        "Implicit Network Access",
        "Implicit Plugin Activation",
        "Automatic Repair / Rollback",
        "Checkpoint / Resume",
        "Parallel Runtime Execution",
        "CLI Boundary",
        "Public SDK Expansion",
        "Stable Serialized Result",
    ):
        assert marker in text


def test_acceptance_gates_are_terminally_closed() -> None:
    text = read(DESIGN)
    for marker in (
        "Focused tests --- Passed",
        "Full regression / coverage --- Passed",
        "pre-commit --- Passed",
        "Design PR #242 required CI --- Passed",
        "Terminal design acceptance --- Completed",
    ):
        assert marker in text


def test_acceptance_record_preserves_implementation_boundary() -> None:
    text = read(ACCEPTANCE)
    for marker in (
        "**Status:** Accepted --- Terminally Closed",
        "Design PR #242",
        "4045a21514e912548456569a272a983f32ba5c4b",
        "Post-merge focused verification --- 10 passed",
        "v1.2.6 Design Contract --- Accepted",
        "Production Implementation --- Not Started",
        "Next --- v1.2.6 Bootstrap Runtime Integration minimum implementation slice",
    ):
        assert marker in text


def test_v1_2_6_minimum_implementation_evidence() -> None:
    design = read(DESIGN)
    runtime = read(PRODUCTION)
    for marker in (
        "Implementation PR #244 --- Merged",
        "Implementation merge --- f126238de83fc4fe12f4cb6de1d281fccd4281d0",
        "Post-merge focused verification --- 18 passed",
        "Production Implementation Slice --- Completed",
        "CLI Boundary / Public SDK Expansion --- Deferred",
    ):
        assert marker in design
    for marker in (
        "class BootstrapRuntimeMode",
        "class BootstrapRuntimeRequest",
        "class BootstrapRuntimeResult",
        "class BootstrapRuntimeCoordinator",
        "def execute(self, request: BootstrapRuntimeRequest)",
    ):
        assert marker in runtime
