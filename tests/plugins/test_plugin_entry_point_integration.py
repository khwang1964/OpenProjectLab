"""Integration tests for transactional Python Entry Point plugin loading."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from generator.plugins.registry import GeneratorRegistry
from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
    PluginError,
)


class AlphaGenerator(BaseGenerator):
    """First valid generator used by Entry Point integration tests."""

    name = "alpha-plugin"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Build a minimal generation plan."""
        return GenerationPlan(generator_name=request.generator_name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Return a minimal generation result."""
        del plan
        return GenerationResult(
            generator_name=request.generator_name,
            dry_run=request.options.dry_run,
        )


class BetaGenerator(AlphaGenerator):
    """Second valid generator."""

    name = "beta-plugin"


class InvalidNameGenerator(AlphaGenerator):
    """Generator rejected by the Plugin SDK naming contract."""

    name = "Invalid_Name"


class DuplicateAlphaGenerator(AlphaGenerator):
    """Generator that duplicates another public runtime name."""

    name = "alpha-plugin"


@dataclass
class FakeEntryPoint:
    """Deterministic stand-in for importlib.metadata.EntryPoint."""

    name: str
    value: str
    target: object
    load_error: BaseException | None = None
    load_count: int = 0

    def load(self) -> object:
        """Return the configured target or raise the configured load error."""
        self.load_count += 1
        if self.load_error is not None:
            raise self.load_error
        return self.target


def _load_entry_points_into_registry(
    entry_points: tuple[FakeEntryPoint, ...],
    registry: GeneratorRegistry,
) -> tuple[type[BaseGenerator], ...]:
    """Call the canonical transactional Entry Point integration API."""
    from generator.plugins.entry_points import load_entry_points_into_registry

    return load_entry_points_into_registry(entry_points, registry)


def _assert_not_registered(
    registry: GeneratorRegistry,
    *names: str,
) -> None:
    """Assert that none of the supplied names exist in the registry."""
    for name in names:
        assert registry.contains(name) is False


def test_all_valid_entry_points_are_registered_transactionally() -> None:
    """Register every generator when the complete batch is valid."""
    entry_points = (
        FakeEntryPoint(
            name="alpha-plugin",
            value="demo:AlphaGenerator",
            target=AlphaGenerator,
        ),
        FakeEntryPoint(
            name="beta-plugin",
            value="demo:BetaGenerator",
            target=BetaGenerator,
        ),
    )
    registry = GeneratorRegistry()

    loaded = _load_entry_points_into_registry(entry_points, registry)

    assert loaded == (AlphaGenerator, BetaGenerator)
    assert registry.get("alpha-plugin") is AlphaGenerator
    assert registry.get("beta-plugin") is BetaGenerator
    assert entry_points[0].load_count == 1
    assert entry_points[1].load_count == 1


def test_valid_then_invalid_entry_point_leaves_registry_unchanged() -> None:
    """Reject the whole batch when a later candidate fails validation."""
    entry_points = (
        FakeEntryPoint(
            name="alpha-plugin",
            value="demo:AlphaGenerator",
            target=AlphaGenerator,
        ),
        FakeEntryPoint(
            name="Invalid_Name",
            value="demo:InvalidNameGenerator",
            target=InvalidNameGenerator,
        ),
    )
    registry = GeneratorRegistry()

    with pytest.raises(PluginError):
        _load_entry_points_into_registry(entry_points, registry)

    _assert_not_registered(
        registry,
        "alpha-plugin",
        "Invalid_Name",
    )


def test_later_entry_point_load_failure_leaves_registry_unchanged() -> None:
    """Do not register earlier successes when a later Entry Point cannot load."""
    entry_points = (
        FakeEntryPoint(
            name="alpha-plugin",
            value="demo:AlphaGenerator",
            target=AlphaGenerator,
        ),
        FakeEntryPoint(
            name="broken-plugin",
            value="broken:BrokenGenerator",
            target=BetaGenerator,
            load_error=ImportError("broken dependency"),
        ),
    )
    registry = GeneratorRegistry()

    with pytest.raises(PluginError):
        _load_entry_points_into_registry(entry_points, registry)

    _assert_not_registered(
        registry,
        "alpha-plugin",
        "broken-plugin",
    )


def test_identity_mismatch_leaves_registry_unchanged() -> None:
    """Reject metadata/runtime name mismatch without partial registration."""
    entry_points = (
        FakeEntryPoint(
            name="alpha-plugin",
            value="demo:AlphaGenerator",
            target=AlphaGenerator,
        ),
        FakeEntryPoint(
            name="metadata-beta",
            value="demo:BetaGenerator",
            target=BetaGenerator,
        ),
    )
    registry = GeneratorRegistry()

    with pytest.raises(PluginError):
        _load_entry_points_into_registry(entry_points, registry)

    _assert_not_registered(
        registry,
        "alpha-plugin",
        "metadata-beta",
        "beta-plugin",
    )


def test_duplicate_names_within_batch_leave_registry_unchanged() -> None:
    """Reject duplicate runtime names before any registration occurs."""
    entry_points = (
        FakeEntryPoint(
            name="alpha-plugin",
            value="demo:AlphaGenerator",
            target=AlphaGenerator,
        ),
        FakeEntryPoint(
            name="alpha-plugin",
            value="demo:DuplicateAlphaGenerator",
            target=DuplicateAlphaGenerator,
        ),
    )
    registry = GeneratorRegistry()

    with pytest.raises(PluginError):
        _load_entry_points_into_registry(entry_points, registry)

    _assert_not_registered(
        registry,
        "alpha-plugin",
    )


def test_existing_registry_collision_preserves_existing_entry() -> None:
    """Reject a colliding batch without replacing or adding registrations."""
    entry_points = (
        FakeEntryPoint(
            name="alpha-plugin",
            value="demo:AlphaGenerator",
            target=AlphaGenerator,
        ),
        FakeEntryPoint(
            name="beta-plugin",
            value="demo:BetaGenerator",
            target=BetaGenerator,
        ),
    )
    registry = GeneratorRegistry()
    registry.register(AlphaGenerator)

    with pytest.raises(PluginError):
        _load_entry_points_into_registry(entry_points, registry)

    assert registry.get("alpha-plugin") is AlphaGenerator
    assert registry.contains("beta-plugin") is False


def test_empty_entry_point_batch_is_a_no_op() -> None:
    """Treat an environment with no third-party plugins as normal."""
    registry = GeneratorRegistry()

    loaded = _load_entry_points_into_registry((), registry)

    assert loaded == ()
    assert registry.contains("alpha-plugin") is False


def test_failed_batch_does_not_execute_generator_lifecycle() -> None:
    """Transactional loading must never invoke generator execution hooks."""

    class LifecycleGuardGenerator(AlphaGenerator):
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

    entry_points = (
        FakeEntryPoint(
            name="lifecycle-guard",
            value="demo:LifecycleGuardGenerator",
            target=LifecycleGuardGenerator,
        ),
    )
    registry = GeneratorRegistry()

    loaded = _load_entry_points_into_registry(entry_points, registry)

    assert loaded == (LifecycleGuardGenerator,)
    assert registry.get("lifecycle-guard") is LifecycleGuardGenerator
