"""Build the v1.1 release candidate without mutating repository identity."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tempfile
import tomllib
from pathlib import Path

REPOSITORY_VERSION = "1.0.0"
CANDIDATE_VERSION = "1.1.0rc1"
CANDIDATE_TAG = "v1.1.0-rc.1"


def _run(*args: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        args,
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"command failed: {' '.join(args)}\n"
            f"stdout:\n{completed.stdout}\n"
            f"stderr:\n{completed.stderr}"
        )
    return completed


def _project_version(pyproject: Path) -> str:
    project = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]
    return str(project["version"])


def _replace_candidate_version(pyproject: Path) -> None:
    text = pyproject.read_text(encoding="utf-8")
    old = f'version = "{REPOSITORY_VERSION}"'
    new = f'version = "{CANDIDATE_VERSION}"'

    if text.count(old) != 1:
        raise RuntimeError(f"expected exactly one repository version anchor {old!r}")

    pyproject.write_text(
        text.replace(old, new, 1),
        encoding="utf-8",
        newline="\n",
    )


def _copy_source(repo: Path, destination: Path) -> None:
    ignored_names = {
        ".git",
        ".venv",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "__pycache__",
        "build",
        "dist",
        "dist-v1.1.8",
        "htmlcov",
    }

    def ignore(_: str, names: list[str]) -> set[str]:
        return {name for name in names if name in ignored_names}

    shutil.copytree(repo, destination, ignore=ignore)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default="dist-v1.1.8",
        help="Artifact output directory relative to repository root",
    )
    args = parser.parse_args()

    repo = Path.cwd().resolve()
    pyproject = repo / "pyproject.toml"

    if not pyproject.is_file():
        raise RuntimeError("Run from the OpenProjectLab repository root.")

    repository_version = _project_version(pyproject)
    if repository_version != REPOSITORY_VERSION:
        raise RuntimeError(
            "Repository canonical version must remain "
            f"{REPOSITORY_VERSION}; got {repository_version}."
        )

    source_sha = _run("git", "rev-parse", "HEAD", cwd=repo).stdout.strip()
    if len(source_sha) != 40:
        raise RuntimeError(f"Unexpected source SHA: {source_sha}")

    output = (repo / args.output_dir).resolve()
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)

    with tempfile.TemporaryDirectory(prefix="opl-v1.1-candidate-") as raw_temp:
        snapshot = Path(raw_temp) / "source"
        _copy_source(repo, snapshot)

        snapshot_pyproject = snapshot / "pyproject.toml"
        _replace_candidate_version(snapshot_pyproject)

        if _project_version(snapshot_pyproject) != CANDIDATE_VERSION:
            raise RuntimeError("Candidate source version override failed.")

        _run(
            str(Path(__import__("sys").executable)),
            "-m",
            "build",
            "--wheel",
            "--sdist",
            "--outdir",
            str(output),
            cwd=snapshot,
        )

    wheels = sorted(output.glob("openprojectlab-1.1.0rc1-*.whl"))
    sdists = sorted(output.glob("openprojectlab-1.1.0rc1.tar.gz"))
    if len(wheels) != 1 or len(sdists) != 1:
        raise RuntimeError("Expected exactly one v1.1.0rc1 wheel and one v1.1.0rc1 sdist.")

    artifacts = sorted([*wheels, *sdists], key=lambda path: path.name)
    manifest = output / "SHA256SUMS"
    manifest.write_text(
        "".join(f"{_sha256(path)}  {path.name}\n" for path in artifacts),
        encoding="utf-8",
        newline="\n",
    )

    evidence = {
        "repository_version": REPOSITORY_VERSION,
        "candidate_version": CANDIDATE_VERSION,
        "candidate_tag": CANDIDATE_TAG,
        "source_commit_sha": source_sha,
        "build_transform": {
            "path": "pyproject.toml",
            "from": REPOSITORY_VERSION,
            "to": CANDIDATE_VERSION,
            "repository_mutated": False,
        },
        "artifacts": [{"filename": path.name, "sha256": _sha256(path)} for path in artifacts],
    }

    evidence_path = output / "candidate-build-evidence.json"
    evidence_path.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )

    # Fail closed if the repository itself changed identity.
    if _project_version(pyproject) != REPOSITORY_VERSION:
        raise RuntimeError("Repository canonical version was mutated.")

    print(f"source commit: {source_sha}")
    print(f"repository version: {REPOSITORY_VERSION}")
    print(f"candidate version: {CANDIDATE_VERSION}")
    print(f"candidate tag: {CANDIDATE_TAG}")
    for path in artifacts:
        print(f"artifact: {path}")
    print(f"manifest: {manifest}")
    print(f"evidence: {evidence_path}")


if __name__ == "__main__":
    main()
