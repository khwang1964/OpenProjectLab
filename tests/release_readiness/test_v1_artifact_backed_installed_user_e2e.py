"""Step 8.9.5 artifact-backed representative installed-user E2E tests."""

from __future__ import annotations

import os
import subprocess
import sys
import tomllib
import venv
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
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
    raw = os.environ.get(WHEEL_ENV)
    if not raw:
        pytest.skip(f"{WHEEL_ENV} is not set; the artifact gate supplies the current wheel")

    wheel = Path(raw).expanduser().resolve()
    if not wheel.is_file():
        pytest.fail(f"{WHEEL_ENV} does not name a wheel file: {wheel}")
    if wheel.suffix != ".whl":
        pytest.fail(f"{WHEEL_ENV} must name a .whl file: {wheel}")
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
    env["PYTHONNOUSERSITE"] = "1"
    return subprocess.run(
        argv,
        cwd=cwd,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


@pytest.fixture(scope="module")
def installed_release_candidate(
    tmp_path_factory: pytest.TempPathFactory,
) -> tuple[Path, Path]:
    wheel = _configured_wheel()
    root = tmp_path_factory.mktemp("opl-v1-installed-user-e2e")
    venv_root = root / "venv"
    work_root = root / "work"
    work_root.mkdir()

    assert REPO_ROOT not in root.parents

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


def test_installed_distribution_identity_and_import_are_outside_source_checkout(
    installed_release_candidate: tuple[Path, Path],
) -> None:
    venv_root, work_root = installed_release_candidate
    python = _venv_python(venv_root)
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]
    code = (
        "import importlib.metadata, pathlib, sys, generator; "
        "source = pathlib.Path(sys.argv[1]).resolve(); "
        "module = pathlib.Path(generator.__file__).resolve(); "
        "print(module); "
        "assert 'site-packages' in str(module); "
        "assert not module.is_relative_to(source); "
        "assert importlib.metadata.version('openprojectlab') == sys.argv[2]"
    )

    result = _run(
        [str(python), "-c", code, str(REPO_ROOT), str(project["version"])],
        cwd=work_root,
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_installed_console_lists_the_complete_builtin_generator_set(
    installed_release_candidate: tuple[Path, Path],
) -> None:
    venv_root, work_root = installed_release_candidate
    opl = _venv_opl(venv_root)

    assert opl.is_file()
    result = _run([str(opl), "list"], cwd=work_root)
    assert result.returncode == 0, result.stdout + result.stderr

    listed = {line.split(maxsplit=1)[0] for line in result.stdout.splitlines() if line.strip()}
    assert EXPECTED_GENERATORS <= listed


def test_installed_console_generates_representative_course_artifact(
    installed_release_candidate: tuple[Path, Path],
) -> None:
    venv_root, work_root = installed_release_candidate
    opl = _venv_opl(venv_root)
    output_root = work_root / "output"
    result = _run(
        [
            str(opl),
            "--output-root",
            str(output_root),
            "course",
            "release-readiness-e2e",
            "--name",
            "Release Readiness E2E",
            "--weeks",
            "2",
            "--language",
            "en",
        ],
        cwd=work_root,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    generated = output_root / "release-readiness-e2e" / "README.md"
    assert generated.is_file()
    assert "Release Readiness E2E" in generated.read_text(encoding="utf-8")


def test_installed_console_rejects_unknown_command_without_artifacts(
    installed_release_candidate: tuple[Path, Path],
) -> None:
    venv_root, work_root = installed_release_candidate
    opl = _venv_opl(venv_root)
    output_root = work_root / "invalid-output"

    result = _run(
        [str(opl), "--output-root", str(output_root), "not-a-generator"],
        cwd=work_root,
    )

    assert result.returncode != 0
    assert not output_root.exists()
