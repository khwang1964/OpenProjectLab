"""Define the contract for removing the legacy generator lifecycle."""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

import pytest

from generator.core.models import (
    GenerateRequest,
    GenerationOperation,
    GenerationPlan,
    GenerationResult,
)
from generator.generators.base import BaseGenerator

LEGACY_LIFECYCLE_METHODS = (
    "validate",
    "prepare",
    "generate",
    "post_generate",
    "cleanup",
)


class RecordingGenerator(BaseGenerator):
    """Record calls made through the canonical execution lifecycle."""

    name = "recording"
    events: ClassVar[list[str]]

    def __init__(self) -> None:
        """Create a generator with an empty lifecycle event log."""
        super().__init__()
        self.events = []
        self.executed_plan: GenerationPlan | None = None

    def generate(self, context: object) -> None:
        """Satisfy the temporary legacy abstract hook.

        This method must be removed with the compatibility implementation
        after BaseGenerator no longer declares legacy lifecycle hooks.
        """
        del context
        raise AssertionError("Legacy generate() must not be called")

    def validate_request(self, request: GenerateRequest) -> None:
        """Record canonical request validation."""
        self.events.append("validate_request")
        assert request.generator_name == self.name

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Record planning and return an immutable generation plan."""
        self.events.append("plan")

        return GenerationPlan(
            generator_name=self.name,
            operations=(
                GenerationOperation(
                    template_name="README.md.j2",
                    destination=request.target / "README.md",
                ),
            ),
        )

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Record execution and preserve the exact plan instance."""
        self.events.append("execute")
        self.executed_plan = plan

        return GenerationResult(
            generator_name=self.name,
            dry_run=request.options.dry_run,
        )


@pytest.fixture
def generation_request(tmp_path: Path) -> GenerateRequest:
    """Return a valid request for legacy-removal contract tests."""
    return GenerateRequest(
        generator_name="recording",
        target=tmp_path / "output",
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "ADR 0009 is accepted, but the legacy BaseGenerator lifecycle "
        "has not been removed yet. Remove this marker with the legacy APIs."
    ),
)
@pytest.mark.parametrize("method_name", LEGACY_LIFECYCLE_METHODS)
def test_base_generator_does_not_expose_legacy_lifecycle_methods(
    method_name: str,
) -> None:
    """Require the legacy GeneratorContext lifecycle to be absent."""
    assert not hasattr(BaseGenerator, method_name)


def test_run_remains_the_canonical_execution_entry_point(
    generation_request: GenerateRequest,
) -> None:
    """Keep run() as the framework-controlled execution entry point."""
    generator = RecordingGenerator()

    result = generator.run(generation_request)

    assert generator.events == [
        "validate_request",
        "plan",
        "execute",
    ]
    assert result == GenerationResult(generator_name="recording")


def test_run_passes_the_exact_generation_plan_to_execute(
    generation_request: GenerateRequest,
) -> None:
    """Preserve the immutable plan object across the execution boundary."""
    generator = RecordingGenerator()

    generator.run(generation_request)

    assert generator.executed_plan is not None
    assert generator.executed_plan.generator_name == "recording"
    assert generator.executed_plan.destinations() == (generation_request.target / "README.md",)


def test_run_does_not_call_legacy_lifecycle_hooks(
    generation_request: GenerateRequest,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Prevent canonical execution from invoking compatibility hooks."""

    def fail_legacy_hook(*args: object, **kwargs: object) -> None:
        del args, kwargs
        raise AssertionError("Legacy lifecycle hook was called")

    for method_name in LEGACY_LIFECYCLE_METHODS:
        monkeypatch.setattr(
            RecordingGenerator,
            method_name,
            fail_legacy_hook,
            raising=False,
        )

    generator = RecordingGenerator()

    result = BaseGenerator.run(generator, generation_request)

    assert generator.events == [
        "validate_request",
        "plan",
        "execute",
    ]
    assert result.generator_name == "recording"


def test_canonical_execution_does_not_create_output_by_itself(
    generation_request: GenerateRequest,
) -> None:
    """Keep validation and planning free from filesystem side effects."""
    generator = RecordingGenerator()

    generator.run(generation_request)

    assert not generation_request.target.exists()


def test_base_generator_abstract_contract_keeps_canonical_hooks() -> None:
    """Require planning and execution to remain concrete extension points."""
    abstract_methods = BaseGenerator.__abstractmethods__

    assert "plan" in abstract_methods
    assert "execute" in abstract_methods
