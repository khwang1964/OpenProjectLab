"""Define the validation contract shared by built-in generators."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import pytest

from generator.core.exceptions import GeneratorValidationError
from generator.core.models import GenerateRequest, GenerationResult, RuntimeOptions
from generator.generators.bootstrap_generator import BootstrapGenerator
from generator.generators.course_generator import CourseGenerator
from generator.generators.week_generator import WeekGenerator


class Generator(Protocol):
    """Describe the built-in generator interface exercised by this contract."""

    name: str

    def generate(self, request: GenerateRequest) -> GenerationResult:
        """Generate content from a request."""

    def run(self, request: GenerateRequest) -> GenerationResult:
        """Run the canonical generator lifecycle."""


GeneratorFactory = Callable[[Path | None], Generator]
EntryPoint = Callable[[Generator, GenerateRequest], GenerationResult]


@dataclass(frozen=True, slots=True)
class GeneratorCase:
    """Describe one built-in generator and its valid request values."""

    name: str
    factory: GeneratorFactory
    templates: tuple[str, ...]
    values: Mapping[str, object]


CASES = (
    GeneratorCase(
        name="bootstrap",
        factory=BootstrapGenerator,
        templates=tuple(BootstrapGenerator.TEMPLATE_MANIFEST.values()),
        values={
            "project_slug": "contract-course",
            "project_name": "Contract Course",
        },
    ),
    GeneratorCase(
        name="course",
        factory=CourseGenerator,
        templates=("course/README.md.j2",),
        values={
            "course_name": "Contract Course",
            "weeks": 16,
        },
    ),
    GeneratorCase(
        name="week",
        factory=WeekGenerator,
        templates=("week/README.md.j2",),
        values={
            "course_name": "Contract Course",
            "week": 1,
            "title": "Introduction",
        },
    ),
)


def _generate(
    generator: Generator,
    request: GenerateRequest,
) -> GenerationResult:
    """Invoke the compatibility generation entry point."""
    return generator.generate(request)


def _run(
    generator: Generator,
    request: GenerateRequest,
) -> GenerationResult:
    """Invoke the canonical lifecycle entry point."""
    return generator.run(request)


ENTRY_POINTS = (_generate, _run)


@pytest.fixture
def generator_case(request: pytest.FixtureRequest) -> GeneratorCase:
    """Return the generator case selected by indirect parametrization."""
    return CASES[request.param]


@pytest.fixture
def generator_and_target(
    tmp_path: Path,
    generator_case: GeneratorCase,
) -> tuple[Generator, Path]:
    """Create the templates and generator required by one contract case."""
    template_root = tmp_path / "templates"
    target = tmp_path / "output"

    for template_name in generator_case.templates:
        template_path = template_root / template_name
        template_path.parent.mkdir(parents=True, exist_ok=True)
        template_path.write_text("generated content\n", encoding="utf-8")

    return generator_case.factory(template_root), target


def _request(
    case: GeneratorCase,
    target: Path,
    *,
    generator_name: str | None = None,
    values: Mapping[str, object] | None = None,
    dry_run: bool = False,
) -> GenerateRequest:
    """Build a request for one validation-contract case."""
    return GenerateRequest(
        generator_name=generator_name or case.name,
        target=target,
        values=case.values if values is None else values,
        options=RuntimeOptions(dry_run=dry_run),
    )


def _assert_validation_error(
    error: GeneratorValidationError,
    *,
    generator: str,
    field: str,
) -> None:
    """Assert the stable structured context exposed by validation errors."""
    assert error.generator == generator
    assert error.field == field
    assert str(error)


@pytest.mark.parametrize("generator_case", range(len(CASES)), indirect=True)
@pytest.mark.parametrize("entry_point", ENTRY_POINTS, ids=("generate", "run"))
def test_generator_name_validation_is_structured_and_has_no_side_effects(
    generator_case: GeneratorCase,
    generator_and_target: tuple[Generator, Path],
    entry_point: EntryPoint,
) -> None:
    """Reject misrouted requests consistently before creating output."""
    generator, target = generator_and_target
    request = _request(
        generator_case,
        target,
        generator_name="different-generator",
    )

    with pytest.raises(GeneratorValidationError) as captured:
        entry_point(generator, request)

    _assert_validation_error(
        captured.value,
        generator=generator_case.name,
        field="generator_name",
    )
    assert not target.exists()


@pytest.mark.parametrize("generator_case", range(len(CASES)), indirect=True)
def test_missing_template_root_is_a_structured_validation_error(
    tmp_path: Path,
    generator_case: GeneratorCase,
) -> None:
    """Report a missing generator dependency through the validation contract."""
    target = tmp_path / "output"
    generator = generator_case.factory(None)

    with pytest.raises(GeneratorValidationError) as captured:
        generator.run(_request(generator_case, target))

    _assert_validation_error(
        captured.value,
        generator=generator_case.name,
        field="template_root",
    )
    assert not target.exists()


@pytest.mark.parametrize("project_slug", (None, "", "Invalid Slug", "a/b"))
@pytest.mark.parametrize("entry_point", ENTRY_POINTS, ids=("generate", "run"))
def test_bootstrap_project_slug_validation_is_structured(
    tmp_path: Path,
    project_slug: object,
    entry_point: EntryPoint,
) -> None:
    """Expose invalid Bootstrap slugs through a stable field contract."""
    target = tmp_path / "output"
    values = {
        "project_slug": project_slug,
        "project_name": "Contract Course",
    }

    with pytest.raises(GeneratorValidationError) as captured:
        entry_point(
            BootstrapGenerator(tmp_path / "templates"),
            GenerateRequest("bootstrap", target, values),
        )

    _assert_validation_error(
        captured.value,
        generator="bootstrap",
        field="project_slug",
    )
    assert not target.exists()


@pytest.mark.parametrize("week", (None, True, "1", 0, -1))
@pytest.mark.parametrize("dry_run", (False, True), ids=("write", "dry-run"))
def test_week_value_validation_runs_in_all_runtime_modes(
    tmp_path: Path,
    week: object,
    dry_run: bool,
) -> None:
    """Validate week values fully during normal and dry-run execution."""
    target = tmp_path / "output"
    values = {
        "course_name": "Contract Course",
        "week": week,
        "title": "Introduction",
    }
    request = GenerateRequest(
        "week",
        target,
        values,
        RuntimeOptions(dry_run=dry_run),
    )

    with pytest.raises(GeneratorValidationError) as captured:
        WeekGenerator(tmp_path / "templates").run(request)

    _assert_validation_error(
        captured.value,
        generator="week",
        field="week",
    )
    assert not target.exists()


@pytest.mark.parametrize(
    "directory_pattern",
    ("week-{missing}", "{week!invalid}", "", ".", "../week-{week:02d}"),
)
def test_week_directory_pattern_validation_is_structured_and_safe(
    tmp_path: Path,
    directory_pattern: str,
) -> None:
    """Reject malformed or escaping week directories before filesystem writes."""
    target = tmp_path / "output"
    values = {
        "course_name": "Contract Course",
        "week": 1,
        "title": "Introduction",
        "directory_pattern": directory_pattern,
    }

    with pytest.raises(GeneratorValidationError) as captured:
        WeekGenerator(tmp_path / "templates").run(
            GenerateRequest("week", target, values),
        )

    _assert_validation_error(
        captured.value,
        generator="week",
        field="directory_pattern",
    )
    assert not target.exists()
    assert not (tmp_path / "week-01").exists()
