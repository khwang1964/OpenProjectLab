"""Stable read-only release-evidence verification CLI."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

from generator.release_audit_bundle import (
    DEFAULT_SCHEMA_REGISTRY,
    AuditBundleCompatibilityCategory,
    AuditBundleMigrationError,
    VerificationAuditBundleBuilder,
    VerificationAuditBundleCodec,
    VerificationAuditBundleRenderer,
    VerificationAuditBundleValidator,
    inspect_audit_bundle_schema,
)
from generator.release_automation import (
    ReadOnlyVerificationInvoker,
    VerificationDocumentError,
    VerificationReportComparator,
    VerificationReportComparisonRenderer,
    VerificationReportFingerprinter,
    VerificationReportFingerprintRenderer,
    VerificationReportInspectionRenderer,
    VerificationReportInspector,
    VerificationReportRenderer,
    VerificationRequestCodec,
    VerificationRequestInspectionRenderer,
    VerificationRequestInspector,
    VerificationRuntimeConfiguration,
    build_verification_runtime,
)

MAX_REQUEST_BYTES = 1024 * 1024
MAX_REPORT_BYTES = 1024 * 1024


def add_release_evidence_parser(subparsers: argparse._SubParsersAction) -> None:
    family = subparsers.add_parser(
        "release-evidence",
        help="穩定唯讀 release evidence 驗證",
    )
    commands = family.add_subparsers(dest="release_evidence_command", required=True)
    verify = commands.add_parser("verify", help="執行一次唯讀 evidence 驗證")
    verify.add_argument("--request", type=Path, required=True, metavar="FILE")
    verify.add_argument("--format", choices=("json", "text"), required=True)
    verify.set_defaults(command_handler=_handle_verify)

    request = commands.add_parser("request", help="離線驗證 request 文件")
    request_commands = request.add_subparsers(dest="request_command", required=True)
    validate = request_commands.add_parser("validate", help="離線驗證 request")
    validate.add_argument("--request", type=Path, required=True, metavar="FILE")
    validate.add_argument("--format", choices=("json", "text"), required=True)
    validate.set_defaults(command_handler=_handle_request_validate)

    report = commands.add_parser("report", help="離線驗證 verification report")
    report_commands = report.add_subparsers(dest="report_command", required=True)
    report_validate = report_commands.add_parser("validate", help="離線驗證 report")
    report_validate.add_argument("--report", type=Path, required=True, metavar="FILE")
    report_validate.add_argument("--format", choices=("json", "text"), required=True)
    report_validate.set_defaults(command_handler=_handle_report_validate)

    report_fingerprint = report_commands.add_parser("fingerprint")
    report_fingerprint.add_argument("--report", required=True)
    report_fingerprint.add_argument("--format", choices=("json", "text"), default="text")
    report_fingerprint.set_defaults(command_handler=_handle_report_fingerprint)

    report_compare = report_commands.add_parser("compare")
    report_compare.add_argument("--left", required=True)
    report_compare.add_argument("--right", required=True)
    report_compare.add_argument("--format", choices=("json", "text"), default="text")
    report_compare.set_defaults(command_handler=_handle_report_compare)

    bundle_parser = commands.add_parser("bundle")
    bundle_commands = bundle_parser.add_subparsers(dest="bundle_command", required=True)
    bundle_create = bundle_commands.add_parser("create")
    bundle_create.add_argument("--request", required=True)
    bundle_create.add_argument("--report", required=True)
    bundle_create.add_argument("--output", required=True)
    bundle_create.set_defaults(command_handler=_handle_bundle_create)
    bundle_inspect = bundle_commands.add_parser("inspect")
    bundle_inspect.add_argument("--bundle", required=True)
    bundle_inspect.add_argument("--format", choices=("json", "text"), default="text")
    bundle_inspect.set_defaults(command_handler=_handle_bundle_inspect)
    bundle_validate = bundle_commands.add_parser("validate")
    bundle_validate.add_argument("--bundle", required=True)
    bundle_validate.add_argument("--format", choices=("json", "text"), default="text")
    bundle_validate.set_defaults(command_handler=_handle_bundle_validate)
    bundle_compatibility = bundle_commands.add_parser("compatibility")
    bundle_compatibility.add_argument("--bundle", required=True)
    bundle_compatibility.add_argument("--format", choices=("json", "text"), default="text")
    bundle_compatibility.set_defaults(command_handler=_handle_bundle_compatibility)
    bundle_migrate = bundle_commands.add_parser("migrate")
    bundle_migrate.add_argument("--bundle", required=True)
    bundle_migrate.add_argument("--target", required=True, metavar="SCHEMA")
    bundle_migrate.add_argument("--preview", action="store_true", required=True)
    bundle_migrate.add_argument("--format", choices=("json", "text"), default="text")
    bundle_migrate.set_defaults(command_handler=_handle_bundle_migrate)


def _read_request(path: Path) -> str:
    with path.open("rb") as stream:
        data = stream.read(MAX_REQUEST_BYTES + 1)
    if len(data) > MAX_REQUEST_BYTES:
        raise VerificationDocumentError("request exceeds the 1 MiB limit")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise VerificationDocumentError("request must be UTF-8") from error


def _read_report(path: Path) -> str:
    with path.open("rb") as stream:
        data = stream.read(MAX_REPORT_BYTES + 1)
    if len(data) > MAX_REPORT_BYTES:
        raise VerificationDocumentError("report exceeds the 1 MiB limit")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise VerificationDocumentError("report must be UTF-8") from error


def _non_interactive_environment() -> tuple[tuple[str, str], ...]:
    environment = dict(os.environ)
    environment["GH_PROMPT_DISABLED"] = "1"
    environment["GIT_TERMINAL_PROMPT"] = "0"
    return tuple(sorted(environment.items()))


def _handle_verify(args: argparse.Namespace) -> int:
    try:
        request = VerificationRequestCodec.decode(_read_request(args.request))
        configuration = VerificationRuntimeConfiguration(
            working_directory=args.project_root,
            environment=_non_interactive_environment(),
        )
        report = ReadOnlyVerificationInvoker(build_verification_runtime(configuration)).invoke(
            request
        )
        output = (
            VerificationReportRenderer.to_json(report)
            if args.format == "json"
            else VerificationReportRenderer.to_text(report)
        )
    except (OSError, VerificationDocumentError, TypeError, ValueError) as error:
        sys.stderr.write(f"error: {error}\n")
        return 2
    sys.stdout.write(output)
    return 0 if report.is_valid else 1


# v1.3.9-offline-request-validation-handler


def _handle_request_validate(args: argparse.Namespace) -> int:
    try:
        inspection = VerificationRequestInspector.inspect(_read_request(args.request))
        output = (
            VerificationRequestInspectionRenderer.to_json(inspection)
            if args.format == "json"
            else VerificationRequestInspectionRenderer.to_text(inspection)
        )
    except (OSError, VerificationDocumentError, TypeError, ValueError) as error:
        sys.stderr.write(f"error: {error}\n")
        return 2
    sys.stdout.write(output)
    return 0


# v1.3.13-offline-report-validation-handler


def _handle_report_validate(args: argparse.Namespace) -> int:
    try:
        inspection = VerificationReportInspector.inspect(_read_report(args.report))
        output = (
            VerificationReportInspectionRenderer.to_json(inspection)
            if args.format == "json"
            else VerificationReportInspectionRenderer.to_text(inspection)
        )
    except (OSError, VerificationDocumentError, TypeError, ValueError) as error:
        sys.stderr.write(f"error: {error}\n")
        return 2
    sys.stdout.write(output)
    return 0 if inspection.report.is_valid else 1


def _handle_report_fingerprint(args: argparse.Namespace) -> int:
    try:
        report = VerificationReportInspector.inspect(_read_report(Path(args.report))).report
        fingerprint = VerificationReportFingerprinter.fingerprint(report)
    except (OSError, UnicodeError, VerificationDocumentError) as error:
        print(str(error), file=sys.stderr)
        return 2
    renderer = VerificationReportFingerprintRenderer
    print(renderer.to_json(fingerprint) if args.format == "json" else renderer.to_text(fingerprint))
    return 0


def _handle_report_compare(args: argparse.Namespace) -> int:
    try:
        left = VerificationReportInspector.inspect(_read_report(Path(args.left))).report
        right = VerificationReportInspector.inspect(_read_report(Path(args.right))).report
        comparison = VerificationReportComparator.compare(left, right)
    except (OSError, UnicodeError, VerificationDocumentError) as error:
        print(str(error), file=sys.stderr)
        return 2
    renderer = VerificationReportComparisonRenderer
    print(renderer.to_json(comparison) if args.format == "json" else renderer.to_text(comparison))
    return 0 if comparison.is_equal else 1


def _read_bundle(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _render_bundle(bundle, validation, output_format: str) -> str:
    renderer = VerificationAuditBundleRenderer
    return (
        renderer.to_json(bundle, validation)
        if output_format == "json"
        else renderer.to_text(bundle, validation)
    )


def _handle_bundle_create(args: argparse.Namespace) -> int:
    output = Path(args.output)
    temporary = output.with_name(f".{output.name}.tmp")
    try:
        if output.exists() or temporary.exists():
            raise OSError("bundle output already exists")
        bundle = VerificationAuditBundleBuilder.build(
            _read_request(Path(args.request)), _read_report(Path(args.report))
        )
        temporary.write_text(
            VerificationAuditBundleCodec.encode(bundle),
            encoding="utf-8",
            newline="\n",
        )
        temporary.replace(output)
    except (OSError, UnicodeError, VerificationDocumentError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    return 0


def _handle_bundle_inspect(args: argparse.Namespace) -> int:
    try:
        bundle = VerificationAuditBundleCodec.decode(_read_bundle(Path(args.bundle)))
    except (OSError, UnicodeError, VerificationDocumentError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(_render_bundle(bundle, None, args.format))
    return 0


def _handle_bundle_validate(args: argparse.Namespace) -> int:
    try:
        bundle = VerificationAuditBundleCodec.decode(_read_bundle(Path(args.bundle)))
        validation = VerificationAuditBundleValidator.validate(bundle)
    except (OSError, UnicodeError, VerificationDocumentError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    print(_render_bundle(bundle, validation, args.format))
    return 0 if validation.is_valid else 1


def _handle_bundle_compatibility(args: argparse.Namespace) -> int:
    try:
        observed = inspect_audit_bundle_schema(_read_bundle(Path(args.bundle)))
        compatibility = DEFAULT_SCHEMA_REGISTRY.classify(observed)
    except (OSError, UnicodeError, VerificationDocumentError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    payload = {
        "category": compatibility.category.value,
        "current_schema": compatibility.current_schema,
        "migration_steps": list(compatibility.migration_steps),
        "observed_schema": compatibility.observed_schema,
    }
    if args.format == "json":
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    else:
        print(f"compatibility: {compatibility.category.value}")
        print(f"observed-schema: {compatibility.observed_schema}")
        print(f"current-schema: {compatibility.current_schema}")
        for step in compatibility.migration_steps:
            print(f"migration-step: {step}")
    return (
        0
        if compatibility.category
        in {
            AuditBundleCompatibilityCategory.CURRENT,
            AuditBundleCompatibilityCategory.MIGRATABLE,
        }
        else 1
    )


def _handle_bundle_migrate(args: argparse.Namespace) -> int:
    try:
        observed = inspect_audit_bundle_schema(_read_bundle(Path(args.bundle)))
        plan = DEFAULT_SCHEMA_REGISTRY.plan(observed, args.target)
    except AuditBundleMigrationError as error:
        print(str(error), file=sys.stderr)
        return 1
    except (OSError, UnicodeError, VerificationDocumentError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 2
    payload = {
        "preview_fingerprint": plan.preview_fingerprint,
        "source_schema": plan.source_schema,
        "steps": list(plan.steps),
        "target_schema": plan.target_schema,
    }
    if args.format == "json":
        print(json.dumps(payload, sort_keys=True, separators=(",", ":")))
    else:
        print(f"source-schema: {plan.source_schema}")
        print(f"target-schema: {plan.target_schema}")
        for step in plan.steps:
            print(f"migration-step: {step}")
        print(f"preview-fingerprint: sha256:{plan.preview_fingerprint}")
    return 0
