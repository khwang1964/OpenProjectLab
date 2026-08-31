"""Stable read-only release-evidence verification CLI."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from generator.release_automation import (
    ReadOnlyVerificationInvoker,
    VerificationDocumentError,
    VerificationReportRenderer,
    VerificationRequestCodec,
    VerificationRequestInspectionRenderer,
    VerificationRequestInspector,
    VerificationRuntimeConfiguration,
    build_verification_runtime,
)

MAX_REQUEST_BYTES = 1024 * 1024


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


def _read_request(path: Path) -> str:
    with path.open("rb") as stream:
        data = stream.read(MAX_REQUEST_BYTES + 1)
    if len(data) > MAX_REQUEST_BYTES:
        raise VerificationDocumentError("request exceeds the 1 MiB limit")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError as error:
        raise VerificationDocumentError("request must be UTF-8") from error


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
