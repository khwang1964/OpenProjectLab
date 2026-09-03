# Audit Bundle Migration Receipt Verification

> v1.3.26-v1.3.28 Design First baseline — Accepted / Completed

## Objective

Define deterministic, offline, read-only verification of an audit-bundle migration
receipt against the exact source document, migrated output, accepted migration plan,
and explicit schema registry.

## v1.3.26 — Canonical receipt contract

- `AuditBundleMigrationReceipt` is immutable and contains the source schema, target
  schema, ordered steps, source SHA-256, output SHA-256, and plan fingerprint.
- Receipt decoding accepts one canonical JSON object with exact required fields and
  rejects duplicate keys, unknown fields, malformed digests, and ambiguous values.
- Receipt field order in input is irrelevant; canonical rendering is byte-stable.
- A receipt records equality evidence only. It is not a signature, identity,
  authorization, trust, provenance, or attestation claim.

## v1.3.27 — Offline verifier

- `AuditBundleMigrationReceiptVerifier` receives explicit source, output, receipt,
  and schema registry inputs and returns an immutable verification result.
- Verification recomputes both document digests, derives the exact migration plan,
  and compares schemas, steps, plan fingerprint, and output identity.
- Every mismatch produces a stable field path and deterministic finding order.
- Unknown schemas, unknown steps, ambiguous plans, malformed documents, and partial
  receipts fail closed; no field is inferred or repaired.

## v1.3.28 — Stable read-only CLI

- `release-evidence bundle verify-migration --bundle SOURCE --output TARGET`
  `--receipt RECEIPT --format json|text`
- Exit 0 means every receipt binding matches; exit 1 means a recorded verification
  mismatch; exit 2 means an input, document, or usage error.
- The command reads bounded local files only and never writes, replaces, deletes,
  executes, migrates, publishes, or mutates repository state.

## Determinism and safety boundary

- Equivalent inputs produce byte-identical results, ordered findings, renderings,
  and exit classifications without invocation-history or process-global state.
- No migration execution, source rewriting, output creation, archive extraction,
  dynamic import, plugin discovery, network access, Git/GitHub operation, or
  repository mutation.
- No signing, authentication, authorization, trust, provenance, attestation,
  encryption, secret management, remote publication, tag, or release operation.

## Code Review Checklist

- [ ] Receipt parsing is strict, canonical, immutable, and fail closed.
- [ ] Source, output, plan, step, schema, and fingerprint bindings are all verified.
- [ ] Findings and renderings are deterministic and use stable field paths.
- [ ] CLI behavior is bounded, offline, read-only, and uses stable exit classes.
- [ ] Equality evidence remains explicitly separate from trust and provenance.
- [ ] Production implementation remains Not Started until design acceptance.
