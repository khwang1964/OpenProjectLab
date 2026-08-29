import json
from collections.abc import Callable
from dataclasses import dataclass
from enum import StrEnum


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
