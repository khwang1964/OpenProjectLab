"""Production tests for the v1.2.9 Bootstrap SDK runtime."""

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

import generator.sdk as sdk
from generator.core.bootstrap_validation import BootstrapValidationFinding
from generator.sdk.bootstrap_runtime import (
    BootstrapSdkExecutionError,
    BootstrapSdkMode,
    BootstrapSdkRequest,
    BootstrapSdkResult,
    BootstrapSdkUsageError,
    run_bootstrap,
)


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


def make_request(
    template_root: Path,
    output_root: Path,
    *,
    mode: BootstrapSdkMode = BootstrapSdkMode.PREVIEW,
    overwrite: bool = False,
    checks: tuple[object, ...] = (),
) -> BootstrapSdkRequest:
    return BootstrapSdkRequest(
        template_root=template_root,
        output_root=output_root,
        project_slug="demo",
        values={
            "project_name": "Demo",
            "project_slug": "demo",
            "language": "zh-TW",
            "license_name": "CC BY 4.0",
        },
        mode=mode,
        overwrite=overwrite,
        validation_checks=checks,
    )


def test_public_module_exports_exact_contract() -> None:
    from generator.sdk import bootstrap_runtime

    assert bootstrap_runtime.__all__ == [
        "BootstrapSdkExecutionError",
        "BootstrapSdkMode",
        "BootstrapSdkRequest",
        "BootstrapSdkResult",
        "BootstrapSdkUsageError",
        "run_bootstrap",
    ]


def test_existing_sdk_root_exports_are_unchanged() -> None:
    assert "BootstrapSdkRequest" not in sdk.__all__
    assert "run_bootstrap" not in sdk.__all__
    assert "BaseGenerator" in sdk.__all__


def test_request_normalizes_to_immutable_data(template_root: Path, tmp_path: Path) -> None:
    request = make_request(template_root, tmp_path / "out")
    assert request.project_slug == "demo"
    assert isinstance(request.values, tuple)
    with pytest.raises(FrozenInstanceError):
        request.project_slug = "other"  # type: ignore[misc]


def test_invalid_request_is_usage_error(template_root: Path, tmp_path: Path) -> None:
    with pytest.raises(BootstrapSdkUsageError):
        BootstrapSdkRequest(
            template_root=template_root,
            output_root=tmp_path,
            project_slug=" ",
            values={},
        )
    with pytest.raises(BootstrapSdkUsageError):
        run_bootstrap(object())  # type: ignore[arg-type]


def test_preview_is_deterministic_and_mutation_free(template_root: Path, tmp_path: Path) -> None:
    output = tmp_path / "out"
    first = run_bootstrap(make_request(template_root, output))
    second = run_bootstrap(make_request(template_root, output))
    assert first == second
    assert first.preview is not None
    assert first.apply_result is None
    assert first.preview.would_mutate is True
    assert not output.exists()


def test_apply_returns_typed_evidence(template_root: Path, tmp_path: Path) -> None:
    output = tmp_path / "out"
    result = run_bootstrap(make_request(template_root, output, mode=BootstrapSdkMode.APPLY))
    assert isinstance(result, BootstrapSdkResult)
    assert result.preview is None
    assert result.apply_result is not None
    assert result.is_valid is None
    assert (output / "demo" / "README.md").exists()


def test_apply_and_validate_returns_valid_result(template_root: Path, tmp_path: Path) -> None:
    result = run_bootstrap(
        make_request(
            template_root,
            tmp_path / "out",
            mode=BootstrapSdkMode.APPLY_AND_VALIDATE,
        )
    )
    assert result.apply_result is not None
    assert result.validation_result is not None
    assert result.is_valid is True


def test_validation_findings_are_normal_invalid_result(template_root: Path, tmp_path: Path) -> None:
    class FindingCheck:
        check_id = "finding"

        def inspect(self, request: object) -> tuple[BootstrapValidationFinding, ...]:
            assert request
            return (
                BootstrapValidationFinding(
                    check_id=self.check_id,
                    severity="error",
                    message="invalid state",
                ),
            )

    result = run_bootstrap(
        make_request(
            template_root,
            tmp_path / "out",
            mode=BootstrapSdkMode.APPLY_AND_VALIDATE,
            checks=(FindingCheck(),),
        )
    )
    assert result.is_valid is False
    assert result.validation_result is not None
    assert result.validation_result.findings[0].message == "invalid state"


def test_check_failure_maps_to_typed_execution_error(template_root: Path, tmp_path: Path) -> None:
    class BrokenCheck:
        check_id = "broken"

        def inspect(self, request: object) -> tuple[BootstrapValidationFinding, ...]:
            del request
            raise RuntimeError("check failed")

    with pytest.raises(BootstrapSdkExecutionError) as captured:
        run_bootstrap(
            make_request(
                template_root,
                tmp_path / "out",
                mode=BootstrapSdkMode.APPLY_AND_VALIDATE,
                checks=(BrokenCheck(),),
            )
        )
    assert captured.value.phase == "validation"
    assert captured.value.failed_identity == "broken"


def test_apply_failure_preserves_step_identity(template_root: Path, tmp_path: Path) -> None:
    output = tmp_path / "out"
    existing = output / "demo" / "README.md"
    existing.parent.mkdir(parents=True)
    existing.write_text("existing", encoding="utf-8")
    with pytest.raises(BootstrapSdkExecutionError) as captured:
        run_bootstrap(make_request(template_root, output, mode=BootstrapSdkMode.APPLY))
    assert captured.value.phase == "apply"
    assert captured.value.failed_identity == "0001:bootstrap"
    assert existing.read_text(encoding="utf-8") == "existing"


def test_sdk_writes_neither_stdout_nor_stderr(
    template_root: Path,
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    run_bootstrap(make_request(template_root, tmp_path / "out"))
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_sdk_module_does_not_depend_on_cli() -> None:
    source = Path(__file__).parents[2] / "generator/sdk/bootstrap_runtime.py"
    text = source.read_text(encoding="utf-8")
    assert "generator.cli" not in text
    assert "print(" not in text


def test_result_is_frozen(template_root: Path, tmp_path: Path) -> None:
    result = run_bootstrap(make_request(template_root, tmp_path / "out"))
    with pytest.raises(FrozenInstanceError):
        result.preview = None  # type: ignore[misc]
