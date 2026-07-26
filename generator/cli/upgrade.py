from __future__ import annotations

import argparse
from pathlib import Path

from generator.core.upgrade import UpgradeError, UpgradeManager


def add_upgrade_parser(subparsers) -> argparse.ArgumentParser:
    parser = subparsers.add_parser(
        "upgrade",
        help="預覽或套用 OpenProjectLab 更新包",
    )
    parser.add_argument("package", type=Path, help="更新 ZIP 路徑")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="實際套用；未指定時只顯示計畫",
    )
    parser.add_argument(
        "--allow-conflicts",
        action="store_true",
        help="允許 add/modify/delete 狀態衝突",
    )
    parser.set_defaults(command_handler=handle_upgrade)
    return parser


def handle_upgrade(args: argparse.Namespace) -> int:
    project_root = Path(getattr(args, "project_root", Path.cwd()))
    manager = UpgradeManager(project_root)

    try:
        if not args.apply:
            plan = manager.inspect(args.package)
            print(f"Package：{plan.package} {plan.version}")
            print(f"新增：{len(plan.added)}")
            print(f"修改：{len(plan.modified)}")
            print(f"刪除：{len(plan.deleted)}")
            print(f"不變：{len(plan.unchanged)}")

            if plan.conflicts:
                print("衝突：")
                for item in plan.conflicts:
                    print(f"  - {item}")

            print("尚未變更任何檔案。使用 --apply 套用更新。")
            return 2 if plan.has_conflicts else 0

        result = manager.apply(
            args.package,
            allow_conflicts=args.allow_conflicts,
        )
        print(
            f"已套用 {result.package} {result.version}，共變更 {len(result.changed_paths)} 個路徑。"
        )
        print(f"備份：{result.backup_dir}")
        return 0

    except UpgradeError as exc:
        print(f"升級失敗：{exc}")
        return 1
