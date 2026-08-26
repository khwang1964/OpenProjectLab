# Bootstrap Apply Execution Architecture

> **Status:** Accepted --- Terminally Closed
> **Target:** OpenProjectLab v1.2.4 --- Bootstrap Apply Execution
> **Predecessor:** v1.2.3 Dry-run Execution Preview --- Accepted / Implemented
> **Production Implementation:** Not Started

## 1. Purpose

This architecture defines the explicit committed-mutation coordination layer
over an authoritative `BootstrapPlan` while preserving existing Generator and
filesystem boundaries.

## 2. Architectural Position

``` text
BootstrapPlan
    ↓
BootstrapApplyExecutor
    ↓ sequentially
Bootstrap step execution adapter
    ↓
GeneratorRegistry → BaseGenerator.run(GenerateRequest)
    ↓
existing filesystem abstraction
    ↓
BootstrapApplyStepResult → BootstrapApplyResult
```

## 3. Responsibilities

- `BootstrapApplyStepResult`: immutable evidence for one completed step.
- `BootstrapApplyResult`: ordered immutable evidence for complete success.
- `BootstrapApplyExecutor`: sequencing and fail-fast coordination only.
- internal step adapter: maps accepted Bootstrap data into the existing
  Generator lifecycle without becoming a public SDK surface.

## 4. Authoritative Boundaries

``` text
BootstrapPlan --- Immutable / Authoritative
Generator Lifecycle --- Reused
Filesystem Abstraction --- Reused
ExpectedEffect --- Descriptive Data Only
ExpectedEffect Direct Execution --- Forbidden
Parallel Mutation Pipeline --- Forbidden
```

The executor never renders templates or writes files directly.

## 5. Execution and Result Semantics

Steps execute sequentially in plan order. Each step delegates through the
existing Generator lifecycle. A complete immutable result is returned only
when all steps succeed. Empty plans return an empty success result.

## 6. Failure Boundary

Apply stops on the first non-recoverable failure. Failure evidence identifies
completed steps, the failed step, and the originating cause. Later steps do
not run. Earlier committed mutations are neither hidden nor automatically
rolled back.

``` text
Fail-fast --- Required
Automatic Rollback --- Not Guaranteed
Transaction-wide Atomicity --- Not Claimed
```

## 7. Closed Scope

``` text
validation runtime --- Not Started
checkpoint / resume --- Deferred
generalized rollback --- Deferred
parallel apply --- Deferred
Implicit Network Access --- Forbidden
Implicit Plugin Activation --- Forbidden
CLI Boundary --- Not Accepted
Public SDK Expansion --- Forbidden
Production Implementation --- Not Started
```

## 8. Test Strategy

Executable contracts verify explicit contracts, authoritative plan reuse,
sequential ordering, Generator/filesystem reuse, descriptive-only expected
effects, fail-fast partial-state evidence, later-step suppression, and closed
future surfaces.

## 9. Code Review Checklist

- [ ] BootstrapPlan stays authoritative and immutable.
- [ ] BaseGenerator.run() remains the execution lifecycle.
- [ ] existing filesystem abstraction owns committed writes.
- [ ] BootstrapApplyExecutor performs coordination only.
- [ ] ExpectedEffect values are never executed directly.
- [ ] step order and result order are deterministic.
- [ ] failure stops later-step execution.
- [ ] partial state is explicit and rollback is not implied.
- [ ] network, plugin, validation, parallelism, CLI, and SDK stay closed.
- [ ] production implementation remains Not Started.

## 10. Current Architecture State

``` text
v1.2.4 Bootstrap Apply Execution --- Accepted
Apply Architecture --- Defined
Core Apply Contracts --- Accepted
Existing Generator / Filesystem Boundaries --- Required
Fail-fast Partial-state Evidence --- Required
Production Implementation --- Not Started
v1.2.4 Acceptance --- Accepted
```


------------------------------------------------------------------------

## Design Acceptance Status

``` text
Design PR #234 --- Merged
Design merge --- 1e0f7ebba9b98dd1c6bfa5edad52efa1bae7f0b6
Post-merge focused verification --- 9 passed
Apply Architecture --- Accepted
Core Apply Contracts --- Accepted
Production Implementation --- Not Started
Next --- v1.2.4 Bootstrap Apply Execution minimum implementation slice
```


------------------------------------------------------------------------

<!-- v1.2.4-bootstrap-apply-execution-terminal-architecture -->

## Minimum Implementation Status

``` text
Apply Architecture --- Accepted / Implemented
Implementation PR #236 --- Merged
Implementation merge --- 1fbf799bd6bc687592a46788fc98f2dda1b79907
Post-merge focused verification --- 30 passed
BootstrapPlan --- Authoritative
Generator Lifecycle / Filesystem Abstraction --- Reused
BootstrapApplyExecutor --- Sequential / Fail-fast Coordination
ExpectedEffect Direct Execution --- Absent
Automatic Rollback / Transaction-wide Atomicity --- Not Claimed
validation runtime --- Not Started
CLI Boundary --- Not Accepted
```
