"""Contract tests for the proposed Open Courseware domain boundary.

These tests intentionally exercise the currently accepted Course/Week generator
contracts and the minimum invariants defined by ADR 0014 without assuming that a
new public courseware domain module already exists.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, dataclass
from pathlib import Path

import pytest

from generator.core.exceptions import GeneratorValidationError
from generator.core.models import GenerateRequest, GenerationPlan, RuntimeOptions
from generator.generators.course_generator import CourseGenerator
from generator.generators.week_generator import WeekGenerator


@dataclass(frozen=True, slots=True)
class _WeekContract:
    number: int
    title: str


@dataclass(frozen=True, slots=True)
class _CourseContract:
    course_id: str
    title: str
    language: str
    weeks: tuple[_WeekContract, ...]


def _week_request(
    tmp_path: Path,
    *,
    week: object,
    title: str = "Streams",
    dry_run: bool = True,
) -> GenerateRequest:
    return GenerateRequest(
        generator_name="week",
        target=tmp_path / "course",
        values={
            "week": week,
            "title": title,
            "record_manifest": False,
        },
        options=RuntimeOptions(dry_run=dry_run),
    )


def _course_request(tmp_path: Path, *, title: str = "Modern Java") -> GenerateRequest:
    return GenerateRequest(
        generator_name="course",
        target=tmp_path / "course",
        values={
            "course_id": "modern-java",
            "course_name": title,
            "title": title,
            "language": "zh-TW",
            "record_manifest": False,
        },
        options=RuntimeOptions(dry_run=True),
    )


def _validate_course_contract(course: _CourseContract) -> _CourseContract:
    if not course.course_id.strip():
        raise ValueError("course_id 不可為空")

    numbers: list[int] = []
    for week in course.weeks:
        if isinstance(week.number, bool) or not isinstance(week.number, int):
            raise ValueError("week number 必須是整數")
        if week.number <= 0:
            raise ValueError("week number 必須大於 0")
        numbers.append(week.number)

    if len(numbers) != len(set(numbers)):
        raise ValueError("同一 Course 不可包含重複的 week number")

    return _CourseContract(
        course_id=course.course_id,
        title=course.title,
        language=course.language,
        weeks=tuple(sorted(course.weeks, key=lambda week: week.number)),
    )


def test_course_identity_is_explicit_and_independent_from_title() -> None:
    course = _CourseContract(
        course_id="modern-java",
        title="Modern Java",
        language="zh-TW",
        weeks=(),
    )
    renamed = _CourseContract(
        course_id=course.course_id,
        title="Modern Java in Action",
        language=course.language,
        weeks=course.weeks,
    )

    assert course.course_id == "modern-java"
    assert renamed.course_id == course.course_id
    assert renamed.title != course.title


@pytest.mark.parametrize("course_id", ["", "   "])
def test_course_identity_must_not_be_empty(course_id: str) -> None:
    course = _CourseContract(
        course_id=course_id,
        title="Modern Java",
        language="zh-TW",
        weeks=(),
    )

    with pytest.raises(ValueError, match="course_id"):
        _validate_course_contract(course)


@pytest.mark.parametrize("week", [1, 2, 16])
def test_existing_week_generator_accepts_positive_integer_week(
    tmp_path: Path,
    week: int,
) -> None:
    generator = WeekGenerator(template_root=tmp_path)

    generator.validate_request(_week_request(tmp_path, week=week))


@pytest.mark.parametrize("week", [0, -1, -10])
def test_existing_week_generator_rejects_non_positive_week(
    tmp_path: Path,
    week: int,
) -> None:
    generator = WeekGenerator(template_root=tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_week_request(tmp_path, week=week))

    assert exc_info.value.generator == "week"
    assert exc_info.value.field == "week"


@pytest.mark.parametrize("week", [True, False])
def test_existing_week_generator_rejects_bool_week(
    tmp_path: Path,
    week: bool,
) -> None:
    generator = WeekGenerator(template_root=tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_week_request(tmp_path, week=week))

    assert exc_info.value.generator == "week"
    assert exc_info.value.field == "week"


def test_course_contract_rejects_duplicate_week_numbers() -> None:
    course = _CourseContract(
        course_id="modern-java",
        title="Modern Java",
        language="zh-TW",
        weeks=(
            _WeekContract(number=3, title="Streams"),
            _WeekContract(number=3, title="Collectors"),
        ),
    )

    with pytest.raises(ValueError, match="重複"):
        _validate_course_contract(course)


def test_course_contract_orders_weeks_by_number_deterministically() -> None:
    course = _CourseContract(
        course_id="modern-java",
        title="Modern Java",
        language="zh-TW",
        weeks=(
            _WeekContract(number=3, title="Streams"),
            _WeekContract(number=1, title="Introduction"),
            _WeekContract(number=2, title="Lambdas"),
        ),
    )

    validated = _validate_course_contract(course)

    assert tuple(week.number for week in validated.weeks) == (1, 2, 3)


def test_week_title_is_not_week_identity() -> None:
    original = _WeekContract(number=3, title="Streams")
    renamed = _WeekContract(number=3, title="Stream Processing")

    assert original.number == renamed.number
    assert original.title != renamed.title


def test_contract_models_are_immutable() -> None:
    course = _CourseContract(
        course_id="modern-java",
        title="Modern Java",
        language="zh-TW",
        weeks=(),
    )

    with pytest.raises(FrozenInstanceError):
        course.title = "Changed"  # type: ignore[misc]


def test_week_plan_uses_generation_plan_as_canonical_planning_boundary(
    tmp_path: Path,
) -> None:
    generator = WeekGenerator(template_root=tmp_path)
    request = _week_request(tmp_path, week=3)

    generator.validate_request(request)
    plan = generator.plan(request)

    assert isinstance(plan, GenerationPlan)
    assert plan.generator_name == "week"
    assert len(plan.operations) == 1
    assert plan.operations[0].destination == (request.target / "week-03" / "README.md")


def test_course_plan_uses_generation_plan_as_canonical_planning_boundary(
    tmp_path: Path,
) -> None:
    generator = CourseGenerator(template_root=tmp_path)
    request = _course_request(tmp_path)

    generator.validate_request(request)
    plan = generator.plan(request)

    assert isinstance(plan, GenerationPlan)
    assert plan.generator_name == "course"
    assert len(plan.operations) == 1
    assert plan.operations[0].destination == request.target / "README.md"


def test_invalid_week_fails_before_planning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    generator = WeekGenerator(template_root=tmp_path)
    request = _week_request(tmp_path, week=0)
    planning_called = False

    original_plan = generator.plan

    def tracking_plan(request: GenerateRequest) -> GenerationPlan:
        nonlocal planning_called
        planning_called = True
        return original_plan(request)

    monkeypatch.setattr(generator, "plan", tracking_plan)

    with pytest.raises(GeneratorValidationError):
        generator.run(request)

    assert planning_called is False
    assert not request.target.exists()


def test_dry_run_preserves_no_filesystem_mutation_for_week(
    tmp_path: Path,
) -> None:
    template_root = tmp_path / "templates"
    template_file = template_root / "week" / "README.md.j2"
    template_file.parent.mkdir(parents=True)
    template_file.write_text("# Week {{ week }}\n", encoding="utf-8")

    target = tmp_path / "course"
    generator = WeekGenerator(template_root=template_root)
    request = _week_request(tmp_path, week=3, dry_run=True)

    result = generator.run(request)

    assert result.generator_name == "week"
    assert result.dry_run is True
    assert result.manifest_updated is False
    assert not target.exists()
