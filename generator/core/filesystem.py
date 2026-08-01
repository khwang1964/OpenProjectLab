"""Provide filesystem operations for OpenProjectLab generators.

This module centralizes directory creation, text-file operations, copying,
removal, atomic writes, dry-run behavior, and compatibility helpers.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path

from generator.core.models import (
    WritePolicy,
    WriteResult,
    WriteStatus,
)


class FileSystemError(RuntimeError):
    """Represent a failure while performing a filesystem operation."""


def ensure_directory(
    path: Path,
    *,
    dry_run: bool = False,
) -> Path:
    """Ensure that a directory exists and return its normalized path.

    Args:
        path: Directory to create or verify.
        dry_run: Return the path without creating the directory.

    Returns:
        The normalized directory path.

    Raises:
        FileSystemError: If the path is not a directory or creation fails.
    """
    normalized_path = Path(path)

    if normalized_path.exists() and not normalized_path.is_dir():
        raise FileSystemError(f"路徑已存在但不是目錄: {normalized_path}")

    if dry_run:
        return normalized_path

    try:
        normalized_path.mkdir(
            parents=True,
            exist_ok=True,
        )
    except OSError as exc:
        raise FileSystemError(f"無法建立目錄: {normalized_path}") from exc

    return normalized_path


def read_text(
    path: Path,
    *,
    encoding: str = "utf-8",
) -> str:
    """Read and return text from a file.

    Args:
        path: File to read.
        encoding: Text encoding used to read the file.

    Returns:
        The file content.

    Raises:
        FileSystemError: If the path is missing, invalid, or unreadable.
    """
    normalized_path = Path(path)

    if not normalized_path.exists():
        raise FileSystemError(f"找不到檔案: {normalized_path}")

    if not normalized_path.is_file():
        raise FileSystemError(f"路徑不是檔案: {normalized_path}")

    try:
        return normalized_path.read_text(encoding=encoding)
    except (OSError, UnicodeError) as exc:
        raise FileSystemError(f"無法讀取檔案: {normalized_path}") from exc


def write_text(
    path: Path,
    content: str,
    *,
    encoding: str = "utf-8",
    policy: WritePolicy | None = None,
    overwrite: bool | None = None,
    dry_run: bool = False,
) -> WriteResult:
    """Write text atomically and return the operation result.

    The ``overwrite`` argument is retained as a compatibility option.
    New callers should use ``policy``.

    Args:
        path: Destination file.
        content: Text content to write.
        encoding: Text encoding used for the file.
        policy: Policy used when the destination already exists.
        overwrite: Legacy overwrite option.
        dry_run: Calculate the result without modifying the filesystem.

    Returns:
        The result of the planned or completed write operation.

    Raises:
        FileSystemError: If arguments conflict or the write fails.
    """
    normalized_path = Path(path)
    effective_policy = _resolve_write_policy(
        policy=policy,
        overwrite=overwrite,
    )

    if normalized_path.exists() and normalized_path.is_dir():
        raise FileSystemError(f"目標路徑是目錄, 無法寫入檔案: {normalized_path}")

    existing_content = _read_existing_content(
        normalized_path,
        encoding=encoding,
    )

    status = _determine_write_status(
        path=normalized_path,
        content=content,
        existing_content=existing_content,
        policy=effective_policy,
    )

    result = WriteResult(
        path=normalized_path,
        status=status,
    )

    if dry_run or status in {
        WriteStatus.SKIPPED,
        WriteStatus.UNCHANGED,
    }:
        return result

    ensure_directory(normalized_path.parent)

    _atomic_write_text(
        normalized_path,
        content,
        encoding=encoding,
    )

    return result


def copy_file(
    source: Path,
    destination: Path,
    *,
    overwrite: bool = True,
    dry_run: bool = False,
) -> Path:
    """Copy one file and preserve basic filesystem metadata.

    Args:
        source: Source file.
        destination: Destination file.
        overwrite: Whether an existing destination may be replaced.
        dry_run: Return the destination without copying the file.

    Returns:
        The normalized destination path.

    Raises:
        FileSystemError: If validation or copying fails.
    """
    normalized_source = Path(source)
    normalized_destination = Path(destination)

    if dry_run:
        return normalized_destination

    if not normalized_source.exists():
        raise FileSystemError(f"找不到來源檔案: {normalized_source}")

    if not normalized_source.is_file():
        raise FileSystemError(f"來源路徑不是檔案: {normalized_source}")

    if normalized_destination.exists() and normalized_destination.is_dir():
        raise FileSystemError(f"目的路徑是目錄: {normalized_destination}")

    if normalized_destination.exists() and not overwrite:
        raise FileSystemError(f"目的檔案已存在且不允許覆寫: {normalized_destination}")

    ensure_directory(normalized_destination.parent)

    try:
        shutil.copy2(
            normalized_source,
            normalized_destination,
        )
    except OSError as exc:
        raise FileSystemError(
            f"無法複製檔案: {normalized_source} -> {normalized_destination}"
        ) from exc

    return normalized_destination


def remove_file(
    path: Path,
    *,
    missing_ok: bool = True,
    dry_run: bool = False,
) -> None:
    """Remove one file.

    Args:
        path: File to remove.
        missing_ok: Ignore a missing file when true.
        dry_run: Validate without removing the file.

    Raises:
        FileSystemError: If validation or removal fails.
    """
    normalized_path = Path(path)

    if normalized_path.exists() and normalized_path.is_dir():
        raise FileSystemError(f"路徑是目錄, 拒絕以 remove_file 刪除: {normalized_path}")

    if dry_run:
        return

    try:
        normalized_path.unlink(missing_ok=missing_ok)
    except FileNotFoundError as exc:
        raise FileSystemError(f"找不到要刪除的檔案: {normalized_path}") from exc
    except OSError as exc:
        raise FileSystemError(f"無法刪除檔案: {normalized_path}") from exc


def _resolve_write_policy(
    *,
    policy: WritePolicy | None,
    overwrite: bool | None,
) -> WritePolicy:
    """Resolve modern and legacy write-policy arguments."""
    if policy is not None and overwrite is not None:
        legacy_policy = WritePolicy.OVERWRITE if overwrite else WritePolicy.CREATE_ONLY

        if policy is not legacy_policy:
            raise FileSystemError("policy 與 overwrite 參數互相衝突")

        return policy

    if policy is not None:
        return policy

    if overwrite is None or overwrite:
        return WritePolicy.OVERWRITE

    return WritePolicy.CREATE_ONLY


def _read_existing_content(
    path: Path,
    *,
    encoding: str,
) -> str | None:
    """Return existing text or None when the path does not exist."""
    if not path.exists():
        return None

    try:
        return path.read_text(encoding=encoding)
    except (OSError, UnicodeError) as exc:
        raise FileSystemError(f"無法讀取既有檔案: {path}") from exc


def _determine_write_status(
    *,
    path: Path,
    content: str,
    existing_content: str | None,
    policy: WritePolicy,
) -> WriteStatus:
    """Determine the result status before writing a file."""
    if existing_content is None:
        return WriteStatus.CREATED

    if policy is WritePolicy.SKIP_EXISTING:
        return WriteStatus.SKIPPED

    if policy is WritePolicy.CREATE_ONLY:
        raise FileSystemError(f"檔案已存在且不允許覆寫: {path}")

    if existing_content == content:
        return WriteStatus.UNCHANGED

    return WriteStatus.UPDATED


def _atomic_write_text(
    path: Path,
    content: str,
    *,
    encoding: str,
) -> None:
    """Write text through a temporary file and atomic replacement."""
    temporary_path: Path | None = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding=encoding,
            newline="",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_file.write(content)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
            temporary_path = Path(temporary_file.name)

        os.replace(temporary_path, path)
    except (OSError, UnicodeError) as exc:
        if temporary_path is not None:
            try:
                temporary_path.unlink(missing_ok=True)
            except OSError:
                pass

        raise FileSystemError(f"無法寫入檔案: {path}") from exc


class FileSystem:
    """Provide a stateless compatibility interface for generators."""

    @staticmethod
    def ensure_directory(
        path: Path,
        *,
        dry_run: bool = False,
    ) -> Path:
        """Ensure that a directory exists."""
        return ensure_directory(
            path,
            dry_run=dry_run,
        )

    @staticmethod
    def ensure_dir(
        path: Path,
        *,
        dry_run: bool = False,
    ) -> Path:
        """Provide a compatibility alias for ensure_directory."""
        return ensure_directory(
            path,
            dry_run=dry_run,
        )

    @staticmethod
    def mkdir(
        path: Path,
        *,
        dry_run: bool = False,
    ) -> Path:
        """Provide a short compatibility alias for ensure_directory."""
        return ensure_directory(
            path,
            dry_run=dry_run,
        )

    @staticmethod
    def read_text(
        path: Path,
        *,
        encoding: str = "utf-8",
    ) -> str:
        """Read text from a file."""
        return read_text(
            path,
            encoding=encoding,
        )

    @staticmethod
    def write_text(
        path: Path,
        content: str,
        *,
        encoding: str = "utf-8",
        policy: WritePolicy | None = None,
        overwrite: bool | None = None,
        dry_run: bool = False,
    ) -> WriteResult:
        """Write text and return its operation result."""
        return write_text(
            path,
            content,
            encoding=encoding,
            policy=policy,
            overwrite=overwrite,
            dry_run=dry_run,
        )

    @staticmethod
    def copy_file(
        source: Path,
        destination: Path,
        *,
        overwrite: bool = True,
        dry_run: bool = False,
    ) -> Path:
        """Copy one file."""
        return copy_file(
            source,
            destination,
            overwrite=overwrite,
            dry_run=dry_run,
        )

    @staticmethod
    def remove_file(
        path: Path,
        *,
        missing_ok: bool = True,
        dry_run: bool = False,
    ) -> None:
        """Remove one file."""
        remove_file(
            path,
            missing_ok=missing_ok,
            dry_run=dry_run,
        )
