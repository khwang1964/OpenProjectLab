import json
from dataclasses import FrozenInstanceError

import pytest

from generator.release_automation import (
    CheckConclusion,
    CheckEvidence,
    CollectionFailureCode,
    CommandResult,
    EvidenceCollectionError,
    FindingCode,
    GitHubEvidenceAdapter,
    PullRequestState,
    ReleaseEvidence,
    ReleaseEvidenceValidator,
    RepositoryEvidenceAdapter,
)
from generator.release_automation import (
    TestEvidence as ReleaseTestEvidence,
)

SHA = "a" * 40


def valid_evidence() -> ReleaseEvidence:
    return ReleaseEvidence(
        repository="khwang1964/OpenProjectLab",
        branch="main",
        candidate_sha=SHA,
        checks=(CheckEvidence("quality", CheckConclusion.PASSED),),
        focused_tests=ReleaseTestEvidence(passed=6),
    )


def test_evidence_is_immutable_and_checks_are_deterministic() -> None:
    evidence = ReleaseEvidence(
        repository="khwang1964/OpenProjectLab",
        branch="main",
        candidate_sha=SHA,
        checks=(
            CheckEvidence("z", CheckConclusion.PASSED),
            CheckEvidence("a", CheckConclusion.PASSED),
        ),
        focused_tests=ReleaseTestEvidence(passed=6),
    )
    assert tuple(check.name for check in evidence.checks) == ("a", "z")
    with pytest.raises(FrozenInstanceError):
        evidence.branch = "other"  # type: ignore[misc]


def test_valid_evidence_passes() -> None:
    result = ReleaseEvidenceValidator().validate(
        valid_evidence(),
        expected_repository="khwang1964/OpenProjectLab",
        expected_branch="main",
        expected_sha=SHA,
    )
    assert result.is_valid
    assert result.findings == ()


def test_missing_or_failed_evidence_fails_closed_in_stable_order() -> None:
    evidence = ReleaseEvidence(
        repository="wrong/repository",
        branch="feature",
        candidate_sha="b" * 40,
        checks=(),
    )
    result = ReleaseEvidenceValidator().validate(
        evidence,
        expected_repository="khwang1964/OpenProjectLab",
        expected_branch="main",
        expected_sha=SHA,
    )
    assert not result.is_valid
    assert tuple(finding.code for finding in result.findings) == (
        FindingCode.REPOSITORY_MISMATCH,
        FindingCode.BRANCH_MISMATCH,
        FindingCode.SHA_MISMATCH,
        FindingCode.MISSING_CHECKS,
        FindingCode.FOCUSED_TESTS_NOT_PASSED,
    )


def test_pending_ci_and_failed_focused_tests_fail_closed() -> None:
    evidence = ReleaseEvidence(
        repository="khwang1964/OpenProjectLab",
        branch="main",
        candidate_sha=SHA,
        checks=(CheckEvidence("quality", CheckConclusion.PENDING),),
        focused_tests=ReleaseTestEvidence(passed=5, failed=1),
    )
    result = ReleaseEvidenceValidator().validate(
        evidence,
        expected_repository="khwang1964/OpenProjectLab",
        expected_branch="main",
        expected_sha=SHA,
    )
    assert tuple(finding.code for finding in result.findings) == (
        FindingCode.CI_NOT_PASSED,
        FindingCode.FOCUSED_TESTS_NOT_PASSED,
    )


# v1.3.2-repository-github-evidence-adapters-tests


class MappingRunner:
    def __init__(
        self,
        results: dict[tuple[str, ...], CommandResult],
    ) -> None:
        self.results = results
        self.commands: list[tuple[str, ...]] = []

    def __call__(
        self,
        command: tuple[str, ...],
    ) -> CommandResult:
        self.commands.append(command)

        return self.results[command]


def repository_results() -> dict[
    tuple[str, ...],
    CommandResult,
]:
    return {
        (
            "git",
            "config",
            "--get",
            "remote.origin.url",
        ): CommandResult("git@github.com:khwang1964/OpenProjectLab.git"),
        (
            "git",
            "branch",
            "--show-current",
        ): CommandResult("main"),
        (
            "git",
            "rev-parse",
            "HEAD",
        ): CommandResult(SHA),
        (
            "git",
            "rev-parse",
            "origin/main",
        ): CommandResult(SHA),
        (
            "git",
            "status",
            "--porcelain",
        ): CommandResult(""),
    }


def test_repository_adapter_collects_read_only_observation() -> None:
    runner = MappingRunner(repository_results())
    observation = RepositoryEvidenceAdapter(runner).collect()

    assert observation.repository == ("khwang1964/OpenProjectLab")
    assert observation.branch == "main"
    assert observation.head_sha == SHA
    assert observation.origin_main_sha == SHA
    assert observation.is_clean

    mutating_commands = {
        "add",
        "commit",
        "merge",
        "push",
        "reset",
    }

    assert all(command[0] == "git" for command in runner.commands)
    assert not mutating_commands.intersection(command[1] for command in runner.commands)

    with pytest.raises(FrozenInstanceError):
        observation.branch = "other"  # type: ignore[misc]


def test_repository_adapter_reports_dirty_tree() -> None:
    results = repository_results()
    results[
        (
            "git",
            "status",
            "--porcelain",
        )
    ] = CommandResult(" M file.py")

    observation = RepositoryEvidenceAdapter(MappingRunner(results)).collect()

    assert not observation.is_clean


def test_repository_adapter_fails_on_command_error() -> None:
    results = repository_results()
    results[
        (
            "git",
            "rev-parse",
            "HEAD",
        )
    ] = CommandResult(
        "",
        returncode=1,
    )

    with pytest.raises(EvidenceCollectionError) as raised:
        RepositoryEvidenceAdapter(MappingRunner(results)).collect()

    assert raised.value.code is (CollectionFailureCode.COMMAND_FAILED)


def test_repository_adapter_rejects_bad_remote() -> None:
    results = repository_results()
    results[
        (
            "git",
            "config",
            "--get",
            "remote.origin.url",
        )
    ] = CommandResult("https://example.com/owner/repository.git")

    with pytest.raises(EvidenceCollectionError) as raised:
        RepositoryEvidenceAdapter(MappingRunner(results)).collect()

    assert raised.value.code is (CollectionFailureCode.MALFORMED_FIELD)


def github_payload() -> dict[str, object]:
    return {
        "number": 275,
        "url": ("https://github.com/khwang1964/OpenProjectLab/pull/275"),
        "state": "MERGED",
        "baseRefName": "main",
        "headRefName": "docs/example",
        "mergeCommit": {"oid": SHA},
        "mergedAt": "2026-08-28T00:00:00Z",
        "statusCheckRollup": [
            {
                "name": "quality",
                "conclusion": "SUCCESS",
                "status": "COMPLETED",
            },
            {
                "name": "packaging",
                "conclusion": "FAILURE",
                "status": "COMPLETED",
            },
            {
                "context": "compatibility",
                "state": "PENDING",
            },
        ],
    }


def github_runner(
    payload: object,
) -> MappingRunner:
    command = (
        "gh",
        "pr",
        "view",
        "275",
        "--json",
        ("number,url,state,baseRefName,headRefName,mergeCommit,mergedAt,statusCheckRollup"),
    )

    return MappingRunner({command: CommandResult(json.dumps(payload))})


def test_github_adapter_collects_stable_observation() -> None:
    observation = GitHubEvidenceAdapter(github_runner(github_payload())).collect(275)

    assert observation.state is (PullRequestState.MERGED)
    assert observation.merge_sha == SHA
    assert tuple(check.name for check in observation.checks) == (
        "compatibility",
        "packaging",
        "quality",
    )
    assert tuple(check.conclusion for check in observation.checks) == (
        CheckConclusion.PENDING,
        CheckConclusion.FAILED,
        CheckConclusion.PASSED,
    )


def test_github_adapter_rejects_malformed_json() -> None:
    runner = github_runner(github_payload())
    command = next(iter(runner.results))
    runner.results[command] = CommandResult("not-json")

    with pytest.raises(EvidenceCollectionError) as raised:
        GitHubEvidenceAdapter(runner).collect(275)

    assert raised.value.code is (CollectionFailureCode.MALFORMED_FIELD)


def test_github_adapter_fails_on_unknown_state() -> None:
    payload = github_payload()
    payload["state"] = "UNKNOWN"

    with pytest.raises(EvidenceCollectionError) as raised:
        GitHubEvidenceAdapter(github_runner(payload)).collect(275)

    assert raised.value.code is (CollectionFailureCode.UNKNOWN_STATE)


def test_github_adapter_rejects_missing_field() -> None:
    payload = github_payload()
    payload["url"] = None

    with pytest.raises(EvidenceCollectionError) as raised:
        GitHubEvidenceAdapter(github_runner(payload)).collect(275)

    assert raised.value.code is (CollectionFailureCode.MISSING_FIELD)
