"""Freeze the OpenProjectLab v1 Courseware domain public contract."""

from dataclasses import FrozenInstanceError

import pytest

from generator.courseware.models import Course, Week


def test_v1_week_accepts_positive_integer_identity() -> None:
    """Keep positive integer Week identity and authored title available."""
    week = Week(number=2, title="Streams")

    assert week.number == 2
    assert week.title == "Streams"


@pytest.mark.parametrize("value", [0, -1, True, False, 1.5, "1", None])
def test_v1_week_rejects_invalid_numbers(value: object) -> None:
    """Reject non-positive and non-integer Week identities."""
    with pytest.raises(ValueError):
        Week(number=value, title="Invalid")  # type: ignore[arg-type]


def test_v1_week_is_immutable() -> None:
    """Keep Week immutable after construction."""
    week = Week(number=1, title="Introduction")

    with pytest.raises(FrozenInstanceError):
        week.number = 2  # type: ignore[misc]


def test_v1_course_normalizes_identity_and_orders_weeks() -> None:
    """Normalize Course identity and order Weeks deterministically by number."""
    week_three = Week(number=3, title="Three")
    week_one = Week(number=1, title="One")
    week_two = Week(number=2, title="Two")

    course = Course(
        course_id="  modern-java  ",
        title="Modern Java",
        language="zh-TW",
        weeks=(week_three, week_one, week_two),
    )

    assert course.course_id == "modern-java"
    assert course.title == "Modern Java"
    assert course.language == "zh-TW"
    assert course.weeks == (week_one, week_two, week_three)


def test_v1_course_rejects_blank_identity() -> None:
    """Reject a blank Course identity."""
    with pytest.raises(ValueError):
        Course(
            course_id="   ",
            title="Invalid",
            language="zh-TW",
        )


def test_v1_course_rejects_duplicate_week_numbers() -> None:
    """Reject duplicate Week identities inside one Course aggregate."""
    with pytest.raises(ValueError):
        Course(
            course_id="duplicate-weeks",
            title="Duplicate Weeks",
            language="zh-TW",
            weeks=(
                Week(number=1, title="First"),
                Week(number=1, title="Duplicate"),
            ),
        )


def test_v1_course_weeks_are_normalized_to_tuple() -> None:
    """Expose Course Weeks as an immutable ordered tuple."""
    course = Course(
        course_id="course",
        title="Course",
        language="en",
        weeks=[
            Week(number=2, title="Two"),
            Week(number=1, title="One"),
        ],
    )

    assert isinstance(course.weeks, tuple)
    assert tuple(week.number for week in course.weeks) == (1, 2)


def test_v1_course_is_immutable() -> None:
    """Keep the Course aggregate immutable after construction."""
    course = Course(
        course_id="course",
        title="Course",
        language="en",
    )

    with pytest.raises(FrozenInstanceError):
        course.title = "Changed"  # type: ignore[misc]
