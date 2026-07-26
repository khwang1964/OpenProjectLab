from pathlib import Path

import yaml

from generator.generators.bootstrap_generator import BootstrapGenerator
from generator.generators.course_generator import CourseGenerator
from generator.generators.week_generator import WeekGenerator


def _templates(root: Path):
    files = {
        "bootstrap/project/README.md.j2": "# {{ project_name }}",
        "bootstrap/project/LICENSE.j2": "{{ license_name }}",
        "bootstrap/project/CONTRIBUTING.md.j2": "Contribute",
        "bootstrap/project/gitignore.j2": ".venv/",
        "bootstrap/project/course.yaml.j2": "name: {{ project_name }}",
        "course/README.md.j2": "# {{ course_name }}",
        "week/README.md.j2": "# Week {{ week }} - {{ title }}",
    }
    for name, content in files.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


def test_generators_accumulate_manifest(tmp_path):
    templates = tmp_path / "templates"
    courses = tmp_path / "courses"
    _templates(templates)
    BootstrapGenerator(templates).generate(
        courses, {"project_slug": "demo", "project_name": "示範課程", "license_name": "CC BY 4.0"}
    )
    project = courses / "demo"
    CourseGenerator(templates).generate(project, {"course_name": "示範課程", "weeks": 16})
    WeekGenerator(templates).generate(
        project, {"course_name": "示範課程", "week": 1, "title": "介紹"}
    )
    data = yaml.safe_load((project / ".opl" / "manifest.yaml").read_text(encoding="utf-8"))
    paths = {item["path"] for item in data["generated"]}
    assert {
        "README.md",
        "LICENSE",
        "CONTRIBUTING.md",
        ".gitignore",
        "course.yaml",
        "week-01/README.md",
    } <= paths
    week = next(item for item in data["generated"] if item["path"] == "week-01/README.md")
    assert week["metadata"] == {"week": 1, "title": "介紹"}


def test_generator_dry_run_does_not_create_manifest(tmp_path):
    templates = tmp_path / "templates"
    _templates(templates)
    project = tmp_path / "course"
    CourseGenerator(templates).generate(project, {"course_name": "Demo"}, dry_run=True)
    assert not (project / ".opl" / "manifest.yaml").exists()


def test_manifest_can_be_disabled(tmp_path):
    templates = tmp_path / "templates"
    _templates(templates)
    project = tmp_path / "course"
    CourseGenerator(templates).generate(project, {"course_name": "Demo"}, record_manifest=False)
    assert (project / "README.md").exists()
    assert not (project / ".opl").exists()
