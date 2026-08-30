# Deterministic Verification I/O Contracts

> v1.3.6 Design First baseline — Proposed / Pending design review

## Context

v1.3.5 defines one internal invocation over immutable request and report objects.
A read-only external entry point also requires deterministic interchange without
exposing Python object construction or permitting ambiguous input.

## Decision

Define strict, versioned serialization contracts for `VerificationRequest` and
`VerificationReport`, plus a deterministic human-readable report renderer.

- UTF-8 JSON with one explicit schema version
- exact required keys and rejection of unknown keys
- stable field names, finding categories, collection ordering, and JSON key order
- finite integers and booleans represented only by their native JSON types
- no timestamps, host paths, environment values, credentials, or random identifiers
- canonical compact JSON ending with exactly one newline
- stable text rendering derived only from the immutable report

## Request decoding

Decoding validates the complete document before invocation. Missing, duplicate,
unknown, incorrectly typed, or out-of-range values fail closed. Repository, branch,
SHA, pull-request, CI, and focused-test identities remain caller supplied. Decoding
performs no discovery, command execution, correction, coercion, or default inference.

## Report encoding

Encoding preserves the accepted report without suppressing or merging findings.
Collection, contradiction, and validation findings retain separate categories and
deterministic order. JSON and text representations must communicate the same status.

## Deferred

- production implementation
- CLI, public SDK, HTTP, RPC, plugin, or entry-point exposure
- file writes, persistence, caching, telemetry, signing, or encryption
- schema migration, compatibility aliases, automatic repair, or enrichment
- pytest, coverage, arbitrary subprocess execution, or Git/GitHub mutation

## Code Review Checklist

- [ ] Request and report schemas have one explicit version.
- [ ] Required keys, types, ranges, and unknown-key rejection are exact.
- [ ] Canonical JSON is byte-stable and ends with one newline.
- [ ] Text and JSON preserve the same status and finding categories.
- [ ] No timestamp, host, environment, credential, or random data can leak.
- [ ] Decoding performs no discovery, coercion, repair, or command execution.
- [ ] Rendering performs no file write, mutation, or publication.
- [ ] Deterministic fixtures cover valid and invalid documents.
