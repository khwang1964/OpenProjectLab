from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, StrictUndefined, TemplateNotFound

from generator.core.exceptions import TemplateError


class TemplateEngine:
    def __init__(self, template_root: Path):
        self.template_root = template_root
        self.environment = Environment(
            loader=FileSystemLoader(str(template_root)),
            undefined=StrictUndefined,
            autoescape=False,
            keep_trailing_newline=True,
        )

    def render(self, template_name: str, variables: dict[str, Any]) -> str:
        try:
            return self.environment.get_template(template_name).render(**variables)
        except TemplateNotFound as exc:
            raise TemplateError(f"找不到模板：{template_name}") from exc
        except Exception as exc:
            raise TemplateError(f"模板渲染失敗：{template_name}: {exc}") from exc
