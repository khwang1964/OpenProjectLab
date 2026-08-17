"""OpenProjectLab v1 clean-wheel installation smoke tests."""

from __future__ import annotations

import os
import subprocess
import sys
import venv
from pathlib import Path

import pytest

WHEEL_ENV = "OPL_TEST_WHEEL"


def _configured_wheel() -> Path:
    raw = os.environ.get(WHEEL_ENV)
    if not raw:
        pytest.skip(f"{WHEEL_ENV} is not set; build a wheel before clean-install smoke tests")
    wheel = Path(raw).expanduser().resolve()
    if not wheel.is_file():
        pytest.fail(f"{WHEEL_ENV} does not name a wheel file: {wheel}")
    return wheel


def _venv_python(venv_root: Path) -> Path:
    if sys.platform == "win32":
        return venv_root / "Scripts" / "python.exe"
    return venv_root / "bin" / "python"


def _venv_opl(venv_root: Path) -> Path:
    if sys.platform == "win32":
        return venv_root / "Scripts" / "opl.exe"
    return venv_root / "bin" / "opl"


def _run(argv: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
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
def installed_distribution(tmp_path_factory: pytest.TempPathFactory) -> tuple[Path, Path]:
    wheel = _configured_wheel()
    root = tmp_path_factory.mktemp("opl-clean-install")
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


def test_v1_clean_wheel_imports_generator_outside_repository(
    installed_distribution: tuple[Path, Path],
) -> None:
    venv_root, work_root = installed_distribution
    python = _venv_python(venv_root)

    result = _run(
        [
            str(python),
            "-c",
            (
                "import pathlib, generator; "
                "p = pathlib.Path(generator.__file__).resolve(); "
                "print(p); "
                "assert 'site-packages' in str(p)"
            ),
        ],
        cwd=work_root,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_v1_clean_wheel_resolves_packaged_template_root(
    installed_distribution: tuple[Path, Path],
) -> None:
    venv_root, work_root = installed_distribution
    python = _venv_python(venv_root)

    result = _run(
        [
            str(python),
            "-c",
            (
                "from generator.resources import package_template_root; "
                "p = package_template_root(); "
                "print(p); "
                "assert p.is_dir(); "
                "assert (p / 'course' / 'README.md.j2').is_file()"
            ),
        ],
        cwd=work_root,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_v1_clean_wheel_exposes_opl_list(
    installed_distribution: tuple[Path, Path],
) -> None:
    venv_root, work_root = installed_distribution
    opl = _venv_opl(venv_root)

    assert opl.is_file()
    result = _run([str(opl), "list"], cwd=work_root)

    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout.strip()


def test_v1_clean_wheel_generates_representative_course_artifact(
    installed_distribution: tuple[Path, Path],
) -> None:
    venv_root, work_root = installed_distribution
    opl = _venv_opl(venv_root)
    output_root = work_root / "output"

    result = _run(
        [
            str(opl),
            "--output-root",
            str(output_root),
            "course",
            "packaging-smoke",
            "--name",
            "Packaging Smoke Course",
            "--weeks",
            "1",
        ],
        cwd=work_root,
    )

    assert result.returncode == 0, result.stdout + result.stderr

    generated = output_root / "packaging-smoke" / "README.md"
    assert generated.is_file()
    assert "Packaging Smoke Course" in generated.read_text(encoding="utf-8")
