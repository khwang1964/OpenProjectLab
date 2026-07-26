from __future__ import annotations

from pathlib import Path, PurePosixPath


def test_manifest_paths_are_safe_relative_paths(
    template_manifest: dict,
) -> None:
    for item in template_manifest["templates"]:
        raw_path = item["path"]
        path = PurePosixPath(raw_path)

        assert not path.is_absolute()
        assert ".." not in path.parts
        assert "." not in path.parts
        assert "\\" not in raw_path
        assert raw_path == path.as_posix()


def test_template_files_are_utf8(
    template_manifest: dict,
    template_root: Path,
) -> None:
    for item in template_manifest["templates"]:
        path = template_root / item["path"]
        path.read_text(encoding="utf-8")


def test_template_paths_do_not_use_reserved_windows_names(
    template_manifest: dict,
) -> None:
    reserved = {
        "CON",
        "PRN",
        "AUX",
        "NUL",
        *(f"COM{i}" for i in range(1, 10)),
        *(f"LPT{i}" for i in range(1, 10)),
    }

    for item in template_manifest["templates"]:
        for part in PurePosixPath(item["path"]).parts:
            assert Path(part).stem.upper() not in reserved
