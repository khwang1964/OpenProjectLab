"""Contract tests for the Milestone 8 Step 8.1-8.8 closure state."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RELEASES_DIR = REPO_ROOT / "docs" / "releases"
ROADMAP_PATH = REPO_ROOT / "docs" / "roadmap.md"

STEP_8_9_DESIGN = "v1.0-full-release-readiness-verification.md"
STEP_8_9_ACCEPTANCE = "v1.0-full-release-readiness-verification-acceptance.md"

GOVERNING_DOCUMENTS = {
    "8.1": ("v1.0-release-readiness.md",),
    "8.2": ("v1.0-public-contract-audit.md",),
    "8.3": ("v1.0-reliability-hardening.md",),
    "8.4": ("v1.0-packaging-installation.md",),
    "8.5": ("v1.0-documentation-user-manuals.md",),
    "8.6": ("v1.0-compatibility-deprecation-policy.md",),
    "8.7": (
        "v1.0-known-limitations.md",
        "../reference/support-matrix.md",
    ),
    "8.8": ("v1.0-release-automation-reproducibility.md",),
}

ACCEPTANCE_RECORDS = {
    "8.2": "v1.0-public-contract-freeze-acceptance.md",
    "8.3": "v1.0-reliability-hardening-acceptance.md",
    "8.4": "v1.0-packaging-installation-acceptance.md",
    "8.5": "v1.0-documentation-user-manuals-acceptance.md",
    "8.6": "v1.0-compatibility-deprecation-policy-acceptance.md",
    "8.7": "v1.0-support-matrix-known-limitations-acceptance.md",
    "8.8": "v1.0-release-automation-reproducibility-acceptance.md",
}

FORBIDDEN_CLOSURE_MARKERS = (
    "<actual result>",
    "<PR number>",
    "Pending closure",
    "Formal Acceptance Pending",
)


def _read(path: Path) -> str:
    """Read one required UTF-8 repository document."""
    assert path.is_file(), f"Required Milestone 8 document is missing: {path}"
    return path.read_text(encoding="utf-8")


def _release_path(relative_path: str) -> Path:
    """Resolve one release-owned path without requiring it to exist."""
    return RELEASES_DIR / relative_path


def _metadata_value(document: str, label: str) -> str:
    """Return a blockquote metadata value while tolerating Markdown hard breaks."""
    pattern = re.compile(
        rf"^>\s*\*\*{re.escape(label)}:\*\*\s*(?P<value>.+?)\\?\s*$",
        re.MULTILINE,
    )
    match = pattern.search(document)
    assert match is not None, f"Missing required metadata field: {label}"
    return match.group("value").strip()


def _roadmap_step_section(roadmap: str, step: str) -> str:
    """Return one Step 8.x roadmap section through the next Step heading."""
    heading = re.compile(rf"^## Step {re.escape(step)}\b.*$", re.MULTILINE)
    match = heading.search(roadmap)
    assert match is not None, f"Roadmap section for Step {step} is missing"

    next_heading = re.compile(r"^## Step 8\.\d+\b.*$", re.MULTILINE)
    next_match = next_heading.search(roadmap, match.end())
    end = next_match.start() if next_match is not None else len(roadmap)
    return roadmap[match.start() : end]


def _roadmap_status(roadmap: str, step: str) -> str:
    """Return the explicit status from one Step 8.x roadmap section."""
    section = _roadmap_step_section(roadmap, step)
    match = re.search(r"^\*\*Status:\*\*\s*(?P<status>.+?)\s*$", section, re.MULTILINE)
    assert match is not None, f"Roadmap Step {step} has no explicit status"
    return match.group("status").strip()


def _prior_release_documents() -> tuple[Path, ...]:
    """Return authoritative release documents owned by Steps 8.1-8.8."""
    relative_paths: set[str] = set()

    for documents in GOVERNING_DOCUMENTS.values():
        for relative_path in documents:
            if not relative_path.startswith("../"):
                relative_paths.add(relative_path)

    relative_paths.update(ACCEPTANCE_RECORDS.values())

    return tuple(
        sorted(
            (RELEASES_DIR / relative_path for relative_path in relative_paths),
            key=lambda path: path.name,
        )
    )


@pytest.mark.parametrize(
    ("step", "relative_paths"),
    tuple(GOVERNING_DOCUMENTS.items()),
)
def test_each_completed_milestone_8_step_has_governing_documents(
    step: str,
    relative_paths: tuple[str, ...],
) -> None:
    """Steps 8.1-8.8 must retain every authoritative governing document."""
    missing = [
        str(_release_path(relative_path))
        for relative_path in relative_paths
        if not _release_path(relative_path).is_file()
    ]

    assert missing == [], f"Step {step} is missing governing documents: {missing}"


def test_step_8_1_release_readiness_baseline_is_formally_closed() -> None:
    """The Milestone 8 baseline must not remain Proposed after Step 8.8."""
    baseline = _read(RELEASES_DIR / "v1.0-release-readiness.md")

    assert _metadata_value(baseline, "Status") == "Accepted"


@pytest.mark.parametrize(
    ("step", "filename"),
    tuple(ACCEPTANCE_RECORDS.items()),
)
def test_steps_8_2_through_8_8_have_accepted_records(
    step: str,
    filename: str,
) -> None:
    """Every completed implementation step must have an Accepted record."""
    record = _read(RELEASES_DIR / filename)

    assert _metadata_value(record, "Status") == "Accepted"
    assert _metadata_value(record, "Step").startswith(step)


def test_prior_release_documents_have_no_unresolved_closure_markers() -> None:
    """Accepted Step 8.1-8.8 documents must contain no closure placeholders."""
    unresolved: list[str] = []

    for path in _prior_release_documents():
        document = _read(path)
        for marker in FORBIDDEN_CLOSURE_MARKERS:
            if marker in document:
                unresolved.append(f"{path.relative_to(REPO_ROOT)}: {marker}")

    assert unresolved == [], "Unresolved Milestone 8 closure markers:\n" + "\n".join(unresolved)


def test_step_8_9_design_examples_are_not_scanned_as_prior_step_debt() -> None:
    """Rule examples in the active governing design must not be false positives."""
    design_path = RELEASES_DIR / STEP_8_9_DESIGN
    design = _read(design_path)

    assert "<actual result>" in design
    assert "<PR number>" in design


def test_step_8_9_documents_are_not_scanned_as_prior_step_debt() -> None:
    """Active Step 8.9 records must not be treated as Step 8.1-8.8 debt."""
    design_path = RELEASES_DIR / STEP_8_9_DESIGN
    acceptance_path = RELEASES_DIR / STEP_8_9_ACCEPTANCE

    assert design_path not in _prior_release_documents()
    assert acceptance_path not in _prior_release_documents()


def test_step_8_10_documents_are_not_scanned_as_prior_step_debt() -> None:
    """Active Step 8.10 records must not be treated as Step 8.1-8.8 debt."""
    step_8_10_documents = {
        RELEASES_DIR / "v1.0-rc-acceptance.md",
        RELEASES_DIR / "v1.0-rc-build-artifact-identity.md",
        RELEASES_DIR / "v1.0-rc-artifact-backed-verification.md",
        RELEASES_DIR / "v1.0-rc-creation-publication-identity.md",
        RELEASES_DIR / "v1.0-rc-acceptance-record.md",
    }

    prior_documents = set(_prior_release_documents())

    assert step_8_10_documents.isdisjoint(prior_documents)


def test_prior_release_document_scope_is_explicit_and_complete() -> None:
    """The closure scan must cover exactly the Step 8.1-8.8 release authorities."""
    expected = {
        RELEASES_DIR / relative_path
        for documents in GOVERNING_DOCUMENTS.values()
        for relative_path in documents
        if not relative_path.startswith("../")
    }
    expected.update(RELEASES_DIR / filename for filename in ACCEPTANCE_RECORDS.values())

    assert set(_prior_release_documents()) == expected


def test_roadmap_marks_step_8_1_as_completed() -> None:
    """The baseline slice uses Completed as its approved terminal state."""
    roadmap = _read(ROADMAP_PATH)

    assert _roadmap_status(roadmap, "8.1") == "Completed"


@pytest.mark.parametrize("step", tuple(f"8.{number}" for number in range(2, 9)))
def test_roadmap_marks_steps_8_2_through_8_8_as_accepted(step: str) -> None:
    """Implementation slices must expose their Accepted terminal state."""
    roadmap = _read(ROADMAP_PATH)

    assert _roadmap_status(roadmap, step) == "Accepted"


def test_roadmap_marks_step_8_9_as_accepted() -> None:
    """The completed full-readiness step must expose its Accepted state."""
    roadmap = _read(ROADMAP_PATH)

    assert _roadmap_status(roadmap, "8.9") == "Accepted"


def test_roadmap_does_not_preapprove_step_8_10() -> None:
    """Step 8.9 closure must not pre-approve RC Acceptance."""
    roadmap = _read(ROADMAP_PATH)

    status = _roadmap_status(roadmap, "8.10")

    assert status in {"Planned", "In Progress"}
