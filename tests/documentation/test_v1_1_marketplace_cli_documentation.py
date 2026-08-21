"""Executable EN / zh-TW Marketplace CLI documentation parity tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from generator.cli.main import main

ROOT = Path(__file__).resolve().parents[2]
EN_MARKETPLACE = ROOT / "docs" / "user-guide" / "en" / "marketplace.md"
ZH_TW_MARKETPLACE = ROOT / "docs" / "user-guide" / "zh-TW" / "marketplace.md"
EN_CLI = ROOT / "docs" / "user-guide" / "en" / "cli.md"
ZH_TW_CLI = ROOT / "docs" / "user-guide" / "zh-TW" / "cli.md"

COMMAND_SHAPES = (
    "opl marketplace versions IDENTITY --catalog FILE [--json]",
    "opl marketplace inspect COORDINATE --catalog FILE [--json]",
    "opl marketplace verify COORDINATE --catalog FILE --payload-root DIR [--json]",
    ("opl marketplace install COORDINATE --catalog FILE --payload-root DIR [--dry-run] [--json]"),
)

FUNCTIONAL_TERMS = (
    "versions",
    "inspect",
    "verify",
    "install",
    "--catalog",
    "--payload-root",
    "--dry-run",
    "--json",
    "schema_version: 1",
    "stdout",
    "stderr",
    "SHA-256",
    "process-local",
    "non-persistent",
    "non-activating",
    "opl marketplace list",
)

DEFERRED_TERMS = (
    "remote Marketplace",
    "network fallback",
    "dependency resolution",
    "signing",
    "ratings/reviews",
    "automatic activation",
    "AI CLI",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("path", (EN_MARKETPLACE, ZH_TW_MARKETPLACE))
def test_bilingual_marketplace_manuals_document_exact_command_shapes(path: Path) -> None:
    text = _read(path)

    for command in COMMAND_SHAPES:
        assert command in text


@pytest.mark.parametrize("path", (EN_MARKETPLACE, ZH_TW_MARKETPLACE))
def test_bilingual_marketplace_manuals_have_functional_parity(path: Path) -> None:
    text = _read(path)

    for term in FUNCTIONAL_TERMS + DEFERRED_TERMS:
        assert term in text


def test_bilingual_cli_chapters_link_marketplace_workflow() -> None:
    for path in (EN_CLI, ZH_TW_CLI):
        text = _read(path)
        assert "Marketplace" in text
        assert "marketplace.md" in text
        for command in ("versions", "inspect", "verify", "install"):
            assert f"`{command}`" in text


def test_manuals_explicitly_reject_global_list_and_activation() -> None:
    for path in (EN_MARKETPLACE, ZH_TW_MARKETPLACE):
        text = _read(path)
        rejected = "no `opl marketplace list`" in text.lower()
        rejected = rejected or "沒有 `opl marketplace list`" in text
        assert rejected
        assert "artifact installed != artifact activated" in text


def test_documented_versions_example_executes(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    payload = b"documented payload"
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
                        "description": "Documentation fixture",
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
            }
        ),
        encoding="utf-8",
    )

    assert (
        main(
            (
                "marketplace",
                "versions",
                "community/demo",
                "--catalog",
                str(catalog),
                "--json",
            )
        )
        == 0
    )
    output = capsys.readouterr()
    document = json.loads(output.out)
    assert document == {
        "command": "versions",
        "identity": "community/demo",
        "schema_version": 1,
        "versions": ["1.2.3"],
    }
    assert output.err == ""
