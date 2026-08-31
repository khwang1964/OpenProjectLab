# Verification Report Usability

> v1.3.11-v1.3.13 Design First baseline — Design Accepted / Completed

## Purpose

Define one deterministic, read-only report-usability train on top of the accepted
verification request, runtime, invocation, and stable CLI boundaries.

## v1.3.11 — Canonical verification report serialization

- Serialize the accepted immutable verification report as schema-version-1 JSON.
- Preserve field identity, ordering, scalar types, evidence ordering, and failure data.
- Require strict decoding and canonical round-trip equality.
- Reject unknown schema versions, unknown fields, malformed values, and lossy coercion.
- Serialization is pure and cannot invoke Git, GitHub, subprocesses, or a runtime.

## v1.3.12 — Offline report validation and inspection

- Accept only bounded UTF-8 report documents supplied explicitly by the caller.
- Validate and inspect reports without constructing or invoking a verification runtime.
- Produce deterministic JSON or text inspection output from the decoded report.
- Distinguish document errors from a valid report that records verification failure.
- Own no cache, persistence, discovery, retry, polling, or mutable cross-call state.

## v1.3.13 — Stable result and exit-code contract

- Extend the stable `release-evidence` CLI family with report-only operations.
- Keep human-readable output on stdout and diagnostics on stderr deterministic.
- Define stable exit categories for success, recorded verification failure, and input or
  usage error without exposing platform-specific subprocess return codes.
- Preserve all existing request, preview, verify, and request-validation behavior.
- CLI stability does not authorize execution beyond the accepted read-only allowlist.

## Explicit non-goals

- no production implementation in this Design Train
- no stdin, output-file persistence, batch, queue, watch, retry, polling, or scheduling
- no SDK, HTTP, RPC, plugin, marketplace, remote service, or credential management
- no repository discovery, enrichment, repair, mutation, release, or publication
- no arbitrary subprocess and no test execution

## Code Review Checklist

- [ ] The three contracts compose without overlapping authority.
- [ ] Report serialization is canonical, strict, deterministic, and pure.
- [ ] Offline inspection cannot construct or invoke a runtime.
- [ ] Exit categories do not leak platform-specific process return codes.
- [ ] Existing stable CLI behavior remains additive and compatible.
- [ ] Production implementation remains Not Started for all three slices.

<!-- v1.3.11-v1.3.13-verification-report-usability-terminal-alignment-architecture -->

## Implementation alignment

- Production implementation — Implemented.
- PR #302 merge and synchronized-main focused verification — Completed.
- Terminal alignment — Pending merge and verification.
- Implementation acceptance — Pending separate closure.
