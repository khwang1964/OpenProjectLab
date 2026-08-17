"""Harden the OpenProjectLab v1 Plugin loading reliability boundary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from generator.plugins.entry_points import load_entry_points_into_registry
from generator.plugins.registry import GeneratorRegistry
from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
    PluginError,
)


class AlphaGenerator(BaseGenerator):
    name = "alpha"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        del request
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        del request, plan
        return GenerationResult(generator_name=self.name)


class BetaGenerator(BaseGenerator):
    name = "beta"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        del request
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        del request, plan
        return GenerationResult(generator_name=self.name)


class GammaGenerator(BaseGenerator):
    name = "gamma"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        del request
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        del request, plan
        return GenerationResult(generator_name=self.name)


class InvalidNameGenerator(BaseGenerator):
    name = "Invalid_Name"

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        del request
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        del request, plan
        return GenerationResult(generator_name=self.name)


class RequiresArgumentGenerator(BaseGenerator):
    name = "requires-argument"

    def __init__(self, required: str) -> None:
        super().__init__()
        self.required = required

    def plan(self, request: GenerateRequest) -> GenerationPlan:
        del request
        return GenerationPlan(generator_name=self.name)

    def execute(
        self,
        request: GenerateRequest,
        plan: GenerationPlan,
    ) -> GenerationResult:
        del request, plan
        return GenerationResult(generator_name=self.name)


@dataclass(frozen=True)
class FakeEntryPoint:
    name: str
    candidate: Any

    def load(self) -> Any:
        return self.candidate


def test_v1_invalid_last_plugin_leaves_registry_unchanged() -> None:
    """Reject a whole batch when the final candidate fails validation."""
    registry = GeneratorRegistry()
    entries = (
        FakeEntryPoint("alpha", AlphaGenerator),
        FakeEntryPoint("beta", BetaGenerator),
        FakeEntryPoint("Invalid_Name", InvalidNameGenerator),
    )

    with pytest.raises(PluginError):
        load_entry_points_into_registry(entries, registry)  # type: ignore[arg-type]

    assert not registry.contains("alpha")
    assert not registry.contains("beta")
    assert not registry.contains("Invalid_Name")


def test_v1_duplicate_batch_leaves_registry_unchanged() -> None:
    """Reject duplicate names before any registration occurs."""
    registry = GeneratorRegistry()
    entries = (
        FakeEntryPoint("alpha", AlphaGenerator),
        FakeEntryPoint("alpha", AlphaGenerator),
    )

    with pytest.raises(PluginError):
        load_entry_points_into_registry(entries, registry)  # type: ignore[arg-type]

    assert not registry.contains("alpha")


def test_v1_existing_conflict_leaves_new_batch_members_unregistered() -> None:
    """Reject conflicts with existing state before committing new members."""
    registry = GeneratorRegistry()
    registry.register(AlphaGenerator)
    entries = (
        FakeEntryPoint("beta", BetaGenerator),
        FakeEntryPoint("alpha", AlphaGenerator),
    )

    with pytest.raises(PluginError):
        load_entry_points_into_registry(entries, registry)  # type: ignore[arg-type]

    assert registry.get("alpha") is AlphaGenerator
    assert not registry.contains("beta")


def test_v1_zero_argument_construction_failure_leaves_registry_unchanged() -> None:
    """Reject a Generator that cannot satisfy zero-argument construction."""
    registry = GeneratorRegistry()
    entries = (
        FakeEntryPoint("alpha", AlphaGenerator),
        FakeEntryPoint("requires-argument", RequiresArgumentGenerator),
    )

    with pytest.raises(PluginError):
        load_entry_points_into_registry(entries, registry)  # type: ignore[arg-type]

    assert not registry.contains("alpha")
    assert not registry.contains("requires-argument")


def test_v1_registry_remains_usable_after_failed_batch() -> None:
    """Allow later valid registration after an atomic batch failure."""
    registry = GeneratorRegistry()
    invalid_entries = (
        FakeEntryPoint("alpha", AlphaGenerator),
        FakeEntryPoint("Invalid_Name", InvalidNameGenerator),
    )

    with pytest.raises(PluginError):
        load_entry_points_into_registry(  # type: ignore[arg-type]
            invalid_entries,
            registry,
        )

    valid_entries = (
        FakeEntryPoint("beta", BetaGenerator),
        FakeEntryPoint("gamma", GammaGenerator),
    )
    loaded = load_entry_points_into_registry(  # type: ignore[arg-type]
        valid_entries,
        registry,
    )

    assert loaded == (BetaGenerator, GammaGenerator)
    assert registry.get("beta") is BetaGenerator
    assert registry.get("gamma") is GammaGenerator


def test_v1_successful_plugin_batch_preserves_authored_order() -> None:
    """Keep validated return order deterministic."""
    registry = GeneratorRegistry()
    entries = (
        FakeEntryPoint("gamma", GammaGenerator),
        FakeEntryPoint("alpha", AlphaGenerator),
        FakeEntryPoint("beta", BetaGenerator),
    )

    loaded = load_entry_points_into_registry(  # type: ignore[arg-type]
        entries,
        registry,
    )

    assert loaded == (GammaGenerator, AlphaGenerator, BetaGenerator)
