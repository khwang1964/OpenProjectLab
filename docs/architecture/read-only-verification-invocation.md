# Read-only Verification Invocation Boundary

> v1.3.5 Design First baseline — Proposed / Pending design review

## Context

v1.3.1 established immutable evidence and validation. v1.3.2 added read-only
repository and GitHub adapters. v1.3.3 added deterministic orchestration, and
v1.3.4 added the internal runtime composition root. The remaining internal-use
gap is one explicit invocation boundary that accepts a complete caller-supplied
request, performs exactly one verification, and returns the accepted report.

## Decision

Introduce one internal `ReadOnlyVerificationInvoker` contract:

- constructed from an accepted `VerificationRuntime`
- accepts exactly one immutable `VerificationRequest`
- invokes the accepted `ReleaseEvidenceVerificationOrchestrator` exactly once
- returns the existing immutable `VerificationReport` unchanged
- owns no mutable state before, during, or after invocation
- never infers, repairs, retries, persists, or publishes evidence

## Invocation lifecycle

One invocation follows a fixed sequence:

1. validate that the request is a complete `VerificationRequest`
2. delegate once to the runtime's accepted orchestrator
3. preserve collection, contradiction, and validation findings
4. return the resulting `VerificationReport`

Requests execute independently. A completed or failed invocation cannot affect a
later invocation, and there is no session, queue, batch, or shared result cache.

## Failure boundary

- Request-type or invocation-contract violations fail before adapter execution.
- Adapter and command failures remain structured collection findings.
- Identity contradictions remain structured contradiction findings.
- Validator failures remain structured validation findings.
- The invoker never converts an exception or failure into success-shaped evidence.
- The invoker adds no retry, polling, fallback, prompt, or exception suppression.

## Authority boundary

The invoker may cause only the read commands already accepted and implemented by
v1.3.4. It receives focused-test evidence from the request; it does not execute
pytest, coverage, or an arbitrary subprocess.

## Deferred

- production implementation
- CLI, public SDK, HTTP, RPC, plugin, or entry-point exposure
- repository, pull-request, SHA, or focused-test evidence inference
- test execution and arbitrary subprocess execution
- retry, polling, batch, queue, cache, persistence, telemetry, or scheduling
- credential prompts, privilege escalation, and interactive recovery
- commit, push, merge, tag, release, publication, or document writes

## Code Review Checklist

- [ ] The invoker accepts only a complete immutable `VerificationRequest`.
- [ ] Each invocation delegates to the accepted orchestrator exactly once.
- [ ] The existing immutable `VerificationReport` is returned unchanged.
- [ ] Collection, contradiction, and validation failures remain distinguishable.
- [ ] No success-shaped fallback is introduced.
- [ ] Invocations share no mutable state, cache, session, queue, or batch.
- [ ] Only the v1.3.4 accepted read-command authority is reachable.
- [ ] No test execution, mutation, CLI, SDK, release, or publication is added.
- [ ] Deterministic fakes cover success, failure, and invocation independence.
- [ ] Architecture, release, governance, and contract tests remain aligned.
