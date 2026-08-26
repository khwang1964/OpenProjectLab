"""Fail-closed v1.2.2 Bootstrap Planning Core design contract."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs" / "releases" / "v1.2.2-bootstrap-planning-core.md"
V1_2_1_DESIGN = ROOT / "docs" / "releases" / "v1.2.1-bootstrap-framework-design.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v1_2_2_design_is_terminally_accepted() -> None:
    text = _read(DESIGN)

    assert "OpenProjectLab v1.2.2 Bootstrap Planning Core" in text
    assert "**Status:** Accepted --- Terminally Closed" in text
    assert "v1.2.2 Bootstrap Planning Core --- Accepted" in text
    assert "v1.2 Implementation --- Not Started" in text


def test_v1_2_2_is_bound_to_accepted_v1_2_1_design() -> None:
    text = _read(DESIGN)
    predecessor = _read(V1_2_1_DESIGN)

    assert "**Predecessor:** v1.2.1 Bootstrap Framework Design Baseline --- Accepted" in text
    assert "v1.2.1 Bootstrap Framework Design Baseline --- Accepted" in predecessor


def test_planning_core_contracts_are_explicit() -> None:
    text = _read(DESIGN)

    for marker in (
        "### 3.1 BootstrapStep",
        "### 3.2 BootstrapPlan",
        "### 3.3 BootstrapPlanner",
        "BootstrapStep",
        "BootstrapPlan",
        "BootstrapPlanner",
    ):
        assert marker in text


def test_planning_is_mutation_free_and_non_executing() -> None:
    text = _read(DESIGN)

    for marker in (
        "Filesystem Mutation --- Forbidden",
        "Network Access --- Forbidden",
        "Plugin Activation --- Forbidden",
        "must not:",
        "execute a generator",
        "mutate the filesystem",
    ):
        assert marker in text


def test_existing_registry_and_generator_lifecycle_are_reused() -> None:
    text = _read(DESIGN)

    for marker in (
        "GeneratorRegistry Reuse",
        "reuse the existing GeneratorRegistry",
        "alternative generator registry",
        "existing generator lifecycle remains authoritative",
    ):
        assert marker in text


def test_deterministic_ordering_and_equivalent_plan_behavior_are_required() -> None:
    text = _read(DESIGN)

    for marker in (
        "stable step ordering",
        "stable expected-effect ordering",
        "Equivalent-Plan Behavior",
        "equivalent input produces equivalent ordered steps",
        "repeated planning does not produce nondeterministic ordering",
    ):
        assert marker in text


def test_expected_effects_are_data_only() -> None:
    text = _read(DESIGN)

    assert "Expected effects are descriptive planning data" in text
    assert "they are not execution commands" in text
    assert "expected effects remain data only" in text


def test_future_execution_surfaces_remain_closed() -> None:
    text = _read(DESIGN)

    for marker in (
        "dry-run execution --- Not Started",
        "apply execution --- Not Started",
        "validation runtime --- Not Started",
        "checkpoint / resume --- Deferred",
        "generalized rollback --- Deferred",
        "CLI Boundary --- Not Accepted",
    ):
        assert marker in text


def test_acceptance_gates_are_terminally_accepted() -> None:
    text = _read(DESIGN)

    for marker in (
        "BootstrapStep contract --- Accepted",
        "BootstrapPlan contract --- Accepted",
        "BootstrapPlanner contract --- Accepted",
        "Deterministic ordering --- Accepted",
        "Equivalent-plan behavior --- Accepted",
        "GeneratorRegistry reuse --- Accepted",
        "Generator lifecycle preservation --- Accepted",
        "Mutation-free planning --- Accepted",
        "No generator execution --- Accepted",
        "No network access --- Accepted",
        "No plugin activation --- Accepted",
        "Expected-effect representation --- Accepted",
        "Focused tests --- Passed",
        "Design PR #226 required CI --- Passed",
        "Design PR #226 squash merge --- Completed",
        "main synchronization --- Completed",
        "Post-merge consistency verification --- Passed",
        "Terminal design acceptance --- Completed",
        "v1.2.2 Bootstrap Planning Core --- Accepted",
        "v1.2 Implementation --- Not Started",
    ):
        assert marker in text


def test_v1_2_2_design_acceptance_closure_evidence() -> None:
    text = _read(DESIGN)

    assert "Design PR #226 --- Merged" in text
    assert "Design merge --- c76c1b931da7d0aaf13792546b451c46f4769fe0" in text
    assert "Post-merge consistency verification --- Passed" in text
    assert "BootstrapStep contract --- Accepted" in text
    assert "BootstrapPlan contract --- Accepted" in text
    assert "BootstrapPlanner contract --- Accepted" in text
    assert "dry-run execution --- Not Started" in text
    assert "apply execution --- Not Started" in text
    assert "validation runtime --- Not Started" in text
    assert "checkpoint / resume --- Deferred" in text
    assert "generalized rollback --- Deferred" in text
    assert "CLI Boundary --- Not Accepted" in text
    assert "v1.2 Implementation --- Not Started" in text
