"""本機檔案系統操作工具。

此模組集中處理 OpenProjectLab 產生器所需的檔案與目錄操作，
避免各產生器直接散落使用 ``Path``、``shutil`` 等低階 API。
"""

from __future__ import annotations

import os
import shutil
import tempfile
from pathlib import Path


class FileSystemError(RuntimeError):
    """檔案系統操作失敗時拋出的統一例外。"""


def ensure_directory(path: Path, *, dry_run: bool = False) -> Path:
    """確保目錄存在並回傳該目錄。

    Args:
        path: 要建立或確認存在的目錄。
        dry_run: 若為 ``True``，只回傳路徑而不建立目錄。

    Returns:
        已存在的目錄路徑。

    Raises:
        FileSystemError: 路徑已存在但不是目錄，或目錄建立失敗。
    """
    path = Path(path)

    if dry_run:
        return path

    if path.exists() and not path.is_dir():
        raise FileSystemError(f"路徑已存在但不是目錄：{path}")

    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        raise FileSystemError(f"無法建立目錄：{path}") from exc

    return path


def read_text(path: Path, *, encoding: str = "utf-8") -> str:
    """讀取文字檔內容。

    Args:
        path: 要讀取的檔案。
        encoding: 文字編碼，預設為 UTF-8。

    Raises:
        FileSystemError: 路徑不存在、不是檔案或讀取失敗。
    """
    path = Path(path)

    if not path.exists():
        raise FileSystemError(f"找不到檔案：{path}")
    if not path.is_file():
        raise FileSystemError(f"路徑不是檔案：{path}")

    try:
        return path.read_text(encoding=encoding)
    except OSError as exc:
        raise FileSystemError(f"無法讀取檔案：{path}") from exc


def write_text(
    path: Path,
    content: str,
    *,
    encoding: str = "utf-8",
    overwrite: bool = True,
    dry_run: bool = False,
) -> Path:
    """以原子方式寫入文字檔，必要時自動建立父目錄。

    寫入內容會先存入同一目錄中的暫存檔，再透過 ``os.replace`` 取代
    目標檔案，避免寫入中斷時留下不完整檔案。

    Args:
        path: 目標檔案。
        content: 要寫入的文字內容。
        encoding: 文字編碼，預設為 UTF-8。
        overwrite: 是否允許覆寫既有檔案。
        dry_run: 若為 ``True``，只回傳目標路徑而不寫入檔案。

    Returns:
        寫入完成的檔案路徑。

    Raises:
        FileSystemError: 目標為目錄、禁止覆寫或寫入失敗。
    """
    path = Path(path)

    if dry_run:
        return path

    if path.exists() and path.is_dir():
        raise FileSystemError(f"目標路徑是目錄，無法寫入檔案：{path}")
    if path.exists() and not overwrite:
        raise FileSystemError(f"檔案已存在且不允許覆寫：{path}")

    ensure_directory(path.parent)

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
            temporary_path.unlink(missing_ok=True)
        raise FileSystemError(f"無法寫入檔案：{path}") from exc

    return path


def copy_file(
    source: Path,
    destination: Path,
    *,
    overwrite: bool = True,
    dry_run: bool = False,
) -> Path:
    """複製單一檔案並保留基本檔案中繼資料。

    Args:
        source: 來源檔案。
        destination: 目的檔案。
        overwrite: 是否允許覆寫既有目的檔案。
        dry_run: 若為 ``True``，只回傳目的路徑而不複製檔案。

    Returns:
        複製完成的目的檔案路徑。

    Raises:
        FileSystemError: 來源無效、目的為目錄、禁止覆寫或複製失敗。
    """
    source = Path(source)
    destination = Path(destination)

    if dry_run:
        return destination

    if not source.exists():
        raise FileSystemError(f"找不到來源檔案：{source}")
    if not source.is_file():
        raise FileSystemError(f"來源路徑不是檔案：{source}")
    if destination.exists() and destination.is_dir():
        raise FileSystemError(f"目的路徑是目錄：{destination}")
    if destination.exists() and not overwrite:
        raise FileSystemError(f"目的檔案已存在且不允許覆寫：{destination}")

    ensure_directory(destination.parent)

    try:
        shutil.copy2(source, destination)
    except OSError as exc:
        raise FileSystemError(f"無法複製檔案：{source} -> {destination}") from exc

    return destination


def remove_file(
    path: Path,
    *,
    missing_ok: bool = True,
    dry_run: bool = False,
) -> None:
    """刪除單一檔案。

    Args:
        path: 要刪除的檔案。
        missing_ok: 檔案不存在時是否忽略。
        dry_run: 若為 ``True``，不刪除檔案。

    Raises:
        FileSystemError: 路徑為目錄、檔案不存在且不允許忽略，或刪除失敗。
    """
    path = Path(path)

    if dry_run:
        return

    if path.exists() and path.is_dir():
        raise FileSystemError(f"路徑是目錄，拒絕以 remove_file 刪除：{path}")

    try:
        path.unlink(missing_ok=missing_ok)
    except FileNotFoundError as exc:
        raise FileSystemError(f"找不到要刪除的檔案：{path}") from exc
    except OSError as exc:
        raise FileSystemError(f"無法刪除檔案：{path}") from exc


class FileSystem:
    """向後相容的無狀態檔案系統介面。"""

    @staticmethod
    def ensure_directory(path: Path, *, dry_run: bool = False) -> Path:
        """確保目錄存在。"""
        return ensure_directory(path, dry_run=dry_run)

    @staticmethod
    def ensure_dir(path: Path, *, dry_run: bool = False) -> Path:
        """``ensure_directory`` 的相容別名。"""
        return ensure_directory(path, dry_run=dry_run)

    @staticmethod
    def mkdir(path: Path, *, dry_run: bool = False) -> Path:
        """``ensure_directory`` 的簡短相容別名。"""
        return ensure_directory(path, dry_run=dry_run)

    @staticmethod
    def read_text(path: Path, *, encoding: str = "utf-8") -> str:
        """讀取文字檔。"""
        return read_text(path, encoding=encoding)

    @staticmethod
    def write_text(
        path: Path,
        content: str,
        *,
        encoding: str = "utf-8",
        overwrite: bool = True,
        dry_run: bool = False,
    ) -> Path:
        """寫入文字檔。"""
        return write_text(
            path,
            content,
            encoding=encoding,
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
        """複製單一檔案。"""
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
        """刪除單一檔案。"""
        remove_file(path, missing_ok=missing_ok, dry_run=dry_run)
