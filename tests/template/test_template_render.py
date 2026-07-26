from __future__ import annotations

import pytest
import yaml


@pytest.mark.parametrize(
    ("template_name", "context", "expected"),
    [
        (
            "bootstrap/project/README.md.j2",
            {
                "project_name": "Modern Java in Action",
                "project_slug": "modern-java",
            },
            "# Modern Java in Action",
        ),
        (
            "bootstrap/project/LICENSE.j2",
            {"project_name": "Modern Java in Action"},
            "Modern Java in Action",
        ),
        (
            "bootstrap/project/CONTRIBUTING.md.j2",
            {"project_name": "Modern Java in Action"},
            "# 貢獻指南",
        ),
        (
            "bootstrap/project/gitignore.j2",
            {},
            "__pycache__/",
        ),
        (
            "bootstrap/project/course.yaml.j2",
            {
                "project_name": "Modern Java in Action",
                "project_slug": "modern-java",
                "weeks": 16,
            },
            'slug: "modern-java"',
        ),
        (
            "course/README.md.j2",
            {
                "course_name": "Modern Java in Action",
                "weeks": 16,
            },
            "# Modern Java in Action",
        ),
        (
            "week/README.md.j2",
            {
                "course_name": "Modern Java in Action",
                "week": 1,
                "week_padded": "01",
                "title": "課程介紹",
            },
            "# Week 01：課程介紹",
        ),
        (
            "lab/README.md.j2",
            {
                "course_name": "Modern Java in Action",
                "week": 1,
                "title": "開發環境",
            },
            "# Lab：開發環境",
        ),
        (
            "assignment/README.md.j2",
            {
                "course_name": "Modern Java in Action",
                "week": 1,
                "title": "Java 基礎",
            },
            "# 作業：Java 基礎",
        ),
        (
            "quiz/README.md.j2",
            {
                "course_name": "Modern Java in Action",
                "week": 1,
                "title": "Week 01 Quiz",
            },
            "# 小考：Week 01 Quiz",
        ),
        (
            "slides/title.md.j2",
            {
                "course_name": "Modern Java in Action",
                "title": "現代 Java 概覽",
            },
            'title: "現代 Java 概覽"',
        ),
        (
            "slides/agenda.md.j2",
            {"agenda": ["課程介紹", "環境設定"]},
            "1. 課程介紹",
        ),
        (
            "slides/chapter.md.j2",
            {"title": "Lambda Expressions"},
            "# Lambda Expressions",
        ),
        (
            "website/index.md.j2",
            {"course_name": "Modern Java in Action"},
            "# Modern Java in Action",
        ),
    ],
)
def test_templates_render_with_reference_context(
    template_environment,
    template_name: str,
    context: dict,
    expected: str,
) -> None:
    rendered = template_environment.get_template(template_name).render(context)
    assert expected in rendered


def test_rendered_course_yaml_is_valid_yaml(
    template_environment,
) -> None:
    rendered = template_environment.get_template("bootstrap/project/course.yaml.j2").render(
        project_name="Modern Java in Action",
        project_slug="modern-java",
        weeks=16,
    )

    data = yaml.safe_load(rendered)
    assert data["schema_version"] == "1.0"
    assert data["course"]["slug"] == "modern-java"
    assert data["course"]["weeks"] == 16
