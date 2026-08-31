import json
import subprocess
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class CheckConclusion(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    PENDING = "pending"


@dataclass(frozen=True, slots=True)
class CheckEvidence:
    name: str
    conclusion: CheckConclusion

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("check name must not be empty")


@dataclass(frozen=True, slots=True)
class TestEvidence:
    passed: int
    failed: int = 0
    skipped: int = 0
    deselected: int = 0

    def __post_init__(self) -> None:
        if min(self.passed, self.failed, self.skipped, self.deselected) < 0:
            raise ValueError("test counts must not be negative")


@dataclass(frozen=True, slots=True)
class ReleaseEvidence:
    repository: str
    branch: str
    candidate_sha: str
    checks: tuple[CheckEvidence, ...]
    focused_tests: TestEvidence | None = None

    def __post_init__(self) -> None:
        if not self.repository.strip() or not self.branch.strip():
            raise ValueError("repository and branch must not be empty")
        if len(self.candidate_sha) != 40:
            raise ValueError("candidate SHA must contain 40 characters")
        names = tuple(check.name for check in self.checks)
        if len(names) != len(set(names)):
            raise ValueError("check names must be unique")
        object.__setattr__(self, "checks", tuple(sorted(self.checks, key=lambda check: check.name)))


class FindingCode(StrEnum):
    REPOSITORY_MISMATCH = "repository_mismatch"
    BRANCH_MISMATCH = "branch_mismatch"
    SHA_MISMATCH = "sha_mismatch"
    MISSING_CHECKS = "missing_checks"
    CI_NOT_PASSED = "ci_not_passed"
    FOCUSED_TESTS_NOT_PASSED = "focused_tests_not_passed"


@dataclass(frozen=True, slots=True)
class ValidationFinding:
    code: FindingCode
    message: str


@dataclass(frozen=True, slots=True)
class ValidationResult:
    findings: tuple[ValidationFinding, ...]

    @property
    def is_valid(self) -> bool:
        return not self.findings


class ReleaseEvidenceValidator:
    def validate(
        self,
        evidence: ReleaseEvidence,
        *,
        expected_repository: str,
        expected_branch: str,
        expected_sha: str,
    ) -> ValidationResult:
        findings: list[ValidationFinding] = []
        expected = (
            (FindingCode.REPOSITORY_MISMATCH, evidence.repository, expected_repository),
            (FindingCode.BRANCH_MISMATCH, evidence.branch, expected_branch),
            (FindingCode.SHA_MISMATCH, evidence.candidate_sha, expected_sha),
        )
        for code, actual, wanted in expected:
            if actual != wanted:
                findings.append(ValidationFinding(code, f"expected {wanted!r}, got {actual!r}"))
        if not evidence.checks:
            findings.append(ValidationFinding(FindingCode.MISSING_CHECKS, "required CI is absent"))
        elif any(check.conclusion is not CheckConclusion.PASSED for check in evidence.checks):
            findings.append(
                ValidationFinding(FindingCode.CI_NOT_PASSED, "required CI did not pass")
            )
        if evidence.focused_tests is None or evidence.focused_tests.failed:
            findings.append(
                ValidationFinding(
                    FindingCode.FOCUSED_TESTS_NOT_PASSED,
                    "focused test evidence is absent or failed",
                )
            )
        return ValidationResult(tuple(findings))


# v1.3.2-repository-github-evidence-adapters-implementation


class CollectionFailureCode(StrEnum):
    COMMAND_FAILED = "command_failed"
    MISSING_FIELD = "missing_field"
    MALFORMED_FIELD = "malformed_field"
    UNKNOWN_STATE = "unknown_state"


class EvidenceCollectionError(RuntimeError):
    def __init__(
        self,
        code: CollectionFailureCode,
        message: str,
    ) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True, slots=True)
class CommandResult:
    stdout: str
    returncode: int = 0


type ReadCommand = Callable[[tuple[str, ...]], CommandResult]


@dataclass(frozen=True, slots=True)
class RepositoryObservation:
    repository: str
    branch: str
    head_sha: str
    origin_main_sha: str
    remote_url: str
    is_clean: bool


class PullRequestState(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    MERGED = "MERGED"


@dataclass(frozen=True, slots=True)
class PullRequestObservation:
    number: int
    url: str
    state: PullRequestState
    base_branch: str
    head_branch: str
    checks: tuple[CheckEvidence, ...]
    merge_sha: str | None = None
    merged_at: str | None = None

    def __post_init__(self) -> None:
        ordered = tuple(
            sorted(
                self.checks,
                key=lambda check: check.name,
            )
        )
        object.__setattr__(self, "checks", ordered)


def _is_sha(value: str) -> bool:
    hexadecimal = "0123456789abcdefABCDEF"

    return len(value) == 40 and all(character in hexadecimal for character in value)


class _ReadOnlyAdapter:
    def __init__(self, runner: ReadCommand) -> None:
        self._runner = runner

    def _read(self, *command: str) -> str:
        result = self._runner(tuple(command))

        if result.returncode:
            raise EvidenceCollectionError(
                CollectionFailureCode.COMMAND_FAILED,
                f"read command failed: {' '.join(command)}",
            )

        return result.stdout.strip()


class RepositoryEvidenceAdapter(_ReadOnlyAdapter):
    def collect(self) -> RepositoryObservation:
        remote_url = self._read(
            "git",
            "config",
            "--get",
            "remote.origin.url",
        )
        branch = self._required(
            self._read("git", "branch", "--show-current"),
            "current branch",
        )
        head_sha = self._sha(
            self._read("git", "rev-parse", "HEAD"),
            "HEAD",
        )
        origin_main_sha = self._sha(
            self._read("git", "rev-parse", "origin/main"),
            "origin/main",
        )
        status = self._read("git", "status", "--porcelain")

        return RepositoryObservation(
            repository=self._repository_from_remote(remote_url),
            branch=branch,
            head_sha=head_sha,
            origin_main_sha=origin_main_sha,
            remote_url=self._required(
                remote_url,
                "origin remote",
            ),
            is_clean=not status,
        )

    @staticmethod
    def _required(value: str, field: str) -> str:
        if not value:
            raise EvidenceCollectionError(
                CollectionFailureCode.MISSING_FIELD,
                f"{field} is missing",
            )

        return value

    @staticmethod
    def _sha(value: str, field: str) -> str:
        if not _is_sha(value):
            raise EvidenceCollectionError(
                CollectionFailureCode.MALFORMED_FIELD,
                f"{field} is not a full commit SHA",
            )

        return value

    @staticmethod
    def _repository_from_remote(remote_url: str) -> str:
        prefixes = (
            "git@github.com:",
            "https://github.com/",
        )

        for prefix in prefixes:
            if remote_url.startswith(prefix):
                repository = remote_url.removeprefix(prefix).removesuffix(".git").strip("/")

                if len(repository.split("/")) == 2:
                    return repository

        raise EvidenceCollectionError(
            CollectionFailureCode.MALFORMED_FIELD,
            "origin remote is not a canonical GitHub repository",
        )


class GitHubEvidenceAdapter(_ReadOnlyAdapter):
    def collect(
        self,
        pr_number: int,
    ) -> PullRequestObservation:
        if pr_number <= 0:
            raise EvidenceCollectionError(
                CollectionFailureCode.MALFORMED_FIELD,
                "pull-request number must be positive",
            )

        fields = "number,url,state,baseRefName,headRefName,mergeCommit,mergedAt,statusCheckRollup"
        raw = self._read(
            "gh",
            "pr",
            "view",
            str(pr_number),
            "--json",
            fields,
        )

        try:
            payload = json.loads(raw)
        except json.JSONDecodeError as error:
            raise EvidenceCollectionError(
                CollectionFailureCode.MALFORMED_FIELD,
                "GitHub response is not valid JSON",
            ) from error

        if not isinstance(payload, dict):
            raise EvidenceCollectionError(
                CollectionFailureCode.MALFORMED_FIELD,
                "GitHub response must be an object",
            )

        number = self._positive_int(
            payload.get("number"),
            "pull-request number",
        )

        if number != pr_number:
            raise EvidenceCollectionError(
                CollectionFailureCode.MALFORMED_FIELD,
                "pull-request number does not match the request",
            )

        return PullRequestObservation(
            number=number,
            url=self._required_string(
                payload.get("url"),
                "pull-request URL",
            ),
            state=self._state(payload.get("state")),
            base_branch=self._required_string(
                payload.get("baseRefName"),
                "base branch",
            ),
            head_branch=self._required_string(
                payload.get("headRefName"),
                "head branch",
            ),
            checks=self._checks(payload.get("statusCheckRollup")),
            merge_sha=self._merge_sha(payload.get("mergeCommit")),
            merged_at=self._optional_string(
                payload.get("mergedAt"),
                "merge timestamp",
            ),
        )

    @staticmethod
    def _required_string(
        value: object,
        field: str,
    ) -> str:
        if not isinstance(value, str) or not value.strip():
            raise EvidenceCollectionError(
                CollectionFailureCode.MISSING_FIELD,
                f"{field} is missing",
            )

        return value.strip()

    @staticmethod
    def _optional_string(
        value: object,
        field: str,
    ) -> str | None:
        if value is None:
            return None

        if not isinstance(value, str) or not value.strip():
            raise EvidenceCollectionError(
                CollectionFailureCode.MALFORMED_FIELD,
                f"{field} is malformed",
            )

        return value.strip()

    @staticmethod
    def _positive_int(
        value: object,
        field: str,
    ) -> int:
        if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
            raise EvidenceCollectionError(
                CollectionFailureCode.MALFORMED_FIELD,
                f"{field} must be a positive integer",
            )

        return value

    @staticmethod
    def _state(value: object) -> PullRequestState:
        try:
            return PullRequestState(value)
        except (TypeError, ValueError) as error:
            raise EvidenceCollectionError(
                CollectionFailureCode.UNKNOWN_STATE,
                "pull-request state is unknown",
            ) from error

    @staticmethod
    def _merge_sha(value: object) -> str | None:
        if value is None:
            return None

        if not isinstance(value, dict) or not _is_sha(str(value.get("oid", ""))):
            raise EvidenceCollectionError(
                CollectionFailureCode.MALFORMED_FIELD,
                "merge commit is malformed",
            )

        return str(value["oid"])

    @classmethod
    def _checks(
        cls,
        value: object,
    ) -> tuple[CheckEvidence, ...]:
        if not isinstance(value, list):
            raise EvidenceCollectionError(
                CollectionFailureCode.MISSING_FIELD,
                "required-check observations are missing",
            )

        checks: list[CheckEvidence] = []

        for item in value:
            if not isinstance(item, dict):
                raise EvidenceCollectionError(
                    CollectionFailureCode.MALFORMED_FIELD,
                    "required-check observation is malformed",
                )

            name = item.get("name") or item.get("context")
            conclusion = item.get("conclusion")
            status = item.get("status") or item.get("state")

            checks.append(
                CheckEvidence(
                    cls._required_string(
                        name,
                        "required-check name",
                    ),
                    cls._check_conclusion(
                        conclusion,
                        status,
                    ),
                )
            )

        names = tuple(check.name for check in checks)

        if len(names) != len(set(names)):
            raise EvidenceCollectionError(
                CollectionFailureCode.MALFORMED_FIELD,
                "required-check names must be unique",
            )

        return tuple(
            sorted(
                checks,
                key=lambda check: check.name,
            )
        )

    @staticmethod
    def _check_conclusion(
        conclusion: object,
        status: object,
    ) -> CheckConclusion:
        normalized_conclusion = str(conclusion or "").upper()
        normalized_status = str(status or "").upper()

        if normalized_conclusion == "SUCCESS":
            return CheckConclusion.PASSED

        if not normalized_conclusion and normalized_status == "SUCCESS":
            return CheckConclusion.PASSED

        failed_conclusions = {
            "ACTION_REQUIRED",
            "CANCELLED",
            "FAILURE",
            "STARTUP_FAILURE",
            "TIMED_OUT",
        }

        if normalized_conclusion in failed_conclusions:
            return CheckConclusion.FAILED

        if not normalized_conclusion and normalized_status in {"ERROR", "FAILURE"}:
            return CheckConclusion.FAILED

        pending_states = {
            "EXPECTED",
            "IN_PROGRESS",
            "PENDING",
            "QUEUED",
        }

        if not normalized_conclusion and normalized_status in pending_states:
            return CheckConclusion.PENDING

        raise EvidenceCollectionError(
            CollectionFailureCode.UNKNOWN_STATE,
            "required-check conclusion is unknown",
        )


# v1.3.3-release-evidence-verification-orchestration-implementation


class VerificationFindingStage(StrEnum):
    COLLECTION = "collection"
    CONTRADICTION = "contradiction"
    VALIDATION = "validation"


class VerificationFindingCode(StrEnum):
    COLLECTION_FAILED = "collection_failed"
    DIRTY_TREE = "dirty_tree"
    UNSYNCHRONIZED_MAIN = "unsynchronized_main"
    PULL_REQUEST_NOT_MERGED = "pull_request_not_merged"
    PULL_REQUEST_BASE_MISMATCH = "pull_request_base_mismatch"
    MISSING_MERGE_IDENTITY = "missing_merge_identity"
    MERGE_SHA_MISMATCH = "merge_sha_mismatch"


@dataclass(frozen=True, slots=True)
class VerificationRequest:
    expected_repository: str
    expected_branch: str
    expected_sha: str
    pull_request_number: int
    focused_tests: TestEvidence | None

    def __post_init__(self) -> None:
        if not self.expected_repository.strip() or not self.expected_branch.strip():
            raise ValueError("expected repository and branch must not be empty")
        if not _is_sha(self.expected_sha):
            raise ValueError("expected SHA must be a full commit SHA")
        if self.pull_request_number <= 0:
            raise ValueError("pull-request number must be positive")


@dataclass(frozen=True, slots=True)
class VerificationFinding:
    stage: VerificationFindingStage
    code: str
    message: str


@dataclass(frozen=True, slots=True)
class VerificationReport:
    repository: RepositoryObservation | None
    pull_request: PullRequestObservation | None
    evidence: ReleaseEvidence | None
    findings: tuple[VerificationFinding, ...]

    @property
    def is_valid(self) -> bool:
        return self.evidence is not None and not self.findings


class ReleaseEvidenceVerificationOrchestrator:
    def __init__(
        self,
        repository_adapter: RepositoryEvidenceAdapter,
        github_adapter: GitHubEvidenceAdapter,
        validator: ReleaseEvidenceValidator | None = None,
    ) -> None:
        self._repository_adapter = repository_adapter
        self._github_adapter = github_adapter
        self._validator = validator or ReleaseEvidenceValidator()

    def verify(self, request: VerificationRequest) -> VerificationReport:
        try:
            repository = self._repository_adapter.collect()
            pull_request = self._github_adapter.collect(request.pull_request_number)
        except EvidenceCollectionError as error:
            finding = VerificationFinding(
                VerificationFindingStage.COLLECTION,
                VerificationFindingCode.COLLECTION_FAILED,
                f"{error.code.value}: {error}",
            )
            return VerificationReport(None, None, None, (finding,))

        contradictions: list[VerificationFinding] = []

        def contradiction(code: VerificationFindingCode, message: str) -> None:
            contradictions.append(
                VerificationFinding(VerificationFindingStage.CONTRADICTION, code, message)
            )

        if not repository.is_clean:
            contradiction(VerificationFindingCode.DIRTY_TREE, "working tree is not clean")
        if request.expected_branch == "main" and repository.head_sha != repository.origin_main_sha:
            contradiction(
                VerificationFindingCode.UNSYNCHRONIZED_MAIN,
                "HEAD and origin/main do not agree",
            )
        if pull_request.state is not PullRequestState.MERGED:
            contradiction(
                VerificationFindingCode.PULL_REQUEST_NOT_MERGED,
                "pull request is not merged",
            )
        if pull_request.base_branch != request.expected_branch:
            contradiction(
                VerificationFindingCode.PULL_REQUEST_BASE_MISMATCH,
                "pull-request base does not match the expected branch",
            )
        if pull_request.merge_sha is None or pull_request.merged_at is None:
            contradiction(
                VerificationFindingCode.MISSING_MERGE_IDENTITY,
                "merged pull request lacks merge SHA or timestamp",
            )
        elif pull_request.merge_sha != request.expected_sha:
            contradiction(
                VerificationFindingCode.MERGE_SHA_MISMATCH,
                "pull-request merge SHA does not match the expected SHA",
            )

        evidence = ReleaseEvidence(
            repository=repository.repository,
            branch=repository.branch,
            candidate_sha=repository.head_sha,
            checks=pull_request.checks,
            focused_tests=request.focused_tests,
        )
        validation = self._validator.validate(
            evidence,
            expected_repository=request.expected_repository,
            expected_branch=request.expected_branch,
            expected_sha=request.expected_sha,
        )
        findings = contradictions + [
            VerificationFinding(
                VerificationFindingStage.VALIDATION,
                finding.code.value,
                finding.message,
            )
            for finding in validation.findings
        ]
        return VerificationReport(repository, pull_request, evidence, tuple(findings))


# v1.3.4-read-only-verification-runtime-wiring-implementation


_GITHUB_PR_FIELDS = (
    "number,url,state,baseRefName,headRefName,mergeCommit,mergedAt,statusCheckRollup"
)


@dataclass(frozen=True, slots=True)
class VerificationRuntimeConfiguration:
    working_directory: Path
    git_executable: str = "git"
    gh_executable: str = "gh"
    timeout_seconds: float = 30.0
    environment: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(self, "working_directory", Path(self.working_directory))
        if not self.git_executable.strip() or not self.gh_executable.strip():
            raise ValueError("runtime executable names must not be empty")
        if self.timeout_seconds <= 0:
            raise ValueError("runtime command timeout must be positive")
        environment = tuple(sorted(self.environment))
        if any(
            not isinstance(key, str) or not key or not isinstance(value, str)
            for key, value in environment
        ):
            raise ValueError("runtime environment entries must be non-empty strings")
        keys = tuple(key for key, _ in environment)
        if len(keys) != len(set(keys)):
            raise ValueError("runtime environment keys must be unique")
        object.__setattr__(self, "environment", environment)


type RuntimeProcess = Callable[
    [tuple[str, ...], Path, float, dict[str, str] | None],
    CommandResult,
]


def _run_read_process(
    command: tuple[str, ...],
    working_directory: Path,
    timeout_seconds: float,
    environment: dict[str, str] | None,
) -> CommandResult:
    try:
        completed = subprocess.run(
            command,
            cwd=working_directory,
            env=environment,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired:
        return CommandResult("", returncode=124)
    except OSError, ValueError:
        return CommandResult("", returncode=127)
    return CommandResult(completed.stdout, returncode=completed.returncode)


class ReadOnlyVerificationCommandExecutor:
    def __init__(
        self,
        configuration: VerificationRuntimeConfiguration,
        process: RuntimeProcess = _run_read_process,
    ) -> None:
        self.configuration = configuration
        self._process = process

    def __call__(self, command: tuple[str, ...]) -> CommandResult:
        self._validate(command)
        executable = (
            self.configuration.git_executable
            if command[0] == "git"
            else self.configuration.gh_executable
        )
        environment = (
            dict(self.configuration.environment) if self.configuration.environment else None
        )
        return self._process(
            (executable, *command[1:]),
            self.configuration.working_directory,
            self.configuration.timeout_seconds,
            environment,
        )

    @staticmethod
    def _validate(command: tuple[str, ...]) -> None:
        allowed_git = {
            ("git", "config", "--get", "remote.origin.url"),
            ("git", "branch", "--show-current"),
            ("git", "rev-parse", "HEAD"),
            ("git", "rev-parse", "origin/main"),
            ("git", "status", "--porcelain"),
        }
        if command in allowed_git:
            return
        if (
            len(command) == 6
            and command[:3] == ("gh", "pr", "view")
            and command[3].isdigit()
            and int(command[3]) > 0
            and command[4:] == ("--json", _GITHUB_PR_FIELDS)
        ):
            return
        raise EvidenceCollectionError(
            CollectionFailureCode.MALFORMED_FIELD,
            "runtime command is outside the accepted read-only policy",
        )


@dataclass(frozen=True, slots=True)
class VerificationRuntime:
    command: ReadOnlyVerificationCommandExecutor
    repository_adapter: RepositoryEvidenceAdapter
    github_adapter: GitHubEvidenceAdapter
    validator: ReleaseEvidenceValidator
    orchestrator: ReleaseEvidenceVerificationOrchestrator


def build_verification_runtime(
    configuration: VerificationRuntimeConfiguration,
    process: RuntimeProcess = _run_read_process,
) -> VerificationRuntime:
    command = ReadOnlyVerificationCommandExecutor(configuration, process)
    repository_adapter = RepositoryEvidenceAdapter(command)
    github_adapter = GitHubEvidenceAdapter(command)
    validator = ReleaseEvidenceValidator()
    orchestrator = ReleaseEvidenceVerificationOrchestrator(
        repository_adapter,
        github_adapter,
        validator,
    )
    return VerificationRuntime(
        command,
        repository_adapter,
        github_adapter,
        validator,
        orchestrator,
    )


# v1.3.5-v1.3.7-read-only-verification-delivery-train-implementation


class VerificationDocumentError(ValueError):
    """Raised when a deterministic verification document is invalid."""


@dataclass(frozen=True, slots=True)
class ReadOnlyVerificationInvoker:
    runtime: VerificationRuntime

    def __post_init__(self) -> None:
        if not isinstance(self.runtime, VerificationRuntime):
            raise TypeError("runtime must be a VerificationRuntime")

    def invoke(self, request: VerificationRequest) -> VerificationReport:
        if not isinstance(request, VerificationRequest):
            raise TypeError("request must be a VerificationRequest")
        return self.runtime.orchestrator.verify(request)


class VerificationRequestCodec:
    SCHEMA_VERSION = 1
    _KEYS = {
        "schema_version",
        "expected_repository",
        "expected_branch",
        "expected_sha",
        "pull_request_number",
        "focused_tests",
    }
    _TEST_KEYS = {"passed", "failed", "skipped", "deselected"}

    @classmethod
    def decode(cls, document: str) -> VerificationRequest:
        try:
            payload = json.loads(document, object_pairs_hook=cls._strict_object)
        except (json.JSONDecodeError, TypeError) as error:
            raise VerificationDocumentError("request is not valid JSON") from error
        if not isinstance(payload, dict):
            raise VerificationDocumentError("request must be a JSON object")
        cls._require_exact_keys(payload, cls._KEYS, "request")
        if payload["schema_version"] != cls.SCHEMA_VERSION or isinstance(
            payload["schema_version"], bool
        ):
            raise VerificationDocumentError("schema_version must be integer 1")
        repository = cls._required_string(payload["expected_repository"], "expected_repository")
        branch = cls._required_string(payload["expected_branch"], "expected_branch")
        sha = cls._required_string(payload["expected_sha"], "expected_sha")
        pr_number = cls._integer(
            payload["pull_request_number"],
            "pull_request_number",
            positive=True,
        )
        tests_payload = payload["focused_tests"]
        if not isinstance(tests_payload, dict):
            raise VerificationDocumentError("focused_tests must be an object")
        cls._require_exact_keys(tests_payload, cls._TEST_KEYS, "focused_tests")
        tests = TestEvidence(
            passed=cls._integer(tests_payload["passed"], "passed"),
            failed=cls._integer(tests_payload["failed"], "failed"),
            skipped=cls._integer(tests_payload["skipped"], "skipped"),
            deselected=cls._integer(tests_payload["deselected"], "deselected"),
        )
        try:
            return VerificationRequest(repository, branch, sha, pr_number, tests)
        except (TypeError, ValueError) as error:
            raise VerificationDocumentError(str(error)) from error

    @staticmethod
    def _require_exact_keys(payload: dict[str, object], expected: set[str], field: str) -> None:
        if set(payload) != expected:
            raise VerificationDocumentError(f"{field} keys must match the schema exactly")

    @staticmethod
    def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
        result: dict[str, object] = {}
        for key, value in pairs:
            if key in result:
                raise VerificationDocumentError(f"duplicate JSON key: {key}")
            result[key] = value
        return result

    @staticmethod
    def _required_string(value: object, field: str) -> str:
        if not isinstance(value, str) or not value.strip():
            raise VerificationDocumentError(f"{field} must be a non-empty string")
        return value

    @staticmethod
    def _integer(value: object, field: str, *, positive: bool = False) -> int:
        if not isinstance(value, int) or isinstance(value, bool):
            raise VerificationDocumentError(f"{field} must be an integer")
        if value < (1 if positive else 0):
            raise VerificationDocumentError(f"{field} is out of range")
        return value


class VerificationReportRenderer:
    SCHEMA_VERSION = 1

    @classmethod
    def to_json(cls, report: VerificationReport) -> str:
        return (
            json.dumps(
                cls._payload(report),
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n"
        )

    @classmethod
    def to_text(cls, report: VerificationReport) -> str:
        payload = cls._payload(report)
        lines = [f"status: {payload['status']}"]
        for name in ("repository", "pull_request", "evidence"):
            value = payload[name]
            lines.append(f"{name}: {json.dumps(value, ensure_ascii=False, sort_keys=True)}")
        lines.append("findings:")
        lines.extend(
            f"- [{item['stage']}/{item['code']}] {item['message']}" for item in payload["findings"]
        )
        if not payload["findings"]:
            lines.append("- none")
        return "\n".join(lines) + "\n"

    @classmethod
    def _payload(cls, report: VerificationReport) -> dict[str, object]:
        if not isinstance(report, VerificationReport):
            raise TypeError("report must be a VerificationReport")
        repository = report.repository
        pull_request = report.pull_request
        evidence = report.evidence
        return {
            "schema_version": cls.SCHEMA_VERSION,
            "status": "passed" if report.is_valid else "failed",
            "repository": None
            if repository is None
            else {
                "repository": repository.repository,
                "branch": repository.branch,
                "head_sha": repository.head_sha,
                "origin_main_sha": repository.origin_main_sha,
                "remote_url": repository.remote_url,
                "is_clean": repository.is_clean,
            },
            "pull_request": None
            if pull_request is None
            else {
                "number": pull_request.number,
                "url": pull_request.url,
                "state": pull_request.state.value,
                "base_branch": pull_request.base_branch,
                "head_branch": pull_request.head_branch,
                "merge_sha": pull_request.merge_sha,
                "merged_at": pull_request.merged_at,
                "checks": [
                    {"name": check.name, "conclusion": check.conclusion.value}
                    for check in pull_request.checks
                ],
            },
            "evidence": None
            if evidence is None
            else {
                "repository": evidence.repository,
                "branch": evidence.branch,
                "candidate_sha": evidence.candidate_sha,
                "checks": [
                    {"name": check.name, "conclusion": check.conclusion.value}
                    for check in evidence.checks
                ],
                "focused_tests": None
                if evidence.focused_tests is None
                else {
                    "passed": evidence.focused_tests.passed,
                    "failed": evidence.focused_tests.failed,
                    "skipped": evidence.focused_tests.skipped,
                    "deselected": evidence.focused_tests.deselected,
                },
            },
            "findings": [
                {
                    "stage": finding.stage.value,
                    "code": str(finding.code),
                    "message": finding.message,
                }
                for finding in report.findings
            ],
        }


# v1.3.8-v1.3.10-verification-request-usability-stable-cli-implementation


class VerificationRequestEncoder:
    SCHEMA_VERSION = 1

    @classmethod
    def encode(cls, request: VerificationRequest) -> str:
        if not isinstance(request, VerificationRequest):
            raise TypeError("request must be a VerificationRequest")
        tests = request.focused_tests
        if tests is None:
            raise VerificationDocumentError("focused_tests must be present")
        payload = {
            "schema_version": cls.SCHEMA_VERSION,
            "expected_repository": request.expected_repository,
            "expected_branch": request.expected_branch,
            "expected_sha": request.expected_sha,
            "pull_request_number": request.pull_request_number,
            "focused_tests": {
                "passed": tests.passed,
                "failed": tests.failed,
                "skipped": tests.skipped,
                "deselected": tests.deselected,
            },
        }
        return (
            json.dumps(
                payload,
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n"
        )


@dataclass(frozen=True, slots=True)
class VerificationRequestInspection:
    request: VerificationRequest
    canonical_request: str


class VerificationRequestInspector:
    @staticmethod
    def inspect(document: str) -> VerificationRequestInspection:
        request = VerificationRequestCodec.decode(document)
        return VerificationRequestInspection(
            request,
            VerificationRequestEncoder.encode(request),
        )


class VerificationRequestInspectionRenderer:
    @staticmethod
    def to_json(inspection: VerificationRequestInspection) -> str:
        if not isinstance(inspection, VerificationRequestInspection):
            raise TypeError("inspection must be a VerificationRequestInspection")
        return (
            json.dumps(
                {
                    "schema_version": 1,
                    "status": "valid",
                    "request": json.loads(inspection.canonical_request),
                },
                ensure_ascii=False,
                separators=(",", ":"),
                sort_keys=True,
            )
            + "\n"
        )

    @staticmethod
    def to_text(inspection: VerificationRequestInspection) -> str:
        request = inspection.request
        return (
            "status: valid\n"
            f"expected_repository: {request.expected_repository}\n"
            f"expected_branch: {request.expected_branch}\n"
            f"expected_sha: {request.expected_sha}\n"
            f"pull_request_number: {request.pull_request_number}\n"
        )


# v1.3.11-v1.3.13-verification-report-usability-implementation


class VerificationReportCodec:
    """Strict schema-version-1 verification-report decoder."""

    SCHEMA_VERSION = 1
    _ROOT_KEYS = {
        "schema_version",
        "status",
        "repository",
        "pull_request",
        "evidence",
        "findings",
    }

    @classmethod
    def decode(cls, document: str) -> VerificationReport:
        try:
            payload = json.loads(
                document,
                object_pairs_hook=VerificationRequestCodec._strict_object,
            )
        except (json.JSONDecodeError, TypeError) as error:
            raise VerificationDocumentError("report is not valid JSON") from error
        if not isinstance(payload, dict):
            raise VerificationDocumentError("report must be a JSON object")
        VerificationRequestCodec._require_exact_keys(payload, cls._ROOT_KEYS, "report")
        version = payload["schema_version"]
        if version != cls.SCHEMA_VERSION or isinstance(version, bool):
            raise VerificationDocumentError("schema_version must be integer 1")
        report = cls._report(payload)
        expected = "passed" if report.is_valid else "failed"
        if payload["status"] != expected:
            raise VerificationDocumentError("status contradicts report contents")
        return report

    @classmethod
    def _report(cls, payload: dict[str, object]) -> VerificationReport:
        renderer = VerificationReportRenderer
        repository = cls._repository(payload["repository"])
        pull_request = cls._pull_request(payload["pull_request"])
        evidence = cls._evidence(payload["evidence"])
        findings_payload = payload["findings"]
        if not isinstance(findings_payload, list):
            raise VerificationDocumentError("findings must be an array")
        findings = tuple(cls._finding(item) for item in findings_payload)
        report = VerificationReport(repository, pull_request, evidence, findings)
        if renderer._payload(report) != payload:
            raise VerificationDocumentError("report values do not match the canonical schema")
        return report

    @staticmethod
    def _object(value: object, keys: set[str], field: str) -> dict[str, object]:
        if not isinstance(value, dict):
            raise VerificationDocumentError(f"{field} must be an object")
        VerificationRequestCodec._require_exact_keys(value, keys, field)
        return value

    @classmethod
    def _repository(cls, value: object) -> RepositoryObservation | None:
        if value is None:
            return None
        item = cls._object(
            value,
            {"repository", "branch", "head_sha", "origin_main_sha", "remote_url", "is_clean"},
            "repository",
        )
        if not isinstance(item["is_clean"], bool):
            raise VerificationDocumentError("is_clean must be boolean")
        strings = {
            key: VerificationRequestCodec._required_string(item[key], key)
            for key in item
            if key != "is_clean"
        }
        if not _is_sha(strings["head_sha"]) or not _is_sha(strings["origin_main_sha"]):
            raise VerificationDocumentError("repository SHAs must be full commit SHAs")
        return RepositoryObservation(**strings, is_clean=item["is_clean"])

    @classmethod
    def _pull_request(cls, value: object) -> PullRequestObservation | None:
        if value is None:
            return None
        item = cls._object(
            value,
            {
                "number",
                "url",
                "state",
                "base_branch",
                "head_branch",
                "checks",
                "merge_sha",
                "merged_at",
            },
            "pull_request",
        )
        checks = cls._checks(item["checks"])
        merge_sha = item["merge_sha"]
        if merge_sha is not None and (not isinstance(merge_sha, str) or not _is_sha(merge_sha)):
            raise VerificationDocumentError("merge_sha must be null or a full commit SHA")
        merged_at = item["merged_at"]
        if merged_at is not None and (not isinstance(merged_at, str) or not merged_at.strip()):
            raise VerificationDocumentError("merged_at must be null or a non-empty string")
        try:
            return PullRequestObservation(
                VerificationRequestCodec._integer(item["number"], "number", positive=True),
                VerificationRequestCodec._required_string(item["url"], "url"),
                PullRequestState(item["state"]),
                VerificationRequestCodec._required_string(item["base_branch"], "base_branch"),
                VerificationRequestCodec._required_string(item["head_branch"], "head_branch"),
                checks,
                merge_sha,
                merged_at,
            )
        except (TypeError, ValueError) as error:
            raise VerificationDocumentError(str(error)) from error

    @classmethod
    def _checks(cls, value: object) -> tuple[CheckEvidence, ...]:
        if not isinstance(value, list):
            raise VerificationDocumentError("checks must be an array")
        checks = []
        for raw in value:
            item = cls._object(raw, {"name", "conclusion"}, "check")
            try:
                checks.append(
                    CheckEvidence(
                        VerificationRequestCodec._required_string(item["name"], "name"),
                        CheckConclusion(item["conclusion"]),
                    )
                )
            except (TypeError, ValueError) as error:
                raise VerificationDocumentError(str(error)) from error
        if len({check.name for check in checks}) != len(checks):
            raise VerificationDocumentError("check names must be unique")
        return tuple(checks)

    @classmethod
    def _evidence(cls, value: object) -> ReleaseEvidence | None:
        if value is None:
            return None
        item = cls._object(
            value,
            {"repository", "branch", "candidate_sha", "checks", "focused_tests"},
            "evidence",
        )
        tests = item["focused_tests"]
        focused = None
        if tests is not None:
            test_item = cls._object(
                tests, {"passed", "failed", "skipped", "deselected"}, "focused_tests"
            )
            focused = TestEvidence(
                **{key: VerificationRequestCodec._integer(test_item[key], key) for key in test_item}
            )
        try:
            return ReleaseEvidence(
                VerificationRequestCodec._required_string(item["repository"], "repository"),
                VerificationRequestCodec._required_string(item["branch"], "branch"),
                VerificationRequestCodec._required_string(item["candidate_sha"], "candidate_sha"),
                cls._checks(item["checks"]),
                focused,
            )
        except (TypeError, ValueError) as error:
            raise VerificationDocumentError(str(error)) from error

    @classmethod
    def _finding(cls, value: object) -> VerificationFinding:
        item = cls._object(value, {"stage", "code", "message"}, "finding")
        try:
            return VerificationFinding(
                VerificationFindingStage(item["stage"]),
                VerificationRequestCodec._required_string(item["code"], "code"),
                VerificationRequestCodec._required_string(item["message"], "message"),
            )
        except (TypeError, ValueError) as error:
            raise VerificationDocumentError(str(error)) from error


class VerificationReportEncoder:
    @staticmethod
    def encode(report: VerificationReport) -> str:
        if not isinstance(report, VerificationReport):
            raise TypeError("report must be a VerificationReport")
        return VerificationReportRenderer.to_json(report)


@dataclass(frozen=True, slots=True)
class VerificationReportInspection:
    report: VerificationReport

    @property
    def status(self) -> str:
        return "passed" if self.report.is_valid else "failed"


class VerificationReportInspector:
    @staticmethod
    def inspect(document: str) -> VerificationReportInspection:
        return VerificationReportInspection(VerificationReportCodec.decode(document))


class VerificationReportInspectionRenderer:
    @staticmethod
    def to_json(inspection: VerificationReportInspection) -> str:
        if not isinstance(inspection, VerificationReportInspection):
            raise TypeError("inspection must be a VerificationReportInspection")
        return VerificationReportEncoder.encode(inspection.report)

    @staticmethod
    def to_text(inspection: VerificationReportInspection) -> str:
        if not isinstance(inspection, VerificationReportInspection):
            raise TypeError("inspection must be a VerificationReportInspection")
        return VerificationReportRenderer.to_text(inspection.report)
