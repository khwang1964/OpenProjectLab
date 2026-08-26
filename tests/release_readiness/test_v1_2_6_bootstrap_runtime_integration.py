"""v1.2.6 Bootstrap Runtime Integration design contract."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs/releases/v1.2.6-bootstrap-runtime-integration.md"
ARCH = ROOT / "docs/architecture/bootstrap-runtime-integration.md"
PREVIOUS = ROOT / "docs/releases/v1.2.5-bootstrap-validation-runtime.md"
PRODUCTION = ROOT / "generator/core/bootstrap_runtime.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_design_first_boundary() -> None:
    text = read(DESIGN)
    assert "Design / Contract Definition --- In Progress" in text
    assert "Production Implementation --- Not Started" in text
    assert "v1.2.6 Acceptance --- Not Accepted" in text
    assert not PRODUCTION.exists()


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


def test_acceptance_gates_are_pending() -> None:
    text = read(DESIGN)
    for marker in (
        "Focused tests --- Pending",
        "Full regression / coverage --- Pending",
        "pre-commit --- Pending",
        "Design PR required CI --- Pending",
        "Terminal design acceptance --- Pending",
    ):
        assert marker in text
