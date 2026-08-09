"""Contract tests for third-party generators using only generator.sdk."""

from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
)


class ExamplePluginGenerator(BaseGenerator):
    """Minimal third-party-style Generator implemented through the public SDK."""

    name = "example"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Build an empty immutable plan for the example Plugin."""
        del request
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Execute the example plan and return the shared result contract."""
        del request
        assert plan.generator_name == self.name

        return GenerationResult(generator_name=self.name)


def test_plugin_generator_supports_zero_argument_construction() -> None:
    """Require Plugin SDK v1 generators to support zero-argument construction."""
    generator = ExamplePluginGenerator()

    assert generator.name == "example"


def test_plugin_generator_runs_through_public_sdk_contract(tmp_path) -> None:
    """Run a third-party-style Generator entirely through public SDK types."""
    generator = ExamplePluginGenerator()
    request = GenerateRequest(
        generator_name=generator.name,
        target=tmp_path,
    )

    result = generator.run(request)

    assert result.generator_name == generator.name
    assert result.writes == ()
    assert result.warnings == ()
