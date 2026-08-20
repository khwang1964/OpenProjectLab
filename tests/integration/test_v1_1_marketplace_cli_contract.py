"""Govern the v1.1 Marketplace CLI contract before implementation."""

from __future__ import annotations

from pathlib import Path

from generator.cli.main import build_parser

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "docs" / "releases" / "v1.1-marketplace-cli-contract.md"
V1_MARKETPLACE_TEST = ROOT / "tests" / "marketplace" / "test_v1_marketplace_public_contract.py"
MARKETPLACE_E2E = ROOT / "tests" / "integration" / "test_marketplace_e2e.py"

EXPECTED_SUBCOMMANDS = ("versions", "inspect", "verify", "install")


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalized(path: Path) -> str:
    return " ".join(_read(path).split())


def _top_level_commands() -> frozenset[str]:
    parser = build_parser()

    for action in parser._actions:
        choices = getattr(action, "choices", None)
        if isinstance(choices, dict) and "list" in choices:
            return frozenset(choices)

    raise AssertionError("CLI subcommand registry was not found")


def test_marketplace_cli_contract_is_accepted_before_implementation() -> None:
    contract = _read(CONTRACT)

    assert "# OpenProjectLab v1.1 Marketplace CLI Contract" in contract
    assert "**Status:** Accepted" in contract
    assert "v1.1.3 --- Marketplace CLI Contract" in contract
    assert "**Governing PR:** #170" in contract
    assert "**Governing Merge Commit:** `5f63bd3dc438ba1ea5e10b8225c761964c1819bc`" in contract
    assert "**Marketplace CLI Contract:** Accepted" in contract
    assert "**Marketplace CLI Implementation:** Not Started" in contract
    assert "**Formal v1.1 Acceptance:** Not Accepted" in contract


def test_marketplace_command_is_not_registered_during_contract_design() -> None:
    contract = _read(CONTRACT)

    assert "marketplace" not in _top_level_commands()
    assert "must not register `marketplace` until v1.1.4" in _normalized(CONTRACT)
    assert "contract design and fail-closed automation only" in contract


def test_contract_preserves_existing_marketplace_evidence() -> None:
    contract = _read(CONTRACT)

    assert V1_MARKETPLACE_TEST.is_file()
    assert MARKETPLACE_E2E.is_file()
    for boundary in (
        "MarketplaceRepository.find()",
        "available_versions()",
        "ArtifactAcquirer.acquire()",
        "verify_integrity()",
        "ArtifactInstaller.install()",
    ):
        assert boundary in contract


def test_contract_defines_exact_proposed_command_inventory() -> None:
    contract = _read(CONTRACT)

    for subcommand in EXPECTED_SUBCOMMANDS:
        assert f"opl marketplace {subcommand} " in contract
    assert "this contract does not invent `opl marketplace list`" in contract
    assert "No aliases or short options are part of the contract" in contract


def test_contract_defines_identity_coordinate_and_catalog_syntax() -> None:
    prose = _normalized(CONTRACT)

    assert "namespace/name@MAJOR.MINOR.PATCH" in prose
    assert "`--catalog FILE` is required for every Marketplace subcommand" in prose
    assert '"schema_version": 1' in prose
    assert '"artifacts": [' in prose
    assert "duplicate exact coordinates are rejected" in prose
    assert "does not add its loader or raw JSON objects to `generator.sdk`" in prose


def test_contract_keeps_payload_resolution_local_and_safe() -> None:
    prose = _normalized(CONTRACT)

    assert "`verify` and `install` require `--payload-root DIR`" in prose
    assert 'distribution.kind == "file"' in prose
    assert "Absolute paths, drive-prefixed paths, traversal (`..`)" in prose
    assert "escaping the payload root are rejected before bytes are read" in prose
    assert "No network fallback exists" in prose


def test_contract_preserves_pipeline_and_dry_run_side_effect_boundaries() -> None:
    prose = _normalized(CONTRACT)

    assert "exact repository lookup" in prose
    assert "local payload acquisition" in prose
    assert "SHA-256 verification" in prose
    assert "does not call the installer" in prose
    assert "`--dry-run` completes lookup, acquisition, and integrity verification" in prose
    assert "does not call `install()`" in prose
    assert "Failure in any earlier step leaves installer state unchanged" in prose


def test_contract_defines_opt_in_deterministic_json_without_new_exit_taxonomy() -> None:
    prose = _normalized(CONTRACT)

    assert "`--json` is an explicit opt-in machine-readable contract" in prose
    assert 'command --- "versions" | "inspect" | "verify" | "install"' in prose
    assert '"status":"installed"' in prose
    assert "one UTF-8 JSON object to stdout" in prose
    assert "No finer Stable exit taxonomy is introduced" in prose
    assert "| `0` | Successful command" in prose
    assert "| `2` | Usage, parsing, catalog" in prose


def test_contract_keeps_installation_non_activating_and_non_persistent() -> None:
    prose = _normalized(CONTRACT)

    assert "does not promise persistence across CLI processes" in prose
    assert "automatic Plugin or Generator activation" in prose
    assert "entry-point discovery or Generator execution" in prose
    assert "remote Marketplace or Community Repository hosting" in prose
    assert "it does not prove authenticity, publisher trust, or safety" in prose


def test_contract_keeps_later_slices_not_started() -> None:
    contract = _read(CONTRACT)

    assert "Marketplace CLI Implementation --- Not Started" in contract
    assert "AI CLI Contract --- Not Started" in contract
    assert "AI CLI Implementation --- Not Started" in contract
    assert "Formal v1.1 Acceptance --- Not Accepted" in contract
