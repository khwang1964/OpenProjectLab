"""v1.1.4.7 production Marketplace parser and handler integration tests."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import pytest

from generator.cli.main import build_parser, main

EXPECTED_MARKETPLACE_COMMANDS = frozenset({"versions", "inspect", "verify", "install"})


def _marketplace_parser() -> argparse.ArgumentParser:
    parser = build_parser()
    top_level = next(
        action
        for action in parser._actions
        if isinstance(getattr(action, "choices", None), dict) and "marketplace" in action.choices
    )
    return top_level.choices["marketplace"]


def _marketplace_commands() -> frozenset[str]:
    parser = _marketplace_parser()
    action = next(
        action
        for action in parser._actions
        if isinstance(getattr(action, "choices", None), dict) and action.choices
    )
    return frozenset(action.choices)


def _catalog(tmp_path: Path, payload: bytes = b"payload") -> tuple[Path, Path]:
    payload_root = tmp_path / "payloads"
    payload_path = payload_root / "packages" / "demo.opl"
    payload_path.parent.mkdir(parents=True)
    payload_path.write_bytes(payload)
    catalog = tmp_path / "catalog.json"
    catalog.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "artifacts": [
                    {
                        "schema_version": 1,
                        "identity": {"namespace": "community", "name": "demo"},
                        "version": "1.2.3",
                        "artifact_type": "template",
                        "description": "CLI fixture: 台灣",
                        "compatibility": ">=1.0,<2.0",
                        "distribution": {
                            "kind": "file",
                            "reference": "packages/demo.opl",
                        },
                        "integrity": {
                            "algorithm": "sha256",
                            "digest": hashlib.sha256(payload).hexdigest(),
                        },
                    }
                ],
            },
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )
    return catalog, payload_root


def test_registers_exact_accepted_marketplace_inventory() -> None:
    assert _marketplace_commands() == EXPECTED_MARKETPLACE_COMMANDS
    assert "list" not in _marketplace_commands()


@pytest.mark.parametrize(
    "argv",
    (
        ("marketplace", "versions", "community/demo", "--catalog", "catalog.json"),
        (
            "marketplace",
            "inspect",
            "community/demo@1.2.3",
            "--catalog",
            "catalog.json",
        ),
        (
            "marketplace",
            "verify",
            "community/demo@1.2.3",
            "--catalog",
            "catalog.json",
            "--payload-root",
            "payloads",
        ),
        (
            "marketplace",
            "install",
            "community/demo@1.2.3",
            "--catalog",
            "catalog.json",
            "--payload-root",
            "payloads",
            "--dry-run",
            "--json",
        ),
    ),
)
def test_accepts_exact_reviewed_command_shapes(argv: tuple[str, ...]) -> None:
    args = build_parser().parse_args(argv)

    assert args.command == "marketplace"
    assert args.marketplace_command in EXPECTED_MARKETPLACE_COMMANDS
    assert callable(args.command_handler)


def test_rejects_unaccepted_marketplace_list_command() -> None:
    with pytest.raises(SystemExit) as exc_info:
        build_parser().parse_args(("marketplace", "list"))

    assert exc_info.value.code == 2


def test_versions_and_inspect_execute_through_production_main(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    catalog, _ = _catalog(tmp_path)

    assert main(("marketplace", "versions", "community/demo", "--catalog", str(catalog))) == 0
    versions = capsys.readouterr()
    assert versions.out == "1.2.3\n"
    assert versions.err == ""

    assert (
        main(
            (
                "marketplace",
                "inspect",
                "community/demo@1.2.3",
                "--catalog",
                str(catalog),
                "--json",
            )
        )
        == 0
    )
    inspected = capsys.readouterr()
    assert json.loads(inspected.out)["coordinate"] == "community/demo@1.2.3"
    assert inspected.err == ""


@pytest.mark.parametrize("dry_run", (False, True))
def test_verify_and_install_execute_with_safe_local_payload(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    dry_run: bool,
) -> None:
    catalog, payload_root = _catalog(tmp_path)
    command = "install" if dry_run else "verify"
    argv = [
        "marketplace",
        command,
        "community/demo@1.2.3",
        "--catalog",
        str(catalog),
        "--payload-root",
        str(payload_root),
        "--json",
    ]
    if dry_run:
        argv.append("--dry-run")

    assert main(tuple(argv)) == 0
    output = capsys.readouterr()
    document = json.loads(output.out)
    assert document["command"] == command
    assert document["coordinate"] == "community/demo@1.2.3"
    assert output.err == ""


def test_install_executes_non_activating_process_local_handler(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    catalog, payload_root = _catalog(tmp_path)

    assert (
        main(
            (
                "marketplace",
                "install",
                "community/demo@1.2.3",
                "--catalog",
                str(catalog),
                "--payload-root",
                str(payload_root),
                "--json",
            )
        )
        == 0
    )
    output = capsys.readouterr()
    document = json.loads(output.out)
    assert document["status"] == "installed"
    assert document["dry_run"] is False
    assert output.err == ""


def test_handled_failure_uses_stderr_exit_two_and_no_success_json(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    missing = tmp_path / "missing.json"

    assert (
        main(
            (
                "marketplace",
                "versions",
                "community/demo",
                "--catalog",
                str(missing),
                "--json",
            )
        )
        == 2
    )
    output = capsys.readouterr()
    assert output.out == ""
    assert output.err.startswith("error: ")
    assert "{" not in output.err


def test_marketplace_registration_preserves_legacy_list(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert main(("--list",)) == 0
    output = capsys.readouterr()
    assert "bootstrap" in output.out
    assert "marketplace" not in output.out
    assert output.err == ""
