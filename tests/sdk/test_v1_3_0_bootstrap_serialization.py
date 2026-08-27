"""Production tests for the v1.3.0 Bootstrap SDK serialization contract."""

import json
from pathlib import Path

import pytest

import generator.sdk as sdk
from generator.core.bootstrap_validation import BootstrapValidationFinding
from generator.sdk.bootstrap_runtime import BootstrapSdkMode, BootstrapSdkRequest, run_bootstrap
from generator.sdk.bootstrap_serialization import (
    BootstrapSchemaVersion,
    BootstrapSerializationError,
    deserialize_bootstrap_request,
    deserialize_bootstrap_result,
    serialize_bootstrap_request,
    serialize_bootstrap_result,
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


def request(
    template_root: Path,
    output: Path,
    mode: BootstrapSdkMode = BootstrapSdkMode.PREVIEW,
    checks: tuple[object, ...] = (),
) -> BootstrapSdkRequest:
    return BootstrapSdkRequest(
        template_root=template_root,
        output_root=output,
        project_slug="demo",
        values={
            "project_name": "範例",
            "project_slug": "demo",
            "language": "zh-TW",
            "license_name": "CC BY 4.0",
        },
        mode=mode,
        validation_checks=checks,
    )


def test_schema_and_exports_are_exact() -> None:
    from generator.sdk import bootstrap_serialization

    assert BootstrapSchemaVersion.V1_0.value == "opl.bootstrap/1.0"
    assert bootstrap_serialization.__all__ == [
        "BootstrapSchemaVersion",
        "BootstrapSerializationError",
        "deserialize_bootstrap_request",
        "deserialize_bootstrap_result",
        "serialize_bootstrap_request",
        "serialize_bootstrap_result",
    ]


def test_existing_sdk_root_exports_remain_unchanged() -> None:
    assert "BootstrapSchemaVersion" not in sdk.__all__
    assert "BaseGenerator" in sdk.__all__


def test_request_encoding_is_canonical_and_deterministic(
    template_root: Path, tmp_path: Path
) -> None:
    value = request(template_root, tmp_path / "out")
    first = serialize_bootstrap_request(value)
    second = serialize_bootstrap_request(value)
    assert first == second
    assert ": " not in first
    assert ", " not in first
    assert "範例" in first
    assert json.loads(first)["schema"] == "opl.bootstrap/1.0"


def test_request_round_trip_preserves_supported_contract(
    template_root: Path, tmp_path: Path
) -> None:
    value = request(template_root, tmp_path / "out", BootstrapSdkMode.APPLY)
    decoded = deserialize_bootstrap_request(serialize_bootstrap_request(value))
    assert decoded == value
    assert serialize_bootstrap_request(decoded) == serialize_bootstrap_request(value)


def test_paths_use_forward_slashes(template_root: Path, tmp_path: Path) -> None:
    document = json.loads(serialize_bootstrap_request(request(template_root, tmp_path / "out")))
    assert "\\" not in document["payload"]["template_root"]
    assert "\\" not in document["payload"]["output_root"]


def test_plugin_checks_are_explicitly_deferred(template_root: Path, tmp_path: Path) -> None:
    with pytest.raises(BootstrapSerializationError, match="Plugin validation checks"):
        serialize_bootstrap_request(request(template_root, tmp_path, checks=(object(),)))


def test_preview_result_round_trip_is_exact(template_root: Path, tmp_path: Path) -> None:
    result = run_bootstrap(request(template_root, tmp_path / "out"))
    document = serialize_bootstrap_result(result)
    decoded = deserialize_bootstrap_result(document)
    assert serialize_bootstrap_result(decoded) == document
    assert decoded.plan.generator_ids == result.plan.generator_ids
    assert decoded.preview is not None
    assert result.preview is not None
    assert tuple(effect.kind for effect in decoded.preview.expected_effects) == tuple(
        effect.kind for effect in result.preview.expected_effects
    )


def test_apply_result_round_trip_is_exact(template_root: Path, tmp_path: Path) -> None:
    result = run_bootstrap(request(template_root, tmp_path / "out", BootstrapSdkMode.APPLY))
    document = serialize_bootstrap_result(result)
    decoded = deserialize_bootstrap_result(document)
    assert serialize_bootstrap_result(decoded) == document
    assert decoded.apply_result == result.apply_result
    assert decoded.plan.generator_ids == result.plan.generator_ids


def test_validation_findings_preserve_order(template_root: Path, tmp_path: Path) -> None:
    class Check:
        check_id = "ordered"

        def inspect(self, value: object) -> tuple[BootstrapValidationFinding, ...]:
            assert value
            return (
                BootstrapValidationFinding(check_id="ordered", severity="warning", message="first"),
                BootstrapValidationFinding(check_id="ordered", severity="error", message="second"),
            )

    result = run_bootstrap(
        request(template_root, tmp_path / "out", BootstrapSdkMode.APPLY_AND_VALIDATE, (Check(),))
    )
    document = serialize_bootstrap_result(result)
    decoded = deserialize_bootstrap_result(document)
    assert serialize_bootstrap_result(decoded) == document
    assert decoded.validation_result is not None
    assert tuple(item.message for item in decoded.validation_result.findings) == ("first", "second")


@pytest.mark.parametrize(
    "document",
    [
        '{"schema":"opl.bootstrap/1.0","schema":"opl.bootstrap/1.0","document_type":"bootstrap-request","payload":{}}',
        '{"schema":"opl.bootstrap/9.0","document_type":"bootstrap-request","payload":{}}',
        '{"schema":"opl.bootstrap/1.0","document_type":"other","payload":{}}',
        '{"schema":"opl.bootstrap/1.0","document_type":"bootstrap-request","payload":{"unknown":1}}',
        '{"schema":"opl.bootstrap/1.0","document_type":"bootstrap-request","payload":{"template_root":".","output_root":".","project_slug":"demo","values":{},"mode":"bad","overwrite":false}}',
        '{"schema":"opl.bootstrap/1.0","document_type":"bootstrap-request","payload":{"template_root":".","output_root":".","project_slug":"demo","values":{"bad":NaN},"mode":"preview","overwrite":false}}',
    ],
)
def test_malformed_documents_fail_closed(document: str) -> None:
    with pytest.raises(BootstrapSerializationError):
        deserialize_bootstrap_request(document)


def test_wrong_json_types_fail_closed() -> None:
    document = '{"schema":"opl.bootstrap/1.0","document_type":"bootstrap-request","payload":[]}'
    with pytest.raises(BootstrapSerializationError, match="payload must be an object"):
        deserialize_bootstrap_request(document)


def test_decode_is_silent_and_non_executing(
    template_root: Path,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    import generator.sdk.bootstrap_runtime as runtime

    document = serialize_bootstrap_request(request(template_root, tmp_path / "out"))
    monkeypatch.setattr(runtime, "run_bootstrap", lambda value: pytest.fail("runtime executed"))
    decoded = deserialize_bootstrap_request(document)
    assert decoded.project_slug == "demo"
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == ""


def test_module_has_no_cli_or_object_hook_dependency() -> None:
    source = Path(__file__).parents[2] / "generator/sdk/bootstrap_serialization.py"
    text = source.read_text(encoding="utf-8")
    assert "generator.cli" not in text
    assert "object_hook=" not in text
    assert "print(" not in text
