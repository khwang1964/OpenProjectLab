"""Fail-closed v1.2.5 Bootstrap Validation Runtime design contract."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs" / "releases" / "v1.2.5-bootstrap-validation-runtime.md"
ARCHITECTURE = ROOT / "docs" / "architecture" / "bootstrap-validation-runtime.md"
PREDECESSOR = ROOT / "docs" / "releases" / "v1.2.4-bootstrap-apply-execution.md"
PRODUCTION = ROOT / "generator" / "core" / "bootstrap_validation.py"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v1_2_5_design_is_fail_closed_and_unaccepted() -> None:
    text = _read(DESIGN)
    assert "OpenProjectLab v1.2.5 Bootstrap Validation Runtime" in text
    assert "**Status:** Design / Contract Definition --- In Progress" in text
    assert "Production Implementation --- Not Started" in text
    assert "v1.2.5 Acceptance --- Not Accepted" in text
    assert not PRODUCTION.exists()


def test_v1_2_5_is_bound_to_terminal_v1_2_4() -> None:
    text = _read(DESIGN)
    predecessor = _read(PREDECESSOR)
    assert "v1.2.4 Bootstrap Apply Execution --- Accepted / Implemented" in text
    assert "Implementation PR #236 --- Merged" in predecessor
    assert "Production Implementation Slice --- Completed" in predecessor


def test_validation_contracts_are_explicit() -> None:
    text = _read(DESIGN)
    for marker in (
        "### 3.1 BootstrapValidationRequest",
        "### 3.2 BootstrapValidationCheck",
        "### 3.3 BootstrapValidationFinding",
        "### 3.4 BootstrapValidationResult",
        "### 3.5 BootstrapValidator",
        "BootstrapValidator.validate(request)",
    ):
        assert marker in text


def test_validation_is_inspection_only() -> None:
    combined = _read(DESIGN) + _read(ARCHITECTURE)
    for marker in (
        "Validation --- Inspection Only",
        "Filesystem Mutation --- Forbidden",
        "Silent Repair --- Forbidden",
        "Apply / Re-apply --- Forbidden",
        "Manifest / Backup / Checkpoint Writes --- Forbidden",
    ):
        assert marker in combined


def test_ordering_and_validity_are_deterministic() -> None:
    text = _read(DESIGN)
    for marker in (
        "check order is explicit and stable",
        "finding order follows check order",
        "equivalent request and observable state produce equivalent results",
        "duplicate check identities are rejected",
        "error`, `warning`, and `info",
        "invalid when one or more `error` findings exist",
    ):
        assert marker in text


def test_invalid_state_and_check_failure_are_distinct() -> None:
    combined = _read(DESIGN) + _read(ARCHITECTURE)
    for marker in (
        "Invalid State --- Finding",
        "Check Execution Failure --- Fail Closed",
        "Success-shaped Partial Result --- Forbidden",
        "failed check identity",
        "already completed check evidence",
    ):
        assert marker in combined


def test_validation_never_repairs_or_rolls_back() -> None:
    text = _read(DESIGN)
    assert "Validation failure does not imply automatic rollback" in text
    assert "must not call apply" in text
    assert "Automatic Repair --- Forbidden" in text
    assert "Automatic Rollback --- Not Applicable / Not Performed" in text


def test_future_surfaces_remain_closed() -> None:
    combined = _read(DESIGN) + _read(ARCHITECTURE)
    for marker in (
        "repair workflow --- Deferred",
        "checkpoint / resume --- Deferred",
        "generalized rollback --- Deferred",
        "parallel validation --- Deferred",
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
        "v1.2.5 Acceptance --- Not Accepted",
    ):
        assert marker in text
