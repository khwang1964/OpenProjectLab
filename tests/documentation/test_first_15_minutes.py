"""Executable First 15 Minutes documentation smoke tests."""

from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path

import pytest

WHEEL_ENV = "OPL_TEST_WHEEL"

EXPECTED_GENERATORS = {
    "assignment",
    "bootstrap",
    "course",
    "lab",
    "quiz",
    "slides",
    "website",
    "week",
}


def _configured_wheel() -> Path:
    """Return the wheel configured for installed-user documentation tests."""
    raw = os.environ.get(WHEEL_ENV)
    if not raw:
        pytest.skip(f"{WHEEL_ENV} is not set; build a wheel before First 15 Minutes tests")

    wheel = Path(raw).expanduser().resolve()
    if not wheel.is_file():
        pytest.fail(f"{WHEEL_ENV} does not name a wheel file: {wheel}")

    return wheel


def _venv_python(venv_root: Path) -> Path:
    """Return the Python executable inside a test virtual environment."""
    if sys.platform == "win32":
        return venv_root / "Scripts" / "python.exe"
    return venv_root / "bin" / "python"


def _venv_opl(venv_root: Path) -> Path:
    """Return the installed opl console entry point."""
    if sys.platform == "win32":
        return venv_root / "Scripts" / "opl.exe"
    return venv_root / "bin" / "opl"


def _run(
    argv: list[str],
    *,
    cwd: Path,
) -> subprocess.CompletedProcess[str]:
    """Run a subprocess without inheriting repository-specific PYTHONPATH."""
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)

    return subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.fixture(scope="module")
def installed_documentation_distribution(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[Path, Path]:
    """Install the configured wheel into a fresh environment for documentation smoke tests."""
    wheel = _configured_wheel()
    root = tmp_path_factory.mktemp("opl-first-15-minutes")
    venv_root = root / "venv"
    work_root = root / "work"
    work_root.mkdir()

    venv.EnvBuilder(with_pip=True, clear=True).create(venv_root)
    python = _venv_python(venv_root)

    installed = _run(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--disable-pip-version-check",
            str(wheel),
        ],
        cwd=work_root,
    )
    assert installed.returncode == 0, installed.stdout + installed.stderr

    return venv_root, work_root


def test_first_15_minutes_installed_cli_lists_generators(
    installed_documentation_distribution: tuple[Path, Path],
) -> None:
    """The documented installed-user workflow exposes the expected built-in Generators."""
    venv_root, work_root = installed_documentation_distribution
    opl = _venv_opl(venv_root)

    assert opl.is_file()

    result = _run([str(opl), "list"], cwd=work_root)

    assert result.returncode == 0, result.stdout + result.stderr

    listed_generators = {
        line.split(maxsplit=1)[0] for line in result.stdout.splitlines() if line.strip()
    }

    assert EXPECTED_GENERATORS <= listed_generators


def test_first_15_minutes_dry_run_does_not_persist_course_readme(
    installed_documentation_distribution: tuple[Path, Path],
) -> None:
    """The Quick Start dry-run command validates without persisting the course README."""
    venv_root, work_root = installed_documentation_distribution
    opl = _venv_opl(venv_root)
    output_root = work_root / "dry-run-output"

    result = _run(
        [
            str(opl),
            "--output-root",
            str(output_root),
            "course",
            "demo-course",
            "--name",
            "Demo Course",
            "--weeks",
            "4",
            "--language",
            "en",
            "--dry-run",
        ],
        cwd=work_root,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert not (output_root / "demo-course" / "README.md").exists()


def test_first_15_minutes_generates_representative_course_readme(
    installed_documentation_distribution: tuple[Path, Path],
) -> None:
    """The documented Quick Start generates the representative Course artifact."""
    venv_root, work_root = installed_documentation_distribution
    opl = _venv_opl(venv_root)
    output_root = work_root / "output"

    result = _run(
        [
            str(opl),
            "--output-root",
            str(output_root),
            "course",
            "demo-course",
            "--name",
            "Demo Course",
            "--weeks",
            "4",
            "--language",
            "en",
        ],
        cwd=work_root,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    generated = output_root / "demo-course" / "README.md"
    assert generated.is_file()

    content = generated.read_text(encoding="utf-8")
    assert "Demo Course" in content
