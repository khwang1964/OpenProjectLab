# Verification Audit Bundle Portability

> v1.3.17-v1.3.19 Design First baseline — Proposed / Pending design review

## Objective

Define a deterministic, portable, offline audit bundle that groups an accepted
verification request, its report, canonical fingerprints, and explicit manifest
metadata without adding trust or publication claims.

## v1.3.17 — Immutable bundle and canonical codec

- `VerificationAuditBundle` is immutable and owns one request document, one report
  document, their canonical fingerprints, a schema version, and deterministic
  metadata.
- Canonical JSON uses UTF-8, sorted keys, compact separators, explicit schema
  identity, and rejects duplicate or unknown fields.
- Bundle identity is a lowercase SHA-256 digest over canonical bundle bytes.
- The digest is an equality aid, not a signature or trust decision.

## v1.3.18 — Offline consistency validation

- Validation decodes the embedded documents with the accepted strict codecs.
- Request/report repository, pull-request, commit, evidence, and lifecycle identities
  must agree with the manifest.
- Every embedded fingerprint is recomputed; supplied values are never trusted.
- Failures are immutable, ordered by stable field path, deterministic, and
  fail-closed.
- Validation performs no network, Git, GitHub, subprocess, cache, or repository
  mutation.

## v1.3.19 — Stable CLI boundary

- `release-evidence bundle create --request FILE --report FILE --output FILE`
- `release-evidence bundle inspect --bundle FILE --format json|text`
- `release-evidence bundle validate --bundle FILE --format json|text`
- Create and inspect return 0 on success and 2 for input, document, or usage errors.
- Validate returns 0 for a valid bundle, 1 for recorded semantic inconsistency, and
  2 for input, document, or usage errors.
- Output-file replacement must be atomic and explicit; overwrite is denied unless
  separately authorized by the future implementation contract.

## Security and scope boundary

- No archive extraction, dynamic imports, arbitrary paths, or executable payloads.
- No signing, authentication, authorization, provenance, attestation, encryption,
  secret management, transparency log, or remote publication claim.
- No runtime verification execution, repository mutation, release creation, tag,
  upload, CLI plugin discovery, or public SDK expansion.

## Determinism

Independent invocations with identical accepted inputs produce byte-identical bundle
documents, fingerprints, validation findings, renderings, and exit classifications.
An earlier invocation cannot affect a later invocation.

## Code Review Checklist

- [ ] Data models are frozen and validate complete invariants.
- [ ] Codec rejects duplicates, unknown fields, invalid schema, and non-canonical data.
- [ ] Fingerprints are recomputed from accepted canonical documents.
- [ ] Validation is offline, stateless, deterministic, and fail-closed.
- [ ] CLI commands preserve the accepted exit-code and mutation boundaries.
- [ ] Security non-claims remain explicit in code, tests, and manuals.
- [ ] Production implementation remains Not Started until design acceptance.
