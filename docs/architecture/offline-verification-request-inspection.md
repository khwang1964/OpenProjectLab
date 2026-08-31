# Offline Verification Request Inspection

> v1.3.9 Design First baseline — Accepted / Terminally Closed

## Context

Canonical request serialization enables a safe offline boundary where a caller can
validate and inspect a request before allowing any repository or GitHub command.

## Decision

Define one stateless offline inspection service and one explicit experimental command:

`opl release-evidence request validate --request <path> --format json|text`

The lifecycle is fixed:

1. read one caller-selected bounded UTF-8 document
2. decode with the accepted strict schema-version-1 codec
3. encode the immutable request canonically
4. render one deterministic validation result
5. return exit status `0` for valid input or `2` for invalid/unreadable input

JSON output contains only `schema_version`, `status`, and the canonical request.
Text output communicates the same status and explicit request identities. Successful
output uses stdout; diagnostics use stderr; each output ends with one newline.

## Offline authority boundary

Validation never builds a verification runtime and never invokes Git, GitHub, pytest,
coverage, an adapter, the orchestrator, or an arbitrary subprocess. It cannot modify
the request or repository and cannot write an output file.

## Deferred

- production implementation
- stdin, globbing, batch, queue, watch, retry, polling, and interactive mode
- automatic repair, defaults, discovery, enrichment, and credential handling
- public SDK, HTTP, RPC, plugin, cache, persistence, telemetry, and scheduling
- mutation, test execution, release, publication, and output files

## Code Review Checklist

- [ ] Request path and output format remain explicit and mandatory.
- [ ] Exactly one bounded UTF-8 document is read.
- [ ] Strict decoding and canonical encoding are reused unchanged.
- [ ] Valid and invalid status/stream/exit-code combinations are exhaustive.
- [ ] No runtime, adapter, Git, GitHub, test, or arbitrary command can execute.
- [ ] No repair, discovery, mutation, persistence, or output file is added.
