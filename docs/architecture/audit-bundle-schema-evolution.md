# Audit Bundle Schema Evolution

> v1.3.20-v1.3.22 Design First baseline — Accepted / Completed

## Objective

Define deterministic, offline schema compatibility and migration-preview contracts
for verification audit bundles without modifying source bundles or accepting unknown
schemas implicitly.

## v1.3.20 — Compatibility classification

- `AuditBundleSchemaCompatibility` is immutable and classifies an observed schema as
  `CURRENT`, `MIGRATABLE`, `FUTURE`, or `UNSUPPORTED`.
- Classification uses an explicit registry of known schema identities and directed
  migration edges; lexical or numeric guessing is forbidden.
- Unknown and future schemas fail closed and never decode through the current codec.
- Equivalent inputs produce byte-identical classifications and ordered findings.

## v1.3.21 — Migration planning

- `AuditBundleMigrationPlan` is immutable and contains the source schema, target
  schema, ordered explicit steps, and deterministic preview fingerprint.
- Planning validates every migration edge before producing a plan.
- Planning never executes a migration, rewrites a bundle, or writes a file.
- Cycles, missing edges, ambiguous paths, downgrades, and unsupported targets fail
  closed with stable field paths.

## v1.3.22 — Stable preview CLI

- `release-evidence bundle compatibility --bundle FILE --format json|text`
- `release-evidence bundle migrate --bundle FILE --target SCHEMA --preview`
- Compatibility returns 0 only for current or explicitly migratable schemas, 1 for a
  recorded incompatibility, and 2 for input, document, or usage errors.
- Migration preview returns 0 only for one valid deterministic plan and never writes
  output; all failures use stable exit classes.

## Security and scope boundary

- No migration execution, source rewrite, output file, archive extraction, dynamic
  import, plugin discovery, network access, Git/GitHub access, or repository mutation.
- No signing, authentication, authorization, trust, provenance, attestation,
  encryption, secret management, remote publication, tag, or release operation.
- No automatic fallback from an unknown schema to the current decoder.

## Determinism

Compatibility classification, migration paths, findings, preview fingerprints,
renderings, and exit classifications are independent of invocation history and
process-global mutable state.

## Code Review Checklist

- [ ] Compatibility categories and schema identities are immutable and explicit.
- [ ] The migration graph rejects ambiguity, cycles, downgrade, and unknown edges.
- [ ] Preview planning performs no migration or filesystem mutation.
- [ ] CLI syntax and exit classes are stable and fail closed.
- [ ] Security non-claims remain explicit in code, tests, and manuals.
- [ ] Production implementation remains Not Started until design acceptance.
