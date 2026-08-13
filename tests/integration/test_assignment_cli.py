import json
from pathlib import Path

import pytest

from generator.cli import main as cli


@pytest.fixture
def assignment_template_root(tmp_path: Path) -> Path:
    root = tmp_path / "templates"
    assignment = root / "assignment"
    assignment.mkdir(parents=True)
    (assignment / "README.md.j2").write_text(
        """# 作業：{{ title }}

> Week {{ week_padded }} · Assignment ID: `{{ assignment_id }}`

{% if objectives is defined and objectives %}
## 學習目標

{% for objective in objectives %}
- {{ objective }}
{% endfor %}

{% endif %}
{% if instructions is defined and instructions %}
## 作業說明

{{ instructions }}

{% endif %}
{% if deliverables is defined and deliverables %}
## 繳交內容

{% for deliverable in deliverables %}
- {{ deliverable }}
{% endfor %}

{% endif %}
{% if resources is defined and resources %}
## 參考資源

{% for resource in resources %}
- {{ resource }}
{% endfor %}

{% endif %}
{% if submission is defined and submission %}
## 繳交方式

{{ submission }}

{% endif %}
""",
        encoding="utf-8",
    )
    return root


@pytest.fixture
def content_file(tmp_path: Path) -> Path:
    path = tmp_path / "assignment.json"
    path.write_text(
        json.dumps(
            {
                "objectives": [
                    "Use stream pipelines.",
                    "Choose terminal operations.",
                ],
                "instructions": "Complete all tasks.",
                "deliverables": [
                    "src/StreamsHomework.java",
                    "README.md",
                ],
                "resources": [
                    "docs/streams.md",
                    "examples/streams.java",
                ],
                "submission": "Submit the requested files.",
            },
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


def test_list_command_includes_assignment(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["list"]) == 0
    assert "assignment" in capsys.readouterr().out


def test_legacy_list_option_includes_assignment(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["--list"]) == 0
    assert "assignment" in capsys.readouterr().out


def test_assignment_command_generates_assignment_readme(
    assignment_template_root: Path,
    content_file: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    argv = _roots(assignment_template_root, output_root) + [
        "assignment",
        "modern-java",
        "--week",
        "4",
        "--assignment-id",
        "streams-homework",
        "--title",
        "Streams Homework",
        "--content-file",
        str(content_file),
        "--no-manifest",
    ]

    assert cli.main(argv) == 0

    readme = (
        output_root / "modern-java" / "week-04" / "assignment" / "streams-homework" / "README.md"
    )
    output = capsys.readouterr().out
    content = readme.read_text(encoding="utf-8")

    assert readme.exists()
    assert "# 作業：Streams Homework" in content
    assert "Use stream pipelines." in content
    assert "Choose terminal operations." in content
    assert "src/StreamsHomework.java" in content
    assert "docs/streams.md" in content
    assert "Submit the requested files." in content
    assert f"作業檔案：{readme}" in output
    assert "GenerationResult(" not in output


def test_assignment_command_preserves_structured_content_order(
    assignment_template_root: Path,
    content_file: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "courses"
    argv = _roots(assignment_template_root, output_root) + [
        "assignment",
        "modern-java",
        "--week",
        "4",
        "--assignment-id",
        "streams-homework",
        "--title",
        "Streams Homework",
        "--content-file",
        str(content_file),
        "--no-manifest",
    ]

    assert cli.main(argv) == 0

    readme = (
        output_root / "modern-java" / "week-04" / "assignment" / "streams-homework" / "README.md"
    )
    content = readme.read_text(encoding="utf-8")

    assert content.index("Use stream pipelines.") < content.index("Choose terminal operations.")
    assert content.index("src/StreamsHomework.java") < content.index(
        "README.md",
        content.index("src/StreamsHomework.java"),
    )
    assert content.index("docs/streams.md") < content.index("examples/streams.java")


def test_assignment_command_dry_run_has_no_side_effect(
    assignment_template_root: Path,
    content_file: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    argv = _roots(assignment_template_root, output_root) + [
        "assignment",
        "modern-java",
        "--week",
        "4",
        "--assignment-id",
        "streams-homework",
        "--title",
        "Streams Homework",
        "--content-file",
        str(content_file),
        "--dry-run",
        "--no-manifest",
    ]

    assert cli.main(argv) == 0
    assert not output_root.exists()
    assert "[DRY-RUN]" in capsys.readouterr().out


def test_assignment_command_rejects_zero_week(
    content_file: Path,
) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli.main(
            [
                "assignment",
                "modern-java",
                "--week",
                "0",
                "--assignment-id",
                "streams-homework",
                "--title",
                "Streams Homework",
                "--content-file",
                str(content_file),
            ]
        )

    assert exc_info.value.code == 2


def test_assignment_command_rejects_path_like_assignment_id(
    assignment_template_root: Path,
    content_file: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    argv = _roots(assignment_template_root, output_root) + [
        "assignment",
        "modern-java",
        "--week",
        "4",
        "--assignment-id",
        "../escape",
        "--title",
        "Invalid",
        "--content-file",
        str(content_file),
    ]

    assert cli.main(argv) == 2
    assert "錯誤：" in capsys.readouterr().err


def test_assignment_command_rejects_missing_content_file(
    assignment_template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    missing = tmp_path / "missing-assignment.json"
    argv = _roots(assignment_template_root, output_root) + [
        "assignment",
        "modern-java",
        "--week",
        "4",
        "--assignment-id",
        "streams-homework",
        "--title",
        "Streams Homework",
        "--content-file",
        str(missing),
    ]

    assert cli.main(argv) == 2
    assert "錯誤：" in capsys.readouterr().err


def test_assignment_command_rejects_invalid_content_json(
    assignment_template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    content_file = tmp_path / "assignment.json"
    content_file.write_text("{not-json", encoding="utf-8")

    argv = _roots(assignment_template_root, output_root) + [
        "assignment",
        "modern-java",
        "--week",
        "4",
        "--assignment-id",
        "streams-homework",
        "--title",
        "Streams Homework",
        "--content-file",
        str(content_file),
    ]

    assert cli.main(argv) == 2
    assert "錯誤：" in capsys.readouterr().err


def test_assignment_command_rejects_non_object_content_json(
    assignment_template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    content_file = tmp_path / "assignment.json"
    content_file.write_text('["not", "an", "object"]', encoding="utf-8")

    argv = _roots(assignment_template_root, output_root) + [
        "assignment",
        "modern-java",
        "--week",
        "4",
        "--assignment-id",
        "streams-homework",
        "--title",
        "Streams Homework",
        "--content-file",
        str(content_file),
    ]

    assert cli.main(argv) == 2
    assert "錯誤：" in capsys.readouterr().err


def test_assignment_without_force_does_not_overwrite(
    assignment_template_root: Path,
    content_file: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    readme = (
        output_root / "modern-java" / "week-04" / "assignment" / "streams-homework" / "README.md"
    )
    readme.parent.mkdir(parents=True)
    readme.write_text("existing", encoding="utf-8")

    argv = _roots(assignment_template_root, output_root) + [
        "assignment",
        "modern-java",
        "--week",
        "4",
        "--assignment-id",
        "streams-homework",
        "--title",
        "Streams Homework",
        "--content-file",
        str(content_file),
        "--no-manifest",
    ]

    assert cli.main(argv) == 2
    assert readme.read_text(encoding="utf-8") == "existing"
    assert "不允許覆寫" in capsys.readouterr().err


def test_assignment_with_force_overwrites_existing_artifact(
    assignment_template_root: Path,
    content_file: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "courses"
    readme = (
        output_root / "modern-java" / "week-04" / "assignment" / "streams-homework" / "README.md"
    )
    readme.parent.mkdir(parents=True)
    readme.write_text("existing", encoding="utf-8")

    argv = _roots(assignment_template_root, output_root) + [
        "assignment",
        "modern-java",
        "--week",
        "4",
        "--assignment-id",
        "streams-homework",
        "--title",
        "Streams Homework",
        "--content-file",
        str(content_file),
        "--force",
        "--no-manifest",
    ]

    assert cli.main(argv) == 0
    assert readme.read_text(encoding="utf-8") != "existing"
