"""Harden the OpenProjectLab v1 Generator lifecycle reliability boundary."""

from __future__ import annotations

from pathlib import Path

import pytest

from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
)


class LifecycleProbeGenerator(BaseGenerator):
    name = "lifecycle-probe"

    def __init__(self, *, fail_at: str | None = None) -> None:
        super().__init__()
        self.fail_at = fail_at
        self.calls: list[str] = []

    def validate_request(self, request: GenerateRequest) -> None:
        del request
        self.calls.append("validate")
        if self.fail_at == "validate":
            raise ValueError("validation failed")

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        del request
        self.calls.append("plan")
        if self.fail_at == "plan":
            raise RuntimeError("planning failed")
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        del request, plan
        self.calls.append("execute")
        if self.fail_at == "execute":
            raise OSError("execution failed")
        return GenerationResult(generator_name=self.name)


def _request(tmp_path: Path) -> GenerateRequest:
    return GenerateRequest(
        generator_name=LifecycleProbeGenerator.name,
        target=tmp_path,
    )


def test_v1_validation_failure_prevents_plan_and_execute(tmp_path: Path) -> None:
    generator = LifecycleProbeGenerator(fail_at="validate")

    with pytest.raises(ValueError, match="validation failed"):
        generator.run(_request(tmp_path))

    assert generator.calls == ["validate"]


def test_v1_planning_failure_prevents_execute(tmp_path: Path) -> None:
    generator = LifecycleProbeGenerator(fail_at="plan")

    with pytest.raises(RuntimeError, match="planning failed"):
        generator.run(_request(tmp_path))

    assert generator.calls == ["validate", "plan"]


def test_v1_execution_failure_preserves_original_exception_type(
    tmp_path: Path,
) -> None:
    generator = LifecycleProbeGenerator(fail_at="execute")

    with pytest.raises(OSError, match="execution failed"):
        generator.run(_request(tmp_path))

    assert generator.calls == ["validate", "plan", "execute"]


def test_v1_successful_lifecycle_runs_in_canonical_order(tmp_path: Path) -> None:
    generator = LifecycleProbeGenerator()

    result = generator.run(_request(tmp_path))

    assert generator.calls == ["validate", "plan", "execute"]
    assert result == GenerationResult(generator_name=generator.name)


def test_v1_deterministic_generator_can_repeat_equivalent_requests(
    tmp_path: Path,
) -> None:
    first = LifecycleProbeGenerator()
    second = LifecycleProbeGenerator()
    request = _request(tmp_path)

    first_result = first.run(request)
    second_result = second.run(request)

    assert first.calls == second.calls == ["validate", "plan", "execute"]
    assert first_result == second_result
