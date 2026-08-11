from pathlib import Path

import pytest

from generator.cli import main as cli


@pytest.fixture
def lab_template_root(tmp_path: Path) -> Path:
    root = tmp_path / "templates"
    lab = root / "lab"
    lab.mkdir(parents=True)
    (lab / "README.md.j2").write_text(
        "# {{ title }}\nWeek {{ week }}\n",
        encoding="utf-8",
    )
    return root


def _roots(template_root: Path, output_root: Path) -> list[str]:
    return [
        "--template-root",
        str(template_root),
        "--output-root",
        str(output_root),
    ]


def test_list_command_includes_lab(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["list"]) == 0
    assert "lab" in capsys.readouterr().out


def test_legacy_list_option_includes_lab(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["--list"]) == 0
    assert "lab" in capsys.readouterr().out


def test_lab_command_generates_lab_readme(
    lab_template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    argv = _roots(lab_template_root, output_root) + [
        "lab",
        "modern-java",
        "--week",
        "3",
        "--lab-id",
        "streams-practice",
        "--title",
        "Streams Practice",
        "--no-manifest",
    ]

    assert cli.main(argv) == 0

    readme = output_root / "modern-java" / "week-03" / "lab" / "streams-practice" / "README.md"
    output = capsys.readouterr().out

    assert readme.exists()
    assert "# Streams Practice" in readme.read_text(encoding="utf-8")
    assert "Week 3" in readme.read_text(encoding="utf-8")
    assert f"Lab 檔案：{readme}" in output
    assert "GenerationResult(" not in output


def test_lab_command_dry_run_has_no_side_effect(
    lab_template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    argv = _roots(lab_template_root, output_root) + [
        "lab",
        "modern-java",
        "--week",
        "3",
        "--lab-id",
        "streams-practice",
        "--title",
        "Streams Practice",
        "--dry-run",
        "--no-manifest",
    ]

    assert cli.main(argv) == 0
    assert not output_root.exists()
    assert "[DRY-RUN]" in capsys.readouterr().out


def test_lab_command_rejects_zero_week() -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli.main(
            [
                "lab",
                "modern-java",
                "--week",
                "0",
                "--lab-id",
                "streams-practice",
                "--title",
                "Streams Practice",
            ]
        )

    assert exc_info.value.code == 2


def test_lab_command_rejects_path_like_lab_id(
    lab_template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    argv = _roots(lab_template_root, output_root) + [
        "lab",
        "modern-java",
        "--week",
        "3",
        "--lab-id",
        "../escape",
        "--title",
        "Invalid",
    ]

    assert cli.main(argv) == 2
    assert "錯誤：" in capsys.readouterr().err


def test_lab_without_force_does_not_overwrite(
    lab_template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    readme = output_root / "modern-java" / "week-03" / "lab" / "streams-practice" / "README.md"
    readme.parent.mkdir(parents=True)
    readme.write_text("existing", encoding="utf-8")

    argv = _roots(lab_template_root, output_root) + [
        "lab",
        "modern-java",
        "--week",
        "3",
        "--lab-id",
        "streams-practice",
        "--title",
        "Streams Practice",
        "--no-manifest",
    ]

    assert cli.main(argv) == 2
    assert readme.read_text(encoding="utf-8") == "existing"
    assert "不允許覆寫" in capsys.readouterr().err
