"""Deterministic coordination of accepted Bootstrap runtimes."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from generator.core.bootstrap_apply import BootstrapApplyExecutor, BootstrapApplyResult
from generator.core.bootstrap_dry_run import BootstrapDryRunExecutor, BootstrapDryRunPreview
from generator.core.bootstrap_planning import BootstrapPlan
from generator.core.bootstrap_validation import (
    BootstrapValidationRequest,
    BootstrapValidationResult,
    BootstrapValidator,
)


class BootstrapRuntimeMode(str, Enum):
    """Select one closed Bootstrap runtime lifecycle."""

    PREVIEW = "preview"
    APPLY = "apply"
    APPLY_AND_VALIDATE = "apply-and-validate"


class BootstrapRuntimePlanner(Protocol):
    """Create one authoritative plan from injected planning intent."""

    def plan(self, request: object) -> BootstrapPlan:
        """Return the authoritative plan exactly once."""


@dataclass(frozen=True, slots=True)
class BootstrapRuntimeRequest:
    """Hold immutable coordination inputs and an explicit mode."""

    planning_request: object
    mode: BootstrapRuntimeMode
    validation_request: BootstrapValidationRequest | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.mode, BootstrapRuntimeMode):
            raise TypeError("mode must be a BootstrapRuntimeMode")
        if self.mode is BootstrapRuntimeMode.APPLY_AND_VALIDATE:
            if not isinstance(self.validation_request, BootstrapValidationRequest):
                raise ValueError("apply-and-validate requires a validation_request")
        elif self.validation_request is not None:
            raise ValueError("validation_request is only valid for apply-and-validate")


@dataclass(frozen=True, slots=True)
class BootstrapRuntimeResult:
    """Expose authoritative plan and only actually completed phase evidence."""

    plan: BootstrapPlan
    preview: BootstrapDryRunPreview | None = None
    apply_result: BootstrapApplyResult | None = None
    validation_result: BootstrapValidationResult | None = None


class BootstrapRuntimeCoordinator:
    """Coordinate accepted runtimes without duplicating their behavior."""

    def __init__(
        self,
        *,
        planner: BootstrapRuntimePlanner,
        dry_run: BootstrapDryRunExecutor,
        apply_executor: BootstrapApplyExecutor,
        validator: BootstrapValidator,
    ) -> None:
        self._planner = planner
        self._dry_run = dry_run
        self._apply = apply_executor
        self._validator = validator

    def execute(self, request: BootstrapRuntimeRequest) -> BootstrapRuntimeResult:
        """Run the selected phases sequentially and fail closed."""
        if not isinstance(request, BootstrapRuntimeRequest):
            raise TypeError("bootstrap runtime requires a BootstrapRuntimeRequest")

        plan = self._planner.plan(request.planning_request)
        if not isinstance(plan, BootstrapPlan):
            raise TypeError("Bootstrap planner must return BootstrapPlan")

        if request.mode is BootstrapRuntimeMode.PREVIEW:
            return BootstrapRuntimeResult(
                plan=plan,
                preview=self._dry_run.preview(plan),
            )

        apply_result = self._apply.apply(plan)
        if request.mode is BootstrapRuntimeMode.APPLY:
            return BootstrapRuntimeResult(plan=plan, apply_result=apply_result)

        validation_request = request.validation_request
        assert validation_request is not None
        if validation_request.apply_result not in (None, apply_result):
            raise ValueError("validation request contains different apply evidence")
        if validation_request.apply_result is None:
            validation_request = BootstrapValidationRequest(
                target=validation_request.target,
                context=validation_request.context,
                apply_result=apply_result,
            )
        return BootstrapRuntimeResult(
            plan=plan,
            apply_result=apply_result,
            validation_result=self._validator.validate(validation_request),
        )
