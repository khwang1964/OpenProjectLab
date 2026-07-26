from __future__ import annotations

from jinja2 import TemplateSyntaxError


def test_all_manifest_templates_exist(
    template_manifest: dict,
    template_root,
) -> None:
    missing = [
        item["path"]
        for item in template_manifest["templates"]
        if not (template_root / item["path"]).is_file()
    ]
    assert missing == []


def test_all_jinja_templates_compile(
    template_manifest: dict,
    template_environment,
) -> None:
    errors: list[str] = []

    for item in template_manifest["templates"]:
        template_name = item["path"]
        if not template_name.endswith(".j2"):
            continue

        try:
            template_environment.get_template(template_name)
        except TemplateSyntaxError as exc:
            errors.append(f"{template_name}:{exc.lineno}: {exc.message}")

    assert errors == []


def test_no_unregistered_jinja_templates(
    template_manifest: dict,
    template_root,
) -> None:
    registered = {
        item["path"] for item in template_manifest["templates"] if item["path"].endswith(".j2")
    }
    discovered = {
        path.relative_to(template_root).as_posix() for path in template_root.rglob("*.j2")
    }
    assert discovered == registered
