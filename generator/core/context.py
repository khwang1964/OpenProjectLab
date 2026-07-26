from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from generator.core.config import ProjectConfig


@dataclass(slots=True)
class GeneratorContext:
    """保存一次 Generator 執行所需的上下文。"""

    output_dir: Path
    variables: dict[str, Any] = field(default_factory=dict)
    config: ProjectConfig | None = None
    project_root: Path = field(default_factory=Path.cwd)
    dry_run: bool = False
    force: bool = False

    def resolved_output_dir(self) -> Path:
        """回傳正規化後的輸出目錄。"""
        return self.output_dir.expanduser().resolve()
