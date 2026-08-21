"""Keep v1.1.4 Marketplace CLI implementation Design First and fail closed."""

from __future__ import annotations

from pathlib import Path

from generator.cli.main import build_parser
from generator.marketplace.repository import MarketplaceRepository

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "docs" / "releases" / "v1.1-marketplace-cli-implementation.md"
CONTRACT = ROOT / "docs" / "releases" / "v1.1-marketplace-cli-contract.md"
ROADMAP = ROOT / "docs" / "roadmap.md"
HISTORY = ROOT / "docs" / "HISTORY.md"
CHANGELOG = ROOT / "CHANGELOG.md"


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


def test_implementation_baseline_starts_without_product_registration() -> None:
    baseline = _read(BASELINE)

    assert "# OpenProjectLab v1.1 Marketplace CLI Implementation Baseline" in baseline
    assert "v1.1.4 --- Marketplace CLI Implementation" in baseline
    assert "**Implementation:** versions / inspect In Progress" in baseline
    assert "**Production Parser Registration:** Not Started" in baseline
    assert "**Formal v1.1 Acceptance:** Not Accepted" in baseline
    assert "v1.1.4.1 Implementation Baseline / Architecture        Complete" in baseline
    assert "v1.1.4.2 Internal Catalog and Parsing Adapters          Complete" in baseline
    assert "v1.1.4.3 versions / inspect                             In Progress" in baseline
    assert "marketplace" not in _top_level_commands()


def test_baseline_preserves_exact_accepted_command_inventory() -> None:
    baseline = _read(BASELINE)
    prose = _normalized(BASELINE)

    for subcommand in ("versions", "inspect", "verify", "install"):
        assert f"opl marketplace {subcommand} " in baseline

    assert "No aliases, short options" in baseline
    assert "`opl marketplace list`" in baseline
    assert "outside the accepted CLI surface" in prose


def test_internal_global_enumeration_does_not_expand_cli_scope() -> None:
    contract_prose = _normalized(CONTRACT)
    baseline_prose = _normalized(BASELINE)

    assert "list_artifacts" in MarketplaceRepository.__dict__
    assert "`list_artifacts()`" in contract_prose
    assert "does not expose that internal capability" in contract_prose
    assert "must not leak into parser registration" in baseline_prose


def test_architecture_reuses_existing_marketplace_boundaries() -> None:
    baseline = _read(BASELINE)

    for boundary in (
        "ArtifactIdentity",
        "ArtifactVersion",
        "ArtifactCoordinate",
        "MarketplaceArtifact",
        "InMemoryMarketplaceRepository.find()",
        "available_versions()",
        "ArtifactAcquirer.acquire()",
        "verify_integrity()",
        "ArtifactInstaller.install()",
    ):
        assert boundary in baseline

    assert "must not broaden `generator.marketplace.__all__`" in baseline
    assert "must not" in _normalized(BASELINE)


def test_baseline_defines_fail_closed_catalog_and_payload_safety() -> None:
    prose = _normalized(BASELINE)

    assert "read one explicit `--catalog FILE` as UTF-8 JSON" in prose
    assert "reject malformed JSON, wrong types" in prose
    assert "duplicate exact coordinates" in prose
    assert "Windows drive-prefixed references" in prose
    assert "symlinks escaping the root" in prose
    assert "No network fallback is permitted" in prose
    assert "integrity failures must occur before installation" in prose


def test_baseline_defines_command_side_effect_boundaries() -> None:
    prose = _normalized(BASELINE)

    assert "`versions`, `inspect`, `verify`, or `install --dry-run`" in prose
    assert "installer state is unchanged" in prose
    assert "complete verification but never call `install()`" in prose
    assert "process-local, non-activating, and non-persistent" in prose
    assert "reject duplicate installation without replacing existing payload bytes" in prose


def test_baseline_requires_output_exit_and_failure_contracts() -> None:
    prose = _normalized(BASELINE)

    assert "Human-readable success output goes to stdout" in prose
    assert "Diagnostics go to stderr" in prose
    assert "success emits exactly one UTF-8 JSON object" in prose
    assert "A handled failure emits no success JSON document" in prose
    assert "No finer Stable exit taxonomy" in prose
    assert "| `0` | Successful Marketplace command" in prose
    assert "| `2` | Usage, catalog" in prose


def test_delivery_sequence_delays_production_registration() -> None:
    baseline = _read(BASELINE)

    assert "v1.1.4.1 Implementation Baseline / Architecture" in baseline
    assert "v1.1.4.2 Internal Catalog and Parsing Adapters" in baseline
    assert "v1.1.4.6 Deterministic JSON and Diagnostics" in baseline
    assert "v1.1.4.7 Production Parser Registration" in baseline
    assert "v1.1.4.8 EN / zh-TW User Manual Updates" in baseline
    assert "Production registration occurs only after internal adapters" in baseline


def test_bilingual_manual_and_canonical_demo_obligations_are_explicit() -> None:
    baseline = _read(BASELINE)
    prose = _normalized(BASELINE)

    assert "docs/user-guide/en/marketplace.md" in baseline
    assert "docs/user-guide/zh-TW/marketplace.md" in baseline
    assert "functional parity rather than literal translation" in baseline
    assert "canonical executable use-case demo remains inside the OPL repository" in baseline
    assert "does not create a separate demo repository" in prose


def test_trackers_start_v1_1_4_without_claiming_implementation() -> None:
    for tracker in (ROADMAP, HISTORY, CHANGELOG):
        prose = _normalized(tracker).lower()
        assert "v1.1.4 marketplace cli implementation" in prose
        assert "in progress" in prose
        assert "production parser registration" in prose
        assert "not started" in prose
        assert "formal v1.1 acceptance" in prose
        assert "not accepted" in prose


def test_internal_adapter_terminal_alignment_records_merged_evidence() -> None:
    merge_sha = "0ac32017b1420464c7c52a2b63993fc4e27a63b4"

    for tracker in (ROADMAP, HISTORY, CHANGELOG, BASELINE):
        prose = _normalized(tracker)
        lower_prose = prose.lower()
        assert "implementation pr #174" in lower_prose
        assert merge_sha in prose
        assert "production parser registration" in lower_prose
        assert "not started" in lower_prose
        assert "formal v1.1 acceptance" in lower_prose
        assert "not accepted" in lower_prose
        assert "v1.1.4.3 versions / inspect" in lower_prose


def test_code_review_and_acceptance_gates_are_complete() -> None:
    baseline = _read(BASELINE)
    prose = _normalized(BASELINE)

    for heading in (
        "### Architecture",
        "### Safety and behavior",
        "### Tests",
        "### Documentation and demo",
        "## 14. Acceptance Gates",
    ):
        assert heading in baseline

    assert "installed-wheel Marketplace CLI verification" in baseline
    assert "terminal documentation alignment complete" in prose
