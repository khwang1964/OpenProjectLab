"""Contract tests for the proposed Quiz Generator."""

from __future__ import annotations

from pathlib import Path

import pytest

from generator.core.exceptions import GeneratorValidationError
from generator.core.models import GenerateRequest, GenerationPlan, GenerationResult, RuntimeOptions
from generator.generators.base import BaseGenerator

pytest.importorskip(
    "generator.generators.quiz_generator",
    reason="QuizGenerator implementation lands in Step 5.4C",
)

from generator.generators.quiz_generator import QuizGenerator


def _questions() -> tuple[dict[str, object], ...]:
    return (
        {
            "id": "q1",
            "prompt": "Which operation is intermediate?",
            "choices": ("map", "collect", "count", "reduce"),
            "correct_answer": "map",
        },
        {
            "id": "q2",
            "prompt": "Which operation produces a result?",
            "choices": ("filter", "map", "collect", "peek"),
            "correct_answer": "collect",
        },
    )


_DEFAULT_QUESTIONS = object()


def _request(
    tmp_path: Path,
    *,
    generator_name: str = "quiz",
    week: object = 3,
    quiz_id: object = "streams-basics",
    title: object = "Streams Basics Quiz",
    questions: object = _DEFAULT_QUESTIONS,
    dry_run: bool = True,
    overwrite: bool = False,
) -> GenerateRequest:
    return GenerateRequest(
        generator_name=generator_name,
        target=tmp_path / "course",
        values={
            "week": week,
            "quiz_id": quiz_id,
            "title": title,
            "questions": (_questions() if questions is _DEFAULT_QUESTIONS else questions),
            "record_manifest": False,
        },
        options=RuntimeOptions(
            dry_run=dry_run,
            overwrite=overwrite,
        ),
    )


def _generator(tmp_path: Path) -> QuizGenerator:
    return QuizGenerator(template_root=tmp_path / "templates")


def test_quiz_generator_is_base_generator() -> None:
    assert issubclass(QuizGenerator, BaseGenerator)


def test_quiz_generator_has_canonical_identity() -> None:
    assert QuizGenerator.name == "quiz"


def test_quiz_generator_accepts_minimum_valid_request(tmp_path: Path) -> None:
    generator = _generator(tmp_path)

    generator.validate_request(_request(tmp_path))


@pytest.mark.parametrize("week", [0, -1, -10])
def test_quiz_generator_rejects_non_positive_week(
    tmp_path: Path,
    week: int,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, week=week))

    assert exc_info.value.generator == "quiz"
    assert exc_info.value.field == "week"


@pytest.mark.parametrize("week", [True, False])
def test_quiz_generator_rejects_bool_week(
    tmp_path: Path,
    week: bool,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, week=week))

    assert exc_info.value.generator == "quiz"
    assert exc_info.value.field == "week"


@pytest.mark.parametrize("week", ["3", 3.0, None])
def test_quiz_generator_rejects_non_integer_week(
    tmp_path: Path,
    week: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, week=week))

    assert exc_info.value.field == "week"


@pytest.mark.parametrize("quiz_id", ["", "   "])
def test_quiz_generator_rejects_empty_quiz_id(
    tmp_path: Path,
    quiz_id: str,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, quiz_id=quiz_id))

    assert exc_info.value.generator == "quiz"
    assert exc_info.value.field == "quiz_id"


@pytest.mark.parametrize(
    "quiz_id",
    [
        "../streams",
        "quiz/streams",
        r"quiz\streams",
        "/absolute",
    ],
)
def test_quiz_generator_rejects_path_like_quiz_id(
    tmp_path: Path,
    quiz_id: str,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, quiz_id=quiz_id))

    assert exc_info.value.field == "quiz_id"


@pytest.mark.parametrize("quiz_id", [None, 3, True])
def test_quiz_generator_rejects_non_string_quiz_id(
    tmp_path: Path,
    quiz_id: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, quiz_id=quiz_id))

    assert exc_info.value.field == "quiz_id"


@pytest.mark.parametrize("title", ["", "   "])
def test_quiz_generator_rejects_empty_title(
    tmp_path: Path,
    title: str,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, title=title))

    assert exc_info.value.generator == "quiz"
    assert exc_info.value.field == "title"


@pytest.mark.parametrize("title", [None, 3, True])
def test_quiz_generator_rejects_non_string_title(
    tmp_path: Path,
    title: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, title=title))

    assert exc_info.value.field == "title"


def test_quiz_generator_rejects_wrong_generator_name(tmp_path: Path) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(
            _request(tmp_path, generator_name="week"),
        )

    assert exc_info.value.generator == "quiz"
    assert exc_info.value.field == "generator_name"


@pytest.mark.parametrize(
    "questions",
    [
        (),
        [],
    ],
)
def test_quiz_generator_rejects_empty_questions(
    tmp_path: Path,
    questions: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, questions=questions))

    assert exc_info.value.generator == "quiz"
    assert exc_info.value.field == "questions"


@pytest.mark.parametrize("questions", [None, "q1", 3, True])
def test_quiz_generator_rejects_invalid_questions_collection(
    tmp_path: Path,
    questions: object,
) -> None:
    generator = _generator(tmp_path)

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(
            _request(tmp_path, questions=questions),
        )

    assert exc_info.value.field == "questions"


def test_quiz_generator_rejects_duplicate_question_ids(tmp_path: Path) -> None:
    generator = _generator(tmp_path)
    questions = (
        {
            "id": "q1",
            "prompt": "First question",
            "choices": ("a", "b"),
            "correct_answer": "a",
        },
        {
            "id": "q1",
            "prompt": "Second question",
            "choices": ("c", "d"),
            "correct_answer": "c",
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, questions=questions))

    assert exc_info.value.field in {"questions", "question_id"}


@pytest.mark.parametrize("question_id", ["", "   ", None, 3, True])
def test_quiz_generator_rejects_invalid_question_id(
    tmp_path: Path,
    question_id: object,
) -> None:
    generator = _generator(tmp_path)
    questions = (
        {
            "id": question_id,
            "prompt": "Question",
            "choices": ("a", "b"),
            "correct_answer": "a",
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, questions=questions))

    assert exc_info.value.field in {"questions", "question_id"}


@pytest.mark.parametrize("prompt", ["", "   ", None, 3, True])
def test_quiz_generator_rejects_invalid_question_prompt(
    tmp_path: Path,
    prompt: object,
) -> None:
    generator = _generator(tmp_path)
    questions = (
        {
            "id": "q1",
            "prompt": prompt,
            "choices": ("a", "b"),
            "correct_answer": "a",
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, questions=questions))

    assert exc_info.value.field in {"questions", "prompt"}


@pytest.mark.parametrize(
    "choices",
    [
        (),
        ("only-one",),
        [],
        ["only-one"],
    ],
)
def test_quiz_generator_rejects_insufficient_choices(
    tmp_path: Path,
    choices: object,
) -> None:
    generator = _generator(tmp_path)
    questions = (
        {
            "id": "q1",
            "prompt": "Question",
            "choices": choices,
            "correct_answer": "only-one",
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, questions=questions))

    assert exc_info.value.field in {"questions", "choices"}


def test_quiz_generator_rejects_correct_answer_not_in_choices(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    questions = (
        {
            "id": "q1",
            "prompt": "Question",
            "choices": ("a", "b"),
            "correct_answer": "c",
        },
    )

    with pytest.raises(GeneratorValidationError) as exc_info:
        generator.validate_request(_request(tmp_path, questions=questions))

    assert exc_info.value.field in {"questions", "correct_answer"}


def test_quiz_generator_preserves_question_and_choice_order(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    questions = (
        {
            "id": "q2",
            "prompt": "Second",
            "choices": ("b", "a", "c"),
            "correct_answer": "b",
        },
        {
            "id": "q1",
            "prompt": "First",
            "choices": ("c", "b", "a"),
            "correct_answer": "c",
        },
    )
    request = _request(tmp_path, questions=questions)

    generator.validate_request(request)
    plan = generator.plan(request)

    assert isinstance(plan, GenerationPlan)
    assert plan.generator_name == "quiz"
    assert len(plan.operations) == 1

    context = plan.operations[0].context
    assert tuple(question["id"] for question in context["questions"]) == ("q2", "q1")
    assert tuple(context["questions"][0]["choices"]) == ("b", "a", "c")
    assert tuple(context["questions"][1]["choices"]) == ("c", "b", "a")


def test_quiz_plan_uses_generation_plan_as_canonical_boundary(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path)

    generator.validate_request(request)
    plan = generator.plan(request)

    assert isinstance(plan, GenerationPlan)
    assert plan.generator_name == "quiz"
    assert len(plan.operations) == 1
    assert plan.operations[0].destination == (
        request.target / "week-03" / "quiz" / "streams-basics" / "README.md"
    )


def test_quiz_plan_destination_does_not_depend_on_title(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    original = _request(tmp_path, title="Streams Basics Quiz")
    renamed = _request(tmp_path, title="Stream Processing Checkpoint")

    generator.validate_request(original)
    generator.validate_request(renamed)

    original_plan = generator.plan(original)
    renamed_plan = generator.plan(renamed)

    assert original_plan.operations[0].destination == renamed_plan.operations[0].destination


def test_quiz_plan_is_deterministic_for_same_request(
    tmp_path: Path,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path)

    generator.validate_request(request)

    first = generator.plan(request)
    second = generator.plan(request)

    assert first == second


def test_invalid_quiz_request_fails_before_planning(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    generator = _generator(tmp_path)
    request = _request(tmp_path, week=0)
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


def test_quiz_dry_run_preserves_no_filesystem_mutation(
    tmp_path: Path,
) -> None:
    template_root = tmp_path / "templates"
    template_file = template_root / "quiz" / "README.md.j2"
    template_file.parent.mkdir(parents=True)
    template_file.write_text(
        "# {{ title }}\n\nWeek {{ week }}\n",
        encoding="utf-8",
    )

    generator = QuizGenerator(template_root=template_root)
    request = _request(tmp_path, dry_run=True)

    result = generator.run(request)

    assert isinstance(result, GenerationResult)
    assert result.generator_name == "quiz"
    assert result.dry_run is True
    assert result.manifest_updated is False
    assert not request.target.exists()
