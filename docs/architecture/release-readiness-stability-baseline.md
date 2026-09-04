# v1.4.0 Release Readiness Stability Baseline

> Design First baseline — Proposed / Pending design review

## Objective

Define a deterministic, fail-closed, evidence-backed stability assessment for the
accepted v1.3 platform before any v1.4 release identity, tag, artifact, publication,
or compatibility promotion is authorized.

## Evidence snapshot

- `ReleaseReadinessStabilitySnapshot` is immutable and binds the explicit repository
  identity, evaluated revision, required-check results, focused and full-regression
  summaries, coverage result and threshold, accepted audit-bundle chain identity,
  supported public surfaces, known limitations, and evidence collection time.
- Decoding accepts one canonical JSON object with exact required fields and rejects
  duplicate keys, unknown fields, malformed revisions, invalid counts, non-finite
  coverage values, missing gates, and contradictory evidence.
- canonical rendering is byte-stable. Repository paths, credentials, host identity,
  environment secrets, and process-dependent values are excluded.
- The snapshot records observed evidence only. It is not a signature, authorization,
  trust, provenance, release approval, or publication instruction.

## Deterministic stability evaluator

- `ReleaseReadinessStabilityEvaluator` receives an explicit snapshot, an explicit
  stability policy, and the accepted contract registry; it performs no discovery.
- Stable outcomes are `READY`, `BLOCKED`, and `INDETERMINATE`, with deterministic
  findings, stable field paths, stable ordering, and documented reason codes.
- Missing, stale, malformed, incomplete, conflicting, or revision-mismatched evidence
  fails closed as `INDETERMINATE` or `BLOCKED`; it can never produce `READY`.
- `READY` requires synchronized repository identity, successful required CI checks,
  passing focused and full regression evidence, coverage meeting the configured
  threshold, accepted audit-chain verification, and no unresolved release blocker.
- The evaluator cannot waive gates, infer absent results, reuse evidence from another
  revision, change support classification, or convert assumptions into facts.

## Stable bounded read-only CLI

- `release-evidence readiness evaluate --snapshot SNAPSHOT --policy POLICY`
  `--format json|text`
- Explicit document and aggregate-byte limits reject unbounded input before parsing.
- Exit 0 means `READY`; exit 1 means `BLOCKED`; exit 2 means invalid input, usage error,
  or `INDETERMINATE` evidence that cannot establish readiness.
- The command reads only explicitly named local files and never discovers, writes,
  repairs, stages, commits, pushes, merges, tags, publishes, or mutates repository state.

## Stability and release boundary

- v1.4.0 readiness evaluates the accepted v1.3 public CLI, SDK, Bootstrap Framework,
  release-evidence, audit-bundle, and migration-verification contracts without silently
  expanding their compatibility promises.
- Passing evaluation is necessary evidence, not release authorization. Version changes,
  tags, artifacts, GitHub Releases, package publication, signing, and promotion remain
  separate explicitly authorized transitions.
- No network access, Git/GitHub operation, dynamic import, plugin discovery, credential
  lookup, secret management, remote attestation, rollback, repair, or repository mutation.

## Code Review Checklist

- [ ] Snapshot parsing is strict, canonical, immutable, and fail closed.
- [ ] Evidence is bound to one explicit repository identity and revision.
- [ ] Required checks, tests, coverage, audit chain, limitations, and blockers are explicit.
- [ ] Missing, stale, conflicting, or revision-mismatched evidence cannot yield `READY`.
- [ ] Outcomes, findings, reason codes, field paths, and renderings are deterministic.
- [ ] CLI limits are enforced before parsing and all inputs are explicitly named.
- [ ] Evaluation remains offline, bounded, read-only, and free of implicit discovery.
- [ ] Readiness evidence remains separate from release authorization and publication.
- [ ] Existing v1.3 compatibility boundaries are preserved without silent promotion.
- [ ] Production implementation remains Not Started until design acceptance.
