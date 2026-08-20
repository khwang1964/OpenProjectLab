"""Fail-closed governing-contract tests for v1.0 GA Acceptance."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PYPROJECT = REPO_ROOT / "pyproject.toml"
ROADMAP = REPO_ROOT / "docs" / "roadmap.md"
GA_CONTRACT = REPO_ROOT / "docs" / "releases" / "v1.0-ga-acceptance.md"
RC_CONTRACT = REPO_ROOT / "docs" / "releases" / "v1.0-rc-acceptance.md"
RC_RECORD = REPO_ROOT / "docs" / "releases" / "v1.0-rc-acceptance-record.md"

EXPECTED_CURRENT_VERSION = "1.0.0rc1"
EXPECTED_RC = "v1.0.0-rc.1"
EXPECTED_GA = "v1.0.0"


def _read(path: Path) -> str:
    assert path.is_file(), f"Required GA acceptance file is missing: {path}"
    return path.read_text(encoding="utf-8")


def _normalized(path: Path) -> str:
    return " ".join(_read(path).split())


def _metadata_value(document: str, label: str) -> str:
    pattern = re.compile(
        rf"^>\s*\*\*{re.escape(label)}:\*\*\s*(?P<value>.+?)\\?\s*$",
        re.MULTILINE,
    )
    match = pattern.search(document)
    assert match is not None, f"Missing required metadata field: {label}"
    return match.group("value").strip()


def _project_version() -> str:
    data = tomllib.loads(_read(PYPROJECT))
    project = data["project"]
    assert isinstance(project, dict)
    version = project["version"]
    assert isinstance(version, str)
    return version


def _roadmap_step_section(roadmap: str, step: str) -> str:
    heading = re.compile(rf"^## Step {re.escape(step)}\b.*$", re.MULTILINE)
    match = heading.search(roadmap)
    assert match is not None, f"Roadmap section for Step {step} is missing"

    next_heading = re.compile(r"^## Step 8\.\d+\b.*$", re.MULTILINE)
    next_match = next_heading.search(roadmap, match.end())
    end = next_match.start() if next_match is not None else len(roadmap)
    return roadmap[match.start() : end]


def _roadmap_status(roadmap: str, step: str) -> str:
    section = _roadmap_step_section(roadmap, step)
    match = re.search(r"^\*\*Status:\*\*\s*(?P<status>.+?)\s*$", section, re.MULTILINE)
    assert match is not None, f"Roadmap Step {step} has no explicit status"
    return match.group("status").strip()


def test_ga_acceptance_governing_document_exists() -> None:
    assert GA_CONTRACT.is_file()


def test_ga_contract_metadata_identifies_ga_gate() -> None:
    document = _read(GA_CONTRACT)

    assert _metadata_value(document, "Status").startswith("Design / Contract Definition")
    assert _metadata_value(document, "Milestone") == "v1.0 GA Acceptance"
    assert _metadata_value(document, "Step").startswith("GA ")
    assert _metadata_value(document, "Target GA") == f"`{EXPECTED_GA}`"


def test_ga_contract_requires_accepted_rc_predecessor() -> None:
    ga = _read(GA_CONTRACT)
    rc_contract = _read(RC_CONTRACT)
    rc_record = _read(RC_RECORD)

    assert _metadata_value(ga, "Predecessor").startswith("Step 8.10")
    assert _metadata_value(ga, "Predecessor").endswith("Accepted")
    assert _metadata_value(ga, "Accepted RC") == f"`{EXPECTED_RC}`"
    assert _metadata_value(rc_contract, "Status") == "Accepted"
    assert _metadata_value(rc_record, "Status") == "Accepted"


def test_current_repository_remains_on_rc_version_before_ga_version_gate() -> None:
    assert _project_version() == EXPECTED_CURRENT_VERSION


def test_ga_contract_keeps_rc_and_ga_identities_distinct() -> None:
    normalized = _normalized(GA_CONTRACT)

    assert EXPECTED_RC in normalized
    assert EXPECTED_GA in normalized
    assert "RC identity" in normalized
    assert "GA identity" in normalized
    assert EXPECTED_RC != EXPECTED_GA


def test_ga_contract_requires_actual_rc_validation_evidence() -> None:
    normalized = _normalized(GA_CONTRACT)

    assert "RC validation / observation evidence" in normalized
    assert "defects discovered after RC publication" in normalized
    assert "GA blocker review" in normalized


def test_ga_contract_defines_fail_closed_issue_classification() -> None:
    normalized = _normalized(GA_CONTRACT)

    for required in (
        "GA blocker",
        "GA correction",
        "Post-GA patch candidate",
        "v1.1+ deferred improvement",
    ):
        assert required in normalized

    assert "must not be reclassified merely to complete the release" in normalized


def test_ga_contract_fixes_canonical_stable_version_and_tag() -> None:
    normalized = _normalized(GA_CONTRACT)

    assert "canonical Python package version is: ```text 1.0.0 ```" in normalized
    assert "canonical human-facing release tag is: ```text v1.0.0 ```" in normalized
    assert "GitHub Release prerelease == false" in normalized


def test_ga_version_transition_is_not_authorized_yet() -> None:
    normalized = _normalized(GA_CONTRACT)

    assert "only after the GA baseline / RC evidence review" in normalized
    assert "GA.1 does not change the package version or create the GA tag" in normalized
    assert "v1.0.0 tag --- Not yet authorized" in normalized


def test_ga_contract_requires_fresh_ga_artifacts() -> None:
    normalized = _normalized(GA_CONTRACT)

    assert "freshly built from the approved GA source commit" in normalized
    assert "openprojectlab-1.0.0-py3-none-any.whl" in normalized
    assert "openprojectlab-1.0.0.tar.gz" in normalized
    assert "SHA256SUMS.txt" in normalized
    assert "RC artifacts such as `1.0.0rc1`" in normalized


def test_ga_contract_requires_artifact_backed_verification_with_zero_required_skips() -> None:
    normalized = _normalized(GA_CONTRACT)

    assert "actual GA wheel" in normalized
    assert "source-checkout isolation" in normalized
    assert "First 15 Minutes workflow" in normalized
    assert "representative installed-user E2E" in normalized
    assert "Required artifact-backed skips: ```text 0 ```" in normalized


def test_ga_contract_preserves_public_compatibility_support_and_docs_boundaries() -> None:
    normalized = _normalized(GA_CONTRACT)

    for required in (
        "Step 8.2 Stable public-contract freeze",
        "Step 8.5 bilingual User Manual parity",
        "Step 8.6 compatibility and deprecation policy",
        "Step 8.7 support matrix and known limitations",
        "EN / zh-TW structure and functional parity",
        "support matrix remains evidence-backed",
        "Known limitations",
    ):
        assert required in normalized


def test_ga_contract_requires_fresh_full_regression_evidence() -> None:
    normalized = _normalized(GA_CONTRACT)

    assert "full pytest" in normalized
    assert "coverage >= 67.0%" in normalized
    assert "Historical RC counts must not be reused as GA completion evidence" in normalized


def test_ga_contract_requires_required_ci_without_pr_publication() -> None:
    normalized = _normalized(GA_CONTRACT)

    assert "Quality checks" in normalized
    assert "Packaging artifact verification" in normalized
    assert "Ordinary PR CI must not publish the GA Release" in normalized


def test_ga_publication_is_draft_first_and_stable() -> None:
    normalized = _normalized(GA_CONTRACT)

    assert "GA publication must be draft-first" in normalized
    assert "draft true before final validation" in normalized
    assert "prerelease false" in normalized
    assert "stable/non-prerelease classification" in normalized


def test_ga_contract_prohibits_rewriting_published_ga_identity() -> None:
    normalized = _normalized(GA_CONTRACT)

    assert "do not force-move the tag" in normalized
    assert "do not replace wheel bytes" in normalized
    assert "do not replace sdist bytes" in normalized
    assert "v1.0.1" in normalized


def test_ga_contract_requires_formal_postmerge_acceptance() -> None:
    normalized = _normalized(GA_CONTRACT)

    for required in (
        "reviewed acceptance PR",
        "required CI passing",
        "squash merge",
        "synchronized `main`",
        "post-merge consistency verification",
        "cross-document terminal-state alignment",
        "no unresolved GA blocker",
    ):
        assert required in normalized


def test_ga_contract_requires_real_evidence_not_placeholders() -> None:
    normalized = _normalized(GA_CONTRACT)

    assert "must include actual evidence" in normalized
    assert "No placeholder counts as completion evidence" in normalized
    assert "No future GA source SHA" in normalized
    assert "is pre-filled by this governing contract" in normalized


def test_ga_contract_does_not_preaccept_ga() -> None:
    """The current GA state must remain unaccepted during contract definition."""
    document = _read(GA_CONTRACT)
    normalized = " ".join(document.split())

    assert "v1.0.0 GA Acceptance --- Not Accepted" in normalized
    assert _metadata_value(document, "Status").startswith("Design / Contract Definition")

    current_state = document.split("## 30. Current State", maxsplit=1)[1]
    current_state = current_state.split("\n---\n", maxsplit=1)[0]

    assert "v1.0.0 GA Acceptance --- Not Accepted" in current_state
    assert "v1.0.0 GA Acceptance --- Accepted" not in current_state


def test_step_8_10_remains_accepted_in_roadmap() -> None:
    roadmap = _read(ROADMAP)
    assert _roadmap_status(roadmap, "8.10") == "Accepted"
