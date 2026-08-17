"""Apply the Step 8.4 package-resource CLI resolution change."""

from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CLI = PROJECT_ROOT / "generator" / "cli" / "main.py"

RESOURCE_IMPORT = "from generator.resources import package_template_root"
WEEK_IMPORT = "from generator.generators.week_generator import WeekGenerator"

OLD_DEFAULT = 'DEFAULT_TEMPLATE_ROOT = PROJECT_ROOT / "templates"'
NEW_DEFAULT = "DEFAULT_TEMPLATE_ROOT = package_template_root()"


def main() -> int:
    text = CLI.read_text(encoding="utf-8")

    if RESOURCE_IMPORT not in text:
        if WEEK_IMPORT not in text:
            raise RuntimeError(f"CLI import anchor not found: {WEEK_IMPORT!r}")
        text = text.replace(
            WEEK_IMPORT,
            f"{WEEK_IMPORT}\n{RESOURCE_IMPORT}",
            1,
        )

    if OLD_DEFAULT in text:
        text = text.replace(OLD_DEFAULT, NEW_DEFAULT, 1)
    elif NEW_DEFAULT not in text:
        raise RuntimeError(f"CLI default-template-root anchor not found: {OLD_DEFAULT!r}")

    CLI.write_text(text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
