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


# v1.3.3-release-evidence-verification-orchestration-tests


def _orchestration_imports():
    from generator.release_automation import (
        ReleaseEvidenceVerificationOrchestrator,
        VerificationFindingCode,
        VerificationFindingStage,
        VerificationRequest,
    )

    return (
        ReleaseEvidenceVerificationOrchestrator,
        VerificationFindingCode,
        VerificationFindingStage,
        VerificationRequest,
    )


class StaticAdapter:
    def __init__(self, observation=None, error=None) -> None:
        self.observation = observation
        self.error = error
        self.calls = []

    def collect(self, *args):
        self.calls.append(args)
        if self.error is not None:
            raise self.error
        return self.observation


def _repository_observation(**changes):
    from generator.release_automation import RepositoryObservation

    values = dict(
        repository="khwang1964/OpenProjectLab",
        branch="main",
        head_sha=SHA,
        origin_main_sha=SHA,
        remote_url="git@github.com:khwang1964/OpenProjectLab.git",
        is_clean=True,
    )
    values.update(changes)
    return RepositoryObservation(**values)


def _pull_request_observation(**changes):
    from generator.release_automation import PullRequestObservation

    values = dict(
        number=280,
        url="https://github.com/khwang1964/OpenProjectLab/pull/280",
        state=PullRequestState.MERGED,
        base_branch="main",
        head_branch="docs/example",
        checks=(CheckEvidence("quality", CheckConclusion.PASSED),),
        merge_sha=SHA,
        merged_at="2026-08-29T12:20:10Z",
    )
    values.update(changes)
    return PullRequestObservation(**values)


def _request(**changes):
    *_, VerificationRequest = _orchestration_imports()
    values = dict(
        expected_repository="khwang1964/OpenProjectLab",
        expected_branch="main",
        expected_sha=SHA,
        pull_request_number=280,
        focused_tests=ReleaseTestEvidence(passed=11),
    )
    values.update(changes)
    return VerificationRequest(**values)


def test_orchestrator_composes_valid_immutable_report() -> None:
    ReleaseEvidenceVerificationOrchestrator, *_ = _orchestration_imports()
    report = ReleaseEvidenceVerificationOrchestrator(
        StaticAdapter(_repository_observation()),
        StaticAdapter(_pull_request_observation()),
    ).verify(_request())
    assert report.is_valid
    assert report.evidence is not None
    assert report.evidence.focused_tests == ReleaseTestEvidence(passed=11)
    with pytest.raises(FrozenInstanceError):
        report.evidence = None  # type: ignore[misc]


def test_orchestrator_collects_repository_before_pull_request() -> None:
    ReleaseEvidenceVerificationOrchestrator, *_ = _orchestration_imports()
    repository = StaticAdapter(_repository_observation())
    github = StaticAdapter(_pull_request_observation())
    ReleaseEvidenceVerificationOrchestrator(repository, github).verify(_request())
    assert repository.calls == [()]
    assert github.calls == [(280,)]


def test_collection_failure_returns_no_partial_observations() -> None:
    ReleaseEvidenceVerificationOrchestrator, _, Stage, _ = _orchestration_imports()
    error = EvidenceCollectionError(CollectionFailureCode.COMMAND_FAILED, "boom")
    report = ReleaseEvidenceVerificationOrchestrator(
        StaticAdapter(_repository_observation()), StaticAdapter(error=error)
    ).verify(_request())
    assert not report.is_valid
    assert report.repository is report.pull_request is report.evidence is None
    assert report.findings[0].stage is Stage.COLLECTION


@pytest.mark.parametrize(
    ("repository_changes", "pr_changes", "expected_code"),
    [
        ({"is_clean": False}, {}, "dirty_tree"),
        ({"origin_main_sha": "b" * 40}, {}, "unsynchronized_main"),
        ({}, {"state": PullRequestState.OPEN}, "pull_request_not_merged"),
        ({}, {"base_branch": "release"}, "pull_request_base_mismatch"),
        ({}, {"merge_sha": None}, "missing_merge_identity"),
        ({}, {"merge_sha": "b" * 40}, "merge_sha_mismatch"),
    ],
)
def test_identity_and_lifecycle_contradictions_fail_closed(
    repository_changes, pr_changes, expected_code
) -> None:
    ReleaseEvidenceVerificationOrchestrator, *_ = _orchestration_imports()
    report = ReleaseEvidenceVerificationOrchestrator(
        StaticAdapter(_repository_observation(**repository_changes)),
        StaticAdapter(_pull_request_observation(**pr_changes)),
    ).verify(_request())
    assert not report.is_valid
    assert expected_code in tuple(str(finding.code) for finding in report.findings)


def test_pending_ci_and_missing_focused_tests_remain_validation_failures() -> None:
    ReleaseEvidenceVerificationOrchestrator, _, Stage, _ = _orchestration_imports()
    report = ReleaseEvidenceVerificationOrchestrator(
        StaticAdapter(_repository_observation()),
        StaticAdapter(
            _pull_request_observation(checks=(CheckEvidence("quality", CheckConclusion.PENDING),))
        ),
    ).verify(_request(focused_tests=None))
    assert tuple(finding.stage for finding in report.findings) == (
        Stage.VALIDATION,
        Stage.VALIDATION,
    )


# v1.3.4-read-only-verification-runtime-wiring-tests


def _runtime_imports():
    from generator.release_automation import (
        ReadOnlyVerificationCommandExecutor,
        VerificationRuntimeConfiguration,
        build_verification_runtime,
    )

    return (
        ReadOnlyVerificationCommandExecutor,
        VerificationRuntimeConfiguration,
        build_verification_runtime,
    )


class RecordingProcess:
    def __init__(self, result: CommandResult | None = None) -> None:
        self.result = result if result is not None else CommandResult("ok")
        self.calls = []

    def __call__(self, command, working_directory, timeout_seconds, environment):
        self.calls.append((command, working_directory, timeout_seconds, environment))
        return self.result


def test_runtime_configuration_is_immutable_and_deterministic(tmp_path) -> None:
    _, Configuration, _ = _runtime_imports()
    configuration = Configuration(
        tmp_path,
        environment=(("Z", "last"), ("A", "first")),
    )
    assert configuration.environment == (("A", "first"), ("Z", "last"))
    with pytest.raises(FrozenInstanceError):
        configuration.timeout_seconds = 1  # type: ignore[misc]


@pytest.mark.parametrize(
    "changes",
    [
        {"git_executable": " "},
        {"gh_executable": ""},
        {"timeout_seconds": 0},
        {"environment": (("A", "1"), ("A", "2"))},
    ],
)
def test_runtime_configuration_rejects_invalid_policy(tmp_path, changes) -> None:
    _, Configuration, _ = _runtime_imports()
    with pytest.raises(ValueError):
        Configuration(tmp_path, **changes)


def test_executor_runs_allowed_git_command_with_explicit_runtime(tmp_path) -> None:
    Executor, Configuration, _ = _runtime_imports()
    process = RecordingProcess(CommandResult("main"))
    executor = Executor(
        Configuration(
            tmp_path,
            git_executable="custom-git",
            timeout_seconds=7,
            environment=(("LANG", "C"),),
        ),
        process,
    )
    assert executor(("git", "branch", "--show-current")) == CommandResult("main")
    assert process.calls == [
        (("custom-git", "branch", "--show-current"), tmp_path, 7, {"LANG": "C"})
    ]


def test_executor_accepts_exact_github_read_command(tmp_path) -> None:
    Executor, Configuration, _ = _runtime_imports()
    process = RecordingProcess()
    executor = Executor(Configuration(tmp_path, gh_executable="custom-gh"), process)
    fields = "number,url,state,baseRefName,headRefName,mergeCommit,mergedAt,statusCheckRollup"
    executor(("gh", "pr", "view", "284", "--json", fields))
    assert process.calls[0][0][0] == "custom-gh"


@pytest.mark.parametrize(
    "command",
    [
        ("git", "push"),
        ("git", "status", "--porcelain", "--ignored"),
        ("gh", "pr", "merge", "284"),
        ("gh", "pr", "view", "0", "--json", "number"),
    ],
)
def test_executor_rejects_commands_outside_policy_before_execution(tmp_path, command) -> None:
    Executor, Configuration, _ = _runtime_imports()
    process = RecordingProcess()
    executor = Executor(Configuration(tmp_path), process)
    with pytest.raises(EvidenceCollectionError) as raised:
        executor(command)
    assert raised.value.code is CollectionFailureCode.MALFORMED_FIELD
    assert process.calls == []


def test_factory_wires_components_without_running_process(tmp_path) -> None:
    _, Configuration, build_runtime = _runtime_imports()
    process = RecordingProcess()
    runtime = build_runtime(Configuration(tmp_path), process)
    assert runtime.command.configuration.working_directory == tmp_path
    assert runtime.repository_adapter is not None
    assert runtime.github_adapter is not None
    assert runtime.validator is not None
    assert runtime.orchestrator is not None
    assert process.calls == []
