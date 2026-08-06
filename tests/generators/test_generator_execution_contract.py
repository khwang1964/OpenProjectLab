"""Define the canonical execution contract shared by generators."""

from __future__ import annotations

from pathlib import Path

import pytest

from generator.core.models import (
    GenerateRequest,
    GenerationOperation,
    GenerationPlan,
    GenerationResult,
    RuntimeOptions,
    WritePolicy,
)
from generator.generators.base import BaseGenerator


class ValidationFailure(RuntimeError):
    """Represent a deliberate validation failure in contract tests."""


class PlanningFailure(RuntimeError):
    """Represent a deliberate planning failure in contract tests."""


class ExecutionFailure(RuntimeError):
    """Represent a deliberate execution failure in contract tests."""


class RecordingGenerator(BaseGenerator):
    """Record lifecycle calls made through the canonical run entry point."""

    name = "recording"

    def __init__(
        self,
        *,
        fail_validation: bool = False,
        fail_planning: bool = False,
        fail_execution: bool = False,
    ) -> None:
        """Configure lifecycle failures for one contract test."""
        super().__init__()
        self.events: list[str] = []
        self.fail_validation = fail_validation
        self.fail_planning = fail_planning
        self.fail_execution = fail_execution
        self.received_request: GenerateRequest | None = None
        self.received_plan: GenerationPlan | None = None

    def validate_request(self, request: GenerateRequest) -> None:
        """Record and optionally reject the request."""
        self.events.append("validate")
        self.received_request = request

        if self.fail_validation:
            raise ValidationFailure("validation failed")

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Record planning and return one immutable operation."""
        self.events.append("plan")

        if self.fail_planning:
            raise PlanningFailure("planning failed")

        return GenerationPlan(
            generator_name=self.name,
            operations=(
                GenerationOperation(
                    template_name="README.md.j2",
                    destination=request.target / "README.md",
                    context=request.values,
                    write_policy=request.options.write_policy,
                ),
            ),
        )

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Record execution and return a result without filesystem mutation."""
        self.events.append("execute")
        self.received_request = request
        self.received_plan = plan

        if self.fail_execution:
            raise ExecutionFailure("execution failed")

        return GenerationResult(
            generator_name=self.name,
            dry_run=request.options.dry_run,
        )


@pytest.fixture
def generation_request(tmp_path: Path) -> GenerateRequest:
    """Return a valid request for execution-contract tests."""
    return GenerateRequest(
        generator_name="recording",
        target=tmp_path / "output",
        values={"project_name": "Execution Contract"},
    )


def test_run_executes_the_canonical_lifecycle_in_order(
    generation_request: GenerateRequest,
) -> None:
    """Run validation, planning, and execution in the required order."""
    generator = RecordingGenerator()

    result = generator.run(generation_request)

    assert generator.events == [
        "validate",
        "plan",
        "execute",
    ]
    assert generator.received_request is generation_request
    assert generator.received_plan is not None
    assert result == GenerationResult(generator_name="recording")


def test_run_passes_the_created_plan_to_execution(
    generation_request: GenerateRequest,
) -> None:
    """Execute exactly the immutable plan produced by planning."""
    generator = RecordingGenerator()

    generator.run(generation_request)

    assert generator.received_plan == GenerationPlan(
        generator_name="recording",
        operations=(
            GenerationOperation(
                template_name="README.md.j2",
                destination=generation_request.target / "README.md",
                context=generation_request.values,
                write_policy=WritePolicy.CREATE_ONLY,
            ),
        ),
    )


def test_validation_failure_stops_before_planning_and_execution(
    generation_request: GenerateRequest,
) -> None:
    """Stop the lifecycle immediately when request validation fails."""
    generator = RecordingGenerator(fail_validation=True)

    with pytest.raises(ValidationFailure, match="validation failed"):
        generator.run(generation_request)

    assert generator.events == ["validate"]
    assert generator.received_plan is None
    assert not generation_request.target.exists()


def test_planning_failure_stops_before_execution(
    generation_request: GenerateRequest,
) -> None:
    """Prevent execution when an immutable plan cannot be produced."""
    generator = RecordingGenerator(fail_planning=True)

    with pytest.raises(PlanningFailure, match="planning failed"):
        generator.run(generation_request)

    assert generator.events == [
        "validate",
        "plan",
    ]
    assert generator.received_plan is None
    assert not generation_request.target.exists()


def test_execution_failure_is_propagated_without_restarting_lifecycle(
    generation_request: GenerateRequest,
) -> None:
    """Propagate execution errors after one validation and planning pass."""
    generator = RecordingGenerator(fail_execution=True)

    with pytest.raises(ExecutionFailure, match="execution failed"):
        generator.run(generation_request)

    assert generator.events == [
        "validate",
        "plan",
        "execute",
    ]
    assert generator.received_plan is not None


def test_dry_run_uses_the_complete_lifecycle_without_filesystem_mutation(
    tmp_path: Path,
) -> None:
    """Validate, plan, and simulate execution during dry-run mode."""
    target = tmp_path / "output"
    generation_request = GenerateRequest(
        generator_name="recording",
        target=target,
        values={"project_name": "Execution Contract"},
        options=RuntimeOptions(dry_run=True),
    )
    generator = RecordingGenerator()

    result = generator.run(generation_request)

    assert generator.events == [
        "validate",
        "plan",
        "execute",
    ]
    assert result.dry_run is True
    assert result.writes == ()
    assert result.manifest_updated is False
    assert not target.exists()
