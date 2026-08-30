# Read-only Verification Runtime Wiring

> v1.3.4 Design First baseline — Accepted / Terminally Closed

## Context

v1.3.1 established immutable evidence and fail-closed validation. v1.3.2 added
deterministic read-only repository and GitHub adapters. v1.3.3 composed those
contracts into one verification orchestrator. The remaining runtime gap is a
minimum composition root that wires those accepted components without granting
mutation, test-execution, CLI, SDK, or release authority.

## Decision

Introduce an internal read-only runtime wiring boundary with:

- immutable explicit runtime configuration
- one deterministic command executor implementing the existing `ReadCommand`
- an exact allowlist for adapter-issued Git and GitHub read commands
- explicit repository working directory
- deterministic command result and failure mapping
- one factory that constructs the repository adapter, GitHub adapter, validator,
  and verification orchestrator

## Runtime configuration

Configuration carries only explicit runtime policy:

- repository working directory
- executable identities for `git` and `gh`, defaulting to their canonical names
- command timeout as a positive finite value
- optional explicit environment mapping, copied immutably when supplied

Configuration does not discover repositories, credentials, expected release
identities, pull-request numbers, or focused-test results.

## Command policy

The executor accepts only the exact read commands already required by the accepted
adapters:

- `git config --get remote.origin.url`
- `git branch --show-current`
- `git rev-parse HEAD`
- `git rev-parse origin/main`
- `git status --porcelain`
- `gh pr view <positive-number> --json <accepted-fields>`

Unknown executables, extra options, shell strings, mutation verbs, redirects, and
compound commands fail closed before process execution. Commands are passed as an
argument vector with `shell=False` semantics.

## Failure boundary

- Process exit status and captured standard output become the existing
  `CommandResult` contract.
- Timeout, missing executable, invalid working directory, and OS execution failure
  become stable runtime errors; they never become success-shaped evidence.
- Standard error may support diagnostics but must not be interpreted as evidence.
- No automatic retry, polling, fallback executable, or credential prompt is allowed.

## Factory boundary

The factory creates only internal accepted components:

1. read-only command executor
2. `RepositoryEvidenceAdapter`
3. `GitHubEvidenceAdapter`
4. `ReleaseEvidenceValidator`
5. `ReleaseEvidenceVerificationOrchestrator`

It does not run verification, infer a request, execute tests, or mutate state.

## Deferred

- production implementation
- CLI and public SDK exposure
- pytest, coverage, or arbitrary subprocess execution
- commit, push, merge, tag, release, publication, or document writes
- retry, polling, caching, persistence, telemetry, and credential management
- shell invocation, user prompts, and platform-specific fallback discovery

## Code Review Checklist

- [ ] Runtime configuration is explicit, immutable, and validated.
- [ ] Only the accepted Git and GitHub read commands are executable.
- [ ] Commands use argument vectors and never a shell command string.
- [ ] Working directory and timeout are explicit.
- [ ] Runtime failures remain stable and fail closed.
- [ ] Existing adapters, validator, and orchestrator are reused unchanged.
- [ ] The factory constructs components but performs no verification.
- [ ] No test execution, mutation, CLI, SDK, release, or publication is added.
- [ ] Deterministic fakes cover policy, wiring, and failure boundaries.
- [ ] Architecture, release, governance, and contract tests remain aligned.
