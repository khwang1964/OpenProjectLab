"""Typed, deterministic, and silent Bootstrap SDK runtime adapter."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from generator.core.bootstrap_apply import (
    BootstrapApplyError,
    BootstrapApplyExecutor,
    BootstrapApplyResult,
)
from generator.core.bootstrap_dry_run import BootstrapDryRunExecutor, BootstrapDryRunPreview
from generator.core.bootstrap_planning import (
    BootstrapPlan,
    BootstrapStep,
    ExpectedEffect,
    FrozenMapping,
    _freeze_mapping,
)
from generator.core.bootstrap_runtime import (
    BootstrapRuntimeCoordinator,
    BootstrapRuntimeMode,
    BootstrapRuntimeRequest,
)
from generator.core.bootstrap_validation import (
    BootstrapValidationCheck,
    BootstrapValidationError,
    BootstrapValidationRequest,
    BootstrapValidationResult,
    BootstrapValidator,
)
from generator.core.models import GenerateRequest, GenerationResult, RuntimeOptions
from generator.generators.bootstrap_generator import BootstrapGenerator


class BootstrapSdkMode(str, Enum):
    """Select one public SDK bootstrap lifecycle."""

    PREVIEW = "preview"
    APPLY = "apply"
    APPLY_AND_VALIDATE = "apply-and-validate"


class BootstrapSdkUsageError(ValueError):
    """Report invalid SDK input before runtime execution."""


class BootstrapSdkExecutionError(RuntimeError):
    """Report fail-closed runtime failure with completed evidence."""

    def __init__(
        self,
        message: str,
        *,
        phase: str,
        failed_identity: str | None = None,
        completed_evidence: tuple[object, ...] = (),
    ) -> None:
        super().__init__(message)
        self.phase = phase
        self.failed_identity = failed_identity
        self.completed_evidence = tuple(completed_evidence)


@dataclass(frozen=True, slots=True)
class BootstrapSdkRequest:
    """Hold normalized immutable inputs for one SDK lifecycle."""

    template_root: Path
    output_root: Path
    project_slug: str
    values: FrozenMapping | Mapping[str, object]
    mode: BootstrapSdkMode = BootstrapSdkMode.PREVIEW
    overwrite: bool = False
    validation_checks: tuple[BootstrapValidationCheck, ...] | Sequence[BootstrapValidationCheck] = (
        field(default_factory=tuple)
    )

    def __post_init__(self) -> None:
        if not isinstance(self.mode, BootstrapSdkMode):
            raise BootstrapSdkUsageError("mode must be a BootstrapSdkMode")
        slug = self.project_slug.strip().lower()
        if not slug:
            raise BootstrapSdkUsageError("project_slug must not be empty")
        if not isinstance(self.values, Mapping | tuple):
            raise BootstrapSdkUsageError("values must be a mapping")
        try:
            frozen_values = (
                _freeze_mapping(self.values)
                if isinstance(self.values, Mapping)
                else tuple(self.values)
            )
        except (TypeError, ValueError) as exc:
            raise BootstrapSdkUsageError(str(exc)) from exc
        object.__setattr__(self, "template_root", Path(self.template_root))
        object.__setattr__(self, "output_root", Path(self.output_root))
        object.__setattr__(self, "project_slug", slug)
        object.__setattr__(self, "values", frozen_values)
        object.__setattr__(self, "validation_checks", tuple(self.validation_checks))


@dataclass(frozen=True, slots=True)
class BootstrapSdkResult:
    """Expose immutable core lifecycle evidence without process policy."""

    plan: BootstrapPlan
    preview: BootstrapDryRunPreview | None = None
    apply_result: BootstrapApplyResult | None = None
    validation_result: BootstrapValidationResult | None = None

    @property
    def is_valid(self) -> bool | None:
        """Return validation state only when validation executed."""
        return self.validation_result.is_valid if self.validation_result is not None else None


class _SdkPlanner:
    def __init__(self, generator: BootstrapGenerator, project_root: Path) -> None:
        self._generator = generator
        self._project_root = project_root

    def plan(self, request: object) -> BootstrapPlan:
        if not isinstance(request, GenerateRequest):
            raise TypeError("Bootstrap SDK planner requires GenerateRequest")
        self._generator.validate_request(request)
        effects = tuple(
            ExpectedEffect(kind="create-directory", target=str(self._project_root / name))
            for name in BootstrapGenerator.DIRECTORY_MANIFEST
        ) + tuple(
            ExpectedEffect(kind="create-file", target=str(self._project_root / name))
            for name in BootstrapGenerator.TEMPLATE_MANIFEST
        )
        return BootstrapPlan(
            normalized_intent={"project_slug": request.values["project_slug"]},
            steps=(
                BootstrapStep(
                    step_id="0001:bootstrap",
                    generator_id="bootstrap",
                    normalized_inputs=request.values,
                    expected_effects=effects,
                    mutation_allowed=True,
                ),
            ),
            expected_effects=effects,
        )


class _SdkStepRunner:
    def __init__(self, generator: BootstrapGenerator, request: GenerateRequest) -> None:
        self._generator = generator
        self._request = request

    def run_step(self, plan: BootstrapPlan, step: BootstrapStep) -> GenerationResult:
        if plan.steps != (step,) or step.generator_id != BootstrapGenerator.name:
            raise ValueError("Bootstrap SDK apply received an unexpected plan")
        return self._generator.run(self._request)


def run_bootstrap(request: BootstrapSdkRequest) -> BootstrapSdkResult:
    """Execute one SDK lifecycle without writing streams or deriving exit codes."""
    if not isinstance(request, BootstrapSdkRequest):
        raise BootstrapSdkUsageError("run_bootstrap requires a BootstrapSdkRequest")

    values = dict(request.values)
    values.setdefault("project_slug", request.project_slug)
    project_root = request.output_root / request.project_slug
    generator = BootstrapGenerator(request.template_root)
    generation_request = GenerateRequest(
        generator_name=BootstrapGenerator.name,
        target=request.output_root,
        values=values,
        options=RuntimeOptions(overwrite=request.overwrite, dry_run=False),
    )
    runtime_mode = BootstrapRuntimeMode(request.mode.value)
    validation_request = (
        BootstrapValidationRequest(target=project_root, context=values)
        if request.mode is BootstrapSdkMode.APPLY_AND_VALIDATE
        else None
    )
    coordinator = BootstrapRuntimeCoordinator(
        planner=_SdkPlanner(generator, project_root),
        dry_run=BootstrapDryRunExecutor(),
        apply_executor=BootstrapApplyExecutor(_SdkStepRunner(generator, generation_request)),
        validator=BootstrapValidator(request.validation_checks),
    )
    try:
        result = coordinator.execute(
            BootstrapRuntimeRequest(
                planning_request=generation_request,
                mode=runtime_mode,
                validation_request=validation_request,
            )
        )
    except BootstrapApplyError as exc:
        raise BootstrapSdkExecutionError(
            str(exc),
            phase="apply",
            failed_identity=exc.failed_step_id,
            completed_evidence=exc.completed_steps,
        ) from exc
    except BootstrapValidationError as exc:
        raise BootstrapSdkExecutionError(
            str(exc),
            phase="validation",
            failed_identity=exc.failed_check_id,
            completed_evidence=exc.completed_findings,
        ) from exc
    except Exception as exc:
        raise BootstrapSdkExecutionError(str(exc), phase="runtime") from exc

    return BootstrapSdkResult(
        plan=result.plan,
        preview=result.preview,
        apply_result=result.apply_result,
        validation_result=result.validation_result,
    )


__all__ = [
    "BootstrapSdkExecutionError",
    "BootstrapSdkMode",
    "BootstrapSdkRequest",
    "BootstrapSdkResult",
    "BootstrapSdkUsageError",
    "run_bootstrap",
]
