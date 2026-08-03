"""OpenProjectLab command-line interface."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from generator.cli.upgrade import add_upgrade_parser
from generator.core.config import ProjectConfig
from generator.core.models import (
    GenerateRequest,
    GenerationResult,
    RuntimeOptions,
)
from generator.generators.bootstrap_generator import BootstrapGenerator
from generator.generators.course_generator import CourseGenerator
from generator.generators.week_generator import WeekGenerator

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_CONFIG = PROJECT_ROOT / "config" / "default.yaml"
DEFAULT_TEMPLATE_ROOT = PROJECT_ROOT / "templates"
DEFAULT_OUTPUT_ROOT = PROJECT_ROOT / "courses"


def build_parser() -> argparse.ArgumentParser:
    """建立並回傳 OpenProjectLab CLI argument parser。"""
    parser = argparse.ArgumentParser(
        prog="opl",
        description="OpenProjectLab 開放教材專案產生器",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG,
        metavar="FILE",
        help=f"設定檔路徑（預設：{DEFAULT_CONFIG}）",
    )
    parser.add_argument(
        "--template-root",
        type=Path,
        metavar="DIR",
        help="覆寫模板根目錄",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        metavar="DIR",
        help="覆寫課程輸出根目錄",
    )
    parser.add_argument(
        "--list",
        dest="legacy_list",
        action="store_true",
        help=argparse.SUPPRESS,
    )

    # command 不設 required=True，因為必須保留舊版 `opl --list` 相容性。
    # main() 會在解析後自行驗證是否提供了命令。
    subparsers = parser.add_subparsers(dest="command")
    add_upgrade_parser(subparsers)

    list_parser = subparsers.add_parser("list", help="列出可用產生器")
    list_parser.set_defaults(handler=_handle_list)

    bootstrap = subparsers.add_parser(
        "bootstrap",
        help="建立完整課程專案骨架",
    )
    bootstrap.add_argument("project_slug", help="專案代號，例如 modern-java")
    bootstrap.add_argument("--name", required=True, help="課程或專案名稱")
    bootstrap.add_argument("--language", default="zh-TW", help="教材語言")
    bootstrap.add_argument(
        "--license",
        dest="license_name",
        default="CC BY 4.0",
        help="開放授權名稱",
    )
    bootstrap.add_argument("--copyright-year", help="著作權年份")
    bootstrap.add_argument("--copyright-holder", help="著作權人")
    _add_write_options(bootstrap)
    bootstrap.set_defaults(handler=_handle_bootstrap)

    course = subparsers.add_parser(
        "course",
        help="產生課程 README",
    )
    course.add_argument("project_slug", help="專案代號，例如 modern-java")
    course.add_argument("--name", required=True, help="課程名稱")
    course.add_argument("--language", default="zh-TW", help="教材語言")
    course.add_argument("--weeks", type=_positive_int, default=16, help="課程週數")
    course.add_argument("--textbook", help="主要教材")
    course.add_argument("--instructor", help="授課教師")
    course.add_argument("--description", help="課程簡介")
    course.add_argument(
        "--license",
        dest="license_name",
        default="CC BY 4.0",
        help="開放授權名稱",
    )
    _add_write_options(course)
    course.set_defaults(handler=_handle_course)

    week = subparsers.add_parser(
        "week",
        help="產生每週教材 README",
    )
    week.add_argument("project_slug", help="專案代號，例如 modern-java")
    week.add_argument("--week", type=_positive_int, required=True, help="週次")
    week.add_argument("--title", required=True, help="本週主題")
    week.add_argument("--course-name", help="課程名稱；預設使用專案代號")
    week.add_argument("--language", default="zh-TW", help="教材語言")
    week.add_argument("--textbook-chapter", help="教材章節")
    week.add_argument(
        "--directory-pattern",
        default="week-{week:02d}",
        help="週次目錄格式",
    )
    _add_write_options(week)
    week.set_defaults(handler=_handle_week)

    return parser


def _add_write_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="只驗證並顯示預計輸出，不修改檔案",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="允許覆寫既有檔案",
    )
    parser.add_argument(
        "--no-manifest",
        action="store_true",
        help="不要更新 .opl/manifest.yaml",
    )


def _positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("必須是整數") from exc
    if number <= 0:
        raise argparse.ArgumentTypeError("必須大於 0")
    return number


def _load_config(path: Path) -> ProjectConfig | None:
    if path == DEFAULT_CONFIG and not path.exists():
        return None
    return ProjectConfig.load(path)


def _resolve_roots(args: argparse.Namespace) -> tuple[Path, Path]:
    config = _load_config(args.config)
    config_paths: dict[str, Any] = config.paths if config is not None else {}

    template_value = (
        args.template_root
        or config_paths.get("template_root")
        or config_paths.get("templates")
        or DEFAULT_TEMPLATE_ROOT
    )
    output_value = (
        args.output_root
        or config_paths.get("course_root")
        or config_paths.get("courses")
        or config_paths.get("output_root")
        or DEFAULT_OUTPUT_ROOT
    )

    return (
        _resolve_project_path(Path(template_value)),
        _resolve_project_path(Path(output_value)),
    )


def _resolve_project_path(path: Path) -> Path:
    path = path.expanduser()
    if path.is_absolute():
        return path.resolve()
    return (PROJECT_ROOT / path).resolve()


def _handle_list(args: argparse.Namespace) -> int:
    del args
    rows = (
        (BootstrapGenerator.name, BootstrapGenerator.description),
        (CourseGenerator.name, CourseGenerator.description),
        (WeekGenerator.name, WeekGenerator.description),
    )
    for name, description in rows:
        print(f"{name:<10} {description}")
    return 0


def _handle_bootstrap(args: argparse.Namespace) -> int:
    template_root, output_root = _resolve_roots(args)
    project_root = output_root / args.project_slug
    context: dict[str, Any] = {
        "project_name": args.name,
        "project_slug": args.project_slug,
        "language": args.language,
        "license_name": args.license_name,
    }
    if args.copyright_year:
        context["copyright_year"] = args.copyright_year
    if args.copyright_holder:
        context["copyright_holder"] = args.copyright_holder

    context["record_manifest"] = not args.no_manifest
    result = BootstrapGenerator(template_root).generate(
        GenerateRequest(
            generator_name=BootstrapGenerator.name,
            target=output_root,
            values=context,
            options=RuntimeOptions(
                overwrite=args.force,
                dry_run=args.dry_run,
            ),
        ),
    )
    _print_bootstrap_result(result, project_root)
    return 0


def _handle_course(args: argparse.Namespace) -> int:
    template_root, output_root = _resolve_roots(args)
    project_root = output_root / args.project_slug
    context: dict[str, Any] = {
        "course_name": args.name,
        "language": args.language,
        "weeks": args.weeks,
        "license_name": args.license_name,
    }
    for key in ("textbook", "instructor", "description"):
        value = getattr(args, key)
        if value:
            context[key] = value

    context["record_manifest"] = not args.no_manifest
    result = CourseGenerator(template_root).generate(
        GenerateRequest(
            generator_name=CourseGenerator.name,
            target=project_root,
            values=context,
            options=RuntimeOptions(
                overwrite=args.force,
                dry_run=args.dry_run,
            ),
        ),
    )
    _print_file_result("課程檔案", result)
    return 0


def _handle_week(args: argparse.Namespace) -> int:
    template_root, output_root = _resolve_roots(args)
    project_root = output_root / args.project_slug
    context: dict[str, Any] = {
        "week": args.week,
        "title": args.title,
        "course_name": args.course_name or args.project_slug,
        "language": args.language,
    }
    if args.textbook_chapter:
        context["textbook_chapter"] = args.textbook_chapter
    context["directory_pattern"] = args.directory_pattern
    context["record_manifest"] = not args.no_manifest

    result = WeekGenerator(template_root).generate(
        GenerateRequest(
            generator_name=WeekGenerator.name,
            target=project_root,
            values=context,
            options=RuntimeOptions(
                overwrite=args.force,
                dry_run=args.dry_run,
            ),
        ),
    )
    _print_file_result("週次檔案", result)
    return 0


def _print_bootstrap_result(result: GenerationResult, project_root: Path) -> None:
    prefix = "[DRY-RUN] " if result.dry_run else ""
    print(f"{prefix}專案根目錄：{project_root}")
    print(f"{prefix}檔案：")
    for path in result.affected_paths:
        print(f"  - {path}")


def _print_file_result(label: str, result: GenerationResult) -> None:
    prefix = "[DRY-RUN] " if result.dry_run else ""
    for path in result.affected_paths:
        print(f"{prefix}{label}：{path}")


def main(argv: Sequence[str] | None = None) -> int:
    """執行 OpenProjectLab CLI 並回傳 process exit code。"""
    parser = build_parser()
    args = parser.parse_args(argv)
    args.project_root = PROJECT_ROOT

    handler = getattr(args, "command_handler", None)
    if handler is not None:
        return handler(args)

    if args.legacy_list:
        if args.command is not None:
            parser.error("--list 不可與子命令同時使用")
        return _handle_list(args)

    if args.command is None:
        parser.error("the following arguments are required: command")

    try:
        return int(args.handler(args))
    except (ValueError, RuntimeError, OSError) as exc:
        print(f"錯誤：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
