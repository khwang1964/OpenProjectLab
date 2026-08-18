"""Contract tests for the v1 release workflow."""

from __future__ import annotations

from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "release.yml"


def _load_workflow() -> dict[str, object]:
    """Load the release workflow while normalizing PyYAML YAML 1.1 keys."""
    with WORKFLOW_PATH.open("r", encoding="utf-8") as stream:
        data = yaml.safe_load(stream)

    assert isinstance(data, dict)

    # PyYAML follows YAML 1.1 scalar rules by default and may parse the
    # GitHub Actions key ``on`` as boolean True. GitHub Actions treats
    # ``on`` as the literal workflow-trigger key. Normalize only that
    # parser artifact so the tests validate GitHub's actual schema.
    if "on" not in data and True in data:
        data["on"] = data.pop(True)

    return data


def _jobs(workflow: dict[str, object]) -> dict[str, object]:
    """Return the workflow jobs mapping."""
    jobs = workflow.get("jobs")
    assert isinstance(jobs, dict)
    return jobs


def test_release_workflow_exists() -> None:
    """Step 8.8.4 requires a repository-owned release workflow."""
    assert WORKFLOW_PATH.is_file()


def test_release_workflow_is_not_triggered_by_pull_request() -> None:
    """Untrusted pull-request execution must never publish a release."""
    workflow = _load_workflow()
    triggers = workflow.get("on")

    assert isinstance(triggers, dict)
    assert "pull_request" not in triggers
    assert "pull_request_target" not in triggers


def test_release_workflow_requires_explicit_maintainer_trigger() -> None:
    """Release publication must start from an explicit maintainer action."""
    workflow = _load_workflow()
    triggers = workflow.get("on")

    assert isinstance(triggers, dict)
    assert "workflow_dispatch" in triggers


def test_release_workflow_has_explicit_minimum_top_level_permissions() -> None:
    """Default workflow token permissions must remain read-only."""
    workflow = _load_workflow()
    permissions = workflow.get("permissions")

    assert permissions == {"contents": "read"}


def test_release_workflow_contains_verification_and_publication_jobs() -> None:
    """Verification and publication must remain separate trust boundaries."""
    jobs = _jobs(_load_workflow())

    assert "verify-release" in jobs
    assert "publish-release" in jobs


def test_publication_depends_on_verification() -> None:
    """Publication must not run unless release verification succeeds."""
    jobs = _jobs(_load_workflow())
    publish = jobs["publish-release"]

    assert isinstance(publish, dict)
    assert publish.get("needs") == "verify-release"


def test_verification_job_has_no_write_permission() -> None:
    """Build/test verification must not receive release publication rights."""
    jobs = _jobs(_load_workflow())
    verify = jobs["verify-release"]

    assert isinstance(verify, dict)
    permissions = verify.get("permissions")

    assert permissions in (None, {"contents": "read"})


def test_publication_job_has_only_required_write_permission() -> None:
    """Only the publication job may receive contents write permission."""
    jobs = _jobs(_load_workflow())
    publish = jobs["publish-release"]

    assert isinstance(publish, dict)
    assert publish.get("permissions") == {"contents": "write"}


def test_release_workflow_uses_ubuntu_and_python_314_for_verification() -> None:
    """Release verification must stay on the supported CI runtime."""
    jobs = _jobs(_load_workflow())
    verify = jobs["verify-release"]

    assert isinstance(verify, dict)
    assert verify.get("runs-on") == "ubuntu-latest"

    steps = verify.get("steps")
    assert isinstance(steps, list)

    setup_python_steps = [
        step
        for step in steps
        if isinstance(step, dict) and str(step.get("uses", "")).startswith("actions/setup-python@")
    ]
    assert len(setup_python_steps) == 1

    with_config = setup_python_steps[0].get("with")
    assert isinstance(with_config, dict)
    assert str(with_config.get("python-version")) == "3.14"


def test_release_workflow_cleans_build_outputs_before_build() -> None:
    """Stale dist/build files must not enter a release bundle."""
    jobs = _jobs(_load_workflow())
    verify = jobs["verify-release"]

    assert isinstance(verify, dict)
    steps = verify.get("steps")
    assert isinstance(steps, list)

    commands = "\n".join(str(step.get("run", "")) for step in steps if isinstance(step, dict))

    assert "rm -rf build dist" in commands
    assert "python -m build" in commands


def test_release_workflow_runs_release_contract_tests_before_publication() -> None:
    """Release-specific contract automation must run in verification."""
    jobs = _jobs(_load_workflow())
    verify = jobs["verify-release"]

    assert isinstance(verify, dict)
    steps = verify.get("steps")
    assert isinstance(steps, list)

    commands = "\n".join(str(step.get("run", "")) for step in steps if isinstance(step, dict))

    assert "python -m pytest tests/release -v --no-cov" in commands


def test_release_workflow_verifies_built_artifact_paths() -> None:
    """Installed-user checks must target the exact wheel built by this run."""
    jobs = _jobs(_load_workflow())
    verify = jobs["verify-release"]

    assert isinstance(verify, dict)
    steps = verify.get("steps")
    assert isinstance(steps, list)

    commands = "\n".join(str(step.get("run", "")) for step in steps if isinstance(step, dict))

    assert "OPL_TEST_WHEEL" in commands
    assert "select_current_wheel" in commands
    assert 'Path("dist")' in commands
    assert 'expected_project="openprojectlab"' in commands


def test_release_workflow_generates_checksums_before_upload() -> None:
    """Checksums must be generated before the release bundle is handed off."""
    jobs = _jobs(_load_workflow())
    verify = jobs["verify-release"]

    assert isinstance(verify, dict)
    steps = verify.get("steps")
    assert isinstance(steps, list)

    step_names = [str(step.get("name", "")) for step in steps if isinstance(step, dict)]

    checksum_index = step_names.index("Generate SHA-256 checksums")
    upload_index = step_names.index("Upload verified release bundle")

    assert checksum_index < upload_index


def test_release_workflow_uploads_verified_bundle_between_jobs() -> None:
    """Publication must consume artifacts produced by verification."""
    jobs = _jobs(_load_workflow())
    verify = jobs["verify-release"]
    publish = jobs["publish-release"]

    assert isinstance(verify, dict)
    assert isinstance(publish, dict)

    verify_steps = verify.get("steps")
    publish_steps = publish.get("steps")
    assert isinstance(verify_steps, list)
    assert isinstance(publish_steps, list)

    uploads = [
        step
        for step in verify_steps
        if isinstance(step, dict)
        and str(step.get("uses", "")).startswith("actions/upload-artifact@")
    ]
    downloads = [
        step
        for step in publish_steps
        if isinstance(step, dict)
        and str(step.get("uses", "")).startswith("actions/download-artifact@")
    ]

    assert len(uploads) == 1
    assert len(downloads) == 1

    upload_with = uploads[0].get("with")
    download_with = downloads[0].get("with")
    assert isinstance(upload_with, dict)
    assert isinstance(download_with, dict)

    assert upload_with.get("name") == "verified-release-bundle"
    assert download_with.get("name") == "verified-release-bundle"


def test_release_workflow_reverifies_checksums_in_publication_job() -> None:
    """Publication must verify downloaded artifact bytes before release."""
    jobs = _jobs(_load_workflow())
    publish = jobs["publish-release"]

    assert isinstance(publish, dict)
    steps = publish.get("steps")
    assert isinstance(steps, list)

    commands = "\n".join(str(step.get("run", "")) for step in steps if isinstance(step, dict))

    assert "sha256sum --check SHA256SUMS.txt" in commands


def test_release_workflow_creates_draft_github_release() -> None:
    """GitHub Release publication must use a draft-first boundary."""
    jobs = _jobs(_load_workflow())
    publish = jobs["publish-release"]

    assert isinstance(publish, dict)
    steps = publish.get("steps")
    assert isinstance(steps, list)

    release_steps = [
        step
        for step in steps
        if isinstance(step, dict)
        and str(step.get("uses", "")).startswith("softprops/action-gh-release@")
    ]

    assert len(release_steps) == 1

    with_config = release_steps[0].get("with")
    assert isinstance(with_config, dict)
    assert with_config.get("draft") is True


def test_release_workflow_does_not_publish_to_package_index() -> None:
    """Step 8.8.4 must not silently add PyPI/package-index publication."""
    raw = WORKFLOW_PATH.read_text(encoding="utf-8").lower()

    forbidden = (
        "pypi",
        "twine upload",
        "pypa/gh-action-pypi-publish",
    )

    for marker in forbidden:
        assert marker not in raw
