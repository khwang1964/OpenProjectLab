"""Test template rendering, path validation, and file-write contracts."""

from pathlib import Path

import pytest

from generator.core.filesystem import FileSystemError
from generator.core.models import WriteStatus
from generator.core.template import (
    TemplateEngine,
    TemplatePathError,
    TemplateRenderer,
    TemplateRenderError,
    render_template,
)


@pytest.fixture
def template_root(tmp_path: Path) -> Path:
    """Create and return a temporary template root directory."""
    root = tmp_path / "templates"
    root.mkdir()
    return root


def write_template(
    root: Path,
    name: str,
    content: str,
) -> Path:
    """Create a template file below the supplied template root."""
    path = root / name
    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    path.write_text(
        content,
        encoding="utf-8",
    )
    return path


def test_renderer_requires_existing_template_root(
    tmp_path: Path,
) -> None:
    """Reject a missing template root directory."""
    with pytest.raises(
        TemplatePathError,
        match="找不到模板根目錄",
    ):
        TemplateRenderer(tmp_path / "missing")


def test_renderer_rejects_file_as_template_root(
    tmp_path: Path,
) -> None:
    """Reject a regular file used as the template root."""
    root = tmp_path / "template.txt"
    root.write_text(
        "content",
        encoding="utf-8",
    )

    with pytest.raises(
        TemplatePathError,
        match="不是目錄",
    ):
        TemplateRenderer(root)


def test_template_root_and_encoding(
    template_root: Path,
) -> None:
    """Expose the normalized template root and default encoding."""
    renderer = TemplateRenderer(template_root)

    assert renderer.template_root == template_root.resolve()
    assert renderer.encoding == "utf-8"


def test_render_template(template_root: Path) -> None:
    """Render a template with multiple context values."""
    write_template(
        template_root,
        "course/README.md.j2",
        "# {{ course_name }}\nLanguage: {{ language }}\n",
    )

    result = TemplateRenderer(template_root).render(
        "course/README.md.j2",
        {
            "course_name": "Modern Java in Action",
            "language": "zh-TW",
        },
    )

    assert result == "# Modern Java in Action\nLanguage: zh-TW\n"


def test_render_unicode_template(template_root: Path) -> None:
    """Render a template containing Unicode text."""
    write_template(
        template_root,
        "week.md.j2",
        "第 {{ week }} 週: {{ topic }}\n",
    )

    result = TemplateRenderer(template_root).render(
        "week.md.j2",
        {
            "week": 1,
            "topic": "現代 Java 程式設計",
        },
    )

    assert result == "第 1 週: 現代 Java 程式設計\n"


def test_render_accepts_path_name(
    template_root: Path,
) -> None:
    """Accept a Path object as the template name."""
    write_template(
        template_root,
        "nested/item.txt.j2",
        "{{ value }}",
    )

    result = TemplateRenderer(template_root).render(
        Path("nested") / "item.txt.j2",
        {"value": "OK"},
    )

    assert result == "OK"


def test_render_uses_empty_context(
    template_root: Path,
) -> None:
    """Render a static template without an explicit context."""
    write_template(
        template_root,
        "static.txt",
        "static content",
    )

    result = TemplateRenderer(template_root).render("static.txt")

    assert result == "static content"


def test_render_rejects_missing_template(
    template_root: Path,
) -> None:
    """Reject a template that does not exist."""
    with pytest.raises(
        TemplateRenderError,
        match="找不到模板",
    ):
        TemplateRenderer(template_root).render("missing.md.j2")


def test_render_rejects_missing_variable(
    template_root: Path,
) -> None:
    """Reject rendering when a required variable is missing."""
    write_template(
        template_root,
        "required.txt.j2",
        "{{ required_value }}",
    )

    with pytest.raises(
        TemplateRenderError,
        match="缺少必要變數",
    ):
        TemplateRenderer(template_root).render(
            "required.txt.j2",
            {},
        )


def test_render_rejects_syntax_error(
    template_root: Path,
) -> None:
    """Reject a template containing invalid syntax."""
    write_template(
        template_root,
        "invalid.txt.j2",
        "{% if enabled %}",
    )

    with pytest.raises(
        TemplateRenderError,
        match="模板渲染失敗",
    ):
        TemplateRenderer(template_root).render(
            "invalid.txt.j2",
            {"enabled": True},
        )


def test_render_does_not_modify_context(
    template_root: Path,
) -> None:
    """Preserve the caller-provided context mapping."""
    write_template(
        template_root,
        "value.txt.j2",
        "{{ nested.value }}",
    )
    context = {
        "nested": {
            "value": "original",
        },
    }

    TemplateRenderer(template_root).render(
        "value.txt.j2",
        context,
    )

    assert context == {
        "nested": {
            "value": "original",
        },
    }


def test_reject_absolute_template_path(
    template_root: Path,
) -> None:
    """Reject an absolute template path."""
    with pytest.raises(
        TemplatePathError,
        match="絕對路徑",
    ):
        TemplateRenderer(template_root).render(template_root / "README.md.j2")


@pytest.mark.parametrize(
    "name",
    [
        "../secret.txt",
        "course/../../secret.txt",
    ],
)
def test_reject_parent_path_traversal(
    template_root: Path,
    name: str,
) -> None:
    """Reject template paths that escape through a parent directory."""
    with pytest.raises(
        TemplatePathError,
        match="父目錄跳脫",
    ):
        TemplateRenderer(template_root).render(name)


@pytest.mark.parametrize(
    "name",
    [
        "",
        ".",
    ],
)
def test_reject_empty_template_path(
    template_root: Path,
    name: str,
) -> None:
    """Reject empty or current-directory template paths."""
    with pytest.raises(
        TemplatePathError,
        match="不可為空",
    ):
        TemplateRenderer(template_root).render(name)


def test_render_to_file(
    template_root: Path,
    tmp_path: Path,
) -> None:
    """Render a template to a file and return its write result."""
    write_template(
        template_root,
        "README.md.j2",
        "# {{ title }}\n",
    )
    output = tmp_path / "output" / "README.md"

    result = TemplateRenderer(template_root).render_to_file(
        "README.md.j2",
        output,
        {"title": "OpenProjectLab"},
    )

    assert result.path == output
    assert result.status is WriteStatus.CREATED
    assert (
        output.read_text(
            encoding="utf-8",
        )
        == "# OpenProjectLab\n"
    )


def test_render_to_file_can_reject_overwrite(
    template_root: Path,
    tmp_path: Path,
) -> None:
    """Reject replacement of an existing file when overwrite is disabled."""
    write_template(
        template_root,
        "output.txt.j2",
        "{{ value }}",
    )
    output = tmp_path / "output.txt"
    output.write_text(
        "existing",
        encoding="utf-8",
    )

    with pytest.raises(
        FileSystemError,
        match="不允許覆寫",
    ):
        TemplateRenderer(template_root).render_to_file(
            "output.txt.j2",
            output,
            {"value": "replacement"},
            overwrite=False,
        )

    assert output.read_text(encoding="utf-8") == "existing"


def test_render_to_file_dry_run_has_no_side_effect(
    template_root: Path,
    tmp_path: Path,
) -> None:
    """Report creation without writing a file during a dry run."""
    write_template(
        template_root,
        "README.md.j2",
        "# {{ title }}\n",
    )
    output = tmp_path / "not-created" / "README.md"

    result = TemplateRenderer(template_root).render_to_file(
        "README.md.j2",
        output,
        {"title": "Dry Run"},
        dry_run=True,
    )

    assert result.path == output
    assert result.status is WriteStatus.CREATED
    assert not output.exists()
    assert not output.parent.exists()


def test_dry_run_still_validates_context(
    template_root: Path,
    tmp_path: Path,
) -> None:
    """Validate required variables even when dry-run mode is enabled."""
    write_template(
        template_root,
        "required.txt.j2",
        "{{ required }}",
    )

    with pytest.raises(
        TemplateRenderError,
        match="缺少必要變數",
    ):
        TemplateRenderer(template_root).render_to_file(
            "required.txt.j2",
            tmp_path / "output.txt",
            {},
            dry_run=True,
        )


def test_template_exists(template_root: Path) -> None:
    """Report whether a template exists below the template root."""
    write_template(
        template_root,
        "exists.txt",
        "content",
    )
    renderer = TemplateRenderer(template_root)

    assert renderer.template_exists("exists.txt") is True
    assert renderer.template_exists("missing.txt") is False


def test_template_engine_alias(
    template_root: Path,
) -> None:
    """Expose TemplateEngine as an alias of TemplateRenderer."""
    assert template_root.is_dir()
    assert TemplateEngine is TemplateRenderer


def test_render_template_function(
    template_root: Path,
) -> None:
    """Render a template through the module-level helper."""
    write_template(
        template_root,
        "function.txt.j2",
        "{{ value }}",
    )

    result = render_template(
        template_root,
        "function.txt.j2",
        {"value": "function API"},
    )

    assert result == "function API"
