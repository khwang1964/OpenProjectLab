"""Freeze the implemented OpenProjectLab v1 public error contract."""

import pytest

from generator.core.exceptions import (
    ConfigurationError,
    GeneratorNotFoundError,
    GeneratorValidationError,
    OPLGeneratorError,
    PluginError,
    TemplateError,
    ValidationError,
)


@pytest.mark.parametrize(
    "error_type",
    [
        ValidationError,
        GeneratorNotFoundError,
        ConfigurationError,
        TemplateError,
        PluginError,
    ],
)
def test_v1_framework_errors_derive_from_base_error(
    error_type: type[OPLGeneratorError],
) -> None:
    """Keep reviewed framework failures under OPLGeneratorError."""
    assert issubclass(error_type, OPLGeneratorError)


def test_v1_generator_validation_error_is_a_validation_error() -> None:
    """Keep Generator validation failures catchable as ValidationError."""
    assert issubclass(GeneratorValidationError, ValidationError)
    assert issubclass(GeneratorValidationError, OPLGeneratorError)


def test_v1_generator_validation_error_exposes_structured_fields() -> None:
    """Freeze the reviewed structured validation fields."""
    error = GeneratorValidationError(
        generator="quiz",
        field="week",
        message="week is invalid",
    )

    assert error.generator == "quiz"
    assert error.field == "week"
    assert error.message == "week is invalid"
    assert str(error) == "week is invalid"


def test_v1_public_errors_remain_standard_exceptions() -> None:
    """Keep public framework errors compatible with normal Exception handling."""
    error = PluginError("plugin failed")

    assert isinstance(error, Exception)
    assert str(error) == "plugin failed"
