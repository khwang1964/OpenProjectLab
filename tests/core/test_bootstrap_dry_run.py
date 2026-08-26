"""Tests for deterministic, mutation-free Bootstrap dry-run previews."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path
from typing import Any

import pytest

from generator.core.bootstrap_dry_run import (
    BootstrapDryRunExecutor,
    BootstrapDryRunPreview,
    BootstrapDryRunStep,
)
from generator.core.bootstrap_planning import (
    BootstrapPlan,
    BootstrapStep,
    ExpectedEffect,
)


def _plan(target: str = "README.md") -> BootstrapPlan:
    effects = (
        ExpectedEffect(kind="create-directory", target="docs"),
        ExpectedEffect(kind="create-file", target=target),
    )
    return BootstrapPlan(
        normalized_intent=(("project", "demo"),),
        steps=(
            BootstrapStep(
                step_id="0001:course",
                generator_id="course",
                normalized_inputs=(("title", "Demo"),),
                expected_effects=effects,
                mutation_allowed=True,
            ),
            BootstrapStep(
                step_id="0002:week",
                generator_id="week",
                normalized_inputs=(("number", 1),),
            ),
        ),
        expected_effects=effects,
    )


def test_preview_preserves_authoritative_plan_order() -> None:
    preview = BootstrapDryRunExecutor().preview(_plan())

    assert tuple(step.step_id for step in preview.steps) == (
        "0001:course",
        "0002:week",
    )
    assert tuple(step.generator_id for step in preview.steps) == (
        "course",
        "week",
    )


def test_preview_preserves_expected_effect_order_as_data() -> None:
    plan = _plan()

    preview = BootstrapDryRunExecutor().preview(plan)

    assert preview.expected_effects == plan.expected_effects
    assert preview.steps[0].expected_effects == plan.steps[0].expected_effects
    assert preview.steps[0].mutation_would_occur is True
    assert preview.would_mutate is True


def test_equivalent_plans_produce_equivalent_previews() -> None:
    executor = BootstrapDryRunExecutor()

    assert executor.preview(_plan()) == executor.preview(_plan())


def test_preview_models_are_immutable() -> None:
    preview = BootstrapDryRunExecutor().preview(_plan())

    with pytest.raises(FrozenInstanceError):
        preview.steps = ()  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        preview.steps[0].generator_id = "week"  # type: ignore[misc]


def test_preview_does_not_mutate_filesystem(tmp_path: Path) -> None:
    target = tmp_path / "README.md"
    before = tuple(tmp_path.iterdir())

    preview = BootstrapDryRunExecutor().preview(_plan(str(target)))

    assert preview.expected_effects[-1].target == str(target)
    assert tuple(tmp_path.iterdir()) == before
    assert not target.exists()


def test_empty_plan_produces_complete_empty_preview() -> None:
    plan = BootstrapPlan(normalized_intent=(), steps=(), expected_effects=())

    preview = BootstrapDryRunExecutor().preview(plan)

    assert preview == BootstrapDryRunPreview(steps=(), expected_effects=())
    assert preview.would_mutate is False


def test_preview_rejects_non_plan_input_fail_closed(tmp_path: Path) -> None:
    before = tuple(tmp_path.iterdir())

    with pytest.raises(TypeError, match="requires a BootstrapPlan"):
        BootstrapDryRunExecutor().preview(object())  # type: ignore[arg-type]

    assert tuple(tmp_path.iterdir()) == before


def test_step_projection_rejects_no_data_or_executes_nothing() -> None:
    step = BootstrapStep(step_id="0001:course", generator_id="course")

    preview_step = BootstrapDryRunStep.from_planned_step(step)

    assert preview_step == BootstrapDryRunStep(
        step_id="0001:course",
        generator_id="course",
    )


def test_preview_has_no_dependency_injection_or_execution_input() -> None:
    executor: Any = BootstrapDryRunExecutor()

    assert vars(executor) == {}
    assert executor.preview(_plan()).steps
