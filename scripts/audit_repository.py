"""Audit the OpenProjectLab repository structure.

This module validates that required project, governance, documentation,
testing, and GitHub automation files exist in the repository.

The command exits with status code 0 when the audit passes and status code 1
when one or more required paths are missing.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True, slots=True)
class RepositoryRequirement:
    """Describe a required repository file or directory."""

    path: str
    kind: str = "file"

    def exists(self, root: Path) -> bool:
        """Return whether the required path exists under the given root."""
        target = root / self.path

        if self.kind == "directory":
            return target.is_dir()

        return target.is_file()


REQUIREMENTS: tuple[RepositoryRequirement, ...] = (
    RepositoryRequirement(".github", "directory"),
    RepositoryRequirement(".github/workflows", "directory"),
    RepositoryRequirement(".github/ISSUE_TEMPLATE", "directory"),
    RepositoryRequirement(".github/workflows/ci.yml"),
    RepositoryRequirement(".github/workflows/template-tests.yml"),
    RepositoryRequirement("docs", "directory"),
    RepositoryRequirement("scripts", "directory"),
    RepositoryRequirement("tests", "directory"),
    RepositoryRequirement("README.md"),
    RepositoryRequirement("CHANGELOG.md"),
    RepositoryRequirement("CONTRIBUTING.md"),
    RepositoryRequirement("SECURITY.md"),
    RepositoryRequirement("CODE_OF_CONDUCT.md"),
    RepositoryRequirement("LICENSE"),
    RepositoryRequirement("docs/ruff-policy.md"),
    RepositoryRequirement("pyproject.toml"),
    RepositoryRequirement(".pre-commit-config.yaml"),
)


def find_missing_requirements(
    root: Path,
    requirements: Iterable[RepositoryRequirement] = REQUIREMENTS,
) -> list[RepositoryRequirement]:
    """Return repository requirements that do not exist under the given root."""
    return [requirement for requirement in requirements if not requirement.exists(root)]


def format_missing_requirement(
    requirement: RepositoryRequirement,
) -> str:
    """Format one missing repository requirement for console output."""
    return f"- {requirement.kind}: {requirement.path}"


def main() -> int:
    """Run the repository audit and return a process exit code."""
    missing = find_missing_requirements(PROJECT_ROOT)

    if not missing:
        print("Repository audit passed.")
        return 0

    print("Repository audit failed.")
    print("Missing required paths:")

    for requirement in missing:
        print(format_missing_requirement(requirement))

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
