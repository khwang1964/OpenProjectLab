"""Freeze the OpenProjectLab v1 Courseware Composition public contract."""

from __future__ import annotations

from pathlib import Path

import pytest

from generator.courseware.composition import CoursewareComposer
from generator.plugins.registry import GeneratorRegistry
from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
    PluginError,
)


class FirstGenerator(BaseGenerator):
    """Record execution of the first representative composed Generator."""

    name = "first"
    calls: list[str] = []

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Return a deterministic empty plan."""
        del request
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Record ordered execution."""
        del request, plan
        self.calls.append(self.name)
        return GenerationResult(generator_name=self.name)


class SecondGenerator(BaseGenerator):
    """Record execution of the second representative composed Generator."""

    name = "second"
    calls = FirstGenerator.calls

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Return a deterministic empty plan."""
        del request
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Record ordered execution."""
        del request, plan
        self.calls.append(self.name)
        return GenerationResult(generator_name=self.name)


class FailingGenerator(BaseGenerator):
    """Fail during execution to verify fail-fast composition behavior."""

    name = "failing"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Return a deterministic empty plan."""
        del request
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Fail with the Generator identity present in the error."""
        del request, plan
        raise RuntimeError("failing generator execution failed")


def _request(name: str, target: Path) -> GenerateRequest:
    """Build one minimal composed Generator request."""
    return GenerateRequest(
        generator_name=name,
        target=target,
    )


def test_v1_composition_plan_preserves_authored_request_order(
    tmp_path: Path,
) -> None:
    """Keep composition planning immutable and authored-order preserving."""
    registry = GeneratorRegistry()
    composer = CoursewareComposer(registry)
    requests = [
        _request("first", tmp_path),
        _request("second", tmp_path),
    ]

    plan = composer.plan(requests)

    assert isinstance(plan, tuple)
    assert plan == tuple(requests)


def test_v1_composition_executes_and_returns_results_in_request_order(
    tmp_path: Path,
) -> None:
    """Execute resolved Generators sequentially in authored request order."""
    FirstGenerator.calls.clear()
    registry = GeneratorRegistry()
    registry.register(FirstGenerator)
    registry.register(SecondGenerator)
    composer = CoursewareComposer(registry)

    results = composer.run(
        (
            _request("first", tmp_path),
            _request("second", tmp_path),
        )
    )

    assert FirstGenerator.calls == ["first", "second"]
    assert tuple(result.generator_name for result in results) == (
        "first",
        "second",
    )


def test_v1_composition_preflights_all_resolution_before_execution(
    tmp_path: Path,
) -> None:
    """Resolve every requested Generator before allowing execution side effects."""
    FirstGenerator.calls.clear()
    registry = GeneratorRegistry()
    registry.register(FirstGenerator)
    composer = CoursewareComposer(registry)

    with pytest.raises(PluginError):
        composer.run(
            (
                _request("first", tmp_path),
                _request("missing", tmp_path),
            )
        )

    assert FirstGenerator.calls == []


def test_v1_composition_is_fail_fast_after_execution_failure(
    tmp_path: Path,
) -> None:
    """Stop executing later Generators after one resolved Generator fails."""
    FirstGenerator.calls.clear()
    registry = GeneratorRegistry()
    registry.register(FailingGenerator)
    registry.register(SecondGenerator)
    composer = CoursewareComposer(registry)

    with pytest.raises(RuntimeError, match="failing"):
        composer.run(
            (
                _request("failing", tmp_path),
                _request("second", tmp_path),
            )
        )

    assert FirstGenerator.calls == []


@pytest.mark.parametrize(
    "requests",
    [
        "first",
        b"first",
        {"generator": "first"},
        1,
        None,
    ],
)
def test_v1_composition_rejects_non_sequence_request_collections(
    requests: object,
) -> None:
    """Require an ordered GenerateRequest sequence as the public input contract."""
    composer = CoursewareComposer(GeneratorRegistry())

    with pytest.raises(TypeError):
        composer.plan(requests)  # type: ignore[arg-type]


def test_v1_composition_rejects_non_request_sequence_members() -> None:
    """Require every composition member to be a GenerateRequest."""
    composer = CoursewareComposer(GeneratorRegistry())

    with pytest.raises(TypeError):
        composer.plan(("not-a-request",))  # type: ignore[arg-type]
