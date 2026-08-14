import json
from pathlib import Path

import pytest

from generator.cli import main as cli


@pytest.fixture
def website_template_root(tmp_path: Path) -> Path:
    root = tmp_path / "templates"
    website = root / "website"
    website.mkdir(parents=True)
    (website / "page.html.j2").write_text(
        """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{{ page.title }} | {{ site_title }}</title>
</head>
<body>
  <header>
    <h1>{{ site_title }}</h1>
    <nav>
      <ul>
{% for item in navigation %}
        <li><a href="/{{ item.path }}">{{ item.title }}</a></li>
{% endfor %}
      </ul>
    </nav>
  </header>

  <main>
    <h2>{{ page.title }}</h2>
    <div>{{ page.content }}</div>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )
    return root


@pytest.fixture
def pages_file(tmp_path: Path) -> Path:
    path = tmp_path / "pages.json"
    path.write_text(
        json.dumps(
            [
                {
                    "path": "index.html",
                    "title": "Home",
                    "content": "Welcome to Modern Java.",
                },
                {
                    "path": "weeks/week-01.html",
                    "title": "Week 01",
                    "content": "Introduction to Modern Java.",
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


def test_list_command_includes_website(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["list"]) == 0
    assert "website" in capsys.readouterr().out


def test_legacy_list_option_includes_website(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(["--list"]) == 0
    assert "website" in capsys.readouterr().out


def test_website_command_generates_static_site(
    website_template_root: Path,
    pages_file: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    argv = _roots(website_template_root, output_root) + [
        "website",
        "modern-java",
        "--title",
        "Modern Java in Action",
        "--pages-file",
        str(pages_file),
        "--no-manifest",
    ]

    assert cli.main(argv) == 0

    home = output_root / "modern-java" / "site" / "index.html"
    week = output_root / "modern-java" / "site" / "weeks" / "week-01.html"
    output = capsys.readouterr().out
    home_content = home.read_text(encoding="utf-8")
    week_content = week.read_text(encoding="utf-8")

    assert home.exists()
    assert week.exists()
    assert "<!doctype html>" in home_content
    assert "Modern Java in Action" in home_content
    assert "<h2>Home</h2>" in home_content
    assert "Welcome to Modern Java." in home_content
    assert "<h2>Week 01</h2>" in week_content
    assert "Introduction to Modern Java." in week_content
    assert f"網站檔案：{home}" in output
    assert f"網站檔案：{week}" in output
    assert "GenerationResult(" not in output


def test_website_command_preserves_page_and_navigation_order(
    website_template_root: Path,
    pages_file: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "courses"
    argv = _roots(website_template_root, output_root) + [
        "website",
        "modern-java",
        "--title",
        "Modern Java in Action",
        "--pages-file",
        str(pages_file),
        "--no-manifest",
    ]

    assert cli.main(argv) == 0

    home = (output_root / "modern-java" / "site" / "index.html").read_text(encoding="utf-8")

    assert home.index("/index.html") < home.index("/weeks/week-01.html")


def test_website_command_dry_run_has_no_side_effect(
    website_template_root: Path,
    pages_file: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    argv = _roots(website_template_root, output_root) + [
        "website",
        "modern-java",
        "--title",
        "Modern Java in Action",
        "--pages-file",
        str(pages_file),
        "--dry-run",
        "--no-manifest",
    ]

    assert cli.main(argv) == 0
    assert not output_root.exists()
    output = capsys.readouterr().out
    assert "[DRY-RUN]" in output


def test_website_command_rejects_missing_pages_file(
    website_template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    missing = tmp_path / "missing-pages.json"
    argv = _roots(website_template_root, output_root) + [
        "website",
        "modern-java",
        "--title",
        "Modern Java in Action",
        "--pages-file",
        str(missing),
    ]

    assert cli.main(argv) == 2
    assert "錯誤：" in capsys.readouterr().err


def test_website_command_rejects_invalid_pages_json(
    website_template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    pages_file = tmp_path / "pages.json"
    pages_file.write_text("{not-json", encoding="utf-8")

    argv = _roots(website_template_root, output_root) + [
        "website",
        "modern-java",
        "--title",
        "Modern Java in Action",
        "--pages-file",
        str(pages_file),
    ]

    assert cli.main(argv) == 2
    assert "錯誤：" in capsys.readouterr().err


def test_website_command_rejects_non_sequence_pages_json(
    website_template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    pages_file = tmp_path / "pages.json"
    pages_file.write_text(
        '{"path": "index.html", "title": "Home", "content": "No list"}',
        encoding="utf-8",
    )

    argv = _roots(website_template_root, output_root) + [
        "website",
        "modern-java",
        "--title",
        "Modern Java in Action",
        "--pages-file",
        str(pages_file),
    ]

    assert cli.main(argv) == 2
    assert "錯誤：" in capsys.readouterr().err


def test_website_command_rejects_pages_without_index(
    website_template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    pages_file = tmp_path / "pages.json"
    pages_file.write_text(
        json.dumps(
            [
                {
                    "path": "about.html",
                    "title": "About",
                    "content": "About this course.",
                }
            ]
        ),
        encoding="utf-8",
    )

    argv = _roots(website_template_root, output_root) + [
        "website",
        "modern-java",
        "--title",
        "Modern Java in Action",
        "--pages-file",
        str(pages_file),
    ]

    assert cli.main(argv) == 2
    assert "錯誤：" in capsys.readouterr().err


def test_website_without_force_does_not_overwrite(
    website_template_root: Path,
    pages_file: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    output_root = tmp_path / "courses"
    home = output_root / "modern-java" / "site" / "index.html"
    home.parent.mkdir(parents=True)
    home.write_text("existing", encoding="utf-8")

    argv = _roots(website_template_root, output_root) + [
        "website",
        "modern-java",
        "--title",
        "Modern Java in Action",
        "--pages-file",
        str(pages_file),
        "--no-manifest",
    ]

    assert cli.main(argv) == 2
    assert home.read_text(encoding="utf-8") == "existing"
    assert "不允許覆寫" in capsys.readouterr().err


def test_website_with_force_overwrites_existing_artifacts(
    website_template_root: Path,
    pages_file: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "courses"
    home = output_root / "modern-java" / "site" / "index.html"
    week = output_root / "modern-java" / "site" / "weeks" / "week-01.html"
    home.parent.mkdir(parents=True)
    week.parent.mkdir(parents=True)
    home.write_text("existing home", encoding="utf-8")
    week.write_text("existing week", encoding="utf-8")

    argv = _roots(website_template_root, output_root) + [
        "website",
        "modern-java",
        "--title",
        "Modern Java in Action",
        "--pages-file",
        str(pages_file),
        "--force",
        "--no-manifest",
    ]

    assert cli.main(argv) == 0
    assert home.read_text(encoding="utf-8") != "existing home"
    assert week.read_text(encoding="utf-8") != "existing week"
