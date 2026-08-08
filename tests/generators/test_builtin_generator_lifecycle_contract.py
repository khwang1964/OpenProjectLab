"""Enforce the canonical lifecycle across built-in generators."""

from __future__ import annotations

import pytest

from generator.generators.base import BaseGenerator
from generator.generators.bootstrap_generator import BootstrapGenerator
from generator.generators.course_generator import CourseGenerator
from generator.generators.week_generator import WeekGenerator

BUILTIN_GENERATORS = (
    BootstrapGenerator,
    CourseGenerator,
    WeekGenerator,
)


@pytest.mark.parametrize(
    "generator_type",
    BUILTIN_GENERATORS,
    ids=lambda generator_type: generator_type.name,
)
def test_builtin_generators_inherit_base_generator(
    generator_type: type[object],
) -> None:
    """Require every built-in generator to use the shared framework."""
    assert issubclass(generator_type, BaseGenerator)


@pytest.mark.parametrize(
    "generator_type",
    BUILTIN_GENERATORS,
    ids=lambda generator_type: generator_type.name,
)
def test_builtin_generators_do_not_override_run(
    generator_type: type[object],
) -> None:
    """Keep run() under BaseGenerator framework control."""
    assert "run" not in generator_type.__dict__
