"""Test the Course Generator and its shared GenerationResult contract."""

from pathlib import Path

import pytest

from generator.core.filesystem import FileSystemError
from generator.core.models import GenerateRequest, GenerationResult, RuntimeOptions
from generator.core.template import TemplateRenderError
from generator.generators.course_generator import CourseGenerator


@pytest.fixture
def template_root(tmp_path: Path) -> Path:
    """Create a minimal Course template pack."""
    root = tmp_path / "templates"
    template = root / "course" / "README.md.j2"
    template.parent.mkdir(parents=True)
    template.write_text(
        "# {{ course_name }}\n\n- 語言：{{ language }}\n- 週數：{{ weeks }}\n",
        encoding="utf-8",
    )
    return root


def valid_context() -> dict[str, object]:
    """Return a valid Course template context."""
    return {
        "course_name": "Modern Java in Action",
        "language": "zh-TW",
        "weeks": 16,
    }


def _request(
    target: Path,
    values: dict[str, object] | None = None,
    *,
    dry_run: bool = False,
    overwrite: bool = True,
    **value_overrides: object,
) -> GenerateRequest:
    """Build an immutable Course generation request for a test case."""
    request_values = dict(values or {})
    request_values.update(value_overrides)
    return GenerateRequest(
        generator_name=CourseGenerator.name,
        target=target,
        values=request_values,
        options=RuntimeOptions(dry_run=dry_run, overwrite=overwrite),
    )


def _generate(
    generator: CourseGenerator,
    target: Path,
    values: dict[str, object] | None = None,
    *,
    dry_run: bool = False,
    overwrite: bool = True,
    **value_overrides: object,
) -> GenerationResult:
    """Generate through the shared request contract."""
    return generator.generate(
        _request(target, values, dry_run=dry_run, overwrite=overwrite, **value_overrides)
    )


def test_course_generator_creates_readme(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "courses" / "modern-java"
    generator = CourseGenerator(template_root)

    result = _generate(generator, output_root, valid_context())

    assert result.affected_paths[0] == output_root / "README.md"
    assert result.affected_paths[0].read_text(encoding="utf-8") == (
        "# Modern Java in Action\n\n- 語言：zh-TW\n- 週數：16\n"
    )


def test_course_generator_supports_unicode(
    template_root: Path,
    tmp_path: Path,
) -> None:
    context = valid_context()
    context["course_name"] = "現代 Java 實戰"
    output_root = tmp_path / "中文課程"

    result = _generate(CourseGenerator(template_root), output_root, context)

    assert "現代 Java 實戰" in result.affected_paths[0].read_text(encoding="utf-8")


def test_course_generator_creates_output_directory(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "nested" / "course"

    _generate(CourseGenerator(template_root), output_root, valid_context())

    assert output_root.is_dir()


def test_course_generator_dry_run(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "not-created"

    result = _generate(
        CourseGenerator(template_root),
        output_root,
        valid_context(),
        dry_run=True,
    )

    assert result.affected_paths[0] == output_root / "README.md"
    assert result.dry_run is True
    assert result.manifest_updated is False
    assert not output_root.exists()


def test_course_generator_dry_run_still_validates_context(
    template_root: Path,
    tmp_path: Path,
) -> None:
    with pytest.raises(TemplateRenderError, match="缺少必要變數"):
        _generate(
            CourseGenerator(template_root),
            tmp_path / "course",
            {"course_name": "Incomplete"},
            dry_run=True,
        )


def test_course_generator_rejects_missing_context(
    template_root: Path,
    tmp_path: Path,
) -> None:
    with pytest.raises(TemplateRenderError, match="缺少必要變數"):
        _generate(
            CourseGenerator(template_root),
            tmp_path / "course",
            {"course_name": "Incomplete"},
        )


def test_course_generator_rejects_missing_template(
    template_root: Path,
    tmp_path: Path,
) -> None:
    with pytest.raises(TemplateRenderError, match="找不到模板"):
        _generate(
            CourseGenerator(template_root),
            tmp_path / "course",
            valid_context(),
            template_name="course/missing.md.j2",
        )


def test_course_generator_does_not_overwrite_when_disabled(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "course"
    output_root.mkdir()
    readme = output_root / "README.md"
    readme.write_text("existing", encoding="utf-8")

    with pytest.raises(FileSystemError, match="不允許覆寫"):
        _generate(
            CourseGenerator(template_root),
            output_root,
            valid_context(),
            overwrite=False,
        )

    assert readme.read_text(encoding="utf-8") == "existing"


def test_course_generator_uses_request_target(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "course"

    generator = CourseGenerator(
        template_root=template_root,
        output_root=output_root,
    )
    result = _generate(generator, output_root, valid_context())

    assert result.affected_paths[0] == output_root / "README.md"


def test_course_generator_supports_template_root_override(
    template_root: Path,
    tmp_path: Path,
) -> None:
    generator = CourseGenerator(template_root=template_root)

    result = _generate(
        generator,
        tmp_path / "course",
        valid_context(),
    )

    assert result.affected_paths[0].exists()


def test_course_generator_requires_template_root(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="template_root"):
        _generate(CourseGenerator(), tmp_path / "course", valid_context())


def test_course_generator_accepts_context_keyword_values(
    template_root: Path,
    tmp_path: Path,
) -> None:
    result = _generate(
        CourseGenerator(template_root),
        tmp_path / "course",
        course_name="Keyword Course",
        language="zh-TW",
        weeks=8,
    )

    assert "# Keyword Course" in result.affected_paths[0].read_text(encoding="utf-8")


def test_course_generator_context_keywords_override_mapping(
    template_root: Path,
    tmp_path: Path,
) -> None:
    context = valid_context()

    result = _generate(
        CourseGenerator(template_root),
        tmp_path / "course",
        context,
        course_name="Overridden",
    )

    assert "# Overridden" in result.affected_paths[0].read_text(encoding="utf-8")


def test_course_generator_custom_output_name(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "course"

    result = _generate(
        CourseGenerator(template_root),
        output_root,
        valid_context(),
        output_name="docs/course.md",
    )

    assert result.affected_paths[0] == output_root / "docs" / "course.md"
    assert result.affected_paths[0].exists()


def test_course_generator_returns_structured_result(
    template_root: Path,
    tmp_path: Path,
) -> None:
    """Course generation should follow the shared result contract."""
    output_root = tmp_path / "course"

    result = _generate(
        CourseGenerator(template_root),
        output_root,
        valid_context(),
    )

    assert type(result) is GenerationResult
    assert result.generator_name == CourseGenerator.name
    assert result.affected_paths == (output_root / "README.md",)
    assert len(result.writes) == 1
    assert result.dry_run is False
    assert result.manifest_updated is True


def test_course_generator_can_disable_manifest_recording(
    template_root: Path,
    tmp_path: Path,
) -> None:
    """Disabling manifest recording should be reflected in the result."""
    result = _generate(
        CourseGenerator(template_root),
        tmp_path / "course",
        valid_context(),
        record_manifest=False,
    )

    assert result.manifest_updated is False


def test_course_generator_run_alias(
    template_root: Path,
    tmp_path: Path,
) -> None:
    result = CourseGenerator(template_root).run(_request(tmp_path / "course", valid_context()))

    assert type(result) is GenerationResult
    assert result.affected_paths[0].exists()
