from pathlib import Path

import pytest

from generator.core.filesystem import (
    FileSystem,
    FileSystemError,
    copy_file,
    ensure_directory,
    read_text,
    remove_file,
    write_text,
)


def test_ensure_directory_creates_nested_directory(tmp_path: Path) -> None:
    target = tmp_path / "courses" / "modern-java" / "week-01"

    result = ensure_directory(target)

    assert result == target
    assert target.is_dir()


def test_ensure_directory_accepts_existing_directory(tmp_path: Path) -> None:
    target = tmp_path / "existing"
    target.mkdir()

    result = ensure_directory(target)

    assert result == target
    assert target.is_dir()


def test_ensure_directory_rejects_existing_file(tmp_path: Path) -> None:
    target = tmp_path / "not-a-directory"
    target.write_text("content", encoding="utf-8")

    with pytest.raises(FileSystemError, match="不是目錄"):
        ensure_directory(target)


def test_write_text_creates_parent_directories(tmp_path: Path) -> None:
    target = tmp_path / "generated" / "docs" / "README.md"

    result = write_text(target, "# OpenProjectLab\n")

    assert result == target
    assert target.read_text(encoding="utf-8") == "# OpenProjectLab\n"


def test_write_text_supports_unicode(tmp_path: Path) -> None:
    target = tmp_path / "課程說明.md"

    write_text(target, "第一週：函數式程式設計\n")

    assert read_text(target) == "第一週：函數式程式設計\n"


def test_write_text_overwrites_existing_file_by_default(tmp_path: Path) -> None:
    target = tmp_path / "output.txt"
    target.write_text("old", encoding="utf-8")

    write_text(target, "new")

    assert target.read_text(encoding="utf-8") == "new"


def test_write_text_can_reject_overwrite(tmp_path: Path) -> None:
    target = tmp_path / "output.txt"
    target.write_text("old", encoding="utf-8")

    with pytest.raises(FileSystemError, match="不允許覆寫"):
        write_text(target, "new", overwrite=False)

    assert target.read_text(encoding="utf-8") == "old"


def test_write_text_rejects_directory_target(tmp_path: Path) -> None:
    target = tmp_path / "directory"
    target.mkdir()

    with pytest.raises(FileSystemError, match="是目錄"):
        write_text(target, "content")


def test_read_text_rejects_missing_file(tmp_path: Path) -> None:
    target = tmp_path / "missing.txt"

    with pytest.raises(FileSystemError, match="找不到檔案"):
        read_text(target)


def test_read_text_rejects_directory(tmp_path: Path) -> None:
    target = tmp_path / "directory"
    target.mkdir()

    with pytest.raises(FileSystemError, match="不是檔案"):
        read_text(target)


def test_copy_file_creates_parent_directory(tmp_path: Path) -> None:
    source = tmp_path / "template.md"
    destination = tmp_path / "course" / "week-01" / "README.md"
    source.write_text("template", encoding="utf-8")

    result = copy_file(source, destination)

    assert result == destination
    assert destination.read_text(encoding="utf-8") == "template"


def test_copy_file_can_reject_overwrite(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    destination = tmp_path / "destination.txt"
    source.write_text("source", encoding="utf-8")
    destination.write_text("destination", encoding="utf-8")

    with pytest.raises(FileSystemError, match="不允許覆寫"):
        copy_file(source, destination, overwrite=False)

    assert destination.read_text(encoding="utf-8") == "destination"


def test_copy_file_rejects_missing_source(tmp_path: Path) -> None:
    source = tmp_path / "missing.txt"
    destination = tmp_path / "destination.txt"

    with pytest.raises(FileSystemError, match="找不到來源檔案"):
        copy_file(source, destination)


def test_remove_file_deletes_existing_file(tmp_path: Path) -> None:
    target = tmp_path / "temporary.txt"
    target.write_text("temporary", encoding="utf-8")

    remove_file(target)

    assert not target.exists()


def test_remove_file_ignores_missing_file_by_default(tmp_path: Path) -> None:
    remove_file(tmp_path / "missing.txt")


def test_remove_file_can_reject_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileSystemError, match="找不到要刪除的檔案"):
        remove_file(tmp_path / "missing.txt", missing_ok=False)


def test_remove_file_rejects_directory(tmp_path: Path) -> None:
    target = tmp_path / "directory"
    target.mkdir()

    with pytest.raises(FileSystemError, match="拒絕"):
        remove_file(target)


def test_filesystem_class_is_importable() -> None:
    assert FileSystem is not None


def test_filesystem_class_ensure_dir_compatibility(tmp_path: Path) -> None:
    target = tmp_path / "legacy" / "directory"

    result = FileSystem.ensure_dir(target)

    assert result == target
    assert target.is_dir()


def test_filesystem_class_mkdir_compatibility(tmp_path: Path) -> None:
    target = tmp_path / "legacy-mkdir"

    result = FileSystem.mkdir(target)

    assert result == target
    assert target.is_dir()


def test_filesystem_class_write_and_read_text(tmp_path: Path) -> None:
    target = tmp_path / "legacy" / "README.md"

    result = FileSystem.write_text(target, "OPL 相容性測試\n")

    assert result == target
    assert FileSystem.read_text(target) == "OPL 相容性測試\n"


def test_filesystem_class_copy_and_remove_file(tmp_path: Path) -> None:
    source = tmp_path / "source.txt"
    destination = tmp_path / "nested" / "destination.txt"
    source.write_text("content", encoding="utf-8")

    result = FileSystem.copy_file(source, destination)

    assert result == destination
    assert destination.read_text(encoding="utf-8") == "content"

    FileSystem.remove_file(destination)

    assert not destination.exists()


def test_ensure_directory_dry_run_does_not_create_directory(
    tmp_path: Path,
) -> None:
    target = tmp_path / "dry-run-directory"

    result = FileSystem.ensure_directory(target, dry_run=True)

    assert result == target
    assert not target.exists()


def test_write_text_dry_run_does_not_create_file(tmp_path: Path) -> None:
    target = tmp_path / "dry-run" / "output.txt"

    result = FileSystem.write_text(target, "content", dry_run=True)

    assert result == target
    assert not target.exists()
    assert not target.parent.exists()


def test_copy_file_dry_run_does_not_require_source(
    tmp_path: Path,
) -> None:
    source = tmp_path / "missing-source.txt"
    destination = tmp_path / "dry-run" / "destination.txt"

    result = FileSystem.copy_file(source, destination, dry_run=True)

    assert result == destination
    assert not destination.exists()


def test_remove_file_dry_run_preserves_file(tmp_path: Path) -> None:
    target = tmp_path / "preserved.txt"
    target.write_text("content", encoding="utf-8")

    FileSystem.remove_file(target, dry_run=True)

    assert target.exists()
