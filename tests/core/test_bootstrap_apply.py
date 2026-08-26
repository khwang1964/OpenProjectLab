"""Tests for sequential, fail-fast Bootstrap apply execution."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from generator.core.bootstrap_apply import (
    BootstrapApplyError,
    BootstrapApplyExecutor,
    BootstrapApplyResult,
    BootstrapApplyStepResult,
    GeneratorBootstrapStepRunner,
)
from generator.core.bootstrap_planning import (
    BootstrapPlan,
    BootstrapStep,
    ExpectedEffect,
)
from generator.core.models import (
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
    RuntimeOptions,
)
from generator.core.registry import GeneratorRegistry
from generator.generators.base import BaseGenerator


def _step(index: int, generator_id: str) -> BootstrapStep:
    return BootstrapStep(
        step_id=f"{index:04d}:{generator_id}",
        generator_id=generator_id,
        normalized_inputs=(("title", generator_id.title()),),
        expected_effects=(ExpectedEffect(kind="create-file", target=f"{generator_id}.md"),),
        mutation_allowed=True,
    )


def _plan(*steps: BootstrapStep) -> BootstrapPlan:
    return BootstrapPlan(
        normalized_intent=(("target", "project"),),
        steps=steps,
        expected_effects=tuple(effect for step in steps for effect in step.expected_effects),
    )


class _RecordingRunner:
    def __init__(self, *, fail_on: str | None = None) -> None:
        self.calls: list[str] = []
        self.fail_on = fail_on

    def run_step(
        self,
        plan: BootstrapPlan,
        step: BootstrapStep,
    ) -> GenerationResult:
        del plan
        self.calls.append(step.step_id)
        if step.step_id == self.fail_on:
            raise RuntimeError("planned failure")
        return GenerationResult(generator_name=step.generator_id)


def test_apply_preserves_authoritative_plan_order() -> None:
    runner = _RecordingRunner()
    plan = _plan(_step(1, "course"), _step(2, "week"))

    result = BootstrapApplyExecutor(runner).apply(plan)

    assert runner.calls == ["0001:course", "0002:week"]
    assert tuple(step.step_id for step in result.completed_steps) == (
        "0001:course",
        "0002:week",
    )
    assert tuple(item.generator_name for item in result.generation_results) == (
        "course",
        "week",
    )


def test_apply_executes_each_step_once() -> None:
    runner = _RecordingRunner()
    plan = _plan(_step(1, "course"), _step(2, "week"))

    BootstrapApplyExecutor(runner).apply(plan)

    assert runner.calls.count("0001:course") == 1
    assert runner.calls.count("0002:week") == 1


def test_empty_plan_returns_empty_immutable_result() -> None:
    result = BootstrapApplyExecutor(_RecordingRunner()).apply(_plan())

    assert result == BootstrapApplyResult()
    assert result.generation_results == ()


def test_apply_results_are_immutable() -> None:
    result = BootstrapApplyExecutor(_RecordingRunner()).apply(_plan(_step(1, "course")))

    with pytest.raises(FrozenInstanceError):
        result.completed_steps = ()  # type: ignore[misc]

    with pytest.raises(FrozenInstanceError):
        result.completed_steps[0].generator_id = "week"  # type: ignore[misc]


def test_failure_stops_later_steps_and_exposes_partial_state() -> None:
    runner = _RecordingRunner(fail_on="0002:week")
    plan = _plan(
        _step(1, "course"),
        _step(2, "week"),
        _step(3, "lab"),
    )

    with pytest.raises(BootstrapApplyError) as captured:
        BootstrapApplyExecutor(runner).apply(plan)

    error = captured.value
    assert runner.calls == ["0001:course", "0002:week"]
    assert error.failed_step_id == "0002:week"
    assert error.generator_id == "week"
    assert tuple(step.step_id for step in error.completed_steps) == ("0001:course",)
    assert isinstance(error.__cause__, RuntimeError)


def test_first_step_failure_has_empty_partial_state() -> None:
    runner = _RecordingRunner(fail_on="0001:course")

    with pytest.raises(BootstrapApplyError) as captured:
        BootstrapApplyExecutor(runner).apply(_plan(_step(1, "course")))

    assert captured.value.completed_steps == ()


def test_expected_effects_are_not_executed_as_filesystem_commands(
    tmp_path: Path,
) -> None:
    target = tmp_path / "course.md"
    step = BootstrapStep(
        step_id="0001:course",
        generator_id="course",
        expected_effects=(ExpectedEffect(kind="create-file", target=str(target)),),
        mutation_allowed=True,
    )

    BootstrapApplyExecutor(_RecordingRunner()).apply(_plan(step))

    assert not target.exists()
    assert tuple(tmp_path.iterdir()) == ()


def test_apply_rejects_non_plan_input() -> None:
    with pytest.raises(TypeError, match="requires a BootstrapPlan"):
        BootstrapApplyExecutor(_RecordingRunner()).apply(object())  # type: ignore[arg-type]


class _LifecycleGenerator(BaseGenerator):
    events: list[str] = []

    def validate_request(self, request: GenerateRequest) -> None:
        self.events.append(f"validate:{request.generator_name}")

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        self.events.append(f"plan:{request.generator_name}")
        return GenerationPlan(generator_name=request.generator_name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        self.events.append(f"execute:{plan.generator_name}")
        return GenerationResult(generator_name=request.generator_name)


def test_registry_runner_reuses_existing_generator_lifecycle(tmp_path: Path) -> None:
    _LifecycleGenerator.events = []
    registry = GeneratorRegistry()
    registry.register("course", _LifecycleGenerator)

    def request_factory(
        plan: BootstrapPlan,
        step: BootstrapStep,
    ) -> GenerateRequest:
        del plan
        return GenerateRequest(
            generator_name=step.generator_id,
            target=tmp_path,
            values=dict(step.normalized_inputs),
            options=RuntimeOptions(),
        )

    executor = BootstrapApplyExecutor(GeneratorBootstrapStepRunner(registry, request_factory))

    result = executor.apply(_plan(_step(1, "course")))

    assert _LifecycleGenerator.events == [
        "validate:course",
        "plan:course",
        "execute:course",
    ]
    assert result.completed_steps[0] == BootstrapApplyStepResult(
        step_id="0001:course",
        generator_id="course",
        generation_result=GenerationResult(generator_name="course"),
    )


def test_registry_runner_rejects_mismatched_request_identity() -> None:
    registry = GeneratorRegistry()
    registry.register("course", _LifecycleGenerator)

    def wrong_request(
        plan: BootstrapPlan,
        step: BootstrapStep,
    ) -> GenerateRequest:
        del plan, step
        return GenerateRequest(generator_name="week", target=Path("project"))

    executor = BootstrapApplyExecutor(GeneratorBootstrapStepRunner(registry, wrong_request))

    with pytest.raises(BootstrapApplyError) as captured:
        executor.apply(_plan(_step(1, "course")))

    assert isinstance(captured.value.__cause__, ValueError)


class _WrongResultRunner:
    def run_step(
        self,
        plan: BootstrapPlan,
        step: BootstrapStep,
    ) -> GenerationResult:
        del plan, step
        return GenerationResult(generator_name="wrong")


def test_apply_rejects_mismatched_result_identity() -> None:
    with pytest.raises(BootstrapApplyError) as captured:
        BootstrapApplyExecutor(_WrongResultRunner()).apply(_plan(_step(1, "course")))

    assert isinstance(captured.value.__cause__, ValueError)
