# Audit Bundle Migration Chain Verification

> v1.3.29-v1.3.31 Design First baseline — Accepted / Completed

## Objective

Define deterministic, offline, read-only verification of an ordered chain of accepted
migration receipts and bundle documents, from one explicit initial bundle to one
explicit final bundle, without executing or repairing any migration.

## v1.3.29 — Canonical chain manifest

- `AuditBundleMigrationChainManifest` is immutable and records a manifest schema,
  initial bundle SHA-256, final bundle SHA-256, and ordered receipt SHA-256 identities.
- Decoding accepts one canonical JSON object with exact required fields and rejects
  duplicate keys, unknown fields, malformed digests, empty chains, and ambiguity.
- Receipt order is significant; canonical rendering is byte-stable and contains no
  filesystem paths, timestamps, host identity, or process-dependent values.
- A chain manifest records equality and continuity evidence only. It is not a
  signature, authorization, trust, provenance, or attestation claim.

## v1.3.30 — Deterministic offline chain verifier

- `AuditBundleMigrationChainVerifier` receives an explicit manifest document, an
  ordered tuple of bundle documents, an ordered tuple of receipt documents, and the
  explicit schema registry.
- A chain of N receipts requires exactly N+1 bundles. Each receipt is verified with
  the accepted single-receipt verifier against its adjacent source and output bundle.
- The verifier checks manifest digests, receipt identities, bundle adjacency, schema
  continuity, ordered steps, plan fingerprints, and the initial/final bindings.
- Count mismatches, broken adjacency, reordered or duplicate receipts, cycles,
  unknown schemas, malformed inputs, and ambiguous plans fail closed.
- Findings use stable indexed field paths and deterministic ordering; no input is
  inferred, reordered, fetched, repaired, or rewritten.

## v1.3.31 — Stable bounded read-only CLI

- `release-evidence bundle verify-migration-chain --manifest MANIFEST`
  `--bundle BUNDLE [--bundle BUNDLE ...]`
  `--receipt RECEIPT [--receipt RECEIPT ...] --format json|text`
- Repeated bundle and receipt arguments preserve command-line order. Explicit count
  and aggregate-byte limits reject unbounded requests before verification.
- Exit 0 means the complete chain matches; exit 1 means deterministic verification
  findings; exit 2 means an input, document, bound, or usage error.
- The command reads only explicitly named local files and never discovers, writes,
  replaces, deletes, executes, migrates, publishes, or mutates repository state.

## Determinism and safety boundary

- Equivalent ordered inputs produce byte-identical results, findings, renderings,
  and exit classifications without invocation-history or process-global state.
- No migration execution, rollback, source rewriting, output creation, directory or
  glob discovery, archive extraction, dynamic import, plugin discovery, network
  access, Git/GitHub operation, or repository mutation.
- No signing, authentication, authorization, identity, trust, provenance,
  attestation, encryption, secret management, remote publication, tag, or release.

## Code Review Checklist

- [ ] Manifest parsing is strict, canonical, immutable, and fail closed.
- [ ] N receipts require exactly N+1 explicitly ordered bundle documents.
- [ ] Every receipt and adjacency edge reuses accepted single-receipt verification.
- [ ] Initial, final, receipt, schema, step, plan, and continuity bindings are checked.
- [ ] Findings and renderings are deterministic and use stable indexed field paths.
- [ ] CLI count and byte bounds are enforced before verification.
- [ ] CLI behavior remains offline, read-only, and free of implicit discovery.
- [ ] Equality and continuity evidence remain separate from trust and provenance.
- [ ] Production implementation remains Not Started until design acceptance.
