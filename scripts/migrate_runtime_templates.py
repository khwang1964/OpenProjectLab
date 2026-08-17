"""Migrate repository runtime templates into package-owned resources.

Run from the repository root:

    python scripts/migrate_runtime_templates.py

The script copies the complete existing ``templates/`` tree to
``generator/resources/templates/``. After verification, use ``--remove-source``
to remove the legacy repository-level tree so only one canonical runtime source
remains.
"""

from __future__ import annotations

import argparse
import filecmp
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_ROOT / "templates"
DESTINATION = PROJECT_ROOT / "generator" / "resources" / "templates"


def _relative_files(root: Path) -> tuple[Path, ...]:
    return tuple(sorted(path.relative_to(root) for path in root.rglob("*") if path.is_file()))


def _assert_identical(source: Path, destination: Path) -> None:
    source_files = _relative_files(source)
    destination_files = _relative_files(destination)

    if source_files != destination_files:
        raise RuntimeError(
            "Template migration produced a different file inventory. "
            f"source={source_files!r}, destination={destination_files!r}"
        )

    mismatched = [
        relative
        for relative in source_files
        if not filecmp.cmp(
            source / relative,
            destination / relative,
            shallow=False,
        )
    ]
    if mismatched:
        raise RuntimeError(f"Template migration changed file content: {mismatched!r}")


def migrate(*, remove_source: bool = False) -> Path:
    """Copy and verify runtime templates, optionally removing the legacy root."""
    if not SOURCE.is_dir():
        if DESTINATION.is_dir():
            return DESTINATION
        raise RuntimeError(f"Template source does not exist: {SOURCE}")

    DESTINATION.parent.mkdir(parents=True, exist_ok=True)

    if DESTINATION.exists():
        shutil.rmtree(DESTINATION)

    shutil.copytree(SOURCE, DESTINATION)
    _assert_identical(SOURCE, DESTINATION)

    if remove_source:
        shutil.rmtree(SOURCE)

    return DESTINATION


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--remove-source",
        action="store_true",
        help="remove legacy repository-level templates/ after verified migration",
    )
    args = parser.parse_args()

    destination = migrate(remove_source=args.remove_source)
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
