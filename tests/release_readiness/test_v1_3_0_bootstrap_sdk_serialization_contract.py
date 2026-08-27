from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs/releases/v1.3.0-bootstrap-sdk-serialization-contract.md"
ARCHITECTURE = ROOT / "docs/architecture/bootstrap-sdk-serialization-contract.md"
ACCEPTANCE = ROOT / "docs/releases/v1.3.0-bootstrap-sdk-serialization-contract-acceptance.md"
ALIGNMENT = ROOT / "docs/releases/v1.3.0-bootstrap-sdk-serialization-implementation-alignment.md"
IMPLEMENTATION_ACCEPTANCE = (
    ROOT / "docs/releases/v1.3.0-bootstrap-sdk-serialization-implementation-acceptance.md"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_design_status_and_predecessor() -> None:
    text = read(DESIGN)
    assert "Accepted --- Terminally Closed" in text
    assert "v1.2.9 Bootstrap SDK Runtime --- Accepted / Completed" in text


def test_public_surface_is_explicit() -> None:
    text = read(DESIGN)
    assert "generator.sdk.bootstrap_serialization" in text
    for name in (
        "BootstrapSchemaVersion",
        "BootstrapSerializationError",
        "serialize_bootstrap_request",
        "deserialize_bootstrap_request",
        "serialize_bootstrap_result",
        "deserialize_bootstrap_result",
    ):
        assert name in text


def test_schema_and_envelope_are_versioned_and_closed() -> None:
    text = read(DESIGN) + read(ARCHITECTURE)
    assert "opl.bootstrap/1.0" in text
    for marker in ("schema", "document_type", "payload"):
        assert marker in text
    assert "bootstrap-request" in text
    assert "bootstrap-result" in text


def test_canonical_encoding_is_deterministic() -> None:
    text = read(DESIGN)
    assert "UTF-8 JSON, sorted object keys, compact separators" in text
    assert "byte-for-byte identical text" in text
    assert "rejects NaN or Infinity" in text


def test_evidence_array_order_is_authoritative() -> None:
    text = read(DESIGN)
    assert "Array order is authoritative" in text
    assert "plan steps" in text
    assert "findings" in text
    assert "completed failure evidence" in text


def test_paths_are_lexical_and_inert() -> None:
    text = read(DESIGN)
    assert "lexical Unicode strings using forward slashes" in text
    assert "must not resolve, canonicalize, access, or test filesystem paths" in text


def test_decoder_is_strict_and_fail_closed() -> None:
    text = read(DESIGN)
    for marker in (
        "duplicate JSON object keys",
        "unknown contract fields",
        "missing required fields",
        "invalid enum values",
        "BootstrapSerializationError",
    ):
        assert marker in text


def test_round_trip_preserves_phase_and_evidence_semantics() -> None:
    text = read(DESIGN)
    assert "round-trip without losing modes" in text
    assert "ordered plan/effect/apply/validation evidence" in text
    assert "absent-phase distinction" in text


def test_deserialization_never_executes_runtime() -> None:
    text = read(DESIGN)
    assert "must not call `run_bootstrap`, plan, preview, apply, or validate" in text
    assert "callers explicitly" in text
    assert "invoke runtime operations separately" in text


def test_serialization_has_no_executable_object_hooks() -> None:
    text = read(DESIGN) + read(ARCHITECTURE)
    assert "never accepts arbitrary Python object hooks" in text
    assert "executable type metadata" in text


def test_deferred_boundaries_and_pending_gates() -> None:
    text = read(DESIGN)
    for marker in (
        "Binary formats",
        "schema migration",
        "digital signing",
        "remote execution",
        "plugin-defined payload extensions",
        "Focused tests --- Passed",
        "Terminal design acceptance --- Accepted",
        "Production implementation --- Accepted / Completed",
        "v1.3.0 Acceptance --- Accepted",
    ):
        assert marker in text


def test_terminal_acceptance_preserves_implementation_boundary() -> None:
    text = read(ACCEPTANCE)
    assert "Accepted --- Completed" in text
    assert "Design PR --- #263" in text
    assert "0ef961e52860434d6631f76859f0cc7c8dbd8af9" in text
    assert "Post-merge focused verification --- 11 passed" in text
    assert "Production implementation --- Accepted / Completed" in text
    assert "minimum serialization implementation slice" in text


def test_implementation_alignment_requires_separate_acceptance() -> None:
    text = read(ALIGNMENT)
    assert "Accepted --- Terminally Closed" in text
    assert "Implementation PR --- #265" in text
    assert "0407b4986d60578183546e98f5dc57aff890f4a7" in text
    assert "Post-merge focused verification --- 30 passed" in text
    assert "2551 passed, 56 skipped, 1 deselected" in text
    assert "Coverage --- 90.94%" in text
    assert "Implementation acceptance --- Accepted / Completed" in text
    assert (ROOT / "generator/sdk/bootstrap_serialization.py").is_file()


def test_production_implementation_is_terminally_accepted() -> None:
    text = read(IMPLEMENTATION_ACCEPTANCE)
    assert "Accepted --- Completed" in text
    assert "Implementation PR --- #265" in text
    assert "0407b4986d60578183546e98f5dc57aff890f4a7" in text
    assert "Alignment PR --- #266" in text
    assert "bcf53936c5dfc16473c0e571ed8aceb8b747a549" in text
    assert "Post-alignment focused verification --- 31 passed" in text
    assert "v1.3.0 Production implementation --- Accepted / Completed" in text
    assert "Next roadmap slice --- Pending explicit Design First definition" in text
