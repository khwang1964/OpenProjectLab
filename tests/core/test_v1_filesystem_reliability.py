"""Harden the OpenProjectLab v1 filesystem reliability boundary."""

from __future__ import annotations

import os
from pathlib import Path

import pytest

from generator.core.filesystem import FileSystemError, remove_file, write_text
from generator.sdk import WritePolicy, WriteStatus


def test_v1_filesystem_dry_run_does_not_create_parent_tree(tmp_path: Path) -> None:
    destination = tmp_path / "missing" / "nested" / "README.md"

    result = write_text(
        destination,
        "planned",
        policy=WritePolicy.OVERWRITE,
        dry_run=True,
    )

    assert result.status is WriteStatus.CREATED
    assert not destination.exists()
    assert not destination.parent.exists()


def test_v1_filesystem_rejects_directory_destination(tmp_path: Path) -> None:
    destination = tmp_path / "README.md"
    destination.mkdir()

    with pytest.raises(FileSystemError):
        write_text(destination, "content", policy=WritePolicy.OVERWRITE)

    assert destination.is_dir()


def test_v1_create_only_failure_preserves_existing_content(tmp_path: Path) -> None:
    destination = tmp_path / "README.md"
    destination.write_text("original", encoding="utf-8")

    with pytest.raises(FileSystemError):
        write_text(destination, "replacement", policy=WritePolicy.CREATE_ONLY)

    assert destination.read_text(encoding="utf-8") == "original"


def test_v1_skip_existing_preserves_existing_content(tmp_path: Path) -> None:
    destination = tmp_path / "README.md"
    destination.write_text("original", encoding="utf-8")

    result = write_text(
        destination,
        "replacement",
        policy=WritePolicy.SKIP_EXISTING,
    )

    assert result.status is WriteStatus.SKIPPED
    assert destination.read_text(encoding="utf-8") == "original"


def test_v1_identical_overwrite_is_unchanged(tmp_path: Path) -> None:
    destination = tmp_path / "README.md"
    destination.write_text("same", encoding="utf-8")

    result = write_text(destination, "same", policy=WritePolicy.OVERWRITE)

    assert result.status is WriteStatus.UNCHANGED
    assert destination.read_text(encoding="utf-8") == "same"


def test_v1_failed_atomic_replace_preserves_existing_content(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "README.md"
    destination.write_text("original", encoding="utf-8")

    def fail_replace(source: os.PathLike[str], target: os.PathLike[str]) -> None:
        del source, target
        raise OSError("simulated replace failure")

    monkeypatch.setattr(os, "replace", fail_replace)

    with pytest.raises(FileSystemError):
        write_text(destination, "replacement", policy=WritePolicy.OVERWRITE)

    assert destination.read_text(encoding="utf-8") == "original"


def test_v1_failed_atomic_replace_cleans_temporary_file(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    destination = tmp_path / "README.md"
    destination.write_text("original", encoding="utf-8")

    def fail_replace(source: os.PathLike[str], target: os.PathLike[str]) -> None:
        del source, target
        raise OSError("simulated replace failure")

    monkeypatch.setattr(os, "replace", fail_replace)

    with pytest.raises(FileSystemError):
        write_text(destination, "replacement", policy=WritePolicy.OVERWRITE)

    leftovers = tuple(
        path
        for path in tmp_path.iterdir()
        if path.name.startswith(".README.md.") and path.suffix == ".tmp"
    )

    assert leftovers == ()


@pytest.mark.parametrize("content", ["", "繁體中文內容\n第二行\n", "emoji: 🧪\n"])
def test_v1_filesystem_supports_deterministic_utf8_content(
    tmp_path: Path,
    content: str,
) -> None:
    destination = tmp_path / "nested" / "content.txt"

    result = write_text(destination, content, policy=WritePolicy.OVERWRITE)

    assert result.status is WriteStatus.CREATED
    assert destination.read_text(encoding="utf-8") == content


def test_v1_remove_file_dry_run_preserves_file(tmp_path: Path) -> None:
    destination = tmp_path / "keep.txt"
    destination.write_text("keep", encoding="utf-8")

    remove_file(destination, dry_run=True)

    assert destination.read_text(encoding="utf-8") == "keep"


def test_v1_remove_missing_file_with_missing_ok_false_uses_filesystem_error(
    tmp_path: Path,
) -> None:
    with pytest.raises(FileSystemError):
        remove_file(tmp_path / "missing.txt", missing_ok=False)
