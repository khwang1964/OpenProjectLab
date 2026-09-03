import hashlib
import json
from pathlib import Path

from generator.cli.main import build_parser
from generator.release_audit_bundle import (
    DEFAULT_SCHEMA_REGISTRY,
    AuditBundleMigrationExecutor,
    AuditBundleMigrationRequest,
)


def invoke(arguments: list[str]) -> int:
    args = build_parser().parse_args(arguments)
    return args.command_handler(args)


def evidence(tmp_path: Path) -> tuple[Path, Path, Path]:
    source_document = json.dumps(
        {
            "metadata": {},
            "report_document": "{}",
            "report_sha256": "1" * 64,
            "request_document": "{}",
            "request_sha256": "0" * 64,
            "schema_version": "0",
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    plan = DEFAULT_SCHEMA_REGISTRY.plan("0", "1")
    request = AuditBundleMigrationRequest(
        hashlib.sha256(source_document.encode()).hexdigest(),
        "1",
        plan.preview_fingerprint,
        True,
    )
    result = AuditBundleMigrationExecutor.execute(request, source_document)
    source = tmp_path / "source.json"
    output = tmp_path / "output.json"
    receipt = tmp_path / "receipt.json"
    source.write_text(source_document, encoding="utf-8")
    output.write_text(result.output_document, encoding="utf-8")
    receipt.write_text(result.receipt, encoding="utf-8")
    return source, output, receipt


def arguments(source: Path, output: Path, receipt: Path) -> list[str]:
    return [
        "release-evidence",
        "bundle",
        "verify-migration",
        "--bundle",
        str(source),
        "--output",
        str(output),
        "--receipt",
        str(receipt),
        "--format",
        "json",
    ]


def test_cli_verifies_exact_receipt_without_mutation(tmp_path: Path, capsys) -> None:
    source, output, receipt = evidence(tmp_path)
    before = {path: path.read_bytes() for path in tmp_path.iterdir()}
    assert invoke(arguments(source, output, receipt)) == 0
    assert json.loads(capsys.readouterr().out) == {"findings": [], "valid": True}
    assert {path: path.read_bytes() for path in tmp_path.iterdir()} == before


def test_cli_returns_one_for_recorded_mismatch(tmp_path: Path, capsys) -> None:
    source, output, receipt = evidence(tmp_path)
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    payload["source_sha256"] = "0" * 64
    receipt.write_text(
        json.dumps(payload, sort_keys=True, separators=(",", ":")),
        encoding="utf-8",
    )
    assert invoke(arguments(source, output, receipt)) == 1
    rendered = json.loads(capsys.readouterr().out)
    assert rendered["valid"] is False
    assert rendered["findings"][0]["path"] == "$.source_sha256"


def test_cli_returns_two_for_malformed_receipt(tmp_path: Path) -> None:
    source, output, receipt = evidence(tmp_path)
    receipt.write_text("not-json", encoding="utf-8")
    assert invoke(arguments(source, output, receipt)) == 2
