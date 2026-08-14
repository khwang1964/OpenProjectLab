from pathlib import Path

import yaml

from generator.core.models import GenerateRequest, GenerationResult, RuntimeOptions
from generator.generators.website_generator import WebsiteGenerator


def _templates(root: Path) -> None:
    page = root / "website" / "page.html.j2"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(
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


def _pages() -> tuple[dict[str, object], ...]:
    return (
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
    )


def _request(
    project: Path,
    *,
    dry_run: bool = False,
    overwrite: bool = False,
    record_manifest: bool = True,
) -> GenerateRequest:
    return GenerateRequest(
        generator_name="website",
        target=project,
        values={
            "course_name": "Modern Java",
            "title": "Modern Java in Action",
            "pages": _pages(),
            "record_manifest": record_manifest,
        },
        options=RuntimeOptions(
            dry_run=dry_run,
            overwrite=overwrite,
        ),
    )


def test_website_generator_renders_expected_static_site(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    result = WebsiteGenerator(templates).generate(
        _request(project, record_manifest=False),
    )

    home = project / "site" / "index.html"
    week = project / "site" / "weeks" / "week-01.html"
    home_content = home.read_text(encoding="utf-8")
    week_content = week.read_text(encoding="utf-8")

    assert isinstance(result, GenerationResult)
    assert result.generator_name == "website"
    assert result.dry_run is False
    assert home.exists()
    assert week.exists()
    assert "<!doctype html>" in home_content
    assert "Modern Java in Action" in home_content
    assert "<h2>Home</h2>" in home_content
    assert "Welcome to Modern Java." in home_content
    assert "<h2>Week 01</h2>" in week_content
    assert "Introduction to Modern Java." in week_content


def test_website_generator_preserves_page_and_navigation_order(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    WebsiteGenerator(templates).generate(
        _request(project, record_manifest=False),
    )

    home = (project / "site" / "index.html").read_text(encoding="utf-8")

    home_link = home.index("/index.html")
    week_link = home.index("/weeks/week-01.html")

    assert home_link < week_link
    assert home.index("Home", home_link) < home.index("Week 01", week_link)


def test_website_generator_records_existing_manifest_schema(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    result = WebsiteGenerator(templates).generate(
        _request(project, overwrite=True),
    )

    manifest_path = project / ".opl" / "manifest.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))

    home = next(item for item in data["generated"] if item["path"] == "site/index.html")
    week = next(item for item in data["generated"] if item["path"] == "site/weeks/week-01.html")

    assert result.manifest_updated is True
    assert home["generator"] == "website"
    assert home["metadata"] == {
        "site_title": "Modern Java in Action",
        "page_title": "Home",
    }
    assert week["generator"] == "website"
    assert week["metadata"] == {
        "site_title": "Modern Java in Action",
        "page_title": "Week 01",
    }


def test_website_generator_dry_run_does_not_create_site_or_manifest(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    result = WebsiteGenerator(templates).generate(
        _request(project, dry_run=True),
    )

    assert result.dry_run is True
    assert result.manifest_updated is False
    assert not project.exists()


def test_website_generator_manifest_can_be_disabled(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    WebsiteGenerator(templates).generate(
        _request(project, record_manifest=False),
    )

    assert (project / "site" / "index.html").exists()
    assert (project / "site" / "weeks" / "week-01.html").exists()
    assert not (project / ".opl").exists()


def test_website_generator_force_overwrites_existing_artifacts(
    tmp_path: Path,
) -> None:
    templates = tmp_path / "templates"
    project = tmp_path / "course"
    _templates(templates)

    home = project / "site" / "index.html"
    week = project / "site" / "weeks" / "week-01.html"
    home.parent.mkdir(parents=True)
    week.parent.mkdir(parents=True)
    home.write_text("existing home", encoding="utf-8")
    week.write_text("existing week", encoding="utf-8")

    WebsiteGenerator(templates).generate(
        _request(
            project,
            overwrite=True,
            record_manifest=False,
        ),
    )

    assert home.read_text(encoding="utf-8") != "existing home"
    assert week.read_text(encoding="utf-8") != "existing week"
