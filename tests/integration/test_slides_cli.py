import json
from pathlib import Path

import pytest

from generator.cli import main as cli


@pytest.fixture
def slides_template_root(tmp_path: Path) -> Path:
    root = tmp_path / "templates"
    slides = root / "slides"
    slides.mkdir(parents=True)
    (slides / "slides.md.j2").write_text(
        """# {{ title }}
{% for slide in slides %}
---

## {{ slide.title }}
{% for item in slide.content %}
- {{ item }}
{% endfor %}
{% endfor %}
""",
        encoding="utf-8",
    )
    return root


@pytest.fixture
def slides_file(tmp_path: Path) -> Path:
    path = tmp_path / "slides.json"
    path.write_text(
        json.dumps(
            [
                {
                    "title": "Learning Objectives",
                    "content": [
                        "Understand reactive systems.",
                        "Explain asynchronous data flows.",
                    ],
                },
                {
                    "title": "Core Concepts",
                    "content": [
                        "Streams",
                        "Backpressure",
                        "Non-blocking execution",
                    ],
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


def test_list_command_includes_slides(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["list"]) == 0
    assert "slides" in capsys.readouterr().out


def test_legacy_list_option_includes_slides(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["--list"]) == 0
    assert "slides" in capsys.readouterr().out


def test_slides_command_generates_markdown_slide_deck(
    slides_template_root: Path,
    slides_file: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    argv = _roots(slides_template_root, output_root) + [
        "slides",
        "modern-java",
        "--title",
        "Week 01: Reactive Programming",
        "--slides-file",
        str(slides_file),
        "--no-manifest",
    ]

    assert cli.main(argv) == 0

    artifact = output_root / "modern-java" / "slides.md"
    output = capsys.readouterr().out
    content = artifact.read_text(encoding="utf-8")

    assert artifact.exists()
    assert "# Week 01: Reactive Programming" in content
    assert "## Learning Objectives" in content
    assert "Understand reactive systems." in content
    assert "Explain asynchronous data flows." in content
    assert "## Core Concepts" in content
    assert "Streams" in content
    assert "Backpressure" in content
    assert "Non-blocking execution" in content
    assert f"投影片檔案：{artifact}" in output
    assert "GenerationResult(" not in output


def test_slides_command_preserves_slide_and_content_order(
    slides_template_root: Path,
    slides_file: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "courses"
    argv = _roots(slides_template_root, output_root) + [
        "slides",
        "modern-java",
        "--title",
        "Week 01: Reactive Programming",
        "--slides-file",
        str(slides_file),
        "--no-manifest",
    ]

    assert cli.main(argv) == 0

    content = (output_root / "modern-java" / "slides.md").read_text(
        encoding="utf-8",
    )

    assert content.index("## Learning Objectives") < content.index("## Core Concepts")
    assert content.index("Understand reactive systems.") < content.index(
        "Explain asynchronous data flows."
    )
    assert (
        content.index("Streams")
        < content.index("Backpressure")
        < content.index("Non-blocking execution")
    )


def test_slides_command_dry_run_has_no_side_effect(
    slides_template_root: Path,
    slides_file: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    argv = _roots(slides_template_root, output_root) + [
        "slides",
        "modern-java",
        "--title",
        "Week 01: Reactive Programming",
        "--slides-file",
        str(slides_file),
        "--dry-run",
        "--no-manifest",
    ]

    assert cli.main(argv) == 0
    assert not output_root.exists()
    assert "[DRY-RUN]" in capsys.readouterr().out


def test_slides_command_rejects_missing_slides_file(
    slides_template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    missing = tmp_path / "missing-slides.json"
    argv = _roots(slides_template_root, output_root) + [
        "slides",
        "modern-java",
        "--title",
        "Week 01: Reactive Programming",
        "--slides-file",
        str(missing),
    ]

    assert cli.main(argv) == 2
    assert "錯誤：" in capsys.readouterr().err


def test_slides_command_rejects_invalid_slides_json(
    slides_template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    slides_file = tmp_path / "slides.json"
    slides_file.write_text("{not-json", encoding="utf-8")

    argv = _roots(slides_template_root, output_root) + [
        "slides",
        "modern-java",
        "--title",
        "Week 01: Reactive Programming",
        "--slides-file",
        str(slides_file),
    ]

    assert cli.main(argv) == 2
    assert "錯誤：" in capsys.readouterr().err


def test_slides_command_rejects_non_sequence_slides_json(
    slides_template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    slides_file = tmp_path / "slides.json"
    slides_file.write_text(
        '{"title": "not a slide sequence"}',
        encoding="utf-8",
    )

    argv = _roots(slides_template_root, output_root) + [
        "slides",
        "modern-java",
        "--title",
        "Week 01: Reactive Programming",
        "--slides-file",
        str(slides_file),
    ]

    assert cli.main(argv) == 2
    assert "錯誤：" in capsys.readouterr().err


def test_slides_without_force_does_not_overwrite(
    slides_template_root: Path,
    slides_file: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    artifact = output_root / "modern-java" / "slides.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("existing", encoding="utf-8")

    argv = _roots(slides_template_root, output_root) + [
        "slides",
        "modern-java",
        "--title",
        "Week 01: Reactive Programming",
        "--slides-file",
        str(slides_file),
        "--no-manifest",
    ]

    assert cli.main(argv) == 2
    assert artifact.read_text(encoding="utf-8") == "existing"
    assert "不允許覆寫" in capsys.readouterr().err


def test_slides_with_force_overwrites_existing_artifact(
    slides_template_root: Path,
    slides_file: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "courses"
    artifact = output_root / "modern-java" / "slides.md"
    artifact.parent.mkdir(parents=True)
    artifact.write_text("existing", encoding="utf-8")

    argv = _roots(slides_template_root, output_root) + [
        "slides",
        "modern-java",
        "--title",
        "Week 01: Reactive Programming",
        "--slides-file",
        str(slides_file),
        "--force",
        "--no-manifest",
    ]

    assert cli.main(argv) == 0
    assert artifact.read_text(encoding="utf-8") != "existing"
