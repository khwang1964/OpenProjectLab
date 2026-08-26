"""Fail-closed v1.2.1 Bootstrap Framework design contract."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs" / "releases" / "v1.2.1-bootstrap-framework-design.md"
V1_2_PLAN = ROOT / "docs" / "releases" / "v1.2-planning-baseline.md"

PREDECESSOR_MERGE = "0ba8d9de613a7a5de8b9335ed156381fc908a7a5"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_design_is_terminally_accepted() -> None:
    text = _read(DESIGN)
    assert "OpenProjectLab v1.2.1 Bootstrap Framework Design Baseline" in text
    assert "**Status:** Accepted --- Terminally Closed" in text
    assert "v1.2.1 Bootstrap Framework Design Baseline --- Accepted" in text
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


def test_acceptance_gates_are_terminally_accepted() -> None:
    text = _read(DESIGN)
    for marker in (
        "BootstrapPlan contract --- Accepted",
        "BootstrapStep contract --- Accepted",
        "BootstrapResult contract --- Accepted",
        "plan semantics --- Accepted",
        "dry-run semantics --- Accepted",
        "apply semantics --- Accepted",
        "filesystem boundary --- Accepted",
        "generator composition boundary --- Accepted",
        "failure semantics --- Accepted",
        "validation semantics --- Accepted",
        "Focused design tests --- Passed",
        "Design PR #224 required CI --- Passed",
        "Design PR #224 squash merge --- Completed",
        "main synchronization --- Completed",
        "Post-merge consistency verification --- Passed",
        "Terminal design acceptance --- Completed",
        "v1.2.1 Bootstrap Framework Design Baseline --- Accepted",
        "v1.2 Implementation --- Not Started",
    ):
        assert marker in text


def test_design_acceptance_closure_evidence() -> None:
    text = _read(DESIGN)
    assert "Design PR #224 --- Merged" in text
    assert "Design merge --- f9f98b35aef679d2521498d6246c201906a3e721" in text
    assert "Focused post-merge verification --- 9 passed" in text
    assert "Architecture Contract --- Accepted" in text
    assert "BootstrapPlan / BootstrapStep / BootstrapResult --- Accepted" in text
    assert "Checkpoint / Resume --- Deferred" in text
    assert "CLI Boundary --- Not Accepted" in text
    assert "v1.2 Implementation --- Not Started" in text
