"""v1.2.7 Bootstrap CLI/runtime wiring design contract."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs/releases/v1.2.7-bootstrap-cli-runtime-wiring.md"
ARCH = ROOT / "docs/architecture/bootstrap-cli-runtime-wiring.md"
CLI = ROOT / "generator/cli/main.py"
LEGACY = ROOT / "generator/main.py"
PYPROJECT = ROOT / "pyproject.toml"
PRODUCTION = ROOT / "generator/cli/bootstrap_runtime.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_design_first_boundary() -> None:
    text = read(DESIGN)
    assert "Design / Contract Definition --- In Progress" in text
    assert "Production CLI Wiring --- Not Started" in text
    assert "v1.2.7 Acceptance --- Not Accepted" in text
    assert not PRODUCTION.exists()


def test_canonical_entrypoint_is_fixed() -> None:
    combined = read(DESIGN) + read(ARCH) + read(PYPROJECT)
    assert 'opl = "generator.cli.main:main"' in combined
    assert "Canonical parser --- generator.cli.main.build_parser" in combined
    assert "generator.main legacy parser registration --- Forbidden" in combined


def test_existing_bootstrap_contract_is_inventory_backed() -> None:
    cli = read(CLI)
    for marker in ('"bootstrap"', '"--dry-run"', '"--force"', "_handle_bootstrap"):
        assert marker in cli
    assert "Existing BootstrapGenerator path unchanged" in read(DESIGN)


def test_mode_mapping_is_explicit() -> None:
    text = read(DESIGN)
    for marker in (
        "Experimental opt-in + --dry-run --- BootstrapRuntimeMode.PREVIEW",
        "Experimental opt-in, no --dry-run --- BootstrapRuntimeMode.APPLY",
        "Experimental validation opt-in --- BootstrapRuntimeMode.APPLY_AND_VALIDATE",
        "Implicit validation --- Forbidden",
    ):
        assert marker in text


def test_adapter_does_not_duplicate_runtime_lifecycle() -> None:
    text = read(DESIGN) + read(ARCH)
    for marker in (
        "BootstrapRuntimeCoordinator.execute(request) exactly once",
        "Coordinator Invocation --- Exactly Once",
        "The adapter translates and renders only",
    ):
        assert marker in text


def test_failure_behavior_is_fail_closed() -> None:
    text = read(DESIGN)
    for marker in (
        "Missing runtime dependency --- Fail Closed / no legacy fallback",
        "Experimental failure fallback to legacy path --- Forbidden",
        "Invalid validation result --- Completed invalid result / non-success exit",
        "Success-shaped partial CLI output --- Forbidden",
    ):
        assert marker in text


def test_existing_cli_and_deferred_boundaries_remain_closed() -> None:
    combined = read(DESIGN) + read(ARCH)
    for marker in (
        "Legacy Grammar --- Preserved",
        "Stable runtime option names --- Not Accepted",
        "Public SDK integration --- Deferred",
        "Repair / rollback --- Deferred",
        "Checkpoint / resume --- Deferred",
        "Parallel phase execution --- Deferred",
    ):
        assert marker in combined


def test_code_review_checklist_is_complete() -> None:
    text = read(DESIGN)
    for marker in (
        "## Code Review Checklist",
        "Only `generator.cli.main` receives parser/handler wiring",
        "Legacy Bootstrap behavior is unchanged",
        "Mode mapping is explicit and conflict tested",
        "CLI output and exit codes have executable contract tests",
        "Architecture, tests, manuals, HISTORY, roadmap, and CHANGELOG align",
    ):
        assert marker in text


def test_acceptance_gates_are_pending() -> None:
    text = read(DESIGN)
    for marker in (
        "Focused tests --- Pending",
        "Full regression / coverage --- Pending",
        "pre-commit --- Pending",
        "Design PR required CI --- Pending",
        "Terminal design acceptance --- Pending",
    ):
        assert marker in text
