"""Tests for the standalone OPL Hello Plugin example."""

from __future__ import annotations

from opl_hello_plugin import HelloGenerator

from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
    RuntimeOptions,
)


def test_hello_generator_implements_public_sdk_contract(tmp_path) -> None:
    """Exercise the example using only public OpenProjectLab SDK types."""
    assert issubclass(HelloGenerator, BaseGenerator)
    assert HelloGenerator.name == "hello-plugin"

    generator = HelloGenerator()
    request = GenerateRequest(
        generator_name="hello-plugin",
        target=tmp_path,
        options=RuntimeOptions(dry_run=True),
    )

    plan = generator.plan(request)
    result = generator.execute(request, plan)

    assert isinstance(plan, GenerationPlan)
    assert plan.generator_name == "hello-plugin"
    assert isinstance(result, GenerationResult)
    assert result.generator_name == "hello-plugin"
    assert result.dry_run is True
