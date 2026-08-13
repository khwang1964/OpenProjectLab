from pathlib import Path

import yaml

from generator.core.models import GenerateRequest, GenerationResult, RuntimeOptions
from generator.generators.quiz_generator import QuizGenerator


def _templates(root: Path) -> None:
    quiz = root / "quiz" / "README.md.j2"
    quiz.parent.mkdir(parents=True, exist_ok=True)
    quiz.write_text(
        """# 小考：{{ title }}

> Week {{ week_padded }} · Quiz ID: `{{ quiz_id }}`

## 題目

{% for question in questions %}
### 第 {{ loop.index }} 題：{{ question.prompt }}

{% for choice in question.choices %}
- {{ choice }}
{% endfor %}

{% endfor %}
""",
        encoding="utf-8",
    )


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


def _request(
    project: Path,
    *,
    dry_run: bool = False,
    overwrite: bool = False,
    record_manifest: bool = True,
) -> GenerateRequest:
    return GenerateRequest(
        generator_name="quiz",
        target=project,
        values={
            "course_name": "Modern Java",
            "week": 3,
            "quiz_id": "streams-basics",
            "title": "Streams Basics Quiz",
            "questions": _questions(),
            "record_manifest": record_manifest,
        },
        options=RuntimeOptions(
            dry_run=dry_run,
            overwrite=overwrite,
        ),
    )


def test_quiz_generator_renders_expected_primary_artifact(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    result = QuizGenerator(templates).generate(
        _request(project, record_manifest=False),
    )

    readme = project / "week-03" / "quiz" / "streams-basics" / "README.md"
    content = readme.read_text(encoding="utf-8")

    assert isinstance(result, GenerationResult)
    assert result.generator_name == "quiz"
    assert result.dry_run is False
    assert readme.exists()
    assert "# 小考：Streams Basics Quiz" in content
    assert "Week 03" in content
    assert "Which operation is intermediate?" in content
    assert "- map" in content
    assert "- collect" in content


def test_quiz_generator_does_not_expose_correct_answers_in_learner_artifact(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    QuizGenerator(templates).generate(
        _request(project, record_manifest=False),
    )

    readme = project / "week-03" / "quiz" / "streams-basics" / "README.md"
    content = readme.read_text(encoding="utf-8")

    assert "correct_answer" not in content
    assert "教師用答案" not in content
    assert "Answer Key" not in content


def test_quiz_generator_records_existing_manifest_schema(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    result = QuizGenerator(templates).generate(
        _request(project, overwrite=True),
    )

    manifest_path = project / ".opl" / "manifest.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    item = next(
        item
        for item in data["generated"]
        if item["path"] == "week-03/quiz/streams-basics/README.md"
    )

    assert result.manifest_updated is True
    assert item["generator"] == "quiz"
    assert item["metadata"] == {
        "week": 3,
        "quiz_id": "streams-basics",
        "title": "Streams Basics Quiz",
    }


def test_quiz_generator_dry_run_does_not_create_artifact_or_manifest(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    result = QuizGenerator(templates).generate(
        _request(project, dry_run=True),
    )

    assert result.dry_run is True
    assert result.manifest_updated is False
    assert not project.exists()


def test_quiz_generator_manifest_can_be_disabled(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    QuizGenerator(templates).generate(
        _request(project, record_manifest=False),
    )

    assert (project / "week-03" / "quiz" / "streams-basics" / "README.md").exists()
    assert not (project / ".opl").exists()


def test_quiz_generator_preserves_question_and_choice_order_in_rendered_output(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    QuizGenerator(templates).generate(
        _request(project, record_manifest=False),
    )

    readme = project / "week-03" / "quiz" / "streams-basics" / "README.md"
    content = readme.read_text(encoding="utf-8")

    first_question = content.index("Which operation is intermediate?")
    second_question = content.index("Which operation produces a result?")
    map_choice = content.index("- map", first_question)
    collect_choice = content.index("- collect", first_question)
    count_choice = content.index("- count", first_question)
    reduce_choice = content.index("- reduce", first_question)

    assert first_question < second_question
    assert map_choice < collect_choice < count_choice < reduce_choice
