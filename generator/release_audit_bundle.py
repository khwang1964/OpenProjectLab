from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any

from generator.release_automation import (
    VerificationDocumentError,
    VerificationReportCodec,
    VerificationReportEncoder,
    VerificationRequestCodec,
    VerificationRequestEncoder,
)

SCHEMA_VERSION = "1"


def _sha256(document: str) -> str:
    return hashlib.sha256(document.encode("utf-8")).hexdigest()


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise VerificationDocumentError(f"duplicate field: {key}")
        result[key] = value
    return result


@dataclass(frozen=True, slots=True)
class VerificationAuditBundle:
    schema_version: str
    request_document: str
    report_document: str
    request_sha256: str
    report_sha256: str
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError("unsupported audit-bundle schema version")
        for name, digest in (
            ("request_sha256", self.request_sha256),
            ("report_sha256", self.report_sha256),
        ):
            if len(digest) != 64 or any(
                character not in "0123456789abcdef" for character in digest
            ):
                raise ValueError(f"{name} must be 64 lowercase hexadecimal characters")
        if self.metadata != tuple(sorted(self.metadata)):
            raise ValueError("metadata must be sorted")
        keys = [key for key, _ in self.metadata]
        if len(keys) != len(set(keys)) or any(not key for key in keys):
            raise ValueError("metadata keys must be nonempty and unique")


class VerificationAuditBundleBuilder:
    @staticmethod
    def build(
        request_document: str, report_document: str, metadata: dict[str, str] | None = None
    ) -> VerificationAuditBundle:
        request = VerificationRequestCodec.decode(request_document)
        report = VerificationReportCodec.decode(report_document)
        canonical_request = VerificationRequestEncoder.encode(request)
        canonical_report = VerificationReportEncoder.encode(report)
        return VerificationAuditBundle(
            SCHEMA_VERSION,
            canonical_request,
            canonical_report,
            _sha256(canonical_request),
            _sha256(canonical_report),
            tuple(sorted((metadata or {}).items())),
        )


class VerificationAuditBundleCodec:
    _FIELDS = frozenset(
        {
            "schema_version",
            "request_document",
            "report_document",
            "request_sha256",
            "report_sha256",
            "metadata",
        }
    )

    @staticmethod
    def encode(bundle: VerificationAuditBundle) -> str:
        payload = {
            "metadata": dict(bundle.metadata),
            "report_document": bundle.report_document,
            "report_sha256": bundle.report_sha256,
            "request_document": bundle.request_document,
            "request_sha256": bundle.request_sha256,
            "schema_version": bundle.schema_version,
        }
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @classmethod
    def decode(cls, document: str) -> VerificationAuditBundle:
        try:
            payload = json.loads(document, object_pairs_hook=_strict_object)
        except (json.JSONDecodeError, TypeError) as error:
            raise VerificationDocumentError("audit bundle is not valid JSON") from error
        if not isinstance(payload, dict) or set(payload) != cls._FIELDS:
            raise VerificationDocumentError("audit bundle fields do not match the schema")
        metadata = payload["metadata"]
        if not isinstance(metadata, dict) or not all(
            isinstance(k, str) and isinstance(v, str) for k, v in metadata.items()
        ):
            raise VerificationDocumentError("audit bundle metadata must map strings to strings")
        try:
            bundle = VerificationAuditBundle(
                payload["schema_version"],
                payload["request_document"],
                payload["report_document"],
                payload["request_sha256"],
                payload["report_sha256"],
                tuple(sorted(metadata.items())),
            )
        except (TypeError, ValueError) as error:
            raise VerificationDocumentError(str(error)) from error
        if cls.encode(bundle) != document:
            raise VerificationDocumentError("audit bundle is not canonical JSON")
        return bundle


@dataclass(frozen=True, slots=True, order=True)
class VerificationAuditBundleFinding:
    path: str
    message: str


@dataclass(frozen=True, slots=True)
class VerificationAuditBundleValidation:
    findings: tuple[VerificationAuditBundleFinding, ...]

    @property
    def is_valid(self) -> bool:
        return not self.findings


class VerificationAuditBundleValidator:
    @staticmethod
    def validate(bundle: VerificationAuditBundle) -> VerificationAuditBundleValidation:
        findings: list[VerificationAuditBundleFinding] = []
        if _sha256(bundle.request_document) != bundle.request_sha256:
            findings.append(
                VerificationAuditBundleFinding(
                    "$.request_sha256", "does not match request_document"
                )
            )
        if _sha256(bundle.report_document) != bundle.report_sha256:
            findings.append(
                VerificationAuditBundleFinding("$.report_sha256", "does not match report_document")
            )
        for path, decoder, document in (
            ("$.request_document", VerificationRequestCodec.decode, bundle.request_document),
            ("$.report_document", VerificationReportCodec.decode, bundle.report_document),
        ):
            try:
                decoder(document)
            except VerificationDocumentError as error:
                findings.append(VerificationAuditBundleFinding(path, str(error)))
        return VerificationAuditBundleValidation(tuple(sorted(findings)))


class VerificationAuditBundleRenderer:
    @staticmethod
    def to_json(
        bundle: VerificationAuditBundle, validation: VerificationAuditBundleValidation | None = None
    ) -> str:
        payload: dict[str, Any] = {
            "metadata": dict(bundle.metadata),
            "report_sha256": bundle.report_sha256,
            "request_sha256": bundle.request_sha256,
            "schema_version": bundle.schema_version,
        }
        if validation is not None:
            payload["findings"] = [
                {"message": item.message, "path": item.path} for item in validation.findings
            ]
            payload["valid"] = validation.is_valid
        return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))

    @staticmethod
    def to_text(
        bundle: VerificationAuditBundle, validation: VerificationAuditBundleValidation | None = None
    ) -> str:
        lines = [
            f"schema: {bundle.schema_version}",
            f"request: sha256:{bundle.request_sha256}",
            f"report: sha256:{bundle.report_sha256}",
        ]
        if validation is not None:
            lines.append(f"valid: {str(validation.is_valid).lower()}")
            lines.extend(f"{item.path}: {item.message}" for item in validation.findings)
        return "\n".join(lines)
