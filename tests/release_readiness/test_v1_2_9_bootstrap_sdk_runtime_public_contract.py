from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs/releases/v1.2.9-bootstrap-sdk-runtime-public-contract.md"
ARCHITECTURE = ROOT / "docs/architecture/bootstrap-sdk-runtime-public-contract.md"
ACCEPTANCE = ROOT / "docs/releases/v1.2.9-bootstrap-sdk-runtime-public-contract-acceptance.md"
ALIGNMENT = ROOT / "docs/releases/v1.2.9-bootstrap-sdk-runtime-implementation-alignment.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_design_first_status_and_predecessor() -> None:
    text = read(DESIGN)
    assert "Accepted --- Terminally Closed" in text
    assert "v1.2.8 Bootstrap CLI Public Contract Stabilization --- Accepted" in text


def test_public_import_path_and_names_are_explicit() -> None:
    text = read(DESIGN)
    assert "generator.sdk.bootstrap_runtime" in text
    for name in (
        "BootstrapSdkRequest",
        "BootstrapSdkResult",
        "BootstrapSdkMode",
        "BootstrapSdkUsageError",
        "BootstrapSdkExecutionError",
        "run_bootstrap",
    ):
        assert name in text


def test_existing_sdk_exports_remain_compatible() -> None:
    text = read(DESIGN)
    assert "Existing `generator.sdk` generator and plugin exports remain source compatible" in text
    assert "not re-exported from `generator.sdk`" in text


def test_modes_and_mutation_boundary_are_fixed() -> None:
    text = read(DESIGN) + read(ARCHITECTURE)
    for marker in ("preview", "apply", "apply-and-validate"):
        assert marker in text
    assert "Apply is the only mutation phase" in text


def test_contract_is_immutable_and_deterministic() -> None:
    text = read(DESIGN)
    assert "Requests, results, findings, and phase evidence are immutable" in text
    assert "ordering is deterministic for identical inputs" in text


def test_failure_taxonomy_is_typed_and_fail_closed() -> None:
    text = read(DESIGN)
    assert "raises `BootstrapSdkUsageError` before runtime execution" in text
    assert "raises `BootstrapSdkExecutionError` and fails closed" in text
    assert "failed check identity, and already completed evidence" in text


def test_findings_are_distinct_from_execution_failure() -> None:
    text = read(DESIGN)
    assert "normal `BootstrapSdkResult`" in text
    assert "findings are not translated into operational exceptions" in text


def test_sdk_is_silent_and_has_no_process_policy() -> None:
    text = read(DESIGN)
    assert "must not write to stdout or stderr" in text
    assert "must not expose or derive process exit codes" in text


def test_cli_and_sdk_are_sibling_adapters() -> None:
    text = read(DESIGN) + read(ARCHITECTURE)
    assert "The SDK must not import the CLI adapter" in text
    assert "Both are sibling adapters over the core bootstrap runtime" in text


def test_validation_never_repairs_or_rolls_back() -> None:
    text = read(DESIGN)
    assert "Validation must not call apply" in text
    assert "must not repair filesystem state" in text
    assert "rollback, hidden retry, or compensating mutation" in text


def test_deferred_boundaries_and_acceptance_gates() -> None:
    text = read(DESIGN)
    for marker in (
        "JSON serialization and schema guarantees",
        "asynchronous",
        "remote execution",
        "plugin-provided validation checks",
        "public bootstrap extension protocol",
        "Focused tests --- Passed",
        "Terminal design acceptance --- Accepted",
        "Production implementation --- Implemented / Awaiting implementation acceptance",
        "v1.2.9 Acceptance --- Accepted",
    ):
        assert marker in text


def test_terminal_acceptance_preserves_implementation_boundary() -> None:
    text = read(ACCEPTANCE)
    assert "Accepted --- Completed" in text
    assert "Design PR --- #257" in text
    assert "28cd71b1a415e876a09fcac15c9fd2e9dc5d8f93" in text
    assert "Post-merge focused verification --- 11 passed" in text
    assert "Production implementation --- Implemented / Awaiting implementation acceptance" in text


def test_implementation_alignment_is_pending_separate_acceptance() -> None:
    text = read(ALIGNMENT)
    assert "Implemented --- Awaiting post-merge acceptance closure" in text
    assert "Implementation PR --- #259" in text
    assert "ae2d6908f2e573c6e155a1b6a6991390bf385b57" in text
    assert "Post-merge focused verification --- 25 passed" in text
    assert "Implementation acceptance closure --- Pending" in text
    assert (ROOT / "generator/sdk/bootstrap_runtime.py").is_file()
