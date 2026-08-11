"""Contract tests for Python Entry Point generator plugins."""

from __future__ import annotations

import importlib
from abc import abstractmethod
from dataclasses import dataclass
from typing import Any, cast

import pytest

from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
    PluginError,
)

EXPECTED_ENTRY_POINT_GROUP = "openprojectlab.generators"


class ValidEntryPointGenerator(BaseGenerator):
    """Concrete generator satisfying the Plugin SDK v1 contract."""

    name = "valid-entry-point"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Build a minimal generation plan for contract testing."""
        return GenerationPlan(generator_name=request.generator_name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Return a minimal generation result for contract testing."""
        del plan
        return GenerationResult(
            generator_name=request.generator_name,
            dry_run=request.options.dry_run,
        )


class MismatchedNameGenerator(ValidEntryPointGenerator):
    """Concrete generator whose runtime name differs from Entry Point metadata."""

    name = "runtime-name"


class AbstractEntryPointGenerator(BaseGenerator):
    """Abstract generator that must be rejected by the shared validator."""

    name = "abstract-entry-point"

    @abstractmethod
    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Remain abstract so this class cannot satisfy the Plugin SDK."""

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Provide the remaining lifecycle method."""
        del plan
        return GenerationResult(
            generator_name=request.generator_name,
            dry_run=request.options.dry_run,
        )


class UnrelatedClass:
    """Class that does not implement the OpenProjectLab generator contract."""


@dataclass
class FakeEntryPoint:
    """Deterministic stand-in for importlib.metadata.EntryPoint."""

    name: str
    value: str
    target: object
    group: str = EXPECTED_ENTRY_POINT_GROUP
    load_error: BaseException | None = None
    load_count: int = 0

    def load(self) -> object:
        """Return the configured target or raise the configured load error."""
        self.load_count += 1
        if self.load_error is not None:
            raise self.load_error
        return self.target


def _entry_point_module() -> Any:
    """Import the canonical Entry Point integration module."""
    return importlib.import_module("generator.plugins.entry_points")


def _discover_plugin_entry_points() -> tuple[object, ...]:
    """Call the canonical metadata discovery function."""
    module = _entry_point_module()
    discover = module.discover_plugin_entry_points
    return cast(tuple[object, ...], discover())


def _load_entry_point_generator(
    entry_point: FakeEntryPoint,
) -> type[BaseGenerator]:
    """Load and validate exactly one generator Entry Point."""
    module = _entry_point_module()
    loader = module.load_entry_point_generator
    return cast(type[BaseGenerator], loader(entry_point))


def test_entry_point_group_is_canonical() -> None:
    """Expose the one canonical Plugin SDK v1 Entry Point group."""
    module = _entry_point_module()

    assert module.PLUGIN_ENTRY_POINT_GROUP == EXPECTED_ENTRY_POINT_GROUP


def test_discovery_queries_only_canonical_group(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Discover metadata only from openprojectlab.generators."""
    module = _entry_point_module()
    expected = (
        FakeEntryPoint(
            name="valid-entry-point",
            value="demo:ValidEntryPointGenerator",
            target=ValidEntryPointGenerator,
        ),
    )
    calls: list[dict[str, object]] = []

    def fake_entry_points(**kwargs: object) -> tuple[FakeEntryPoint, ...]:
        calls.append(dict(kwargs))
        if kwargs == {"group": EXPECTED_ENTRY_POINT_GROUP}:
            return expected
        return ()

    monkeypatch.setattr(module, "entry_points", fake_entry_points)

    discovered = _discover_plugin_entry_points()

    assert discovered == expected
    assert calls == [{"group": EXPECTED_ENTRY_POINT_GROUP}]


def test_empty_entry_point_discovery_is_normal(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Return an empty tuple when no third-party generator plugins are installed."""
    module = _entry_point_module()

    monkeypatch.setattr(
        module,
        "entry_points",
        lambda **kwargs: (),
    )

    assert _discover_plugin_entry_points() == ()


def test_valid_entry_point_loads_generator_class() -> None:
    """Load a valid Entry Point into the same validated generator class."""
    entry_point = FakeEntryPoint(
        name="valid-entry-point",
        value="demo:ValidEntryPointGenerator",
        target=ValidEntryPointGenerator,
    )

    loaded = _load_entry_point_generator(entry_point)

    assert loaded is ValidEntryPointGenerator
    assert entry_point.load_count == 1


@pytest.mark.parametrize(
    "target",
    [
        object(),
        lambda: None,
        42,
        "generator",
    ],
)
def test_entry_point_rejects_non_class_targets(target: object) -> None:
    """Reject Entry Point targets that are not Python classes."""
    entry_point = FakeEntryPoint(
        name="valid-entry-point",
        value="demo:target",
        target=target,
    )

    with pytest.raises(PluginError):
        _load_entry_point_generator(entry_point)


def test_entry_point_rejects_unrelated_class() -> None:
    """Reject a class that does not inherit from BaseGenerator."""
    entry_point = FakeEntryPoint(
        name="valid-entry-point",
        value="demo:UnrelatedClass",
        target=UnrelatedClass,
    )

    with pytest.raises(PluginError):
        _load_entry_point_generator(entry_point)


def test_entry_point_rejects_abstract_generator() -> None:
    """Reject abstract BaseGenerator subclasses through shared validation."""
    entry_point = FakeEntryPoint(
        name="abstract-entry-point",
        value="demo:AbstractEntryPointGenerator",
        target=AbstractEntryPointGenerator,
    )

    with pytest.raises(PluginError):
        _load_entry_point_generator(entry_point)


def test_entry_point_name_must_match_generator_name() -> None:
    """Reject metadata/runtime identity mismatch."""
    entry_point = FakeEntryPoint(
        name="metadata-name",
        value="demo:MismatchedNameGenerator",
        target=MismatchedNameGenerator,
    )

    with pytest.raises(PluginError) as exc_info:
        _load_entry_point_generator(entry_point)

    assert "metadata-name" in str(exc_info.value)
    assert "runtime-name" in str(exc_info.value)


def test_entry_point_load_failure_becomes_plugin_error() -> None:
    """Translate a classifiable Entry Point load failure at the plugin boundary."""
    entry_point = FakeEntryPoint(
        name="broken-plugin",
        value="broken_package:BrokenGenerator",
        target=ValidEntryPointGenerator,
        load_error=ImportError("broken dependency"),
    )

    with pytest.raises(PluginError) as exc_info:
        _load_entry_point_generator(entry_point)

    assert "broken-plugin" in str(exc_info.value)
    assert exc_info.value.__cause__ is not None


def test_entry_point_loading_does_not_execute_generator_lifecycle() -> None:
    """Loading may validate construction but must not run generation lifecycle."""

    class LifecycleGuardGenerator(ValidEntryPointGenerator):
        name = "lifecycle-guard"

        def run(self, request: GenerateRequest) -> GenerationResult:
            raise AssertionError("Entry Point loading must not call run()")

        def plan(self, request: GenerateRequest) -> GenerationPlan:
            raise AssertionError("Entry Point loading must not call plan()")

        def execute(
            self,
            request: GenerateRequest,
            plan: GenerationPlan,
        ) -> GenerationResult:
            raise AssertionError("Entry Point loading must not call execute()")

    entry_point = FakeEntryPoint(
        name="lifecycle-guard",
        value="demo:LifecycleGuardGenerator",
        target=LifecycleGuardGenerator,
    )

    loaded = _load_entry_point_generator(entry_point)

    assert loaded is LifecycleGuardGenerator
    assert entry_point.load_count == 1
