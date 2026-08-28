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
