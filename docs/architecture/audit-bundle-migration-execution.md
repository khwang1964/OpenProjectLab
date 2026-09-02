# Audit Bundle Migration Execution

> v1.3.23-v1.3.25 Design First baseline — Proposed / Pending design review

## Objective

Define deterministic, offline, explicitly authorized audit-bundle migration
execution without modifying the source bundle, silently replacing an output, or
claiming security properties that migration cannot establish.

## Accepted predecessor

The design builds on the accepted v1.3.20-v1.3.22 compatibility classifier,
explicit migration graph, deterministic migration plan, preview fingerprint, and
preview-only CLI. Those accepted contracts remain unchanged.

## v1.3.23 — Deterministic offline migration application

- `AuditBundleMigrationRequest` is immutable and identifies the source bundle,
  explicit target schema, accepted migration-plan fingerprint, and distinct output.
- `AuditBundleMigrationResult` is immutable and records the source identity, target
  identity, ordered executed steps, canonical output digest, and migration receipt.
- Execution accepts only one explicit, unambiguous plan whose preview fingerprint
  matches the request.
- Migration steps are selected only from an immutable local registry; dynamic import,
  plugin discovery, lexical guessing, and network resolution are forbidden.
- Equivalent source bytes, request, registry, and target produce byte-identical
  canonical output and receipt.
- The source bundle is never rewritten or deleted.

## v1.3.24 — Fail-closed output verification

- Output is staged separately and decoded only with the explicit target-schema codec.
- Verification requires the target schema, canonical document invariants, migration
  receipt, and output digest to agree before publication.
- Any step failure, target validation failure, digest mismatch, ambiguous plan, or
  output conflict leaves no published partial output.
- Existing outputs are never silently overwritten.
- A migration receipt is reproducibility evidence only; it is not trust, provenance,
  authentication, authorization, signing, or attestation evidence.

## v1.3.25 — Stable explicitly authorized CLI

- `release-evidence bundle migrate --bundle INPUT --target SCHEMA --output OUTPUT
  --execute`
- `--execute` is mandatory for mutation; omission remains preview-only behavior.
- Input and output must resolve to distinct paths.
- The command refuses an existing output unless a separately designed explicit
  replacement policy is accepted.
- Exit 0 means one verified output was published; exit 1 means compatibility,
  planning, execution, or verification failure; exit 2 means input, document, usage,
  or path error.
- JSON and text results use stable fields and never expose process-dependent paths or
  exception representations.

## Security and scope boundary

- Offline local file output is the only newly proposed mutation.
- No source rewrite, in-place migration, archive extraction, dynamic import, plugin
  discovery, network access, Git/GitHub access, repository mutation, tag, release, or
  remote publication.
- No signing, authentication, authorization system, trust, provenance, attestation,
  encryption, or secret management.
- Explicit CLI authorization controls execution intent only and is not an identity
  or access-control claim.

## Determinism and atomicity

Planning, execution-step order, canonical output, receipts, digests, renderings, and
exit classifications depend only on explicit inputs. A verified output is published
atomically only after every step and target validation succeeds.

## Code Review Checklist

- [ ] Execution requires the exact accepted preview fingerprint.
- [ ] Source and output are distinct and the source remains unchanged.
- [ ] Migration steps come only from an immutable local registry.
- [ ] Failed execution or validation publishes no partial output.
- [ ] Existing output handling is fail closed.
- [ ] Receipts and digests are not represented as trust evidence.
- [ ] Production implementation remains Not Started until design acceptance.
