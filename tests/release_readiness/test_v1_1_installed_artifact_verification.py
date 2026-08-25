"""Installed-user verification for the v1.1 candidate wheel."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs" / "releases" / "v1.1-reliability-artifact-backed-verification.md"
CLEAN_CWD = Path(os.environ.get("TEMP", os.environ.get("TMP", "."))).resolve()

PYTHON_ENV = "OPL_TEST_INSTALLED_PYTHON"
OPL_ENV = "OPL_TEST_INSTALLED_OPL"

EXPECTED_VERSION = "1.1.0rc1"

MARKETPLACE_COMMANDS = (
    "versions",
    "inspect",
    "verify",
    "install",
)

AI_COMMANDS = (
    "course",
    "review",
    "document",
    "template",
)


def _read(path: Path) -> str:
    if not path.is_file():
        pytest.fail(f"Missing required v1.1 release authority: {path}")
    return path.read_text(encoding="utf-8")


def _required_executable(environment_name: str) -> Path:
    raw = os.environ.get(environment_name)
    if not raw:
        pytest.skip(
            f"{environment_name} is not set; the clean-install gate supplies "
            "the installed-user executable"
        )

    path = Path(raw).expanduser().resolve()
    if not path.is_file():
        pytest.fail(f"{environment_name} does not name a file: {path}")

    return path


def _run(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        list(args),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )

    assert completed.returncode == 0, (
        f"command failed: {' '.join(args)}\n"
        f"stdout:\n{completed.stdout}\n"
        f"stderr:\n{completed.stderr}"
    )

    return completed


def test_clean_install_reports_v1_1_candidate_version() -> None:
    python = _required_executable(PYTHON_ENV)

    completed = _run(
        str(python),
        "-c",
        ("import importlib.metadata as m; print(m.version('openprojectlab'))"),
        cwd=CLEAN_CWD,
    )

    assert completed.stdout.strip() == EXPECTED_VERSION


def test_clean_install_import_does_not_resolve_to_source_checkout() -> None:
    python = _required_executable(PYTHON_ENV)

    completed = _run(
        str(python),
        "-c",
        "import generator; print(generator.__file__)",
        cwd=CLEAN_CWD,
    )

    installed_path = Path(completed.stdout.strip()).resolve()
    source_root = (ROOT / "generator").resolve()

    assert installed_path != source_root
    assert source_root not in installed_path.parents
    assert "site-packages" in str(installed_path).lower()


def test_installed_opl_help_and_list_work() -> None:
    opl = _required_executable(OPL_ENV)

    help_result = _run(str(opl), "--help", cwd=CLEAN_CWD)
    list_result = _run(str(opl), "list", cwd=CLEAN_CWD)

    assert "marketplace" in help_result.stdout.lower()
    assert "ai" in help_result.stdout.lower()
    assert list_result.stdout.strip()


@pytest.mark.parametrize("command", MARKETPLACE_COMMANDS)
def test_installed_marketplace_command_surface(command: str) -> None:
    opl = _required_executable(OPL_ENV)

    result = _run(
        str(opl),
        "marketplace",
        command,
        "--help",
        cwd=CLEAN_CWD,
    )

    assert command in result.stdout


def test_installed_marketplace_family_help_works() -> None:
    opl = _required_executable(OPL_ENV)

    result = _run(str(opl), "marketplace", "--help", cwd=CLEAN_CWD)

    for command in MARKETPLACE_COMMANDS:
        assert command in result.stdout


@pytest.mark.parametrize("command", AI_COMMANDS)
def test_installed_ai_command_surface(command: str) -> None:
    opl = _required_executable(OPL_ENV)

    result = _run(
        str(opl),
        "ai",
        command,
        "--help",
        cwd=CLEAN_CWD,
    )

    assert command in result.stdout


def test_installed_ai_family_help_works() -> None:
    opl = _required_executable(OPL_ENV)

    result = _run(str(opl), "ai", "--help", cwd=CLEAN_CWD)

    for command in AI_COMMANDS:
        assert command in result.stdout


def test_installed_artifact_contract_keeps_core_acceptance_offline() -> None:
    text = _read(DESIGN)

    for term in (
        "credential-free",
        "network-independent",
        "Experimental live-provider path is not required",
        "Formal v1.1 Acceptance:** Not Accepted",
    ):
        assert term in text
