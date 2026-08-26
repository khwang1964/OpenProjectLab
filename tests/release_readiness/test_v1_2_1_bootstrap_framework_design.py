"""Fail-closed v1.2.1 Bootstrap Framework design contract."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs" / "releases" / "v1.2.1-bootstrap-framework-design.md"
V1_2_PLAN = ROOT / "docs" / "releases" / "v1.2-planning-baseline.md"

PREDECESSOR_MERGE = "0ba8d9de613a7a5de8b9335ed156381fc908a7a5"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_design_exists_and_is_not_preaccepted() -> None:
    text = _read(DESIGN)
    assert "OpenProjectLab v1.2.1 Bootstrap Framework Design Baseline" in text
    assert "**Status:** Design / Contract Definition --- In Progress" in text
    assert "v1.2.1 Bootstrap Framework Design Baseline --- Not Accepted" in text
    assert "v1.2 Implementation --- Not Started" in text


def test_design_is_bound_to_accepted_v1_2_planning_baseline() -> None:
    text = _read(DESIGN)
    predecessor = _read(V1_2_PLAN)
    assert "**Predecessor:** v1.2 Planning Baseline --- Accepted" in text
    assert f"**Predecessor Merge:** {PREDECESSOR_MERGE}" in text
    assert "v1.2 Planning Baseline --- Accepted" in predecessor


def test_core_contracts_are_explicit() -> None:
    text = _read(DESIGN)
    for marker in ("BootstrapPlan", "BootstrapStep", "BootstrapResult"):
        assert marker in text


def test_plan_dry_run_apply_semantics_are_explicit() -> None:
    text = _read(DESIGN)
    for marker in (
        "### plan",
        "### dry-run",
        "### apply",
        "no filesystem mutation",
        "no committed filesystem mutation",
        "Explicit mutation phase",
    ):
        assert marker in text


def test_existing_lifecycles_are_reused() -> None:
    text = _read(DESIGN)
    for marker in (
        "reuse the existing filesystem abstraction",
        "second transactional mutation engine",
        "composes existing generators",
        "alternative generator registry",
    ):
        assert marker in text


def test_failure_and_validation_are_fail_closed() -> None:
    text = _read(DESIGN)
    for marker in (
        "planning failures produce no mutation",
        "dry-run failures produce no committed mutation",
        "apply stops at the first non-recoverable step failure",
        "generalized rollback is explicitly out of scope",
        "Validation failure does not imply automatic rollback",
    ):
        assert marker in text


def test_checkpoint_resume_and_cli_are_not_preaccepted() -> None:
    text = _read(DESIGN)
    assert "Checkpoint / Resume --- Deferred" in text
    assert "CLI Boundary --- Not Accepted" in text
    assert "illustrative only" in text


def test_non_goals_keep_scope_closed() -> None:
    text = _read(DESIGN)
    for marker in (
        "second filesystem mutation pipeline",
        "second generator lifecycle",
        "generalized transaction rollback",
        "silent network access",
        "automatic plugin activation",
        "new Stable CLI syntax",
        "implementation before design acceptance",
    ):
        assert marker in text


def test_acceptance_gates_remain_fail_closed() -> None:
    text = _read(DESIGN)
    for marker in (
        "BootstrapPlan contract --- Pending",
        "BootstrapStep contract --- Pending",
        "BootstrapResult contract --- Pending",
        "plan semantics --- Pending",
        "dry-run semantics --- Pending",
        "apply semantics --- Pending",
        "filesystem boundary --- Pending",
        "generator composition boundary --- Pending",
        "failure semantics --- Pending",
        "validation semantics --- Pending",
        "Focused design tests --- Pending",
        "Design PR required CI --- Pending",
        "Post-merge consistency verification --- Pending",
        "Terminal design acceptance --- Pending",
        "v1.2.1 Bootstrap Framework Design Baseline --- Not Accepted",
        "v1.2 Implementation --- Not Started",
    ):
        assert marker in text
