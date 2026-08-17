"""Freeze OpenProjectLab v1 built-in Generator identities and artifact paths."""

from pathlib import Path

from generator.generators.assignment_generator import AssignmentGenerator
from generator.generators.bootstrap_generator import BootstrapGenerator
from generator.generators.course_generator import CourseGenerator
from generator.generators.lab_generator import LabGenerator
from generator.generators.quiz_generator import QuizGenerator
from generator.generators.slides_generator import SlidesGenerator
from generator.generators.website_generator import WebsiteGenerator
from generator.generators.week_generator import WeekGenerator
from generator.sdk import GenerateRequest


def test_v1_builtin_generator_identities_are_stable() -> None:
    """Freeze the reviewed v1 built-in Generator public names."""
    actual = {
        BootstrapGenerator.name,
        CourseGenerator.name,
        WeekGenerator.name,
        LabGenerator.name,
        QuizGenerator.name,
        AssignmentGenerator.name,
        SlidesGenerator.name,
        WebsiteGenerator.name,
    }

    assert actual == {
        "bootstrap",
        "course",
        "week",
        "lab",
        "quiz",
        "assignment",
        "slides",
        "website",
    }


def test_v1_lab_artifact_path_is_canonical(tmp_path: Path) -> None:
    """Keep Week-scoped Lab output at its canonical v1 path."""
    generator = LabGenerator()
    request = GenerateRequest(
        generator_name="lab",
        target=tmp_path,
        values={
            "week": 3,
            "lab_id": "streams-practice",
            "title": "Streams Practice",
        },
    )

    plan = generator.plan(request)

    assert plan.destinations() == (tmp_path / "week-03" / "lab" / "streams-practice" / "README.md",)


def test_v1_quiz_artifact_path_is_canonical(tmp_path: Path) -> None:
    """Keep Week-scoped Quiz output at its canonical v1 path."""
    generator = QuizGenerator()
    request = GenerateRequest(
        generator_name="quiz",
        target=tmp_path,
        values={
            "week": 4,
            "quiz_id": "streams-basics",
            "title": "Streams Basics",
            "questions": (
                {
                    "id": "q1",
                    "prompt": "Which choice is correct?",
                    "choices": ("A", "B"),
                    "correct_answer": "A",
                },
            ),
        },
    )

    plan = generator.plan(request)

    assert plan.destinations() == (tmp_path / "week-04" / "quiz" / "streams-basics" / "README.md",)


def test_v1_assignment_artifact_path_is_canonical(tmp_path: Path) -> None:
    """Keep Week-scoped Assignment output at its canonical v1 path."""
    generator = AssignmentGenerator()
    request = GenerateRequest(
        generator_name="assignment",
        target=tmp_path,
        values={
            "week": 5,
            "assignment_id": "streams-homework",
            "title": "Streams Homework",
        },
    )

    plan = generator.plan(request)

    assert plan.destinations() == (
        tmp_path / "week-05" / "assignment" / "streams-homework" / "README.md",
    )


def test_v1_slides_artifact_path_is_canonical(tmp_path: Path) -> None:
    """Keep Slides output at the canonical target-level slides.md path."""
    generator = SlidesGenerator()
    request = GenerateRequest(
        generator_name="slides",
        target=tmp_path,
        values={
            "title": "Week 06 Slides",
            "slides": (
                {
                    "title": "Introduction",
                    "content": ("First point",),
                },
            ),
        },
    )

    plan = generator.plan(request)

    assert plan.destinations() == (tmp_path / "slides.md",)


def test_v1_website_artifact_paths_preserve_authored_page_order(
    tmp_path: Path,
) -> None:
    """Keep Website output under site/ and preserve authored page ordering."""
    generator = WebsiteGenerator()
    request = GenerateRequest(
        generator_name="website",
        target=tmp_path,
        values={
            "title": "Course Website",
            "pages": (
                {
                    "path": "index.html",
                    "title": "Home",
                    "content": "Welcome",
                },
                {
                    "path": "weeks/week-01.html",
                    "title": "Week 01",
                    "content": "Week content",
                },
            ),
        },
    )

    plan = generator.plan(request)

    assert plan.destinations() == (
        tmp_path / "site" / "index.html",
        tmp_path / "site" / "weeks" / "week-01.html",
    )
