"""Tests for deterministic, side-effect-free Bootstrap planning."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from generator.core.bootstrap_planning import (
    BootstrapPlan,
    BootstrapPlanner,
    BootstrapStep,
    ExpectedEffect,
)
from generator.core.exceptions import GeneratorNotFoundError
from generator.core.registry import GeneratorRegistry


class _ExplodingGenerator:
    """A generator type that proves planning never instantiates generators."""

    def __init__(self) -> None:
        raise AssertionError("planner must not instantiate generators")


def _registry(*names: str) -> GeneratorRegistry:
    registry = GeneratorRegistry()
    for name in names:
        registry.register(name, _ExplodingGenerator)
    return registry


def test_bootstrap_step_is_immutable() -> None:
    step = BootstrapStep(
        step_id="0001:course",
        generator_id="course",
    )

    with pytest.raises(FrozenInstanceError):
        step.generator_id = "week"  # type: ignore[misc]


def test_bootstrap_plan_is_immutable() -> None:
    plan = BootstrapPlan(
        normalized_intent=(("project", "demo"),),
        steps=(),
        expected_effects=(),
    )

    with pytest.raises(FrozenInstanceError):
        plan.steps = ()  # type: ignore[misc]


def test_planner_returns_deterministically_ordered_plan() -> None:
    planner = BootstrapPlanner(_registry("week", "course"))

    plan = planner.plan(
        intent={"project": "demo"},
        generator_names=("week", "course"),
    )

    assert plan.generator_ids == ("course", "week")
    assert tuple(step.step_id for step in plan.steps) == (
        "0001:course",
        "0002:week",
    )


def test_equivalent_inputs_produce_equivalent_plan() -> None:
    planner = BootstrapPlanner(_registry("course", "week"))

    first = planner.plan(
        intent={"language": "zh-TW", "project": "demo"},
        generator_names=("week", "course"),
        inputs_by_generator={
            "week": {"number": 1, "topics": ["a", "b"]},
            "course": {"title": "Demo"},
        },
    )
    second = planner.plan(
        intent={"project": "demo", "language": "zh-TW"},
        generator_names=("course", "week"),
        inputs_by_generator={
            "course": {"title": "Demo"},
            "week": {"topics": ["a", "b"], "number": 1},
        },
    )

    assert first == second


def test_planner_rejects_unknown_generator() -> None:
    planner = BootstrapPlanner(_registry("course"))

    with pytest.raises(GeneratorNotFoundError):
        planner.plan(
            intent={},
            generator_names=("course", "missing"),
        )


def test_planner_does_not_execute_or_instantiate_generator() -> None:
    planner = BootstrapPlanner(_registry("course"))

    plan = planner.plan(
        intent={"project": "demo"},
        generator_names=("course",),
    )

    assert plan.generator_ids == ("course",)


def test_planner_does_not_touch_filesystem(tmp_path: Path) -> None:
    planner = BootstrapPlanner(_registry("course"))
    before = tuple(tmp_path.iterdir())

    planner.plan(
        intent={"target": tmp_path},
        generator_names=("course",),
        effects_by_generator={
            "course": (
                {
                    "kind": "create-file",
                    "target": str(tmp_path / "README.md"),
                },
            ),
        },
    )

    assert tuple(tmp_path.iterdir()) == before


def test_expected_effects_are_descriptive_data_only() -> None:
    planner = BootstrapPlanner(_registry("course"))

    plan = planner.plan(
        intent={},
        generator_names=("course",),
        effects_by_generator={
            "course": (
                {"kind": "create-file", "target": "README.md"},
                {"kind": "create-directory", "target": "docs"},
            ),
        },
    )

    assert plan.expected_effects == (
        ExpectedEffect(kind="create-directory", target="docs"),
        ExpectedEffect(kind="create-file", target="README.md"),
    )
    assert plan.steps[0].mutation_allowed is True


def test_input_order_does_not_create_nondeterminism() -> None:
    planner = BootstrapPlanner(_registry("course", "lab", "week"))

    forward = planner.plan(
        intent={"project": "demo"},
        generator_names=("course", "lab", "week"),
    )
    reverse = planner.plan(
        intent={"project": "demo"},
        generator_names=("week", "lab", "course"),
    )

    assert forward == reverse


def test_planning_normalizes_nested_values_deterministically() -> None:
    planner = BootstrapPlanner(_registry("course"))

    first = planner.plan(
        intent={
            "options": {"b": 2, "a": 1},
            "tags": {"beta", "alpha"},
        },
        generator_names=("course",),
    )
    second = planner.plan(
        intent={
            "tags": {"alpha", "beta"},
            "options": {"a": 1, "b": 2},
        },
        generator_names=("course",),
    )

    assert first == second
