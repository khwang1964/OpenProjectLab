"""v1.2.7 Bootstrap CLI/runtime wiring design contract."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs/releases/v1.2.7-bootstrap-cli-runtime-wiring.md"
ARCH = ROOT / "docs/architecture/bootstrap-cli-runtime-wiring.md"
ACCEPTANCE = ROOT / "docs/releases/v1.2.7-bootstrap-cli-runtime-wiring-acceptance.md"
CLI = ROOT / "generator/cli/main.py"
LEGACY = ROOT / "generator/main.py"
PYPROJECT = ROOT / "pyproject.toml"
PRODUCTION = ROOT / "generator/cli/bootstrap_runtime.py"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_design_is_terminally_accepted() -> None:
    text = read(DESIGN)
    assert "Accepted --- Terminally Closed" in text
    assert "Production CLI Wiring --- Not Started" in text
    assert "v1.2.7 Acceptance --- Accepted" in text


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


def test_acceptance_gates_are_terminally_closed() -> None:
    combined = read(DESIGN) + read(ACCEPTANCE)
    for marker in (
        "Design PR #247 --- Merged",
        "Design merge --- a254574d7fc9570402f445518f00714ce5e644e0",
        "Post-merge consistency verification --- 9 passed",
        "Terminal design acceptance --- Completed",
        "v1.2.7 Design Contract --- Accepted",
        "Production CLI Wiring --- Not Started",
    ):
        assert marker in combined


def test_acceptance_preserves_implementation_boundary() -> None:
    text = read(ACCEPTANCE)
    assert "Terminal design acceptance only" in text
    assert "minimum production CLI wiring implementation slice" in text


def test_v1_2_7_minimum_implementation_evidence() -> None:
    combined = read(DESIGN) + read(ARCH) + read(ACCEPTANCE)
    runtime = read(PRODUCTION)
    cli = read(CLI)
    for marker in (
        "Implementation PR #249 --- Merged",
        "Implementation merge --- ea8dcb3df06679ad2cea84eab228db0c97373b4f",
        "Post-merge focused verification --- 16 passed",
        "Production CLI Wiring Slice --- Completed",
        "Legacy no-opt-in path --- Preserved",
    ):
        assert marker in combined
    for marker in (
        "class BootstrapCliRuntimeInput",
        "def execute_bootstrap_runtime",
        "BootstrapRuntimeCoordinator(",
    ):
        assert marker in runtime
    for marker in (
        '"--experimental-runtime"',
        '"--validate"',
        "execute_bootstrap_runtime(",
    ):
        assert marker in cli
