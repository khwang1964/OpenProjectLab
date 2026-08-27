from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs/releases/v1.2.8-bootstrap-cli-public-contract-stabilization.md"
ARCH = ROOT / "docs/architecture/bootstrap-cli-public-contract.md"
ACCEPTANCE = ROOT / "docs/releases/v1.2.8-bootstrap-cli-public-contract-stabilization-acceptance.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_design_first_status_is_explicit() -> None:
    text = read(DESIGN)
    assert "Accepted --- Terminally Closed" in text
    assert (
        "Production implementation --- Implemented / Awaiting terminal alignment acceptance" in text
    )
    assert "v1.2.8 Acceptance --- Accepted" in text


def test_predecessor_is_terminally_accepted() -> None:
    assert "v1.2.7 Bootstrap CLI/runtime wiring --- Accepted / Completed" in read(DESIGN)


def test_legacy_and_experimental_boundaries_are_preserved() -> None:
    text = read(DESIGN)
    for marker in (
        "Current experimental opt-in --- preserved during design",
        "Legacy no-opt-in behavior --- unchanged",
        "Stable public option names --- Proposed, not yet accepted",
    ):
        assert marker in text


def test_exit_status_mapping_is_defined() -> None:
    text = read(DESIGN)
    for marker in (
        "Successful requested operation --- exit 0",
        "Usage or parser error --- exit 2",
        "Runtime execution failure --- exit 1",
        "Internal check execution failure --- exit 1, fail closed",
    ):
        assert marker in text


def test_partial_success_is_forbidden() -> None:
    combined = read(DESIGN) + read(ARCH)
    assert "Success-shaped partial result --- Forbidden" in combined
    assert "success-shaped partial results are forbidden" in combined


def test_output_channels_and_ordering_are_defined() -> None:
    text = read(DESIGN)
    for marker in (
        "deterministic summary --- stdout",
        "operational diagnostics --- stderr",
        "Ordering --- deterministic and lifecycle-defined",
        "Machine-readable JSON output --- Deferred",
    ):
        assert marker in text


def test_validation_never_mutates_or_rolls_back() -> None:
    text = read(DESIGN)
    assert "Validation must not call apply" in text
    assert "must not repair filesystem state" in text
    assert "validation failure does not imply automatic rollback" in text


def test_cli_adapter_ownership_is_bounded() -> None:
    text = read(ARCH)
    assert "CLI adapter owns parsing, normalization, lifecycle invocation" in text
    assert "does not own planning, apply execution" in text


def test_sdk_and_advanced_lifecycle_remain_deferred() -> None:
    combined = read(DESIGN) + read(ARCH)
    for marker in (
        "Programmatic SDK exposure --- Deferred",
        "Advanced lifecycle controls --- Deferred",
        "Stable SDK entrypoints",
    ):
        assert marker in combined


def test_acceptance_gates_are_terminally_closed() -> None:
    text = read(DESIGN)
    for marker in (
        "Focused design-contract verification --- Passed",
        "Pre-commit --- Passed",
        "Full regression / coverage --- Passed",
        "Design PR required CI --- Passed",
        "Post-merge synchronized-main verification --- Passed",
        "Terminal design acceptance --- Accepted",
    ):
        assert marker in text


def test_terminal_acceptance_preserves_implementation_boundary() -> None:
    text = read(ACCEPTANCE)
    for marker in (
        "Design PR #252 --- Merged",
        "Design merge --- 262cdf6b76f811a158579c58ec9fcbeb25dec6fd",
        "Post-merge focused verification --- 10 passed",
        "Terminal design acceptance --- Accepted / Completed",
        "Production stabilization --- Not Started",
    ):
        assert marker in text


def test_minimum_implementation_evidence_is_pending_closure() -> None:
    combined = read(DESIGN) + read(ARCH) + read(ACCEPTANCE)
    for marker in (
        "Implementation PR #254 --- Merged",
        "Implementation merge --- 1d36d568ca0b09cde2f8e12418bfdb63e72f14e2",
        "Post-merge focused verification --- 38 passed",
        "Stable --runtime option --- Implemented",
        "Legacy --experimental-runtime alias --- Preserved",
        "Implementation acceptance --- Pending terminal-alignment merge",
    ):
        assert marker in combined
