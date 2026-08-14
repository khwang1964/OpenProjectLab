"""Contract tests for the proposed Courseware Composition Layer."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import ClassVar

import pytest

from generator.core.exceptions import PluginError
from generator.core.models import (
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
    RuntimeOptions,
)
from generator.generators.base import BaseGenerator
from generator.plugins.registry import GeneratorRegistry

pytest.importorskip(
    "generator.courseware.composition",
    reason="Courseware composition implementation lands after the contract-test step",
)

from generator.courseware.composition import CoursewareComposer


def _request(
    tmp_path: Path,
    generator_name: str,
    *,
    dry_run: bool = False,
    overwrite: bool = False,
    marker: str | None = None,
) -> GenerateRequest:
    values: dict[str, object] = {
        "record_manifest": False,
    }
    if marker is not None:
        values["marker"] = marker

    return GenerateRequest(
        generator_name=generator_name,
        target=tmp_path / "course",
        values=values,
        options=RuntimeOptions(
            dry_run=dry_run,
            overwrite=overwrite,
        ),
    )


def _generator_class(
    name: str,
    events: list[tuple[str, str, GenerateRequest]],
    *,
    failure: BaseException | None = None,
) -> type[BaseGenerator]:
    class _ContractGenerator(BaseGenerator):
        description = f"Contract generator {name}"
        event_log: ClassVar[list[tuple[str, str, GenerateRequest]]] = events
        configured_failure: ClassVar[BaseException | None] = failure

        def run(self, request: GenerateRequest) -> GenerationResult:
            self.event_log.append(("run", name, request))
            return super().run(request)

        def validate_request(self, request: GenerateRequest) -> None:
            self.event_log.append(("validate", name, request))

        def plan(self, request: GenerateRequest) -> GenerationPlan:
            self.event_log.append(("plan", name, request))
            return GenerationPlan(generator_name=name)

        def execute(
            self,
            request: GenerateRequest,
            plan: GenerationPlan,
        ) -> GenerationResult:
            del plan
            self.event_log.append(("execute", name, request))

            if self.configured_failure is not None:
                raise self.configured_failure

            return GenerationResult(
                generator_name=name,
                dry_run=request.options.dry_run,
            )

    _ContractGenerator.name = name
    _ContractGenerator.__name__ = f"{name.title()}ContractGenerator"
    return _ContractGenerator


def _registry(
    *generator_classes: type[BaseGenerator],
) -> GeneratorRegistry:
    registry = GeneratorRegistry()
    for generator_class in generator_classes:
        registry.register(generator_class)
    return registry


def test_courseware_composer_accepts_existing_generator_registry() -> None:
    composer = CoursewareComposer(GeneratorRegistry())

    assert isinstance(composer, CoursewareComposer)


def test_composition_plan_returns_immutable_ordered_request_sequence(
    tmp_path: Path,
) -> None:
    composer = CoursewareComposer(GeneratorRegistry())
    requests = [
        _request(tmp_path, "course"),
        _request(tmp_path, "week"),
        _request(tmp_path, "slides"),
        _request(tmp_path, "website"),
    ]

    plan = composer.plan(requests)

    assert isinstance(plan, tuple)
    assert all(isinstance(request, GenerateRequest) for request in plan)
    assert tuple(request.generator_name for request in plan) == (
        "course",
        "week",
        "slides",
        "website",
    )


def test_composition_plan_preserves_authored_request_order(
    tmp_path: Path,
) -> None:
    composer = CoursewareComposer(GeneratorRegistry())
    requests = [
        _request(tmp_path, "course", marker="course"),
        _request(tmp_path, "week", marker="week-02"),
        _request(tmp_path, "week", marker="week-01"),
        _request(tmp_path, "slides", marker="slides"),
        _request(tmp_path, "website", marker="website"),
    ]

    plan = composer.plan(requests)

    assert tuple(request.values.get("marker") for request in plan) == (
        "course",
        "week-02",
        "week-01",
        "slides",
        "website",
    )


def test_composition_plan_is_deterministic_for_same_input(
    tmp_path: Path,
) -> None:
    composer = CoursewareComposer(GeneratorRegistry())
    requests = (
        _request(tmp_path, "course"),
        _request(tmp_path, "week"),
        _request(tmp_path, "slides"),
        _request(tmp_path, "website"),
    )

    first = composer.plan(requests)
    second = composer.plan(requests)

    assert first == second


def test_composition_planning_does_not_mutate_caller_sequence(
    tmp_path: Path,
) -> None:
    composer = CoursewareComposer(GeneratorRegistry())
    requests = [
        _request(tmp_path, "course", marker="course"),
        _request(tmp_path, "week", marker="week"),
    ]
    snapshot = tuple(requests)
    identities = tuple(id(request) for request in requests)

    composer.plan(requests)

    assert tuple(requests) == snapshot
    assert tuple(id(request) for request in requests) == identities


def test_composition_planning_does_not_mutate_request_values(
    tmp_path: Path,
) -> None:
    composer = CoursewareComposer(GeneratorRegistry())
    request = _request(tmp_path, "course", marker="original")
    original_values = dict(request.values)

    plan = composer.plan([request])

    assert dict(request.values) == original_values
    assert plan[0] is request


@pytest.mark.parametrize(
    "invalid_requests",
    [
        None,
        "course",
        b"course",
        {"generator_name": "course"},
        3,
        True,
    ],
)
def test_composition_plan_rejects_non_request_sequence(
    invalid_requests: object,
) -> None:
    composer = CoursewareComposer(GeneratorRegistry())

    with pytest.raises((TypeError, ValueError)):
        composer.plan(invalid_requests)  # type: ignore[arg-type]


def test_composition_plan_rejects_non_generate_request_item(
    tmp_path: Path,
) -> None:
    composer = CoursewareComposer(GeneratorRegistry())
    requests: Sequence[object] = (
        _request(tmp_path, "course"),
        "week",
    )

    with pytest.raises((TypeError, ValueError)):
        composer.plan(requests)  # type: ignore[arg-type]


def test_composition_plan_accepts_empty_sequence_as_no_work() -> None:
    composer = CoursewareComposer(GeneratorRegistry())

    assert composer.plan(()) == ()


def test_composition_run_uses_canonical_generator_run_boundary(
    tmp_path: Path,
) -> None:
    events: list[tuple[str, str, GenerateRequest]] = []
    course = _generator_class("course", events)
    registry = _registry(course)
    composer = CoursewareComposer(registry)
    request = _request(tmp_path, "course")

    results = composer.run([request])

    assert tuple(event[0] for event in events) == (
        "run",
        "validate",
        "plan",
        "execute",
    )
    assert len(results) == 1
    assert results[0].generator_name == "course"


def test_composition_executes_generators_in_declared_request_order(
    tmp_path: Path,
) -> None:
    events: list[tuple[str, str, GenerateRequest]] = []
    course = _generator_class("course", events)
    week = _generator_class("week", events)
    slides = _generator_class("slides", events)
    website = _generator_class("website", events)

    # Register in a deliberately different order. Registry insertion/discovery
    # order must not become composition execution order.
    registry = _registry(website, slides, week, course)
    composer = CoursewareComposer(registry)

    requests = (
        _request(tmp_path, "course"),
        _request(tmp_path, "week"),
        _request(tmp_path, "slides"),
        _request(tmp_path, "website"),
    )

    composer.run(requests)

    run_order = tuple(
        generator_name for stage, generator_name, _request_value in events if stage == "run"
    )
    assert run_order == ("course", "week", "slides", "website")


def test_composition_results_preserve_execution_order(
    tmp_path: Path,
) -> None:
    events: list[tuple[str, str, GenerateRequest]] = []
    registry = _registry(
        _generator_class("website", events),
        _generator_class("course", events),
        _generator_class("slides", events),
        _generator_class("week", events),
    )
    composer = CoursewareComposer(registry)

    requests = (
        _request(tmp_path, "course"),
        _request(tmp_path, "week"),
        _request(tmp_path, "slides"),
        _request(tmp_path, "website"),
    )

    results = composer.run(requests)

    assert isinstance(results, tuple)
    assert all(isinstance(result, GenerationResult) for result in results)
    assert tuple(result.generator_name for result in results) == (
        "course",
        "week",
        "slides",
        "website",
    )


def test_composition_run_returns_empty_result_collection_for_empty_plan() -> None:
    composer = CoursewareComposer(GeneratorRegistry())

    assert composer.run(()) == ()


def test_composition_preflights_generator_resolution_before_execution(
    tmp_path: Path,
) -> None:
    events: list[tuple[str, str, GenerateRequest]] = []
    course = _generator_class("course", events)
    registry = _registry(course)
    composer = CoursewareComposer(registry)

    requests = (
        _request(tmp_path, "course"),
        _request(tmp_path, "missing-generator"),
    )

    with pytest.raises((PluginError, RuntimeError)) as exc_info:
        composer.run(requests)

    assert events == []
    assert "missing-generator" in str(exc_info.value)


def test_composition_preserves_registry_error_as_failure_cause(
    tmp_path: Path,
) -> None:
    composer = CoursewareComposer(GeneratorRegistry())
    request = _request(tmp_path, "missing-generator")

    with pytest.raises((PluginError, RuntimeError)) as exc_info:
        composer.run([request])

    error = exc_info.value
    assert "missing-generator" in str(error)

    if not isinstance(error, PluginError):
        assert isinstance(error.__cause__, PluginError)


def test_composition_is_fail_fast_and_does_not_run_later_generators(
    tmp_path: Path,
) -> None:
    events: list[tuple[str, str, GenerateRequest]] = []
    failure = ValueError("week contract failure")

    course = _generator_class("course", events)
    week = _generator_class("week", events, failure=failure)
    slides = _generator_class("slides", events)

    composer = CoursewareComposer(_registry(course, week, slides))

    requests = (
        _request(tmp_path, "course"),
        _request(tmp_path, "week"),
        _request(tmp_path, "slides"),
    )

    with pytest.raises((ValueError, RuntimeError)) as exc_info:
        composer.run(requests)

    run_order = tuple(
        generator_name for stage, generator_name, _request_value in events if stage == "run"
    )
    assert run_order == ("course", "week")
    assert "slides" not in run_order
    assert "week" in str(exc_info.value)


def test_composition_failure_preserves_original_exception_chain(
    tmp_path: Path,
) -> None:
    events: list[tuple[str, str, GenerateRequest]] = []
    failure = ValueError("original generator failure")
    broken = _generator_class("week", events, failure=failure)

    composer = CoursewareComposer(_registry(broken))
    request = _request(tmp_path, "week")

    with pytest.raises((ValueError, RuntimeError)) as exc_info:
        composer.run([request])

    error = exc_info.value
    if error is failure:
        assert str(error) == "original generator failure"
    else:
        assert error.__cause__ is failure
        assert "week" in str(error)


def test_composition_does_not_claim_rollback_after_partial_failure(
    tmp_path: Path,
) -> None:
    events: list[tuple[str, str, GenerateRequest]] = []
    failure = RuntimeError("website failed")

    course = _generator_class("course", events)
    website = _generator_class("website", events, failure=failure)

    composer = CoursewareComposer(_registry(course, website))

    with pytest.raises(RuntimeError, match="website failed"):
        composer.run(
            (
                _request(tmp_path, "course"),
                _request(tmp_path, "website"),
            )
        )

    execute_order = tuple(
        generator_name for stage, generator_name, _request_value in events if stage == "execute"
    )
    assert execute_order == ("course", "website")


def test_composition_propagates_dry_run_to_each_generator_request(
    tmp_path: Path,
) -> None:
    events: list[tuple[str, str, GenerateRequest]] = []
    course = _generator_class("course", events)
    week = _generator_class("week", events)
    composer = CoursewareComposer(_registry(course, week))

    results = composer.run(
        (
            _request(tmp_path, "course", dry_run=True),
            _request(tmp_path, "week", dry_run=True),
        )
    )

    run_requests = tuple(request for stage, _generator_name, request in events if stage == "run")

    assert len(run_requests) == 2
    assert all(request.options.dry_run for request in run_requests)
    assert all(result.dry_run for result in results)


def test_composition_does_not_enable_dry_run_implicitly(
    tmp_path: Path,
) -> None:
    events: list[tuple[str, str, GenerateRequest]] = []
    course = _generator_class("course", events)
    composer = CoursewareComposer(_registry(course))

    results = composer.run((_request(tmp_path, "course", dry_run=False),))

    run_request = next(request for stage, _generator_name, request in events if stage == "run")
    assert run_request.options.dry_run is False
    assert results[0].dry_run is False


def test_composition_propagates_overwrite_without_implicit_force(
    tmp_path: Path,
) -> None:
    events: list[tuple[str, str, GenerateRequest]] = []
    course = _generator_class("course", events)
    week = _generator_class("week", events)
    composer = CoursewareComposer(_registry(course, week))

    composer.run(
        (
            _request(tmp_path, "course", overwrite=False),
            _request(tmp_path, "week", overwrite=True),
        )
    )

    run_requests = tuple(request for stage, _generator_name, request in events if stage == "run")

    assert run_requests[0].options.overwrite is False
    assert run_requests[1].options.overwrite is True
    assert run_requests[0].options.force is False
    assert run_requests[1].options.force is False


def test_composition_does_not_create_filesystem_artifacts_with_noop_generators(
    tmp_path: Path,
) -> None:
    events: list[tuple[str, str, GenerateRequest]] = []
    course = _generator_class("course", events)
    website = _generator_class("website", events)
    composer = CoursewareComposer(_registry(course, website))

    target = tmp_path / "course"
    assert not target.exists()

    composer.run(
        (
            _request(tmp_path, "course"),
            _request(tmp_path, "website"),
        )
    )

    assert not target.exists()


def test_composition_does_not_mutate_request_sequence_during_execution(
    tmp_path: Path,
) -> None:
    events: list[tuple[str, str, GenerateRequest]] = []
    course = _generator_class("course", events)
    week = _generator_class("week", events)
    composer = CoursewareComposer(_registry(course, week))

    requests = [
        _request(tmp_path, "course", marker="course"),
        _request(tmp_path, "week", marker="week"),
    ]
    snapshot = tuple(requests)

    composer.run(requests)

    assert tuple(requests) == snapshot
    assert tuple(request.values["marker"] for request in requests) == (
        "course",
        "week",
    )


def test_composition_uses_registry_resolution_not_generator_name_ordering(
    tmp_path: Path,
) -> None:
    events: list[tuple[str, str, GenerateRequest]] = []
    website = _generator_class("website", events)
    course = _generator_class("course", events)

    registry = _registry(website, course)
    composer = CoursewareComposer(registry)

    results = composer.run(
        (
            _request(tmp_path, "course"),
            _request(tmp_path, "website"),
        )
    )

    assert tuple(result.generator_name for result in results) == (
        "course",
        "website",
    )


def test_composition_contract_does_not_require_new_public_sdk_symbols() -> None:
    import generator.sdk as sdk

    forbidden_symbols = {
        "CoursewareComposer",
        "CompositionPlan",
        "CompositionRequest",
        "CompositionResult",
        "CompositionStep",
        "CoursewareComposition",
        "CoursewareOrchestrator",
    }

    assert forbidden_symbols.isdisjoint(set(dir(sdk)))
