"""Test the Week Generator and its shared GenerationResult contract."""

from pathlib import Path

import pytest

from generator.core.filesystem import FileSystemError
from generator.core.models import GenerateRequest, GenerationResult, RuntimeOptions
from generator.core.template import TemplateRenderError
from generator.generators.week_generator import WeekGenerator


@pytest.fixture
def template_root(tmp_path: Path) -> Path:
    """Create a minimal Week template pack."""
    root = tmp_path / "templates"
    template = root / "week" / "README.md.j2"
    template.parent.mkdir(parents=True)
    template.write_text(
        "# Week {{ week_padded }}：{{ title }}\n\n"
        "- 課程：{{ course_name }}\n"
        "- 語言：{{ language }}\n",
        encoding="utf-8",
    )
    return root


def valid_context() -> dict[str, object]:
    """Return a valid Week template context."""
    return {
        "week": 1,
        "title": "課程介紹與現代 Java 概覽",
        "course_name": "Modern Java in Action",
        "language": "zh-TW",
    }


def _request(
    target: Path,
    values: dict[str, object] | None = None,
    *,
    dry_run: bool = False,
    overwrite: bool = True,
    **value_overrides: object,
) -> GenerateRequest:
    """Build an immutable Week generation request for a test case."""
    request_values = dict(values or {})
    request_values.update(value_overrides)
    return GenerateRequest(
        generator_name=WeekGenerator.name,
        target=target,
        values=request_values,
        options=RuntimeOptions(dry_run=dry_run, overwrite=overwrite),
    )


def _generate(
    generator: WeekGenerator,
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


def test_week_generator_creates_week_readme(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "courses" / "modern-java"

    result = _generate(
        WeekGenerator(template_root),
        output_root,
        valid_context(),
    )

    assert result.affected_paths[0] == output_root / "week-01" / "README.md"
    assert result.affected_paths[0].read_text(encoding="utf-8") == (
        "# Week 01：課程介紹與現代 Java 概覽\n\n- 課程：Modern Java in Action\n- 語言：zh-TW\n"
    )


def test_week_generator_formats_week_number(
    template_root: Path,
    tmp_path: Path,
) -> None:
    context = valid_context()
    context["week"] = 7

    result = _generate(
        WeekGenerator(template_root),
        tmp_path / "course",
        context,
    )

    assert result.affected_paths[0].parent.name == "week-07"
    assert "# Week 07" in result.affected_paths[0].read_text(encoding="utf-8")


def test_week_generator_supports_unicode(
    template_root: Path,
    tmp_path: Path,
) -> None:
    context = valid_context()
    context["title"] = "Lambda 與資料流"

    result = _generate(
        WeekGenerator(template_root),
        tmp_path / "中文課程",
        context,
    )

    assert "Lambda 與資料流" in result.affected_paths[0].read_text(encoding="utf-8")


def test_week_generator_creates_output_directory(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "nested" / "course"

    _generate(WeekGenerator(template_root), output_root, valid_context())

    assert (output_root / "week-01").is_dir()


def test_week_generator_dry_run(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "not-created"

    result = _generate(
        WeekGenerator(template_root),
        output_root,
        valid_context(),
        dry_run=True,
    )

    assert result.affected_paths[0] == output_root / "week-01" / "README.md"
    assert result.dry_run is True
    assert result.manifest_updated is False
    assert not output_root.exists()


def test_week_generator_dry_run_still_validates_context(
    template_root: Path,
    tmp_path: Path,
) -> None:
    with pytest.raises(TemplateRenderError, match="缺少必要變數"):
        _generate(
            WeekGenerator(template_root),
            tmp_path / "course",
            {"week": 1},
            dry_run=True,
        )


@pytest.mark.parametrize("week", [0, -1, -99])
def test_week_generator_rejects_non_positive_week(
    template_root: Path,
    tmp_path: Path,
    week: int,
) -> None:
    context = valid_context()
    context["week"] = week

    with pytest.raises(ValueError, match="大於 0"):
        _generate(WeekGenerator(template_root), tmp_path / "course", context)


@pytest.mark.parametrize("week", [1.5, "1", None, True])
def test_week_generator_rejects_non_integer_week(
    template_root: Path,
    tmp_path: Path,
    week: object,
) -> None:
    context = valid_context()
    context["week"] = week

    with pytest.raises(ValueError, match="必須是整數"):
        _generate(WeekGenerator(template_root), tmp_path / "course", context)


def test_week_generator_rejects_missing_week(
    template_root: Path,
    tmp_path: Path,
) -> None:
    context = valid_context()
    del context["week"]

    with pytest.raises(ValueError, match="必須是整數"):
        _generate(WeekGenerator(template_root), tmp_path / "course", context)


def test_week_generator_rejects_missing_template_variable(
    template_root: Path,
    tmp_path: Path,
) -> None:
    with pytest.raises(TemplateRenderError, match="缺少必要變數"):
        _generate(
            WeekGenerator(template_root),
            tmp_path / "course",
            {"week": 1, "title": "Incomplete"},
        )


def test_week_generator_rejects_missing_template(
    template_root: Path,
    tmp_path: Path,
) -> None:
    with pytest.raises(TemplateRenderError, match="找不到模板"):
        _generate(
            WeekGenerator(template_root),
            tmp_path / "course",
            valid_context(),
            template_name="week/missing.md.j2",
        )


def test_week_generator_does_not_overwrite_when_disabled(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "course"
    week_root = output_root / "week-01"
    week_root.mkdir(parents=True)
    readme = week_root / "README.md"
    readme.write_text("existing", encoding="utf-8")

    with pytest.raises(FileSystemError, match="不允許覆寫"):
        _generate(
            WeekGenerator(template_root),
            output_root,
            valid_context(),
            overwrite=False,
        )

    assert readme.read_text(encoding="utf-8") == "existing"


def test_week_generator_uses_request_target(
    template_root: Path,
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "course"

    generator = WeekGenerator(
        template_root=template_root,
        output_root=output_root,
    )
    result = _generate(generator, output_root, valid_context())

    assert result.affected_paths[0] == output_root / "week-01" / "README.md"


def test_week_generator_supports_template_root_override(
    template_root: Path,
    tmp_path: Path,
) -> None:
    result = _generate(
        WeekGenerator(template_root=template_root),
        tmp_path / "course",
        valid_context(),
    )

    assert result.affected_paths[0].exists()


def test_week_generator_requires_template_root(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="template_root"):
        _generate(WeekGenerator(), tmp_path / "course", valid_context())


def test_week_generator_accepts_context_keyword_values(
    template_root: Path,
    tmp_path: Path,
) -> None:
    result = _generate(
        WeekGenerator(template_root),
        tmp_path / "course",
        week=2,
        title="Lambda",
        course_name="Modern Java",
        language="zh-TW",
    )

    assert result.affected_paths[0].parent.name == "week-02"
    assert "Lambda" in result.affected_paths[0].read_text(encoding="utf-8")


def test_week_generator_context_keywords_override_mapping(
    template_root: Path,
    tmp_path: Path,
) -> None:
    result = _generate(
        WeekGenerator(template_root),
        tmp_path / "course",
        valid_context(),
        week=3,
        title="Streams",
    )

    assert result.affected_paths[0].parent.name == "week-03"
    assert "Streams" in result.affected_paths[0].read_text(encoding="utf-8")


def test_week_generator_custom_directory_name(
    template_root: Path,
    tmp_path: Path,
) -> None:
    result = _generate(
        WeekGenerator(template_root),
        tmp_path / "course",
        valid_context(),
        directory_pattern="lesson-{week:03d}",
    )

    assert result.affected_paths[0].parent.name == "lesson-001"


def test_week_generator_custom_output_name(
    template_root: Path,
    tmp_path: Path,
) -> None:
    result = _generate(
        WeekGenerator(template_root),
        tmp_path / "course",
        valid_context(),
        output_name="docs/week.md",
    )

    assert result.affected_paths[0].name == "week.md"
    assert result.affected_paths[0].parent.name == "docs"
    assert result.affected_paths[0].exists()


@pytest.mark.parametrize(
    "pattern",
    [
        "",
        ".",
        "../week-{week:02d}",
    ],
)
def test_week_generator_rejects_invalid_directory_pattern(
    template_root: Path,
    tmp_path: Path,
    pattern: str,
) -> None:
    with pytest.raises(ValueError):
        _generate(
            WeekGenerator(template_root),
            tmp_path / "course",
            valid_context(),
            directory_pattern=pattern,
        )


def test_week_generator_rejects_absolute_directory_pattern(
    template_root: Path,
    tmp_path: Path,
) -> None:
    absolute = str((tmp_path / "week-{week:02d}").resolve())

    with pytest.raises(ValueError, match="絕對路徑"):
        _generate(
            WeekGenerator(template_root),
            tmp_path / "course",
            valid_context(),
            directory_pattern=absolute,
        )


def test_week_generator_rejects_invalid_format_pattern(
    template_root: Path,
    tmp_path: Path,
) -> None:
    with pytest.raises(ValueError, match="directory_pattern"):
        _generate(
            WeekGenerator(template_root),
            tmp_path / "course",
            valid_context(),
            directory_pattern="week-{missing}",
        )


def test_week_generator_run_alias(
    template_root: Path,
    tmp_path: Path,
) -> None:
    result = WeekGenerator(template_root).run(_request(tmp_path / "course", valid_context()))

    assert type(result) is GenerationResult
    assert result.affected_paths[0].exists()


def test_week_generator_returns_structured_result(
    template_root: Path,
    tmp_path: Path,
) -> None:
    """Week generation should follow the shared result contract."""
    output_root = tmp_path / "course"

    result = _generate(
        WeekGenerator(template_root),
        output_root,
        valid_context(),
    )

    assert type(result) is GenerationResult
    assert result.generator_name == WeekGenerator.name
    assert result.affected_paths == (output_root / "week-01" / "README.md",)
    assert len(result.writes) == 1
    assert result.dry_run is False
    assert result.manifest_updated is True


def test_week_generator_can_disable_manifest_recording(
    template_root: Path,
    tmp_path: Path,
) -> None:
    """Disabling manifest recording should be reflected in the result."""
    result = _generate(
        WeekGenerator(template_root),
        tmp_path / "course",
        valid_context(),
        record_manifest=False,
    )

    assert result.manifest_updated is False
