"""Immutable domain models for the Open Courseware Platform."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Week:
    """Represent one ordered teaching unit within a course."""

    number: int
    title: str

    def __post_init__(self) -> None:
        """Validate Week identity invariants."""
        if isinstance(self.number, bool) or not isinstance(self.number, int):
            raise ValueError("week number 必須是整數")
        if self.number <= 0:
            raise ValueError("week number 必須大於 0")


@dataclass(frozen=True, slots=True)
class Course:
    """Represent the root Open Courseware domain aggregate."""

    course_id: str
    title: str
    language: str
    weeks: tuple[Week, ...] = ()

    def __post_init__(self) -> None:
        """Normalize and validate Course invariants."""
        normalized_id = self.course_id.strip()
        normalized_weeks = tuple(self.weeks)

        if not normalized_id:
            raise ValueError("course_id 不可為空")

        numbers = tuple(week.number for week in normalized_weeks)
        if len(numbers) != len(set(numbers)):
            raise ValueError("同一 Course 不可包含重複的 week number")

        object.__setattr__(self, "course_id", normalized_id)
        object.__setattr__(
            self,
            "weeks",
            tuple(sorted(normalized_weeks, key=lambda week: week.number)),
        )
