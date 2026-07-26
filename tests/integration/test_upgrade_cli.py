from __future__ import annotations

import argparse
import zipfile
from hashlib import sha256
from pathlib import Path

import yaml

from generator.cli.upgrade import handle_upgrade


def make_package(path: Path) -> Path:
    content = b"hello"
    manifest = {
        "schema_version": "1.0",
        "package": "cli-test",
        "version": "1.0.0",
        "description": "CLI integration",
        "entries": [
            {
                "path": "hello.txt",
                "operation": "add",
                "sha256": sha256(content).hexdigest(),
            }
        ],
    }

    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr(
            "upgrade-manifest.yaml",
            yaml.safe_dump(manifest, sort_keys=False),
        )
        archive.writestr("payload/hello.txt", content)

    return path


def test_upgrade_cli_preview(tmp_path: Path, capsys) -> None:
    project = tmp_path / "project"
    project.mkdir()
    package = make_package(tmp_path / "patch.zip")

    args = argparse.Namespace(
        package=package,
        apply=False,
        allow_conflicts=False,
        project_root=project,
    )

    assert handle_upgrade(args) == 0
    output = capsys.readouterr().out
    assert "新增：1" in output
    assert "尚未變更任何檔案" in output
    assert not (project / "hello.txt").exists()


def test_upgrade_cli_apply(tmp_path: Path, capsys) -> None:
    project = tmp_path / "project"
    project.mkdir()
    package = make_package(tmp_path / "patch.zip")

    args = argparse.Namespace(
        package=package,
        apply=True,
        allow_conflicts=False,
        project_root=project,
    )

    assert handle_upgrade(args) == 0
    output = capsys.readouterr().out
    assert "已套用 cli-test 1.0.0" in output
    assert (project / "hello.txt").read_text(encoding="utf-8") == "hello"
