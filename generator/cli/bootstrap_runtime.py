"""Stable, fail-closed Bootstrap CLI/runtime adapter."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

from generator.core.bootstrap_apply import BootstrapApplyExecutor
from generator.core.bootstrap_dry_run import BootstrapDryRunExecutor
from generator.core.bootstrap_planning import BootstrapPlan, BootstrapStep, ExpectedEffect
from generator.core.bootstrap_runtime import (
    BootstrapRuntimeCoordinator,
    BootstrapRuntimeMode,
    BootstrapRuntimeRequest,
)
from generator.core.bootstrap_validation import BootstrapValidationRequest, BootstrapValidator
from generator.core.models import GenerateRequest, GenerationResult, RuntimeOptions
from generator.generators.bootstrap_generator import BootstrapGenerator


@dataclass(frozen=True, slots=True)
class BootstrapCliRuntimeInput:
    """Hold normalized CLI inputs without exposing core runtime models publicly."""

    template_root: Path
    output_root: Path
    project_slug: str
    values: dict[str, object]
    overwrite: bool
    dry_run: bool
    validate: bool


class _CliPlanner:
    def __init__(self, generator: BootstrapGenerator, project_root: Path) -> None:
        self._generator = generator
        self._project_root = project_root

    def plan(self, request: object) -> BootstrapPlan:
        if not isinstance(request, GenerateRequest):
            raise TypeError("Bootstrap CLI planner requires GenerateRequest")
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


class _CliStepRunner:
    def __init__(self, generator: BootstrapGenerator, request: GenerateRequest) -> None:
        self._generator = generator
        self._request = request

    def run_step(self, plan: BootstrapPlan, step: BootstrapStep) -> GenerationResult:
        if plan.steps != (step,) or step.generator_id != BootstrapGenerator.name:
            raise ValueError("Bootstrap CLI apply received an unexpected plan")
        return self._generator.run(self._request)


def execute_bootstrap_runtime(value: BootstrapCliRuntimeInput) -> int:
    """Execute one explicitly selected runtime lifecycle and render CLI evidence."""
    if value.validate and value.dry_run:
        raise ValueError("--validate cannot be combined with --dry-run")

    project_root = value.output_root / value.project_slug
    generator = BootstrapGenerator(value.template_root)
    request = GenerateRequest(
        generator_name=BootstrapGenerator.name,
        target=value.output_root,
        values=value.values,
        options=RuntimeOptions(overwrite=value.overwrite, dry_run=False),
    )
    mode = (
        BootstrapRuntimeMode.PREVIEW
        if value.dry_run
        else BootstrapRuntimeMode.APPLY_AND_VALIDATE
        if value.validate
        else BootstrapRuntimeMode.APPLY
    )
    validation_request = (
        BootstrapValidationRequest(target=project_root, context=value.values)
        if value.validate
        else None
    )
    coordinator = BootstrapRuntimeCoordinator(
        planner=_CliPlanner(generator, project_root),
        dry_run=BootstrapDryRunExecutor(),
        apply_executor=BootstrapApplyExecutor(_CliStepRunner(generator, request)),
        validator=BootstrapValidator(()),
    )
    result = coordinator.execute(
        BootstrapRuntimeRequest(
            planning_request=request,
            mode=mode,
            validation_request=validation_request,
        )
    )

    if result.preview is not None:
        print(f"[DRY-RUN] 專案根目錄：{project_root}")
        print("[DRY-RUN] 預計效果：")
        for effect in result.preview.expected_effects:
            print(f"  - {effect.kind}: {effect.target}")
        return 0

    assert result.apply_result is not None
    generation_result = result.apply_result.generation_results[0]
    print(f"專案根目錄：{project_root}")
    print("檔案：")
    for path in generation_result.affected_paths:
        print(f"  - {path}")
    if result.validation_result is not None and not result.validation_result.is_valid:
        print("錯誤：Bootstrap validation failed", file=sys.stderr)
        return 1
    return 0
