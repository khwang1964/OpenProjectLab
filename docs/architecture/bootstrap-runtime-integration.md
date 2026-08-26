# Bootstrap Runtime Integration Architecture

> **Status:** Design / Contract Definition --- In Progress
> **Target:** OpenProjectLab v1.2.6 --- Bootstrap Runtime Integration
> **Production Implementation:** Not Started

``` text
BootstrapRuntimeRequest + Explicit Mode
    ↓
BootstrapRuntimeCoordinator
    ↓ exactly once
BootstrapPlanner → Authoritative BootstrapPlan
    ├─ BootstrapDryRunExecutor
    ├─ BootstrapApplyExecutor
    └─ BootstrapValidator
    ↓
BootstrapRuntimeResult
```

## Invariants

``` text
Planning --- Exactly Once
BootstrapPlan --- Authoritative / Reused
Phase Ordering --- Deterministic / Sequential
Preview Mutation --- Forbidden
Apply Mutation --- Explicit Mode Only
Validation --- Inspection Only
Success-shaped Partial Result --- Forbidden
```

The first phase failure stops later phases. Existing typed errors remain visible;
the coordinator neither repairs state nor manufactures partial success.

``` text
Automatic Repair / Rollback --- Forbidden
Checkpoint / Resume / Parallel Execution --- Deferred
Implicit Network Access / Plugin Activation --- Forbidden
CLI Boundary / Stable Serialization --- Not Accepted
Public SDK Expansion --- Forbidden
Production Implementation --- Not Started
v1.2.6 Acceptance --- Not Accepted
```
