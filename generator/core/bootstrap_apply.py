"""Sequential Bootstrap apply coordination over existing Generator contracts."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Protocol

from generator.core.bootstrap_planning import BootstrapPlan, BootstrapStep
from generator.core.models import GenerateRequest, GenerationResult
from generator.core.registry import GeneratorRegistry

type BootstrapRequestFactory = Callable[[BootstrapPlan, BootstrapStep], GenerateRequest]


class BootstrapStepRunner(Protocol):
    """Describe the internal adapter used to execute one planned step."""

    def run_step(
        self,
        plan: BootstrapPlan,
        step: BootstrapStep,
    ) -> GenerationResult:
        """Delegate one step through an existing Generator lifecycle."""


class GeneratorBootstrapStepRunner:
    """Resolve and run existing Generators without duplicating their lifecycle."""

    def __init__(
        self,
        registry: GeneratorRegistry,
        request_factory: BootstrapRequestFactory,
    ) -> None:
        self._registry = registry
        self._request_factory = request_factory

    def run_step(
        self,
        plan: BootstrapPlan,
        step: BootstrapStep,
    ) -> GenerationResult:
        """Map one Bootstrap step into ``BaseGenerator.run(request)``."""
        request = self._request_factory(plan, step)
        if not isinstance(request, GenerateRequest):
            raise TypeError("Bootstrap request factory must return GenerateRequest")
        if request.generator_name.strip().lower() != step.generator_id:
            raise ValueError("Bootstrap request generator identity does not match the step")

        generator = self._registry.create(step.generator_id)
        result = generator.run(request)
        if not isinstance(result, GenerationResult):
            raise TypeError("Generator run must return GenerationResult")
        return result


@dataclass(frozen=True, slots=True)
class BootstrapApplyStepResult:
    """Record immutable evidence for one successfully completed step."""

    step_id: str
    generator_id: str
    generation_result: GenerationResult


@dataclass(frozen=True, slots=True)
class BootstrapApplyResult:
    """Record ordered immutable evidence for a complete successful apply."""

    completed_steps: tuple[BootstrapApplyStepResult, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "completed_steps", tuple(self.completed_steps))

    @property
    def generation_results(self) -> tuple[GenerationResult, ...]:
        """Return Generator results in authoritative plan order."""
        return tuple(step.generation_result for step in self.completed_steps)


class BootstrapApplyError(RuntimeError):
    """Expose fail-fast partial-state evidence for one failed apply."""

    def __init__(
        self,
        *,
        failed_step_id: str,
        generator_id: str,
        completed_steps: tuple[BootstrapApplyStepResult, ...],
    ) -> None:
        super().__init__(f"Bootstrap apply failed at step: {failed_step_id}")
        self.failed_step_id = failed_step_id
        self.generator_id = generator_id
        self.completed_steps = tuple(completed_steps)


class BootstrapApplyExecutor:
    """Execute Bootstrap steps sequentially through an injected runner."""

    def __init__(self, step_runner: BootstrapStepRunner) -> None:
        self._step_runner = step_runner

    def apply(self, plan: BootstrapPlan) -> BootstrapApplyResult:
        """Apply an authoritative plan in order and stop at first failure."""
        if not isinstance(plan, BootstrapPlan):
            raise TypeError("bootstrap apply requires a BootstrapPlan")

        completed: list[BootstrapApplyStepResult] = []
        for step in plan.steps:
            try:
                generation_result = self._step_runner.run_step(plan, step)
                if not isinstance(generation_result, GenerationResult):
                    raise TypeError("Bootstrap step runner must return GenerationResult")
                if generation_result.generator_name.strip().lower() != step.generator_id:
                    raise ValueError("Generator result identity does not match the step")
            except Exception as exc:
                raise BootstrapApplyError(
                    failed_step_id=step.step_id,
                    generator_id=step.generator_id,
                    completed_steps=tuple(completed),
                ) from exc

            completed.append(
                BootstrapApplyStepResult(
                    step_id=step.step_id,
                    generator_id=step.generator_id,
                    generation_result=generation_result,
                )
            )

        return BootstrapApplyResult(completed_steps=tuple(completed))
