# Canonical Verification Request Serialization

> v1.3.8 Design First baseline — Proposed / Pending design review

## Context

v1.3.6 accepts strict schema-version-1 request decoding, but callers still lack an
accepted inverse operation for producing canonical request JSON. Manual construction
increases formatting and schema drift without adding useful authority.

## Decision

Define one deterministic encoder over an existing immutable `VerificationRequest`:

- accepts only a complete `VerificationRequest`
- emits the existing schema-version-1 field set and no additional keys
- uses native JSON string and integer types without coercion
- preserves the complete focused-test evidence supplied by the caller
- emits canonical compact UTF-8-compatible JSON ending with exactly one newline
- provides byte-stable output for equal requests
- round-trips through the accepted strict decoder without information loss

The encoder performs no discovery, inference, correction, command execution, file
access, persistence, logging, telemetry, or publication.

## Failure boundary

Wrong object types and invalid model state fail before serialization. The encoder
does not suppress errors or manufacture a partially valid document.

## Deferred

- production implementation
- schema version 2, migration, aliases, optional keys, and compatibility repair
- repository, branch, SHA, PR, CI, or focused-test discovery
- CLI registration, SDK, HTTP, RPC, plugin, persistence, and output files
- test execution, arbitrary subprocess, mutation, release, and publication

## Code Review Checklist

- [ ] The encoder accepts only the existing immutable request model.
- [ ] Schema version and exact keys remain identical to the accepted decoder.
- [ ] Equal requests produce byte-identical canonical JSON.
- [ ] Canonical output ends with exactly one newline.
- [ ] Encode/decode round-trip preserves every request field.
- [ ] No discovery, coercion, repair, I/O, command, or mutation is introduced.
