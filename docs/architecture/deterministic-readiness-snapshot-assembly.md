# Deterministic Readiness Snapshot Assembly

> Design First baseline — Proposed / Pending design review

## Objective

Define a deterministic local assembler for the accepted v1.4.0
`ReleaseReadinessStabilitySnapshot` so callers do not manually compose readiness evidence.

## Explicit evidence manifest

- `ReadinessEvidenceManifest` binds one repository identity and 40-character revision to
  explicitly named required-check, focused-test, regression, coverage, audit-chain,
  supported-surface, limitation, blocker, and collection-time inputs.
- Strict canonical JSON decoding rejects duplicate or unknown fields, malformed identities,
  repeated paths, missing gates, unbounded collections, and contradictory declarations.
- Relative evidence paths resolve only beneath an explicit input root; absolute paths,
  traversal, symlinks, and implicit discovery fail closed.

## Deterministic assembler

- `ReleaseReadinessSnapshotAssembler` receives the manifest, explicit input root, bounded
  document reader, and accepted contract registry through dependency injection.
- It validates every document against its accepted codec and binds all evidence to the same
  repository revision before producing an immutable v1.4.0 snapshot.
- Missing, malformed, stale, conflicting, or revision-mismatched evidence produces stable
  ordered findings and no snapshot.
- Canonical snapshot bytes are independent of host paths, directory order, locale,
  environment variables, clocks, credentials, or process state.

## Bounded offline read-only CLI

- `release-evidence readiness assemble --manifest MANIFEST --input-root ROOT --format json|text`
- Explicit file-count, per-document, and aggregate-byte limits apply before decoding.
- Exit 0 emits one canonical snapshot; exit 2 reports invalid or incomplete input.
- The command reads only manifest-named local files and never writes, discovers, repairs,
  stages, commits, pushes, merges, tags, publishes, or accesses a network.

## Authority boundary

Assembly records evidence; it does not evaluate readiness or authorize release. Evaluation
remains a separate v1.4.0 operation. Version mutation, tag and artifact creation, signing,
GitHub Releases, publication, remote collection, credentials, and repository mutation remain
out of scope.

## Code Review Checklist

- [ ] Manifest parsing is strict, canonical, bounded, and fail closed.
- [ ] Every evidence document is explicit and revision-bound.
- [ ] Path containment rejects absolute paths, traversal, symlinks, and discovery.
- [ ] Accepted codecs validate inputs before assembly.
- [ ] Findings, ordering, and canonical output bytes are deterministic.
- [ ] CLI file-count and byte limits are enforced before decoding.
- [ ] Assembly remains offline, read-only, and dependency-injected.
- [ ] Assembly, readiness evaluation, and release authorization remain separate.
- [ ] Architecture, tests, documents, and governance markers agree.
- [ ] Production implementation remains Not Started until design acceptance.
