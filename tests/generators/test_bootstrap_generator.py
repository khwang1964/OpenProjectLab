from pathlib import Path

import pytest

from generator.core.filesystem import FileSystemError
from generator.core.models import GenerationResult
from generator.core.template import TemplateRenderError
from generator.generators.bootstrap_generator import (
    BootstrapGenerator,
    BootstrapResult,
)


@pytest.fixture
def template_root(tmp_path: Path) -> Path:
    root = tmp_path / "templates" / "bootstrap" / "project"
    root.mkdir(parents=True)

    templates = {
        "README.md.j2": "# {{ project_name }}\n",
        "LICENSE.j2": "{{ license_name }}\n",
        "CONTRIBUTING.md.j2": "Contributing to {{ project_name }}\n",
        "gitignore.j2": ".venv/\n",
        "course.yaml.j2": (
            "name: {{ project_name }}\nslug: {{ project_slug }}\nlanguage: {{ language }}\n"
        ),
    }

    for name, content in templates.items():
        (root / name).write_text(content, encoding="utf-8")

    return tmp_path / "templates"


def valid_context() -> dict[str, object]:
    return {
        "project_name": "Modern Java in Action",
        "project_slug": "modern-java",
        "language": "zh-TW",
        "license_name": "CC BY 4.0",
    }


def test_bootstrap_generator_creates_project_structure(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "courses"

    result = BootstrapGenerator(template_root).generate(
        output_root,
        valid_context(),
    )

    assert result.project_root == output_root / "modern-java"
    for directory in ("docs", "assets", "templates", "weeks"):
        assert (result.project_root / directory).is_dir()


def test_bootstrap_generator_generates_all_files(
    template_root: Path,
    tmp_path: Path,
) -> None:
    result = BootstrapGenerator(template_root).generate(
        tmp_path / "courses",
        valid_context(),
    )

    expected = {
        result.project_root / "README.md",
        result.project_root / "LICENSE",
        result.project_root / "CONTRIBUTING.md",
        result.project_root / ".gitignore",
        result.project_root / "course.yaml",
    }

    assert set(result.generated_files) == expected
    assert all(path.exists() for path in expected)


def test_bootstrap_generator_supports_unicode(
    template_root: Path,
    tmp_path: Path,
) -> None:
    context = valid_context()
    context["project_name"] = "現代 Java 實戰"

    result = BootstrapGenerator(template_root).generate(
        tmp_path / "courses",
        context,
    )

    assert "現代 Java 實戰" in (result.project_root / "README.md").read_text(encoding="utf-8")


def test_bootstrap_generator_dry_run_has_no_side_effect(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "courses"

    result = BootstrapGenerator(template_root).generate(
        output_root,
        valid_context(),
        dry_run=True,
    )

    assert result.dry_run is True
    assert result.project_root == output_root / "modern-java"
    assert not output_root.exists()
    assert len(result.generated_files) == 5
    assert len(result.created_directories) == 4


def test_bootstrap_generator_dry_run_still_validates_all_templates(
    template_root: Path,
    tmp_path: Path,
) -> None:
    missing = template_root / "bootstrap" / "project" / "LICENSE.j2"
    missing.unlink()

    with pytest.raises(TemplateRenderError, match="找不到模板"):
        BootstrapGenerator(template_root).generate(
            tmp_path / "courses",
            valid_context(),
            dry_run=True,
        )


def test_bootstrap_generator_rejects_missing_context(
    template_root: Path,
    tmp_path: Path,
) -> None:
    context = valid_context()
    del context["project_name"]

    with pytest.raises(TemplateRenderError, match="缺少必要變數"):
        BootstrapGenerator(template_root).generate(
            tmp_path / "courses",
            context,
        )


@pytest.mark.parametrize(
    "slug",
    [
        "",
        "Modern Java",
        "../modern-java",
        "/course",
        "modern_java",
        "modern/java",
        "modern--java",
        "-modern-java",
        "modern-java-",
    ],
)
def test_bootstrap_generator_rejects_invalid_slug(
    template_root: Path,
    tmp_path: Path,
    slug: str,
) -> None:
    context = valid_context()
    context["project_slug"] = slug

    with pytest.raises(ValueError, match="project_slug"):
        BootstrapGenerator(template_root).generate(
            tmp_path / "courses",
            context,
        )


@pytest.mark.parametrize(
    "slug",
    [
        "modern-java",
        "data-structures",
        "opl-demo-2026",
        "course1",
    ],
)
def test_bootstrap_generator_accepts_valid_slug(
    template_root: Path,
    tmp_path: Path,
    slug: str,
) -> None:
    context = valid_context()
    context["project_slug"] = slug

    result = BootstrapGenerator(template_root).generate(
        tmp_path / "courses",
        context,
        dry_run=True,
    )

    assert result.project_root.name == slug


def test_bootstrap_generator_explicit_slug_overrides_context(
    template_root: Path,
    tmp_path: Path,
) -> None:
    result = BootstrapGenerator(template_root).generate(
        tmp_path / "courses",
        valid_context(),
        project_slug="override-course",
        dry_run=True,
    )

    assert result.project_root.name == "override-course"


def test_bootstrap_generator_missing_template(
    template_root: Path,
    tmp_path: Path,
) -> None:
    (template_root / "bootstrap" / "project" / "README.md.j2").unlink()

    with pytest.raises(TemplateRenderError, match="找不到模板"):
        BootstrapGenerator(template_root).generate(
            tmp_path / "courses",
            valid_context(),
        )


def test_bootstrap_generator_overwrite_false(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "courses"
    project_root = output_root / "modern-java"
    project_root.mkdir(parents=True)
    readme = project_root / "README.md"
    readme.write_text("existing", encoding="utf-8")

    with pytest.raises(FileSystemError, match="不允許覆寫"):
        BootstrapGenerator(template_root).generate(
            output_root,
            valid_context(),
            overwrite=False,
        )

    assert readme.read_text(encoding="utf-8") == "existing"


def test_bootstrap_generator_returns_structured_result(
    template_root: Path,
    tmp_path: Path,
) -> None:
    result = BootstrapGenerator(template_root).generate(
        tmp_path / "courses",
        valid_context(),
        dry_run=True,
    )

    assert isinstance(result, BootstrapResult)
    assert isinstance(result.generated_files, tuple)
    assert isinstance(result.created_directories, tuple)
    assert result.dry_run is True


def test_bootstrap_generator_uses_constructor_output_root(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "courses"
    generator = BootstrapGenerator(
        template_root=template_root,
        output_root=output_root,
    )

    result = generator.generate(context=valid_context(), dry_run=True)

    assert result.project_root == output_root / "modern-java"


def test_bootstrap_generator_supports_template_root_override(
    template_root: Path,
    tmp_path: Path,
) -> None:
    result = BootstrapGenerator().generate(
        tmp_path / "courses",
        valid_context(),
        template_root=template_root,
        dry_run=True,
    )

    assert result.project_root.name == "modern-java"


def test_bootstrap_generator_requires_template_root(
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="template_root"):
        BootstrapGenerator().generate(
            tmp_path / "courses",
            valid_context(),
        )


def test_bootstrap_generator_requires_output_root(
    template_root: Path,
) -> None:
    with pytest.raises(ValueError, match="output_root"):
        BootstrapGenerator(template_root).generate(
            context=valid_context(),
        )


def test_bootstrap_generator_accepts_context_keywords(
    template_root: Path,
    tmp_path: Path,
) -> None:
    result = BootstrapGenerator(template_root).generate(
        tmp_path / "courses",
        project_name="Keyword Project",
        project_slug="keyword-project",
        language="zh-TW",
        license_name="CC BY 4.0",
    )

    assert "# Keyword Project" in (result.project_root / "README.md").read_text(encoding="utf-8")


def test_bootstrap_generator_keyword_context_overrides_mapping(
    template_root: Path,
    tmp_path: Path,
) -> None:
    result = BootstrapGenerator(template_root).generate(
        tmp_path / "courses",
        valid_context(),
        project_name="Overridden Project",
    )

    assert "# Overridden Project" in (result.project_root / "README.md").read_text(encoding="utf-8")


def test_bootstrap_generator_run_alias(
    template_root: Path,
    tmp_path: Path,
) -> None:
    result = BootstrapGenerator(template_root).run(
        tmp_path / "courses",
        valid_context(),
        dry_run=True,
    )

    assert isinstance(result, BootstrapResult)


def test_bootstrap_generator_returns_generation_result(
    template_root: Path,
    tmp_path: Path,
) -> None:
    """Bootstrap generation should use the shared result contract."""
    result = BootstrapGenerator(template_root).generate(
        tmp_path / "courses",
        valid_context(),
    )

    assert isinstance(result, GenerationResult)
    assert result.generator_name == BootstrapGenerator.name
    assert result.dry_run is False


def test_bootstrap_generator_run_returns_generation_result(
    template_root: Path,
    tmp_path: Path,
) -> None:
    """The run alias should preserve the shared result contract."""
    result = BootstrapGenerator(template_root).run(
        tmp_path / "courses",
        valid_context(),
        dry_run=True,
    )

    assert isinstance(result, GenerationResult)
    assert result.generator_name == BootstrapGenerator.name
    assert result.dry_run is True
