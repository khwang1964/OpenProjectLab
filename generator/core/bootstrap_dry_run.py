"""Deterministic, mutation-free Bootstrap dry-run previews."""

from __future__ import annotations

from dataclasses import dataclass, field

from generator.core.bootstrap_planning import (
    BootstrapPlan,
    BootstrapStep,
    ExpectedEffect,
    FrozenMapping,
)


@dataclass(frozen=True, slots=True)
class BootstrapDryRunStep:
    """Project one planned step into immutable preview data."""

    step_id: str
    generator_id: str
    normalized_inputs: FrozenMapping = field(default_factory=tuple)
    expected_effects: tuple[ExpectedEffect, ...] = ()
    mutation_would_occur: bool = False

    @classmethod
    def from_planned_step(cls, step: BootstrapStep) -> BootstrapDryRunStep:
        """Preserve one authoritative planned step without executing it."""
        return cls(
            step_id=step.step_id,
            generator_id=step.generator_id,
            normalized_inputs=step.normalized_inputs,
            expected_effects=step.expected_effects,
            mutation_would_occur=step.mutation_allowed,
        )


@dataclass(frozen=True, slots=True)
class BootstrapDryRunPreview:
    """Represent a complete deterministic preview of a Bootstrap plan."""

    steps: tuple[BootstrapDryRunStep, ...]
    expected_effects: tuple[ExpectedEffect, ...]

    def __post_init__(self) -> None:
        """Keep preview collections immutable even for permissive callers."""
        object.__setattr__(self, "steps", tuple(self.steps))
        object.__setattr__(self, "expected_effects", tuple(self.expected_effects))

    @property
    def would_mutate(self) -> bool:
        """Report whether the authoritative plan describes later mutation."""
        return bool(self.expected_effects)


class BootstrapDryRunExecutor:
    """Project BootstrapPlan data without executing generators or effects."""

    def preview(self, plan: BootstrapPlan) -> BootstrapDryRunPreview:
        """Return an ordered, side-effect-free preview of ``plan``."""
        if not isinstance(plan, BootstrapPlan):
            raise TypeError("dry-run preview requires a BootstrapPlan")

        return BootstrapDryRunPreview(
            steps=tuple(BootstrapDryRunStep.from_planned_step(step) for step in plan.steps),
            expected_effects=plan.expected_effects,
        )
