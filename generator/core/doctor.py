from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from generator.core.config import ProjectConfig
from generator.core.exceptions import ConfigurationError


@dataclass(frozen=True, slots=True)
class DoctorCheck:
    """表示單一環境診斷項目的結果。"""

    name: str
    ok: bool
    detail: str


def run_doctor(config_path: Path, project_root: Path) -> tuple[DoctorCheck, ...]:
    """執行 OpenProjectLab 環境診斷。"""
    checks: list[DoctorCheck] = []

    try:
        config = ProjectConfig.load(config_path)
        checks.append(DoctorCheck("config", True, str(config_path)))
    except ConfigurationError as exc:
        checks.append(DoctorCheck("config", False, str(exc)))
        return tuple(checks)

    template_root = config.template_root(project_root)
    checks.append(
        DoctorCheck(
            "templates",
            template_root.is_dir(),
            str(template_root),
        )
    )

    docs_root = project_root / "docs"
    checks.append(DoctorCheck("docs", docs_root.is_dir(), str(docs_root)))

    tests_root = project_root / "tests"
    checks.append(DoctorCheck("tests", tests_root.is_dir(), str(tests_root)))

    return tuple(checks)
