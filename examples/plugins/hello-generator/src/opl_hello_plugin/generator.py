"""Minimal third-party Generator implemented only against generator.sdk."""

from __future__ import annotations

from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
)


class HelloGenerator(BaseGenerator):
    """Minimal Generator demonstrating the Plugin SDK v1 contract."""

    name = "hello-plugin"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Return an empty deterministic plan."""
        return GenerationPlan(generator_name=request.generator_name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Return a minimal result without external side effects."""
        del plan
        return GenerationResult(
            generator_name=request.generator_name,
            dry_run=request.options.dry_run,
        )
