from pathlib import Path

import pytest

from generator.cli import main as cli


@pytest.fixture
def template_root(tmp_path: Path) -> Path:
    root = tmp_path / "templates"

    bootstrap = root / "bootstrap" / "project"
    bootstrap.mkdir(parents=True)
    (bootstrap / "README.md.j2").write_text("# {{ project_name }}\n", encoding="utf-8")
    (bootstrap / "LICENSE.j2").write_text("{{ license_name }}\n", encoding="utf-8")
    (bootstrap / "CONTRIBUTING.md.j2").write_text(
        "Contribute {{ project_name }}\n", encoding="utf-8"
    )
    (bootstrap / "gitignore.j2").write_text(".venv/\n", encoding="utf-8")
    (bootstrap / "course.yaml.j2").write_text(
        "name: {{ project_name }}\nslug: {{ project_slug }}\nlanguage: {{ language }}\n",
        encoding="utf-8",
    )

    course = root / "course"
    course.mkdir(parents=True)
    (course / "README.md.j2").write_text(
        "# {{ course_name }}\nWeeks: {{ weeks }}\nLanguage: {{ language }}\n",
        encoding="utf-8",
    )

    week = root / "week"
    week.mkdir(parents=True)
    (week / "README.md.j2").write_text(
        (
            "# Week {{ week_padded }}: {{ title }}\n"
            "Course: {{ course_name }}\n"
            "Language: {{ language }}\n"
        ),
        encoding="utf-8",
    )
    return root


def roots(template_root: Path, output_root: Path) -> list[str]:
    return [
        "--template-root",
        str(template_root),
        "--output-root",
        str(output_root),
    ]


def test_list_command_prints_generators(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["list"]) == 0
    output = capsys.readouterr().out
    assert "bootstrap" in output
    assert "course" in output
    assert "week" in output


def test_bootstrap_command_creates_project(
    template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    argv = roots(template_root, output_root) + [
        "bootstrap",
        "modern-java",
        "--name",
        "Modern Java in Action",
        "--force",
    ]

    assert cli.main(argv) == 0
    project = output_root / "modern-java"
    assert (project / "README.md").exists()
    assert (project / "course.yaml").exists()
    assert (project / "weeks").is_dir()
    assert "專案根目錄" in capsys.readouterr().out


def test_bootstrap_dry_run_has_no_side_effect(
    template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    argv = roots(template_root, output_root) + [
        "bootstrap",
        "modern-java",
        "--name",
        "Modern Java",
        "--dry-run",
    ]

    assert cli.main(argv) == 0
    assert not output_root.exists()
    assert "[DRY-RUN]" in capsys.readouterr().out


def test_course_command_generates_readme(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "courses"
    argv = roots(template_root, output_root) + [
        "course",
        "modern-java",
        "--name",
        "Modern Java in Action",
        "--weeks",
        "16",
        "--force",
    ]

    assert cli.main(argv) == 0
    readme = output_root / "modern-java" / "README.md"
    assert readme.exists()
    assert "Weeks: 16" in readme.read_text(encoding="utf-8")


def test_week_command_generates_week_readme(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "courses"
    argv = roots(template_root, output_root) + [
        "week",
        "modern-java",
        "--week",
        "1",
        "--title",
        "課程介紹",
        "--course-name",
        "Modern Java in Action",
        "--force",
    ]

    assert cli.main(argv) == 0
    readme = output_root / "modern-java" / "week-01" / "README.md"
    assert readme.exists()
    assert "Week 01" in readme.read_text(encoding="utf-8")


def test_week_command_rejects_zero_week() -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli.main(
            [
                "week",
                "modern-java",
                "--week",
                "0",
                "--title",
                "Invalid",
            ]
        )
    assert exc_info.value.code == 2


def test_command_returns_two_for_generator_error(
    template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    argv = roots(template_root, output_root) + [
        "bootstrap",
        "Invalid Slug",
        "--name",
        "Invalid",
    ]

    assert cli.main(argv) == 2
    assert "錯誤：" in capsys.readouterr().err


def test_course_without_force_does_not_overwrite(
    template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    readme = output_root / "modern-java" / "README.md"
    readme.parent.mkdir(parents=True)
    readme.write_text("existing", encoding="utf-8")

    argv = roots(template_root, output_root) + [
        "course",
        "modern-java",
        "--name",
        "Modern Java",
    ]

    assert cli.main(argv) == 2
    assert readme.read_text(encoding="utf-8") == "existing"
    assert "不允許覆寫" in capsys.readouterr().err


def test_legacy_list_option_prints_generators(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["--list"]) == 0
    output = capsys.readouterr().out
    assert "bootstrap" in output
    assert "course" in output
    assert "week" in output


def test_legacy_list_option_rejects_subcommand() -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli.main(["--list", "list"])

    assert exc_info.value.code == 2
