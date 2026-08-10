"""Integration tests for plugin validation during loading."""

from __future__ import annotations

import sys
from types import ModuleType

import pytest

from generator.plugins.loader import load_plugin
from generator.plugins.registry import GeneratorRegistry
from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
    PluginError,
)


class ValidAlphaGenerator(BaseGenerator):
    """First valid plugin generator used by loader integration tests."""

    name = "valid-alpha"

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


class ValidBetaGenerator(ValidAlphaGenerator):
    """Second valid plugin generator."""

    name = "valid-beta"


class InvalidNameGenerator(ValidAlphaGenerator):
    """Concrete generator with a name rejected by ADR 0011."""

    name = "Invalid_Name"


class DuplicateAlphaGenerator(ValidAlphaGenerator):
    """Generator that intentionally duplicates another public name."""

    name = "valid-alpha"


def _install_plugin_module(
    monkeypatch: pytest.MonkeyPatch,
    module_name: str,
    *generator_classes: type[BaseGenerator],
) -> None:
    """Install a synthetic plugin module containing the supplied generators."""
    module = ModuleType(module_name)

    for index, generator_class in enumerate(generator_classes):
        setattr(module, f"Generator{index}", generator_class)

    monkeypatch.setitem(sys.modules, module_name, module)


def _assert_not_registered(
    registry: GeneratorRegistry,
    *names: str,
) -> None:
    """Assert that none of the supplied names are present in the registry."""
    for name in names:
        with pytest.raises(PluginError):
            registry.get(name)


def test_load_plugin_registers_all_generators_after_validation(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Register every generator when all discovered candidates are valid."""
    module_name = "tests.synthetic_plugin_validation_all_valid"
    _install_plugin_module(
        monkeypatch,
        module_name,
        ValidAlphaGenerator,
        ValidBetaGenerator,
    )
    registry = GeneratorRegistry()

    loaded = load_plugin(module_name, registry)

    assert loaded == (
        ValidAlphaGenerator,
        ValidBetaGenerator,
    )
    assert registry.get("valid-alpha") is ValidAlphaGenerator
    assert registry.get("valid-beta") is ValidBetaGenerator


def test_load_plugin_rejects_valid_then_invalid_without_partial_registration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reject the whole plugin before registration when a later candidate is invalid."""
    module_name = "tests.synthetic_plugin_validation_valid_invalid"
    _install_plugin_module(
        monkeypatch,
        module_name,
        ValidAlphaGenerator,
        InvalidNameGenerator,
    )
    registry = GeneratorRegistry()

    with pytest.raises(PluginError):
        load_plugin(module_name, registry)

    _assert_not_registered(
        registry,
        "valid-alpha",
        "Invalid_Name",
    )


def test_load_plugin_rejects_invalid_then_valid_without_partial_registration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reject the whole plugin before registration when the first candidate is invalid."""
    module_name = "tests.synthetic_plugin_validation_invalid_valid"
    _install_plugin_module(
        monkeypatch,
        module_name,
        InvalidNameGenerator,
        ValidBetaGenerator,
    )
    registry = GeneratorRegistry()

    with pytest.raises(PluginError):
        load_plugin(module_name, registry)

    _assert_not_registered(
        registry,
        "Invalid_Name",
        "valid-beta",
    )


def test_load_plugin_rejects_duplicate_names_without_partial_registration(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Reject duplicate public names without retaining an earlier registration."""
    module_name = "tests.synthetic_plugin_validation_duplicate"
    _install_plugin_module(
        monkeypatch,
        module_name,
        ValidAlphaGenerator,
        DuplicateAlphaGenerator,
    )
    registry = GeneratorRegistry()

    with pytest.raises(PluginError):
        load_plugin(module_name, registry)

    _assert_not_registered(
        registry,
        "valid-alpha",
    )


def test_failed_plugin_load_preserves_existing_registry_entries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Leave pre-existing registry contents untouched when plugin loading fails."""
    module_name = "tests.synthetic_plugin_validation_preserve_existing"
    _install_plugin_module(
        monkeypatch,
        module_name,
        ValidBetaGenerator,
        InvalidNameGenerator,
    )
    registry = GeneratorRegistry()
    registry.register(ValidAlphaGenerator)

    with pytest.raises(PluginError):
        load_plugin(module_name, registry)

    assert registry.get("valid-alpha") is ValidAlphaGenerator
    _assert_not_registered(
        registry,
        "valid-beta",
        "Invalid_Name",
    )
