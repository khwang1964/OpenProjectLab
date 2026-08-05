"""Contract tests for the shared generator planning lifecycle."""

from pathlib import Path

import pytest

from generator.core.context import GeneratorContext
from generator.core.models import (
    GenerateRequest,
    GenerationOperation,
    GenerationPlan,
    GenerationResult,
    RuntimeOptions,
    WriteResult,
    WriteStatus,
)
from generator.generators.base import BaseGenerator


class LifecycleGenerator(BaseGenerator):
    """Record lifecycle calls made by BaseGenerator.run()."""

    name = "lifecycle"

    def __init__(
        self,
        *,
        validation_error: Exception | None = None,
        planning_error: Exception | None = None,
    ) -> None:
        """Initialize lifecycle observations and injected failures."""
        super().__init__()
        self.events: list[str] = []
        self.validation_error = validation_error
        self.planning_error = planning_error
        self.planned: GenerationPlan | None = None
        self.executed_plan: GenerationPlan | None = None

    def validate_request(self, request: GenerateRequest) -> None:
        """Record request validation."""
        self.events.append("validate")
        if self.validation_error is not None:
            raise self.validation_error

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Build one deterministic generation plan."""
        self.events.append("plan")
        if self.planning_error is not None:
            raise self.planning_error

        self.planned = GenerationPlan(
            generator_name=self.name,
            operations=(
                GenerationOperation(
                    template_name="README.md.tpl",
                    destination=request.target / "README.md",
                ),
            ),
        )
        return self.planned

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Record execution of the supplied plan."""
        self.events.append("execute")
        self.executed_plan = plan
        return GenerationResult(
            generator_name=self.name,
            writes=(
                WriteResult(
                    path=plan.operations[0].destination,
                    status=WriteStatus.CREATED,
                ),
            ),
            dry_run=request.options.dry_run,
        )

    def generate(self, context: GeneratorContext) -> None:
        """Satisfy the legacy abstract hook during lifecycle migration."""
        raise AssertionError("Legacy generate() must not be called")


def make_request(tmp_path: Path, *, dry_run: bool = False) -> GenerateRequest:
    """Build one canonical lifecycle request."""
    return GenerateRequest(
        generator_name=LifecycleGenerator.name,
        target=tmp_path / "output",
        options=RuntimeOptions(dry_run=dry_run),
    )


@pytest.mark.parametrize("dry_run", [False, True])
def test_run_uses_one_plan_for_execution(
    tmp_path: Path,
    *,
    dry_run: bool,
) -> None:
    """Validate, plan, and execute the same plan in either runtime mode."""
    generator = LifecycleGenerator()

    result = generator.run(make_request(tmp_path, dry_run=dry_run))

    assert generator.events == ["validate", "plan", "execute"]
    assert generator.planned is not None
    assert generator.executed_plan is generator.planned
    assert result.generator_name == generator.name
    assert result.dry_run is dry_run
    assert result.writes[0].path == generator.planned.operations[0].destination


def test_validation_failure_prevents_planning_and_execution(
    tmp_path: Path,
) -> None:
    """Propagate validation failures before planning or execution."""
    expected = RuntimeError("validation failed")
    generator = LifecycleGenerator(validation_error=expected)

    with pytest.raises(RuntimeError) as captured:
        generator.run(make_request(tmp_path))

    assert captured.value is expected
    assert generator.events == ["validate"]


def test_planning_failure_prevents_execution(tmp_path: Path) -> None:
    """Propagate planning failures before execution."""
    expected = RuntimeError("planning failed")
    generator = LifecycleGenerator(planning_error=expected)

    with pytest.raises(RuntimeError) as captured:
        generator.run(make_request(tmp_path))

    assert captured.value is expected
    assert generator.events == ["validate", "plan"]
