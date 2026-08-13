import json
from pathlib import Path

import pytest

from generator.cli import main as cli


@pytest.fixture
def quiz_template_root(tmp_path: Path) -> Path:
    root = tmp_path / "templates"
    quiz = root / "quiz"
    quiz.mkdir(parents=True)
    (quiz / "README.md.j2").write_text(
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
    return root


@pytest.fixture
def questions_file(tmp_path: Path) -> Path:
    path = tmp_path / "questions.json"
    path.write_text(
        json.dumps(
            [
                {
                    "id": "q1",
                    "prompt": "Which operation is intermediate?",
                    "choices": ["map", "collect", "count", "reduce"],
                    "correct_answer": "map",
                },
                {
                    "id": "q2",
                    "prompt": "Which operation produces a result?",
                    "choices": ["filter", "map", "collect", "peek"],
                    "correct_answer": "collect",
                },
            ],
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return path


def _roots(template_root: Path, output_root: Path) -> list[str]:
    return [
        "--template-root",
        str(template_root),
        "--output-root",
        str(output_root),
    ]


def test_list_command_includes_quiz(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["list"]) == 0
    assert "quiz" in capsys.readouterr().out


def test_legacy_list_option_includes_quiz(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["--list"]) == 0
    assert "quiz" in capsys.readouterr().out


def test_quiz_command_generates_quiz_readme(
    quiz_template_root: Path,
    questions_file: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    argv = _roots(quiz_template_root, output_root) + [
        "quiz",
        "modern-java",
        "--week",
        "3",
        "--quiz-id",
        "streams-basics",
        "--title",
        "Streams Basics Quiz",
        "--questions-file",
        str(questions_file),
        "--no-manifest",
    ]

    assert cli.main(argv) == 0

    readme = output_root / "modern-java" / "week-03" / "quiz" / "streams-basics" / "README.md"
    output = capsys.readouterr().out
    content = readme.read_text(encoding="utf-8")

    assert readme.exists()
    assert "# 小考：Streams Basics Quiz" in content
    assert "Which operation is intermediate?" in content
    assert "- map" in content
    assert "correct_answer" not in content
    assert f"Quiz 檔案：{readme}" in output
    assert "GenerationResult(" not in output


def test_quiz_command_dry_run_has_no_side_effect(
    quiz_template_root: Path,
    questions_file: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    argv = _roots(quiz_template_root, output_root) + [
        "quiz",
        "modern-java",
        "--week",
        "3",
        "--quiz-id",
        "streams-basics",
        "--title",
        "Streams Basics Quiz",
        "--questions-file",
        str(questions_file),
        "--dry-run",
        "--no-manifest",
    ]

    assert cli.main(argv) == 0
    assert not output_root.exists()
    assert "[DRY-RUN]" in capsys.readouterr().out


def test_quiz_command_rejects_zero_week(
    questions_file: Path,
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli.main(
            [
                "quiz",
                "modern-java",
                "--week",
                "0",
                "--quiz-id",
                "streams-basics",
                "--title",
                "Streams Basics Quiz",
                "--questions-file",
                str(questions_file),
            ]
        )

    assert exc_info.value.code == 2


def test_quiz_command_rejects_path_like_quiz_id(
    quiz_template_root: Path,
    questions_file: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    argv = _roots(quiz_template_root, output_root) + [
        "quiz",
        "modern-java",
        "--week",
        "3",
        "--quiz-id",
        "../escape",
        "--title",
        "Invalid",
        "--questions-file",
        str(questions_file),
    ]

    assert cli.main(argv) == 2
    assert "錯誤：" in capsys.readouterr().err


def test_quiz_command_rejects_missing_questions_file(
    quiz_template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    missing = tmp_path / "missing-questions.json"
    argv = _roots(quiz_template_root, output_root) + [
        "quiz",
        "modern-java",
        "--week",
        "3",
        "--quiz-id",
        "streams-basics",
        "--title",
        "Streams Basics Quiz",
        "--questions-file",
        str(missing),
    ]

    assert cli.main(argv) == 2
    assert "錯誤：" in capsys.readouterr().err


def test_quiz_command_rejects_invalid_questions_json(
    quiz_template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    questions_file = tmp_path / "questions.json"
    questions_file.write_text("{not-json", encoding="utf-8")

    argv = _roots(quiz_template_root, output_root) + [
        "quiz",
        "modern-java",
        "--week",
        "3",
        "--quiz-id",
        "streams-basics",
        "--title",
        "Streams Basics Quiz",
        "--questions-file",
        str(questions_file),
    ]

    assert cli.main(argv) == 2
    assert "錯誤：" in capsys.readouterr().err


def test_quiz_without_force_does_not_overwrite(
    quiz_template_root: Path,
    questions_file: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    readme = output_root / "modern-java" / "week-03" / "quiz" / "streams-basics" / "README.md"
    readme.parent.mkdir(parents=True)
    readme.write_text("existing", encoding="utf-8")

    argv = _roots(quiz_template_root, output_root) + [
        "quiz",
        "modern-java",
        "--week",
        "3",
        "--quiz-id",
        "streams-basics",
        "--title",
        "Streams Basics Quiz",
        "--questions-file",
        str(questions_file),
        "--no-manifest",
    ]

    assert cli.main(argv) == 2
    assert readme.read_text(encoding="utf-8") == "existing"
    assert "不允許覆寫" in capsys.readouterr().err


def test_quiz_with_force_overwrites_existing_artifact(
    quiz_template_root: Path,
    questions_file: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "courses"
    readme = output_root / "modern-java" / "week-03" / "quiz" / "streams-basics" / "README.md"
    readme.parent.mkdir(parents=True)
    readme.write_text("existing", encoding="utf-8")

    argv = _roots(quiz_template_root, output_root) + [
        "quiz",
        "modern-java",
        "--week",
        "3",
        "--quiz-id",
        "streams-basics",
        "--title",
        "Streams Basics Quiz",
        "--questions-file",
        str(questions_file),
        "--force",
        "--no-manifest",
    ]

    assert cli.main(argv) == 0
    assert readme.read_text(encoding="utf-8") != "existing"
