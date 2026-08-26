"""Fail-closed v1.2.2 Bootstrap Planning Core design contract."""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs" / "releases" / "v1.2.2-bootstrap-planning-core.md"
V1_2_1_DESIGN = ROOT / "docs" / "releases" / "v1.2.1-bootstrap-framework-design.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_v1_2_2_design_exists_and_is_not_preaccepted() -> None:
    text = _read(DESIGN)

    assert "OpenProjectLab v1.2.2 Bootstrap Planning Core" in text
    assert "**Status:** Design / Contract Definition --- In Progress" in text
    assert "v1.2.2 Bootstrap Planning Core --- Not Accepted" in text
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


def test_acceptance_gates_remain_fail_closed() -> None:
    text = _read(DESIGN)

    for marker in (
        "BootstrapStep contract --- Pending",
        "BootstrapPlan contract --- Pending",
        "BootstrapPlanner contract --- Pending",
        "Deterministic ordering --- Pending",
        "Equivalent-plan behavior --- Pending",
        "GeneratorRegistry reuse --- Pending",
        "Generator lifecycle preservation --- Pending",
        "Mutation-free planning --- Pending",
        "No generator execution --- Pending",
        "No network access --- Pending",
        "No plugin activation --- Pending",
        "Expected-effect representation --- Pending",
        "Focused tests --- Pending",
        "Design PR required CI --- Pending",
        "Post-merge consistency verification --- Pending",
        "Terminal design acceptance --- Pending",
        "v1.2.2 Bootstrap Planning Core --- Not Accepted",
        "v1.2 Implementation --- Not Started",
    ):
        assert marker in text
