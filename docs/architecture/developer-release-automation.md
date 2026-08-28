# Developer / Release Automation Architecture

## Context

OPL release acceptance spans repository state, pull-request state, CI evidence,
test results, coverage, post-merge verification, and four lifecycle documents.
Manual transcription can allow those identities to drift.

## Proposed components

1. **Evidence collector** reads injected Git, GitHub, CI, pytest, and coverage
   observations without changing repository or remote state.
2. **Evidence normalizer** creates a deterministic ordered snapshot and rejects
   missing or contradictory identities.
3. **Lifecycle validator** checks permitted Pending and Accepted / Completed
   transitions, including the two-PR acceptance boundary.
4. **Document consistency checker** compares the acceptance record, roadmap,
   HISTORY, and CHANGELOG without silently repairing them.
5. **Report renderer** emits stable maintainer-readable diagnostics and a
   machine-testable result.

## Dependency direction

Repository and GitHub adapters provide observations to the core validation
model. The core must not invoke merge, tag, release, publication, force-push,
reset, or branch-deletion operations.

## Failure semantics

Unknown state is not success. Collection failures, absent checks, SHA mismatch,
dirty-tree ambiguity, stale test evidence, and lifecycle disagreement produce a
typed failed result and no document mutation.

## Compatibility

Existing CLI, Bootstrap runtime, serialization formats, public SDK, release
artifacts, and acceptance records remain unchanged by the design slice.
