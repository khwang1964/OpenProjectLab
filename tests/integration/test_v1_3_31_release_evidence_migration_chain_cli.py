import hashlib
import json
from pathlib import Path

from generator.cli.main import build_parser
from generator.release_audit_bundle import (
    DEFAULT_SCHEMA_REGISTRY,
    AuditBundleMigrationChainManifest,
    AuditBundleMigrationChainManifestCodec,
    AuditBundleMigrationExecutor,
    AuditBundleMigrationRequest,
)


def evidence() -> tuple[str, str, str, str]:
    source = json.dumps(
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
        hashlib.sha256(source.encode()).hexdigest(), "1", plan.preview_fingerprint, True
    )
    result = AuditBundleMigrationExecutor.execute(request, source)
    manifest = AuditBundleMigrationChainManifest(
        "1",
        hashlib.sha256(source.encode()).hexdigest(),
        result.output_sha256,
        (hashlib.sha256(result.receipt.encode()).hexdigest(),),
    )
    return (
        source,
        result.output_document,
        result.receipt,
        (AuditBundleMigrationChainManifestCodec.encode(manifest)),
    )


def invoke(arguments: list[str]) -> int:
    args = build_parser().parse_args(arguments)
    return args.command_handler(args)


def files(tmp_path: Path) -> tuple[Path, Path, Path, Path]:
    source_document, output_document, receipt_document, manifest_document = evidence()
    paths = tuple(tmp_path / name for name in ("manifest", "source", "output", "receipt"))
    for path, document in zip(
        paths,
        (manifest_document, source_document, output_document, receipt_document),
        strict=True,
    ):
        path.write_text(document, encoding="utf-8")
    return paths


def arguments(paths: tuple[Path, Path, Path, Path]) -> list[str]:
    manifest, source, output, receipt = paths
    return [
        "release-evidence",
        "bundle",
        "verify-migration-chain",
        "--manifest",
        str(manifest),
        "--bundle",
        str(source),
        "--bundle",
        str(output),
        "--receipt",
        str(receipt),
        "--format",
        "json",
    ]


def test_cli_verifies_chain_without_mutation(tmp_path: Path, capsys) -> None:
    paths = files(tmp_path)
    before = {path: path.read_bytes() for path in tmp_path.iterdir()}
    assert invoke(arguments(paths)) == 0
    assert json.loads(capsys.readouterr().out) == {"findings": [], "valid": True}
    assert {path: path.read_bytes() for path in tmp_path.iterdir()} == before


def test_cli_returns_one_for_count_mismatch(tmp_path: Path, capsys) -> None:
    paths = files(tmp_path)
    args = arguments(paths)
    del args[args.index("--bundle") : args.index("--bundle") + 2]
    assert invoke(args) == 1
    assert json.loads(capsys.readouterr().out)["valid"] is False


def test_cli_rejects_item_bound_before_reading(tmp_path: Path) -> None:
    manifest, source, _, receipt = files(tmp_path)
    args = ["release-evidence", "bundle", "verify-migration-chain", "--manifest", str(manifest)]
    for _ in range(65):
        args.extend(("--bundle", str(source)))
    args.extend(("--receipt", str(receipt)))
    assert invoke(args) == 2
