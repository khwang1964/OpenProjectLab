"""Freeze the OpenProjectLab v1 public Plugin loading contract."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import find_spec
from typing import Any

import pytest

from generator.plugins.entry_points import (
    PLUGIN_ENTRY_POINT_GROUP,
    load_entry_point_generator,
    load_entry_points_into_registry,
)
from generator.plugins.registry import GeneratorRegistry
from generator.plugins.validation import validate_plugin_generator
from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
    PluginError,
)


class AlphaGenerator(BaseGenerator):
    """Valid third-party-style Generator used by the v1 Plugin contract."""

    name = "alpha"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Return a deterministic empty plan."""
        del request
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Return the shared Generator result contract."""
        del request
        assert plan.generator_name == self.name
        return GenerationResult(generator_name=self.name)


class BetaGenerator(BaseGenerator):
    """Second valid Generator used for transactional batch tests."""

    name = "beta"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Return a deterministic empty plan."""
        del request
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Return the shared Generator result contract."""
        del request
        assert plan.generator_name == self.name
        return GenerationResult(generator_name=self.name)


class InvalidNameGenerator(BaseGenerator):
    """Generator whose public name violates the Plugin SDK v1 contract."""

    name = "Invalid_Name"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Return a deterministic empty plan."""
        del request
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        """Return the shared Generator result contract."""
        del request
        return GenerationResult(generator_name=self.name)


@dataclass(frozen=True)
class FakeEntryPoint:
    """Minimal Entry Point test double exposing the production load contract."""

    name: str
    candidate: Any

    def load(self) -> Any:
        """Return the configured candidate."""
        return self.candidate


def test_v1_plugin_entry_point_group_is_canonical() -> None:
    """Freeze the installed Generator Plugin Entry Point group identity."""
    assert PLUGIN_ENTRY_POINT_GROUP == "openprojectlab.generators"


def test_v1_plugin_validation_returns_valid_generator_class() -> None:
    """Accept a concrete zero-argument BaseGenerator subclass."""
    assert validate_plugin_generator(AlphaGenerator) is AlphaGenerator


def test_v1_plugin_validation_rejects_invalid_name() -> None:
    """Reject an invalid public Plugin name before registration."""
    with pytest.raises(PluginError):
        validate_plugin_generator(InvalidNameGenerator)


def test_v1_entry_point_requires_metadata_name_to_match_generator_name() -> None:
    """Reject Entry Point metadata/runtime identity mismatches."""
    entry_point = FakeEntryPoint(
        name="different-name",
        candidate=AlphaGenerator,
    )

    with pytest.raises(PluginError):
        load_entry_point_generator(entry_point)  # type: ignore[arg-type]


def test_v1_registry_rejects_duplicate_name_without_replacement() -> None:
    """Never silently replace an already registered Generator."""
    registry = GeneratorRegistry()
    registry.register(AlphaGenerator)

    with pytest.raises(PluginError):
        registry.register(AlphaGenerator)

    assert registry.get("alpha") is AlphaGenerator


def test_v1_batch_failure_leaves_registry_unchanged() -> None:
    """Validate a complete Entry Point batch before mutating the registry."""
    registry = GeneratorRegistry()

    entry_points = (
        FakeEntryPoint(name="alpha", candidate=AlphaGenerator),
        FakeEntryPoint(
            name="Invalid_Name",
            candidate=InvalidNameGenerator,
        ),
    )

    with pytest.raises(PluginError):
        load_entry_points_into_registry(  # type: ignore[arg-type]
            entry_points,
            registry,
        )

    assert not registry.contains("alpha")
    assert not registry.contains("Invalid_Name")


def test_v1_batch_duplicate_names_leave_registry_unchanged() -> None:
    """Reject duplicate names inside one batch before any registration."""
    registry = GeneratorRegistry()

    entry_points = (
        FakeEntryPoint(name="alpha", candidate=AlphaGenerator),
        FakeEntryPoint(name="alpha", candidate=AlphaGenerator),
    )

    with pytest.raises(PluginError):
        load_entry_points_into_registry(  # type: ignore[arg-type]
            entry_points,
            registry,
        )

    assert not registry.contains("alpha")


def test_v1_existing_registry_conflict_leaves_batch_unregistered() -> None:
    """Reject conflicts with existing registrations before adding batch members."""
    registry = GeneratorRegistry()
    registry.register(AlphaGenerator)

    entry_points = (
        FakeEntryPoint(name="beta", candidate=BetaGenerator),
        FakeEntryPoint(name="alpha", candidate=AlphaGenerator),
    )

    with pytest.raises(PluginError):
        load_entry_points_into_registry(  # type: ignore[arg-type]
            entry_points,
            registry,
        )

    assert registry.get("alpha") is AlphaGenerator
    assert not registry.contains("beta")


def test_v1_legacy_plugin_manager_module_remains_removed() -> None:
    """Keep the removed legacy generator.core.plugin path unsupported."""
    assert find_spec("generator.core.plugin") is None
