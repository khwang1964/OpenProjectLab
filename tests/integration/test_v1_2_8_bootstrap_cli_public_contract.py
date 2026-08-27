"""Integration tests for the v1.2.8 Bootstrap CLI public contract."""

from pathlib import Path
from types import SimpleNamespace

import pytest

from generator.cli import bootstrap_runtime as adapter
from generator.cli import main as cli
from generator.core.filesystem import FileSystemError


def _base(*extra: str) -> list[str]:
    return ["bootstrap", "demo", "--name", "Demo", *extra]


def test_parser_exposes_stable_runtime_option() -> None:
    args = cli.build_parser().parse_args(_base("--runtime"))
    assert args.experimental_runtime is True


def test_legacy_experimental_alias_remains_compatible() -> None:
    args = cli.build_parser().parse_args(_base("--experimental-runtime"))
    assert args.experimental_runtime is True


def test_no_opt_in_preserves_legacy_selection() -> None:
    args = cli.build_parser().parse_args(_base())
    assert args.experimental_runtime is False


def test_stable_runtime_normalizes_once_and_delegates(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: list[adapter.BootstrapCliRuntimeInput] = []

    def execute(value: adapter.BootstrapCliRuntimeInput) -> int:
        captured.append(value)
        return 0

    monkeypatch.setattr(cli, "execute_bootstrap_runtime", execute)
    assert cli.main(_base("--runtime", "--validate")) == 0
    assert len(captured) == 1
    assert captured[0].project_slug == "demo"
    assert captured[0].validate is True


def test_validate_without_runtime_is_usage_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert cli.main(_base("--validate")) == 2
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "requires --experimental-runtime or --runtime" in captured.err


def test_runtime_failure_maps_to_one_and_stderr(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail(value: adapter.BootstrapCliRuntimeInput) -> int:
        del value
        raise RuntimeError("runtime phase failed")

    monkeypatch.setattr(cli, "execute_bootstrap_runtime", fail)
    assert cli.main(_base("--runtime")) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "runtime phase failed" in captured.err


def test_os_failure_maps_to_one_and_stderr(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail(value: adapter.BootstrapCliRuntimeInput) -> int:
        del value
        raise OSError("filesystem phase failed")

    monkeypatch.setattr(cli, "execute_bootstrap_runtime", fail)
    assert cli.main(_base("--runtime")) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "filesystem phase failed" in captured.err


def test_validation_findings_map_to_one_and_stderr(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    class InvalidCoordinator:
        def __init__(self, **components: object) -> None:
            assert components

        def execute(self, request: object) -> object:
            assert request
            generation = SimpleNamespace(affected_paths=())
            apply_result = SimpleNamespace(generation_results=(generation,))
            validation_result = SimpleNamespace(is_valid=False)
            return SimpleNamespace(
                preview=None,
                apply_result=apply_result,
                validation_result=validation_result,
            )

    monkeypatch.setattr(adapter, "BootstrapRuntimeCoordinator", InvalidCoordinator)
    value = adapter.BootstrapCliRuntimeInput(
        template_root=tmp_path,
        output_root=tmp_path / "out",
        project_slug="demo",
        values={
            "project_name": "Demo",
            "project_slug": "demo",
            "language": "zh-TW",
            "license_name": "CC BY 4.0",
        },
        overwrite=False,
        dry_run=False,
        validate=True,
    )
    assert adapter.execute_bootstrap_runtime(value) == 1
    captured = capsys.readouterr()
    assert "專案根目錄：" in captured.out
    assert "Bootstrap validation failed" in captured.err


def test_unknown_option_remains_argparse_exit_two(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    invoked = False

    def execute(value: adapter.BootstrapCliRuntimeInput) -> int:
        nonlocal invoked
        invoked = True
        del value
        return 0

    monkeypatch.setattr(cli, "execute_bootstrap_runtime", execute)
    with pytest.raises(SystemExit) as error:
        cli.main(_base("--runtime", "--unknown-public-option"))
    assert error.value.code == 2
    assert invoked is False


def test_runtime_filesystem_error_maps_to_one(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    def fail(value: adapter.BootstrapCliRuntimeInput) -> int:
        del value
        raise FileSystemError("runtime filesystem phase failed")

    monkeypatch.setattr(cli, "execute_bootstrap_runtime", fail)
    assert cli.main(_base("--runtime")) == 1
    captured = capsys.readouterr()
    assert captured.out == ""
    assert "runtime filesystem phase failed" in captured.err


def test_legacy_missing_structured_file_remains_two(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    missing = tmp_path / "missing-questions.json"
    assert (
        cli.main(
            [
                "quiz",
                "demo",
                "--week",
                "1",
                "--quiz-id",
                "contract",
                "--title",
                "Contract",
                "--questions-file",
                str(missing),
            ]
        )
        == 2
    )
    captured = capsys.readouterr()
    assert captured.out == ""
    assert missing.name in captured.err
