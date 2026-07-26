"""OpenProjectLab 模板渲染核心。"""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound, UndefinedError
from jinja2 import TemplateError as JinjaTemplateError

from generator.core.filesystem import FileSystem


class TemplateEngineError(RuntimeError):
    """模板載入、驗證或渲染失敗時拋出的統一例外。"""


class TemplatePathError(TemplateEngineError):
    """模板路徑不合法或嘗試離開模板根目錄。"""


class TemplateRenderError(TemplateEngineError):
    """模板內容無法成功渲染。"""


class TemplateRenderer:
    """安全、嚴格且支援 dry-run 的 Jinja2 模板渲染器。"""

    def __init__(
        self,
        template_root: Path,
        *,
        encoding: str = "utf-8",
        autoescape: bool = False,
    ) -> None:
        self._template_root = Path(template_root).expanduser().resolve()
        self._encoding = encoding

        if not self._template_root.exists():
            raise TemplatePathError(f"找不到模板根目錄：{self._template_root}")
        if not self._template_root.is_dir():
            raise TemplatePathError(f"模板根路徑不是目錄：{self._template_root}")

        self._environment = Environment(
            loader=FileSystemLoader(
                str(self._template_root),
                encoding=self._encoding,
                followlinks=False,
            ),
            undefined=StrictUndefined,
            autoescape=autoescape,
            keep_trailing_newline=True,
        )

    @property
    def template_root(self) -> Path:
        """回傳正規化後的模板根目錄。"""
        return self._template_root

    @property
    def encoding(self) -> str:
        """回傳目前使用的文字編碼。"""
        return self._encoding

    def render(
        self,
        template_name: str | Path,
        context: Mapping[str, Any] | None = None,
    ) -> str:
        """載入並渲染模板。"""
        normalized_name = self._normalize_template_name(template_name)
        render_context = dict(context or {})

        try:
            template = self._environment.get_template(normalized_name)
            return template.render(render_context)
        except TemplateNotFound as exc:
            raise TemplateRenderError(f"找不到模板：{normalized_name}") from exc
        except UndefinedError as exc:
            raise TemplateRenderError(f"模板缺少必要變數：{normalized_name}；{exc}") from exc
        except JinjaTemplateError as exc:
            raise TemplateRenderError(f"模板渲染失敗：{normalized_name}；{exc}") from exc

    def render_to_file(
        self,
        template_name: str | Path,
        output_path: Path,
        context: Mapping[str, Any] | None = None,
        *,
        overwrite: bool = True,
        dry_run: bool = False,
    ) -> Path:
        """渲染模板並透過 FileSystem 寫入目的檔案。"""
        output_path = Path(output_path)
        content = self.render(template_name, context)
        return FileSystem.write_text(
            output_path,
            content,
            encoding=self._encoding,
            overwrite=overwrite,
            dry_run=dry_run,
        )

    def template_exists(self, template_name: str | Path) -> bool:
        """判斷合法模板路徑是否存在。"""
        normalized_name = self._normalize_template_name(template_name)
        try:
            self._environment.get_template(normalized_name)
        except TemplateNotFound:
            return False
        except JinjaTemplateError as exc:
            raise TemplateRenderError(f"模板檢查失敗：{normalized_name}；{exc}") from exc
        return True

    def _normalize_template_name(self, template_name: str | Path) -> str:
        raw_path = Path(template_name)
        if raw_path.is_absolute():
            raise TemplatePathError(f"模板路徑不可為絕對路徑：{template_name}")
        if not raw_path.parts or str(raw_path) in {"", "."}:
            raise TemplatePathError("模板路徑不可為空")
        if ".." in raw_path.parts:
            raise TemplatePathError(f"模板路徑不可包含父目錄跳脫：{template_name}")

        candidate = (self._template_root / raw_path).resolve()
        try:
            candidate.relative_to(self._template_root)
        except ValueError as exc:
            raise TemplatePathError(f"模板路徑超出模板根目錄：{template_name}") from exc
        return raw_path.as_posix()


TemplateEngine = TemplateRenderer


def render_template(
    template_root: Path,
    template_name: str | Path,
    context: Mapping[str, Any] | None = None,
    *,
    encoding: str = "utf-8",
) -> str:
    """以函式介面渲染單一模板。"""
    return TemplateRenderer(template_root, encoding=encoding).render(template_name, context)
