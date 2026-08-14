from __future__ import annotations


def test_bootstrap_generator_template_contract(
    template_manifest: dict,
) -> None:
    expected = {
        "bootstrap/project/README.md.j2",
        "bootstrap/project/LICENSE.j2",
        "bootstrap/project/CONTRIBUTING.md.j2",
        "bootstrap/project/gitignore.j2",
        "bootstrap/project/course.yaml.j2",
    }
    actual = {
        item["path"] for item in template_manifest["templates"] if item["generator"] == "bootstrap"
    }
    assert actual == expected


def test_core_generator_templates_exist(
    template_manifest: dict,
) -> None:
    expected = {
        "course": {"course/README.md.j2"},
        "week": {"week/README.md.j2"},
        "lab": {"lab/README.md.j2"},
        "assignment": {"assignment/README.md.j2"},
        "quiz": {"quiz/README.md.j2"},
        "website": {"website/page.html.j2"},
    }

    for generator, required_paths in expected.items():
        actual = {
            item["path"]
            for item in template_manifest["templates"]
            if item["generator"] == generator
        }
        assert required_paths <= actual


def test_slide_template_contract(
    template_manifest: dict,
) -> None:
    expected = {
        "slides/title.md.j2",
        "slides/agenda.md.j2",
        "slides/chapter.md.j2",
        "slides/slides.md.j2",
    }
    actual = {
        item["path"] for item in template_manifest["templates"] if item["generator"] == "slides"
    }
    assert actual == expected
