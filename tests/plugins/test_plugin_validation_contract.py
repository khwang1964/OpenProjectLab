"""Contract tests for plugin generator validation."""

from __future__ import annotations

import importlib
from abc import abstractmethod
from typing import Any, cast

import pytest

from generator.sdk import (
    BaseGenerator,
    GenerateRequest,
    GenerationPlan,
    GenerationResult,
    PluginError,
)


class ValidPluginGenerator(BaseGenerator):
    """Concrete generator satisfying the Plugin SDK v1 contract."""

    name = "valid-plugin"

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


class AbstractPluginGenerator(BaseGenerator):
    """Abstract subclass that must not be accepted as a plugin generator."""

    name = "abstract-plugin"

    @abstractmethod
    def plan(self, request: GenerateRequest) -> GenerationPlan:
        """Leave planning abstract so the class remains non-concrete."""

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


class RequiredConstructorArgumentGenerator(ValidPluginGenerator):
    """Generator that violates zero-argument construction."""

    name = "required-constructor"

    def __init__(self, config: object) -> None:
        """Require one constructor argument, which Plugin SDK v1 forbids."""
        super().__init__()
        self.config = config


class UnrelatedClass:
    """Class that resembles no OpenProjectLab generator contract."""


def _validate_plugin_generator(candidate: object) -> type[BaseGenerator]:
    """Load the internal validator without making it part of public SDK imports."""
    module = importlib.import_module("generator.plugins.validation")
    validator = module.validate_plugin_generator
    return cast(Any, validator)(candidate)


def _named_generator(name: object) -> type[BaseGenerator]:
    """Create a concrete generator class with the supplied public name."""
    return type(
        "NamedPluginGenerator",
        (ValidPluginGenerator,),
        {"name": name},
    )


def test_validator_returns_same_valid_generator_class() -> None:
    """Accept a valid generator and preserve its class identity."""
    validated = _validate_plugin_generator(ValidPluginGenerator)

    assert validated is ValidPluginGenerator


@pytest.mark.parametrize(
    "candidate",
    [
        object(),
        lambda: None,
        42,
        "plugin",
    ],
)
def test_validator_rejects_non_class_candidates(candidate: object) -> None:
    """Reject plugin candidates that are not Python classes."""
    with pytest.raises(PluginError):
        _validate_plugin_generator(candidate)


def test_validator_rejects_unrelated_class() -> None:
    """Reject classes that do not inherit from BaseGenerator."""
    with pytest.raises(PluginError):
        _validate_plugin_generator(UnrelatedClass)


def test_validator_rejects_base_generator_itself() -> None:
    """Reject BaseGenerator because it is an extension contract, not a plugin."""
    with pytest.raises(PluginError):
        _validate_plugin_generator(BaseGenerator)


def test_validator_rejects_abstract_generator() -> None:
    """Reject abstract BaseGenerator subclasses before registration."""
    with pytest.raises(PluginError):
        _validate_plugin_generator(AbstractPluginGenerator)


@pytest.mark.parametrize(
    "name",
    [
        "",
        " ",
        " valid-plugin",
        "valid-plugin ",
        "ValidPlugin",
        "valid_plugin",
        "valid.plugin",
        "valid plugin",
        "../valid-plugin",
        "--valid-plugin",
    ],
)
def test_validator_rejects_invalid_public_names(name: object) -> None:
    """Reject names outside the Plugin SDK v1 public naming contract."""
    generator_class = _named_generator(name)

    with pytest.raises(PluginError):
        _validate_plugin_generator(generator_class)


@pytest.mark.parametrize(
    "name",
    [
        "example",
        "example-plugin",
        "course2",
        "java-course",
    ],
)
def test_validator_accepts_valid_public_names(name: str) -> None:
    """Accept names matching the Plugin SDK v1 naming rule."""
    generator_class = _named_generator(name)

    validated = _validate_plugin_generator(generator_class)

    assert validated is generator_class


@pytest.mark.parametrize(
    "name",
    [
        None,
        123,
        object(),
    ],
)
def test_validator_rejects_non_string_public_names(name: object) -> None:
    """Reject generator names that are not strings."""
    generator_class = _named_generator(name)

    with pytest.raises(PluginError):
        _validate_plugin_generator(generator_class)


def test_validator_accepts_zero_argument_construction() -> None:
    """Accept a concrete generator that can be constructed with no arguments."""
    validated = _validate_plugin_generator(ValidPluginGenerator)

    instance = validated()

    assert isinstance(instance, ValidPluginGenerator)


def test_validator_rejects_required_constructor_argument() -> None:
    """Reject generators requiring constructor arguments in Plugin SDK v1."""
    with pytest.raises(PluginError) as exc_info:
        _validate_plugin_generator(RequiredConstructorArgumentGenerator)

    assert exc_info.value.__cause__ is not None or str(exc_info.value)


def test_validation_does_not_execute_generator_lifecycle() -> None:
    """Validation must not invoke run, plan, or execute."""

    class LifecycleGuardGenerator(ValidPluginGenerator):
        name = "lifecycle-guard"

        def run(self, request: GenerateRequest) -> GenerationResult:
            raise AssertionError("validation must not call run()")

        def plan(self, request: GenerateRequest) -> GenerationPlan:
            raise AssertionError("validation must not call plan()")

        def execute(
            self,
            request: GenerateRequest,
            plan: GenerationPlan,
        ) -> GenerationResult:
            raise AssertionError("validation must not call execute()")

    validated = _validate_plugin_generator(LifecycleGuardGenerator)

    assert validated is LifecycleGuardGenerator
