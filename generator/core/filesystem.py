from pathlib import Path

from generator.core.exceptions import ValidationError


class FileSystem:
    def ensure_directory(self, path: Path, *, dry_run: bool = False) -> None:
        if not dry_run:
            path.mkdir(parents=True, exist_ok=True)

    def write_text(
        self, path: Path, content: str, *, overwrite: bool = False, dry_run: bool = False
    ) -> None:
        if path.exists() and not overwrite:
            raise ValidationError(f"拒絕覆寫既有檔案：{path}；請使用 --force")
        if dry_run:
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
