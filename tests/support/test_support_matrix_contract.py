"""Contract tests for the v1 support matrix."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SUPPORT_MATRIX_PATH = REPO_ROOT / "docs" / "reference" / "support-matrix.md"
KNOWN_LIMITATIONS_PATH = REPO_ROOT / "docs" / "releases" / "v1.0-known-limitations.md"

CANONICAL_STATUSES = frozenset(
    {
        "Supported",
        "Experimental",
        "Known Limitation",
        "Deferred",
    }
)

REQUIRED_SUPPORTED_EVIDENCE_MARKERS = frozenset(
    {
        "GitHub Actions / CI coverage",
        "deterministic automated tests",
        "built-artifact / clean-install verification",
        "explicit release-readiness verification",
    }
)


@pytest.fixture(scope="module")
def support_matrix_text() -> str:
    """Return normalized support-matrix text."""
    if not SUPPORT_MATRIX_PATH.is_file():
        pytest.fail(
            f"Missing Step 8.7 support matrix: {SUPPORT_MATRIX_PATH.relative_to(REPO_ROOT)}"
        )

    return _normalize_markdown(SUPPORT_MATRIX_PATH.read_text(encoding="utf-8"))


@pytest.fixture(scope="module")
def known_limitations_text() -> str:
    """Return normalized known-limitations text."""
    if not KNOWN_LIMITATIONS_PATH.is_file():
        pytest.fail(
            "Missing Step 8.7 known-limitations document: "
            f"{KNOWN_LIMITATIONS_PATH.relative_to(REPO_ROOT)}"
        )

    return _normalize_markdown(KNOWN_LIMITATIONS_PATH.read_text(encoding="utf-8"))


def _normalize_markdown(text: str) -> str:
    """Normalize wrapping and lightweight Markdown emphasis."""
    text = text.replace("**", "").replace("__", "")
    return re.sub(r"\s+", " ", text).strip()


def _assert_all_present(text: str, required: frozenset[str]) -> None:
    """Assert that all required semantic markers are present."""
    missing = sorted(marker for marker in required if marker not in text)
    assert missing == [], f"Missing required support-policy markers: {missing}"


def _extract_markdown_table_rows(raw_text: str) -> list[list[str]]:
    """Extract simple pipe-table rows, excluding separators."""
    rows: list[list[str]] = []

    for line in raw_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or not stripped.endswith("|"):
            continue

        cells = [cell.strip() for cell in stripped.strip("|").split("|")]

        if all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells):
            continue

        rows.append(cells)

    return rows


def test_support_matrix_document_exists() -> None:
    """Step 8.7 must have one canonical support-matrix document."""
    assert SUPPORT_MATRIX_PATH.is_file()


def test_support_matrix_defines_canonical_status_vocabulary(
    support_matrix_text: str,
) -> None:
    """All Step 8.7 support classifications must be explicitly defined."""
    _assert_all_present(support_matrix_text, CANONICAL_STATUSES)


def test_supported_claims_require_explicit_evidence(
    support_matrix_text: str,
) -> None:
    """Supported status must be evidence-backed rather than inferred."""
    assert "A Supported claim requires at least one of" in support_matrix_text
    _assert_all_present(
        support_matrix_text,
        REQUIRED_SUPPORTED_EVIDENCE_MARKERS,
    )
    assert (
        "A one-off local success on an untracked environment is not "
        "sufficient for a Supported claim." in support_matrix_text
    )


def test_observed_or_implemented_does_not_equal_supported(
    support_matrix_text: str,
) -> None:
    """Implementation presence alone must not create a support promise."""
    assert "Observed locally ≠ Supported" in support_matrix_text
    assert "Implemented ≠ Supported" in support_matrix_text
    assert "Documented ≠ Supported" in support_matrix_text


def test_environment_support_is_evidence_based(
    support_matrix_text: str,
) -> None:
    """Python and OS support must not exceed actual CI/release evidence."""
    assert (
        "Python version support → Supported only when explicitly "
        "represented in CI or release verification" in support_matrix_text
    )
    assert (
        "OS support → Supported only when directly exercised by CI / "
        "release verification" in support_matrix_text
    )
    assert "Ubuntu (`ubuntu-latest`) + Python 3.14" in support_matrix_text
    assert "Windows + Python 3.14.5" in support_matrix_text
    assert (
        "Other Python versions and operating systems may work, but are "
        "unverified and are not part of the maintained v1.0 support "
        "commitment." in support_matrix_text
    )


def test_experimental_is_not_stable_support(
    support_matrix_text: str,
) -> None:
    """Experimental capability must not be presented as Stable support."""
    assert "Experimental" in support_matrix_text
    assert (
        "does not receive the same support commitment as Supported behavior" in support_matrix_text
    )
    assert "avoid implying Stable compatibility support" in support_matrix_text


def test_deferred_is_outside_v1_scope(
    support_matrix_text: str,
) -> None:
    """Deferred capability must remain outside the v1 support promise."""
    assert "Deferred items are not defects in v1.0" in support_matrix_text
    assert "outside the v1.0 release scope" in support_matrix_text


def test_step_8_2_remains_stable_surface_source_of_truth(
    support_matrix_text: str,
) -> None:
    """Step 8.7 must not redefine Step 8.2 public-contract classification."""
    assert (
        "Step 8.7 does not widen the Step 8.2 Stable public-contract surface."
        in support_matrix_text
    )
    assert (
        "Step 8.2 remains authoritative for Stable contract classification." in support_matrix_text
    )


def test_step_8_8_release_automation_ownership_remains_separate(
    support_matrix_text: str,
) -> None:
    """Support governance must not pre-empt release automation ownership."""
    assert "Step 8.7 does not pre-empt Step 8.8 release automation." in (support_matrix_text)


def test_support_matrix_contains_evidence_column() -> None:
    """The canonical matrix schema must include an Evidence column."""
    raw = SUPPORT_MATRIX_PATH.read_text(encoding="utf-8")
    rows = _extract_markdown_table_rows(raw)

    header = next(
        (
            row
            for row in rows
            if row
            == [
                "Area",
                "Capability / Environment",
                "Status",
                "Evidence",
                "Notes",
            ]
        ),
        None,
    )

    assert header is not None


def test_every_current_supported_table_row_has_evidence() -> None:
    """Every concrete Supported row in the current matrix must cite evidence."""
    raw = SUPPORT_MATRIX_PATH.read_text(encoding="utf-8")
    rows = _extract_markdown_table_rows(raw)

    data_rows = [
        row for row in rows if len(row) == 5 and row[0] != "Area" and row[2] in CANONICAL_STATUSES
    ]

    supported_rows = [row for row in data_rows if row[2] == "Supported"]

    assert supported_rows, "Expected at least one Supported matrix row"

    missing_evidence = [
        row
        for row in supported_rows
        if not row[3] or row[3].lower() in {"none", "n/a", "tbd", "pending"}
    ]

    assert missing_evidence == [], (
        f"Supported matrix rows must include evidence: {missing_evidence}"
    )


def test_support_matrix_and_known_limitations_cross_reference_each_other(
    support_matrix_text: str,
    known_limitations_text: str,
) -> None:
    """The two Step 8.7 governing documents must explicitly cross-reference."""
    assert "docs/releases/v1.0-known-limitations.md" in support_matrix_text
    assert "docs/reference/support-matrix.md" in known_limitations_text


def test_support_matrix_preserves_core_network_independence(
    support_matrix_text: str,
) -> None:
    """Supported core verification must remain deterministic and network-light."""
    assert (
        "Normal core verification is intended to remain deterministic "
        "and network-independent." in support_matrix_text
    )
    assert "paid AI account" in support_matrix_text
    assert "external Marketplace service availability" in support_matrix_text
