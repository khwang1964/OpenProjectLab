# Verification Report Auditability

> v1.3.14-v1.3.16 Design First baseline — Proposed / Pending design review

## Purpose

Define one deterministic offline auditability train on top of the accepted canonical
verification-report document and stable report-validation CLI.

## v1.3.14 — Canonical report fingerprint

- Accept an already decoded immutable `VerificationReport`.
- Encode it through the accepted canonical schema-version-1 report encoder.
- Compute a lowercase SHA-256 hexadecimal fingerprint from the canonical UTF-8 bytes.
- Return one immutable value object containing algorithm and digest identity.
- Reject unsupported algorithms, malformed reports, and non-canonical shortcuts.
- A fingerprint is an equality aid, not a signature, identity, trust, or authenticity claim.

## v1.3.15 — Offline semantic report comparison

- Compare two explicitly supplied, strictly decoded verification reports.
- Produce an immutable comparison containing equality and deterministic differences.
- Compare status, repository, pull request, evidence, checks, tests, and findings.
- Order differences by stable field path, never by discovery or process timing.
- Comparison owns no runtime, repository adapter, network, cache, or mutable state.

## v1.3.16 — Stable audit CLI

- Extend `release-evidence report` with `fingerprint` and `compare` operations.
- Require explicit bounded UTF-8 input files and explicit `json` or `text` output.
- Use stdout for accepted output and stderr for deterministic diagnostics.
- Preserve exit 0 for success/equality, 1 for a valid semantic difference, and 2 for
  document, input, or usage errors.
- Preserve every accepted `verify`, `request validate`, and `report validate` behavior.

## Explicit non-goals

- no production implementation in this Design Train
- no digital signature, key, certificate, identity, trust, or attestation authority
- no stdin, output persistence, batch, queue, watch, retry, polling, or scheduling
- no SDK, HTTP, RPC, plugin, marketplace, remote service, or credential management
- no repository discovery, enrichment, repair, mutation, release, or publication
- no arbitrary subprocess and no test execution

## Code Review Checklist

- [ ] Fingerprints derive only from accepted canonical report bytes.
- [ ] Comparison is semantic, immutable, deterministic, and offline.
- [ ] Exit categories do not expose platform-specific subprocess return codes.
- [ ] Existing stable CLI behavior remains additive and compatible.
- [ ] Security non-claims are explicit and testable.
- [ ] Production implementation remains Not Started for all three slices.
