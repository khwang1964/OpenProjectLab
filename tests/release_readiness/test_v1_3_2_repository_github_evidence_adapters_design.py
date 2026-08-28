from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DESIGN = ROOT / ("docs/releases/v1.3.2-repository-github-evidence-adapters-design.md")
ARCHITECTURE = ROOT / "docs/architecture/developer-release-automation.md"
ROADMAP = ROOT / "docs/roadmap.md"
HISTORY = ROOT / "docs/HISTORY.md"
CHANGELOG = ROOT / "CHANGELOG.md"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_design_is_proposed_and_implementation_is_not_started() -> None:
    text = read(DESIGN)

    assert "Status: Proposed — Pending design review" in text
    assert "Production implementation — Not Started" in text
    assert "Accepted / Completed" in text


def test_repository_observations_are_read_only() -> None:
    text = read(DESIGN)

    required = (
        "repository identity",
        "current branch identity",
        "working-tree cleanliness",
        "local HEAD and `origin/main` commit identities",
        "configured remote identity",
    )

    for item in required:
        assert item in text

    assert "read-only" in text
    assert "immutable observation values" in text


def test_github_observations_fail_closed() -> None:
    text = read(DESIGN)

    required = (
        "pull-request number",
        "merge commit and merge timestamp",
        "required-check names",
        "Unknown GitHub mergeability is not treated as success",
        "Missing fields fail closed",
    )

    for item in required:
        assert item in text


def test_mutating_operations_remain_deferred() -> None:
    text = read(DESIGN)

    deferred = (
        "automatic pull-request merge",
        "force push, reset, or branch deletion",
        "tag, GitHub Release, package publication",
        "credential capture or serialization",
        "end-user CLI or `generator.sdk` expansion",
    )

    for item in deferred:
        assert item in text


def test_architecture_preserves_dependency_direction() -> None:
    text = read(ARCHITECTURE)

    assert "v1.3.2-repository-github-evidence-adapters-design" in text
    assert "read-only observation collection" in text
    assert "existing fail-closed" in text
    assert "validation core" in text
    assert "must not merge, force-push, reset, delete" in text


def test_lifecycle_documents_share_the_proposed_boundary() -> None:
    marker = "v1.3.2-repository-github-evidence-adapters-design"

    for path in (ROADMAP, HISTORY, CHANGELOG):
        text = read(path)
        assert marker in text
        assert "Proposed" in text
        assert "read-only" in text
        assert "deferred" in text.lower()
