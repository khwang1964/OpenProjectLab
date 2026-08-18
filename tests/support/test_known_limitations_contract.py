"""Contract tests for the v1 known-limitations register."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
KNOWN_LIMITATIONS_PATH = REPO_ROOT / "docs" / "releases" / "v1.0-known-limitations.md"
SUPPORT_MATRIX_PATH = REPO_ROOT / "docs" / "reference" / "support-matrix.md"

CANONICAL_CLASSIFICATIONS = frozenset(
    {
        "Supported",
        "Experimental",
        "Known Limitation",
        "Deferred",
    }
)


@pytest.fixture(scope="module")
def known_limitations_text() -> str:
    """Return normalized known-limitations text."""
    if not KNOWN_LIMITATIONS_PATH.is_file():
        pytest.fail(
            "Missing Step 8.7 known-limitations document: "
            f"{KNOWN_LIMITATIONS_PATH.relative_to(REPO_ROOT)}"
        )

    return _normalize_markdown(KNOWN_LIMITATIONS_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def support_matrix_text() -> str:
    """Return normalized support-matrix text."""
    if not SUPPORT_MATRIX_PATH.is_file():
        pytest.fail(
            f"Missing Step 8.7 support matrix: {SUPPORT_MATRIX_PATH.relative_to(REPO_ROOT)}"
        )

    return _normalize_markdown(SUPPORT_MATRIX_PATH.read_text(encoding="utf-8"))


def _normalize_markdown(text: str) -> str:
    """Normalize wrapping and lightweight Markdown emphasis."""
    text = text.replace("**", "").replace("__", "")
    return re.sub(r"\s+", " ", text).strip()


def _extract_register_rows(raw_text: str) -> list[list[str]]:
    """Extract KL register rows from the canonical Markdown table."""
    rows: list[list[str]] = []

    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue

        cells = [cell.strip() for cell in stripped.strip("|").split("|")]

        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue

        if cells and re.fullmatch(r"KL-\d{3}", cells[0]):
            rows.append(cells)

    return rows


def test_known_limitations_document_exists() -> None:
    """Step 8.7 must have a canonical known-limitations document."""
    assert KNOWN_LIMITATIONS_PATH.is_file()


def test_known_limitations_defines_canonical_classifications(
    known_limitations_text: str,
) -> None:
    """The limitation register must use the canonical Step 8.7 vocabulary."""
    missing = sorted(
        classification
        for classification in CANONICAL_CLASSIFICATIONS
        if classification not in known_limitations_text
    )
    assert missing == [], f"Missing limitation classifications: {missing}"


def test_known_limitation_and_deferred_are_distinct(
    known_limitations_text: str,
) -> None:
    """In-scope constraints must remain distinct from out-of-scope capability."""
    assert "Use Known Limitation when:" in known_limitations_text
    assert "Use Deferred when:" in known_limitations_text
    assert "absence does not block v1.0 acceptance" in known_limitations_text


def test_experimental_is_not_stable(
    known_limitations_text: str,
) -> None:
    """Experimental behavior must not be presented as Stable."""
    assert "support evidence or compatibility commitment is incomplete" in (known_limitations_text)
    assert "not part of the full Stable v1.0 support promise" in (known_limitations_text)


def test_known_limitation_register_has_expected_schema() -> None:
    """The canonical KL register must include identity, impact, and mitigation."""
    raw = KNOWN_LIMITATIONS_PATH.read_text(encoding="utf-8")

    expected_header = (
        "| ID | Area | Classification | Limitation | Impact | Mitigation / Workaround | Target |"
    )

    assert expected_header in raw


def test_known_limitation_ids_are_unique_and_stable_shaped() -> None:
    """Published KL identities must use unique KL-NNN identifiers."""
    rows = _extract_register_rows(KNOWN_LIMITATIONS_PATH.read_text(encoding="utf-8"))

    ids = [row[0] for row in rows]

    assert ids, "Expected at least one KL register entry"
    assert all(re.fullmatch(r"KL-\d{3}", limitation_id) for limitation_id in ids)
    assert len(ids) == len(set(ids)), f"Duplicate known-limitation IDs: {ids}"


def test_every_register_entry_has_required_fields() -> None:
    """Every KL row must include classification, impact, mitigation, and target."""
    rows = _extract_register_rows(KNOWN_LIMITATIONS_PATH.read_text(encoding="utf-8"))

    malformed = [row for row in rows if len(row) != 7]
    assert malformed == [], f"Malformed KL rows: {malformed}"

    incomplete = [row for row in rows if any(not cell.strip() for cell in row)]
    assert incomplete == [], f"Incomplete KL rows: {incomplete}"


def test_every_register_classification_is_canonical() -> None:
    """KL rows must not invent unsupported classification labels."""
    rows = _extract_register_rows(KNOWN_LIMITATIONS_PATH.read_text(encoding="utf-8"))

    invalid = [row for row in rows if row[2] not in CANONICAL_CLASSIFICATIONS]

    assert invalid == [], f"Invalid KL classifications: {invalid}"


def test_every_known_limitation_has_impact_and_mitigation() -> None:
    """Known Limitation entries must communicate impact and a workaround."""
    rows = _extract_register_rows(KNOWN_LIMITATIONS_PATH.read_text(encoding="utf-8"))

    known_rows = [row for row in rows if row[2] == "Known Limitation"]

    assert known_rows, "Expected at least one Known Limitation entry"

    bad_rows = [
        row
        for row in known_rows
        if row[4].lower() in {"", "none", "n/a", "tbd", "pending"}
        or row[5].lower() in {"", "none", "n/a", "tbd", "pending"}
    ]

    assert bad_rows == [], (
        f"Known Limitation rows require impact and mitigation/workaround: {bad_rows}"
    )


def test_deferred_entries_are_not_presented_as_supported() -> None:
    """Deferred items must not be represented as v1.0 Supported capability."""
    rows = _extract_register_rows(KNOWN_LIMITATIONS_PATH.read_text(encoding="utf-8"))

    deferred_rows = [row for row in rows if row[2] == "Deferred"]

    assert deferred_rows, "Expected at least one Deferred entry"

    for row in deferred_rows:
        combined = " ".join(row).lower()
        assert "supported" not in combined or "not supported" in combined


def test_environment_uncertainty_is_explicit(
    known_limitations_text: str,
) -> None:
    """Only explicitly evidenced Python/OS combinations may be supported."""
    assert "Exact Python and OS Matrix Must Be Evidence-Based" in (known_limitations_text)
    assert "no unverified Python-version range is advertised" in (known_limitations_text)
    assert (
        "no operating system is marked Supported merely because the code "
        "is portable Python" in known_limitations_text
    )
    assert (
        "Other Python/OS combinations may work, but they are unverified "
        "and carry no v1.0 support commitment." in known_limitations_text
    )


def test_live_ai_boundary_is_experimental(
    known_limitations_text: str,
) -> None:
    """Live-provider operation must remain optional/experimental."""
    assert "Live AI Provider Operation" in known_limitations_text
    assert "Experimental / Optional Operational Verification" in (known_limitations_text)
    assert "FakeAIProvider" in known_limitations_text


def test_cross_generator_rollback_is_a_known_limitation(
    known_limitations_text: str,
) -> None:
    """Composition must not accidentally promise generalized rollback."""
    assert "Courseware Composition Transaction Limitation" in (known_limitations_text)
    assert "does not promise generalized cross-Generator rollback" in (known_limitations_text)


def test_internal_paths_are_not_supported_apis(
    known_limitations_text: str,
) -> None:
    """Importability of Internal modules must not create a support promise."""
    assert "Internal Module Paths Are Not Supported APIs" in (known_limitations_text)
    assert "generator.sdk" in known_limitations_text


def test_built_artifact_boundary_is_explicit(
    known_limitations_text: str,
) -> None:
    """Installed-user support must be based on built artifacts."""
    assert "Editable-Install-Only Behavior Is Not a Release Guarantee" in (known_limitations_text)
    assert "Validate release behavior against the built wheel." in (known_limitations_text)


def test_documentation_language_boundary_is_explicit(
    known_limitations_text: str,
) -> None:
    """Only EN and zh-TW are maintained documentation languages for v1.0."""
    assert "Documentation Language Boundary" in known_limitations_text
    assert "English" in known_limitations_text
    assert "Traditional Chinese (Taiwan)" in known_limitations_text


def test_step_8_8_ownership_is_preserved(
    known_limitations_text: str,
) -> None:
    """Known-limitations work must not pre-empt release automation."""
    assert "Release Automation Not Yet Owned by Step 8.7" in (known_limitations_text)
    assert "Step 8.8 --- Release Automation & Reproducibility" in (known_limitations_text)


def test_support_matrix_and_limitations_do_not_conflict_on_deferred_scope(
    known_limitations_text: str,
    support_matrix_text: str,
) -> None:
    """Both governing docs must preserve the same Deferred ownership."""
    shared_deferred_markers = (
        ("remote Marketplace service", "remote Marketplace service"),
        ("Marketplace CLI", "Marketplace CLI"),
        ("general dependency solving", "general dependency resolver"),
        ("AI Provider Marketplace", "AI Provider Marketplace"),
    )

    for limitations_marker, support_marker in shared_deferred_markers:
        assert limitations_marker in known_limitations_text
        assert support_marker in support_matrix_text
