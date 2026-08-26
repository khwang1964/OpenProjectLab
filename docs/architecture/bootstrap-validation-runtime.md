# Bootstrap Validation Runtime Architecture

> **Status:** Architecture Definition --- In Progress
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
v1.2.5 Bootstrap Validation Runtime --- In Progress
Validation Architecture --- Defined
Core Validation Contracts --- Proposed
Production Implementation --- Not Started
v1.2.5 Acceptance --- Not Accepted
```
