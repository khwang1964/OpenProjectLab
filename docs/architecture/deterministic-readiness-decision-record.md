# Deterministic Readiness Decision Record

> Design First baseline — Proposed / Pending design review

## Objective

Define a canonical offline record that combines an accepted readiness evaluation and optional
baseline comparison into one deterministic, auditable handoff for human release review.

## Decision model

- `ReadinessDecisionRecord` binds the repository, candidate revision, policy revision, exact
  evaluation outcome, optional baseline revision, and exact comparison category.
- Stable dispositions are `REVIEWABLE`, `BLOCKED`, and `INDETERMINATE`; no disposition means
  approved, released, or published.
- `READY` evaluation with no `REGRESSED` or `INCOMPARABLE` comparison is `REVIEWABLE`.
- Any blocked gate or regression is `BLOCKED`; invalid, mismatched, contradictory, or
  incomparable evidence is `INDETERMINATE`.
- Findings preserve stable source, path, reason code, category, and deterministic ordering.

## Bounded offline read-only CLI

- `release-evidence readiness decide --snapshot SNAPSHOT --policy POLICY --baseline BASELINE`
  with `--format json|text`
- `--baseline` is optional; when omitted, the record explicitly reports no comparison evidence.
- Every input uses the accepted strict canonical snapshot or policy codec.
- Per-document and aggregate-byte limits apply before decoding.
- Exit 0 means reviewable, exit 1 means blocked, and exit 2 means invalid or indeterminate.
- Inputs are explicitly named local files; the command performs no discovery or mutation.

## Authority and finish-line boundary

The record is evidence for human review, not release authorization. It does not infer ancestry,
establish provenance or authenticity, waive gates, approve compatibility, access credentials or
networks, or mutate versions, repositories, tags, artifacts, signatures, GitHub Releases, or
publication state.

This is the final planned v1.4 feature slice. After implementation acceptance, the train enters a
finish-line review; a v1.4.4 feature slice requires an explicitly identified acceptance gap or
separate roadmap decision.

## Code Review Checklist

- [ ] Inputs use accepted canonical codecs and explicit repository/revision identities.
- [ ] Dispositions and findings are deterministic and fail closed.
- [ ] Optional baseline absence is explicit and never treated as comparison success.
- [ ] Byte limits apply before decoding and no input discovery occurs.
- [ ] Exit outcomes 0, 1, and 2 match reviewable, blocked, and indeterminate states.
- [ ] The record never claims approval, release, publication, ancestry, or trust.
- [ ] Runtime remains bounded, offline, read-only, and credential-free.
- [ ] Architecture, tests, documentation, governance, and checklist agree.
- [ ] Production implementation remains Not Started until design acceptance.
- [ ] v1.4 exits feature expansion after this slice unless a verified gap requires otherwise.
