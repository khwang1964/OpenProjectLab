from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from generator.core.config import ProjectConfig
from generator.core.context import GeneratorContext
from generator.core.registry import GeneratorRegistry
from generator.generators import (
    BootstrapGenerator,
    CourseGenerator,
    WeekGenerator,
)

# generator/main.py 位於：
# F:\OpenProjectLab\generator\main.py
#
# parents[0] -> F:\OpenProjectLab\generator
# parents[1] -> F:\OpenProjectLab
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DEFAULT_CONFIG = PROJECT_ROOT / "config" / "default.yaml"


def build_registry() -> GeneratorRegistry:
    """建立並註冊所有可用的 Generator。"""
    registry = GeneratorRegistry()

    for generator_class in (
        BootstrapGenerator,
        CourseGenerator,
        WeekGenerator,
    ):
        registry.register(
            generator_class.name,
            generator_class,
        )

    return registry


def build_parser() -> argparse.ArgumentParser:
    """建立 OpenProjectLab CLI ArgumentParser。"""
    parser = argparse.ArgumentParser(
        prog="opl",
        description="OpenProjectLab Framework CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        metavar="FILE",
        help="設定檔路徑",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        metavar="{list,bootstrap,course,week}",
    )

    subparsers.add_parser(
        "list",
        help="列出所有可用的 Generator",
    )

    bootstrap_parser = subparsers.add_parser(
        "bootstrap",
        help="建立新的 OpenProjectLab 專案",
    )
    bootstrap_parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="輸出目錄",
    )
    bootstrap_parser.add_argument(
        "--project-name",
        default="OpenProjectLab",
        help="專案名稱",
    )
    bootstrap_parser.add_argument(
        "--version",
        default="0.1.0",
        help="專案版本",
    )

    course_parser = subparsers.add_parser(
        "course",
        help="建立課程骨架",
    )
    course_parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="輸出目錄",
    )
    course_parser.add_argument(
        "--course-id",
        required=True,
        help="課程識別碼",
    )
    course_parser.add_argument(
        "--title",
        required=True,
        help="課程名稱",
    )

    week_parser = subparsers.add_parser(
        "week",
        help="建立每週教材骨架",
    )
    week_parser.add_argument(
        "--output",
        type=Path,
        required=True,
        help="輸出目錄",
    )
    week_parser.add_argument(
        "--week",
        type=int,
        required=True,
        help="週次",
    )
    week_parser.add_argument(
        "--title",
        required=True,
        help="單元名稱",
    )

    for command_parser in (
        bootstrap_parser,
        course_parser,
        week_parser,
    ):
        command_parser.add_argument(
            "--force",
            action="store_true",
            help="允許覆寫既有檔案",
        )
        command_parser.add_argument(
            "--dry-run",
            action="store_true",
            help="只顯示操作，不實際寫入檔案",
        )

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """OpenProjectLab CLI 進入點。"""
    parser = build_parser()
    args = parser.parse_args(argv)

    registry = build_registry()

    if args.command in (None, "list"):
        print("\n".join(registry.names()))
        return 0

    config = ProjectConfig.load(args.config)

    variables = vars(args).copy()

    for key in (
        "config",
        "command",
        "output",
        "force",
        "dry_run",
    ):
        variables.pop(key, None)

    context = GeneratorContext(
        output_dir=args.output,
        variables=variables,
        config=config,
        project_root=PROJECT_ROOT,
        force=args.force,
        dry_run=args.dry_run,
    )

    generator = registry.create(args.command)
    generator.run(context)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
