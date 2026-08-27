from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DESIGN = ROOT / "docs/releases/v1.3.0-bootstrap-sdk-serialization-contract.md"
ARCHITECTURE = ROOT / "docs/architecture/bootstrap-sdk-serialization-contract.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_design_status_and_predecessor() -> None:
    text = read(DESIGN)
    assert "Design / Contract Definition --- In Progress" in text
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
        "Focused tests --- Pending",
        "Terminal design acceptance --- Pending",
        "Production implementation --- Not Started",
        "v1.3.0 Acceptance --- Not Accepted",
    ):
        assert marker in text
