# Bootstrap Dry-run Execution Preview Architecture

> **Status:** Architecture Definition --- In Progress
> **Target:** OpenProjectLab v1.2.3 --- Dry-run Execution Preview
> **Predecessor:** v1.2.2 Bootstrap Planning Core --- Accepted / Implemented
> **Production Implementation:** Not Started

## 1. Purpose

This architecture defines a deterministic inspection layer over the existing
immutable `BootstrapPlan`. It previews future execution order and expected
effects without crossing into generator execution or persistent mutation.

## 2. Architectural Position

``` text
BootstrapPlanner
    ↓
BootstrapPlan (authoritative)
    ↓
BootstrapDryRunExecutor.preview(plan)
    ↓
BootstrapDryRunPreview
    ├── ordered BootstrapDryRunStep values
    └── ordered ExpectedEffect values
```

## 3. Contract Responsibilities

### BootstrapDryRunStep

Immutable projection of one existing `BootstrapStep`. It preserves stable
identity, generator identity, normalized inputs, and ordered expected effects.

### BootstrapDryRunPreview

Immutable aggregate containing the complete ordered preview. It is an
inspection result, not a plan replacement, manifest, checkpoint, or command
buffer.

### BootstrapDryRunExecutor

Pure projection boundary accepting `BootstrapPlan` and returning
`BootstrapDryRunPreview`. It does not own planning, generator resolution,
generator construction, apply, validation, rollback, persistence, or CLI
composition.

## 4. Authoritative Boundaries

- `BootstrapPlanner` remains the owner of plan construction.
- `BootstrapPlan` remains the authoritative dry-run input.
- existing step and expected-effect ordering is preserved.
- existing Generator lifecycle remains authoritative but is not entered.
- no second registry, planner, filesystem, or mutation pipeline is introduced.

## 5. Determinism

Equivalent accepted plans produce equivalent previews. Preview excludes wall
clock time, random identity, environment-dependent ordering, current working
directory state, and incidental filesystem inspection from equivalence.

## 6. Side-effect and Failure Boundary

``` text
Generator Instantiation --- Forbidden
Generator Execution --- Forbidden
Filesystem Mutation --- Forbidden
Manifest / Backup / Checkpoint Writes --- Forbidden
Network Access --- Forbidden
Plugin Activation --- Forbidden
Failure Partial State --- Forbidden
```

Failure returns no success-shaped partial preview and persists nothing.
Rollback is unnecessary because preview commits no state.

## 7. Deferred and Closed Scope

``` text
apply execution --- Not Started
validation runtime --- Not Started
checkpoint / resume --- Deferred
generalized rollback --- Deferred
CLI Boundary --- Not Accepted
Production Implementation --- Not Started
```

## 8. Test Strategy

Executable contracts verify explicit contracts, authoritative plan reuse,
deterministic ordering, equivalent-preview behavior, descriptive-only effects,
side-effect prohibition, zero-partial-state failure, and closed future
surfaces. Production behavior tests belong to a later implementation slice.

## 9. Architectural Invariants

``` text
BootstrapPlan --- Immutable / Authoritative
BootstrapDryRunStep --- Immutable / Inspectable
BootstrapDryRunPreview --- Immutable / Complete
BootstrapDryRunExecutor --- Projection Only
Preview Ordering --- Deterministic
Expected Effects --- Descriptive Data Only
All Persistent Mutation --- Forbidden
Production Implementation --- Not Started
```

## 10. Code Review Checklist

- [ ] authoritative `BootstrapPlan` is reused without mutation or re-planning;
- [ ] preview preserves step and expected-effect order;
- [ ] no generator is instantiated or executed;
- [ ] no filesystem, manifest, backup, or checkpoint write occurs;
- [ ] no network or plugin activation occurs;
- [ ] equivalent plans require equivalent previews;
- [ ] failure creates no partial preview or persisted state;
- [ ] apply, validation, rollback, checkpoint/resume, and CLI remain closed;
- [ ] production implementation remains Not Started.

## 11. Current Architecture State

``` text
v1.2.2 Bootstrap Planning Core --- Accepted / Implemented
v1.2.3 Dry-run Execution Preview --- In Progress
Dry-run Preview Architecture --- Defined
Core Dry-run Contracts --- Proposed
Production Implementation --- Not Started
v1.2.3 Acceptance --- Not Accepted
```
