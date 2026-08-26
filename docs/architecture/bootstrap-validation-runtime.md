# Bootstrap Validation Runtime Architecture

> **Status:** Accepted --- Terminally Closed
> **Target:** OpenProjectLab v1.2.5 --- Bootstrap Validation Runtime
> **Predecessor:** v1.2.4 Bootstrap Apply Execution --- Accepted / Implemented
> **Production Implementation:** Not Started

## 1. Architectural Position

``` text
observable project state / optional apply evidence
    ↓
BootstrapValidationRequest
    ↓
BootstrapValidator → ordered BootstrapValidationCheck values
    ↓ existing read-only filesystem boundary
BootstrapValidationFinding values
    ↓
BootstrapValidationResult
```

## 2. Responsibilities

- request: immutable validation context;
- check: one stable, injected inspection operation;
- finding: immutable invalid/advisory evidence;
- result: ordered aggregate and deterministic validity;
- validator: ordering, orchestration, and fail-closed error boundary only.

## 3. Invariants

``` text
Validation --- Inspection Only
Filesystem Reads --- Existing Boundary Reused
Filesystem Mutation / Silent Repair --- Forbidden
Apply / Re-apply --- Forbidden
Check Ordering / Finding Ordering --- Deterministic
Invalid State --- Finding
Check Failure --- Fail Closed
Automatic Rollback --- Not Performed
```

## 4. Failure Evidence

Check infrastructure failure stops later checks and exposes failed check
identity plus completed evidence. It never returns a success-shaped partial
result. Ordinary invalid state remains a deterministic finding.

## 5. Closed Scope

``` text
repair / checkpoint-resume / rollback / parallel validation --- Deferred
Implicit Network Access / Plugin Activation --- Forbidden
CLI Boundary / Stable Report Format --- Not Accepted
Public SDK Expansion --- Forbidden
Production Implementation --- Not Started
```

## 6. Code Review Checklist

- [ ] all validation data contracts are immutable;
- [ ] existing read-only filesystem behavior is reused;
- [ ] validation cannot write or repair;
- [ ] ordering and validity are deterministic;
- [ ] invalid state and check failure remain distinct;
- [ ] later checks stop after infrastructure failure;
- [ ] apply and rollback are never invoked;
- [ ] deferred and public surfaces remain closed.

## 7. Current Architecture State

``` text
v1.2.5 Bootstrap Validation Runtime --- Accepted
Validation Architecture --- Defined
Core Validation Contracts --- Accepted
Production Implementation --- Not Started
v1.2.5 Acceptance --- Accepted
```


------------------------------------------------------------------------

## Design Acceptance Status

``` text
Design PR #238 --- Merged
Design merge --- eadc9b96a0a7f4231331da162ee9c586cd9613e6
Post-merge focused verification --- 9 passed
Validation Architecture / Core Contracts --- Accepted
Production Implementation --- Not Started
Next --- v1.2.5 Bootstrap Validation Runtime minimum implementation slice
```


<!-- v1.2.5-bootstrap-validation-runtime-terminal-architecture -->

## Minimum Implementation Status

``` text
Validation Architecture --- Accepted / Implemented
Implementation PR #240 --- Merged
Implementation merge --- 902256c2dbb7ec384abe31decdeeb555240a85ce
Post-merge focused verification --- 20 passed
BootstrapValidator --- Deterministic / Fail Closed
Validation Checks --- Injected / Inspection Only
Invalid State --- Finding
Check Failure --- BootstrapValidationError
Repair / Rollback / Parallel Validation --- Deferred
CLI Boundary --- Not Accepted
```
