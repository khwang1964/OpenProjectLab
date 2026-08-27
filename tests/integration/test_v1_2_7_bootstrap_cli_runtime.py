"""Tests for experimental Bootstrap CLI/runtime wiring."""

from pathlib import Path

import pytest

from generator.cli import main as cli


@pytest.fixture
def template_root(tmp_path: Path) -> Path:
    root = tmp_path / "templates" / "bootstrap" / "project"
    root.mkdir(parents=True)
    files = {
        "README.md.j2": "# {{ project_name }}\n",
        "LICENSE.j2": "{{ license_name }}\n",
        "CONTRIBUTING.md.j2": "Contribute\n",
        "gitignore.j2": ".venv/\n",
        "course.yaml.j2": "slug: {{ project_slug }}\n",
    }
    for name, content in files.items():
        (root / name).write_text(content, encoding="utf-8")
    return root.parents[1]


def _argv(template_root: Path, output_root: Path, *extra: str) -> list[str]:
    return [
        "--template-root",
        str(template_root),
        "--output-root",
        str(output_root),
        "bootstrap",
        "demo",
        "--name",
        "Demo",
        "--experimental-runtime",
        *extra,
    ]


def test_parser_exposes_explicit_experimental_opt_in_only() -> None:
    args = cli.build_parser().parse_args(["bootstrap", "demo", "--name", "Demo"])
    assert args.experimental_runtime is False
    assert args.validate is False


def test_experimental_preview_is_mutation_free(
    template_root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "courses"
    assert cli.main(_argv(template_root, output, "--dry-run")) == 0
    assert not output.exists()
    assert "[DRY-RUN] 預計效果：" in capsys.readouterr().out


def test_experimental_apply_uses_existing_generator_lifecycle(
    template_root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    output = tmp_path / "courses"
    assert cli.main(_argv(template_root, output)) == 0
    assert (output / "demo" / "README.md").exists()
    assert "專案根目錄：" in capsys.readouterr().out


def test_experimental_apply_and_validate_is_explicit(template_root: Path, tmp_path: Path) -> None:
    output = tmp_path / "courses"
    assert cli.main(_argv(template_root, output, "--validate")) == 0
    assert (output / "demo" / "course.yaml").exists()


def test_validate_without_opt_in_fails_closed(capsys: pytest.CaptureFixture[str]) -> None:
    assert cli.main(["bootstrap", "demo", "--name", "Demo", "--validate"]) == 2
    assert "requires --experimental-runtime" in capsys.readouterr().err


def test_validate_and_dry_run_conflict_fails_closed(
    template_root: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert cli.main(_argv(template_root, tmp_path / "out", "--validate", "--dry-run")) == 2
    assert "cannot be combined" in capsys.readouterr().err
