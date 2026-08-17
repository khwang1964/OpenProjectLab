"""Harden the OpenProjectLab v1 Courseware Composition reliability boundary."""

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


class RecordingGenerator(BaseGenerator):
    calls: list[str] = []

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        del request
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        del request, plan
        self.calls.append(self.name)
        return GenerationResult(generator_name=self.name)


class FirstGenerator(RecordingGenerator):
    name = "first"


class SecondGenerator(RecordingGenerator):
    name = "second"


class ThirdGenerator(RecordingGenerator):
    name = "third"


class IdentifiedFailureGenerator(BaseGenerator):
    name = "identified-failure"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        del request
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        del request, plan
        raise ValueError("identified-failure rejected its request")


class AnonymousFailureGenerator(BaseGenerator):
    name = "anonymous-failure"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        del request
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        del request, plan
        raise ValueError("invalid authored value")


def _request(name: str, tmp_path: Path) -> GenerateRequest:
    return GenerateRequest(generator_name=name, target=tmp_path)


def test_v1_missing_generator_preflight_prevents_all_execution(
    tmp_path: Path,
) -> None:
    RecordingGenerator.calls.clear()
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

    assert RecordingGenerator.calls == []


def test_v1_mid_run_failure_prevents_later_generator_execution(
    tmp_path: Path,
) -> None:
    RecordingGenerator.calls.clear()
    registry = GeneratorRegistry()
    registry.register(FirstGenerator)
    registry.register(IdentifiedFailureGenerator)
    registry.register(ThirdGenerator)
    composer = CoursewareComposer(registry)

    with pytest.raises(ValueError, match="identified-failure"):
        composer.run(
            (
                _request("first", tmp_path),
                _request("identified-failure", tmp_path),
                _request("third", tmp_path),
            )
        )

    assert RecordingGenerator.calls == ["first"]


def test_v1_composition_does_not_claim_rollback_of_prior_success(
    tmp_path: Path,
) -> None:
    RecordingGenerator.calls.clear()
    registry = GeneratorRegistry()
    registry.register(FirstGenerator)
    registry.register(IdentifiedFailureGenerator)
    composer = CoursewareComposer(registry)

    with pytest.raises(ValueError):
        composer.run(
            (
                _request("first", tmp_path),
                _request("identified-failure", tmp_path),
            )
        )

    assert RecordingGenerator.calls == ["first"]


def test_v1_identified_failure_preserves_original_exception_type(
    tmp_path: Path,
) -> None:
    registry = GeneratorRegistry()
    registry.register(IdentifiedFailureGenerator)
    composer = CoursewareComposer(registry)

    with pytest.raises(ValueError, match="identified-failure"):
        composer.run((_request("identified-failure", tmp_path),))


def test_v1_anonymous_failure_is_wrapped_with_generator_context(
    tmp_path: Path,
) -> None:
    registry = GeneratorRegistry()
    registry.register(AnonymousFailureGenerator)
    composer = CoursewareComposer(registry)

    with pytest.raises(RuntimeError, match="anonymous-failure") as exc_info:
        composer.run((_request("anonymous-failure", tmp_path),))

    assert isinstance(exc_info.value.__cause__, ValueError)
    assert str(exc_info.value.__cause__) == "invalid authored value"


def test_v1_composition_preserves_deterministic_execution_and_result_order(
    tmp_path: Path,
) -> None:
    registry = GeneratorRegistry()
    registry.register(FirstGenerator)
    registry.register(SecondGenerator)
    registry.register(ThirdGenerator)
    composer = CoursewareComposer(registry)
    requests = (
        _request("first", tmp_path),
        _request("second", tmp_path),
        _request("third", tmp_path),
    )

    RecordingGenerator.calls.clear()
    first_results = composer.run(requests)
    first_calls = tuple(RecordingGenerator.calls)

    RecordingGenerator.calls.clear()
    second_results = composer.run(requests)
    second_calls = tuple(RecordingGenerator.calls)

    assert first_calls == second_calls == ("first", "second", "third")
    assert tuple(result.generator_name for result in first_results) == (
        "first",
        "second",
        "third",
    )
    assert first_results == second_results
