# Release Evidence Verification Orchestration

> v1.3.3 Design First baseline — Accepted / Terminally Closed

## Context

v1.3.1 established immutable release-evidence models and fail-closed validation.
v1.3.2 added deterministic, read-only repository and GitHub evidence adapters.
The remaining architectural gap is a single application-layer workflow that composes
those existing boundaries without acquiring mutation authority.

## Decision

Introduce a deterministic verification orchestrator that accepts an explicit request,
collects repository and pull-request observations through injected read-only adapters,
composes canonical `ReleaseEvidence`, invokes the existing validator, and returns one
immutable report.

``` text
Explicit verification request
        ↓
Repository observation + GitHub PR observation
        ↓
Identity and lifecycle consistency composition
        ↓
Existing ReleaseEvidenceValidator
        ↓
Immutable verification report
```

## Proposed contracts

### Verification request

The request carries only explicit policy inputs:

- explicit expected repository
- explicit expected branch
- explicit expected candidate SHA
- pull-request number
- caller-supplied focused-test evidence

The orchestrator must not discover expected policy from mutable ambient state.

### Verification report

The immutable report contains:

- repository observation
- pull-request observation
- composed release evidence when composition succeeds
- stable ordered findings
- a derived `is_valid` result

The report must distinguish collection failure, observation contradiction, and
validation failure without raising a success-shaped result.

## Consistency rules

- Repository identity must match the explicit expected repository.
- The observed branch must match the explicit expected branch.
- `HEAD` and `origin/main` identity must agree when verification targets synchronized
  `main`.
- A merged pull request must expose a full merge SHA and merge timestamp.
- Pull-request base branch must match the expected branch.
- The applicable candidate SHA must agree with the expected lifecycle state.
- Missing, pending, failed, malformed, unknown, or contradictory CI evidence fails
  closed.
- Missing or failed focused-test evidence fails closed.
- Findings remain deterministic and stably ordered.

## Error boundary

Adapter collection errors become structured orchestration findings. Unexpected
programming errors are not silently converted to valid reports. Partial observations
must never be presented as completed verification evidence.

## Dependency and side-effect boundary

- Repository and GitHub adapters are injected.
- The existing validator is reused rather than duplicated.
- Focused-test evidence is supplied by the caller; the orchestrator does not run
  pytest, subprocess test commands, or coverage.
- No filesystem write, Git mutation, GitHub mutation, merge, tag, release,
  publication, credential handling, retry loop, CLI, or public SDK is authorized.

## Determinism and testing

Contract tests use deterministic fake observations and injected adapters. They verify
stable call ordering, exact composition, immutable reports, identity contradictions,
collection failure, pending/failed CI, and absent/failed focused tests without network
or process execution.

## Deferred

- production implementation
- CLI and public SDK exposure
- executing tests or collecting coverage
- merge/tag/release/publication automation
- retries, polling, caching, persistence, and credentials
- branch cleanup or repository/document mutation

## Code Review Checklist

- [ ] Request policy inputs are explicit and immutable.
- [ ] Existing v1.3.1 models and validator are reused.
- [ ] Existing v1.3.2 read-only adapters remain mutation-free.
- [ ] Repository, branch, SHA, PR, merge, and CI identities fail closed.
- [ ] Collection, contradiction, and validation failures remain distinguishable.
- [ ] Finding order is deterministic.
- [ ] Focused-test evidence remains caller supplied.
- [ ] No test execution, CLI, SDK, mutation, publication, or credentials are added.
- [ ] Unit and release-readiness contracts cover every accepted boundary.
- [ ] Documentation surfaces remain aligned with the same Pending state.
