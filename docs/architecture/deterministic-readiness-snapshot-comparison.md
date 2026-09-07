# Deterministic Readiness Snapshot Comparison

> Design First baseline — Proposed / Pending design review

## Objective

Define an offline comparison contract for two accepted readiness snapshots so evidence drift
between an explicit baseline and candidate revision is visible, deterministic, and auditable.

## Comparison model

- `ReadinessSnapshotComparison` binds the exact baseline and candidate repository identities
  and revisions without treating revision order as ancestry or trust.
- Stable categories are `UNCHANGED`, `IMPROVED`, `REGRESSED`, and `INCOMPARABLE`.
- Deterministic findings cover required checks, focused and regression counts, coverage,
  audit-chain acceptance, supported surfaces, limitations, and release blockers.
- Findings have stable reason codes, field paths, before/after values, and ordering.
- Repository mismatch, malformed input, missing fields, unsupported schemas, or contradictory
  evidence fails closed and cannot report improvement.

## Bounded offline read-only CLI

- `release-evidence readiness compare --baseline BASELINE --candidate CANDIDATE --format json|text`
- Both documents use the accepted strict canonical snapshot codec.
- Per-document and aggregate-byte limits apply before decoding.
- Exit 0 means no regression; exit 1 means regression; exit 2 means invalid or incomparable.
- The command reads only explicitly named local files and performs no discovery or mutation.

## Authority boundary

Comparison describes evidence differences only. It does not prove Git ancestry, provenance,
authenticity, release approval, or compatibility promotion. It cannot waive readiness gates,
collect remote evidence, access credentials or networks, or mutate versions, repositories,
tags, artifacts, signatures, GitHub Releases, or publication state.

## Code Review Checklist

- [ ] Inputs use the accepted strict canonical snapshot codec.
- [ ] Baseline and candidate identities and revisions remain explicit.
- [ ] Categories, reason codes, field paths, values, and ordering are deterministic.
- [ ] Regressions in every readiness gate are fail closed.
- [ ] Incomparable evidence cannot be classified as improved.
- [ ] CLI limits apply before decoding and inputs are explicitly named.
- [ ] Runtime remains offline, bounded, read-only, and free of discovery.
- [ ] Comparison remains separate from ancestry, trust, authorization, and publication.
- [ ] Architecture, tests, documentation, governance, and checklist agree.
- [ ] Production implementation remains Not Started until design acceptance.
