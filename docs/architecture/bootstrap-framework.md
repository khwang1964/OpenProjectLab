# Bootstrap Framework Architecture

> **Status:** Architecture Definition --- In Progress\
> **Target:** OpenProjectLab v1.2.1 --- Bootstrap Framework Design
> Baseline\
> **Predecessor:** v1.2 Planning Baseline --- Accepted\
> **Implementation:** Not Started

## 1. Purpose

The Bootstrap Framework defines a deterministic orchestration layer for
creating and validating OpenProjectLab project structures through
existing generator and filesystem contracts.

Its purpose is to coordinate multiple bootstrap operations without
introducing a second generator lifecycle, a parallel filesystem mutation
pipeline, or hidden execution behavior.

The framework follows the OpenProjectLab design principles:

-   **Design First** --- architecture and public contracts are accepted
    before implementation.
-   **Documentation First** --- lifecycle, compatibility, failure, and
    operational semantics are documented before code.
-   **Automation First** --- behavior must be executable, deterministic,
    testable, and suitable for CI verification.

The v1.2.1 architecture establishes the boundaries required for later
implementation. It does **not** authorize implementation by itself.

## 2. Architectural Principles

The Bootstrap Framework SHALL:

1.  compose existing OpenProjectLab generators rather than duplicate
    them;
2.  reuse the existing filesystem abstraction for all mutations;
3.  separate planning, preview, execution, and validation;
4.  make filesystem effects inspectable before execution;
5.  preserve deterministic offline behavior;
6.  expose explicit failure evidence;
7.  avoid implicit network access and implicit plugin activation;
8.  remain backward compatible with Stable v1.x behavior unless a
    separately accepted compatibility decision states otherwise.

The Bootstrap Framework SHALL NOT become a second application framework
inside OpenProjectLab.

## 3. Existing Boundaries Reused

### 3.1 Generator lifecycle

Bootstrap orchestration sits above the existing generator lifecycle.

``` text
Bootstrap request
      |
      v
Bootstrap planner
      |
      v
BootstrapPlan
      |
      +------------------+
      |                  |
      v                  v
   dry-run             apply
                         |
                         v
                existing generators
                         |
                         v
                filesystem abstraction
                         |
                         v
                    project state
                         |
                         v
                     validate
```

A bootstrap step may sequence or configure an existing generator, but it
must not reproduce generator business logic or bypass generator
lifecycle hooks.

### 3.2 Filesystem abstraction

All committed filesystem mutation must flow through the existing
OpenProjectLab filesystem boundary.

The Bootstrap Framework must not:

-   introduce a second transactional mutation engine;
-   perform direct writes that bypass the existing abstraction;
-   mutate files while computing a plan;
-   hide mutation inside validation or inspection operations.

This preserves one authoritative mutation path.

### 3.3 Registry and plugin boundaries

Bootstrap orchestration may consume services already made available
through accepted OpenProjectLab boundaries.

It must not:

-   create an alternative generator registry;
-   implicitly discover or activate plugins;
-   globally mutate plugin or generator configuration;
-   make network access a hidden consequence of planning.

Any future plugin-aware bootstrap behavior requires an explicit design
contract.

## 4. Core Contracts

### 4.1 BootstrapPlan

`BootstrapPlan` is the deterministic, inspectable representation of
intended bootstrap work before committed mutation occurs.

A plan should identify:

-   normalized bootstrap intent;
-   ordered `BootstrapStep` instances;
-   expected filesystem effects;
-   required validation operations;
-   reproducibility or traceability metadata.

Equivalent supported inputs and equivalent relevant repository state
should produce equivalent plans.

A plan must contain enough information for dry-run diagnostics and
executable contract tests without requiring mutation.

### 4.2 BootstrapStep

`BootstrapStep` represents one logical orchestration operation.

Each step should declare:

-   its stable identity;
-   normalized inputs;
-   the existing generator or service boundary it uses;
-   expected outputs or filesystem effects;
-   whether mutation is permitted during apply;
-   validation expectations;
-   failure propagation behavior.

A step must not bypass the existing generator lifecycle.

### 4.3 BootstrapResult

`BootstrapResult` represents observable execution evidence.

It should report:

-   plan identity or equivalent traceability information;
-   completed steps;
-   skipped steps;
-   the failed step, when applicable;
-   filesystem-effect or generated-artifact summary;
-   validation outcome.

The result is evidence of execution, not a hidden repair mechanism.

## 5. Execution Model

### 5.1 plan

`plan` is a pure planning operation.

Required semantics:

-   no filesystem mutation;
-   no generator apply/execution;
-   no implicit network access;
-   deterministic output for equivalent supported inputs and state;
-   returns an inspectable `BootstrapPlan`.

Planning failure produces no committed mutation.

### 5.2 dry-run

`dry-run` previews execution of a `BootstrapPlan`.

Required semantics:

-   no committed filesystem mutation;
-   reports expected filesystem effects;
-   may reuse existing dry-run-capable generator behavior;
-   produces deterministic evidence suitable for tests and diagnostics;
-   never silently falls back to apply.

Dry-run failure produces no committed mutation.

### 5.3 apply

`apply` is the explicit mutation phase.

Required semantics:

-   consumes or derives a valid `BootstrapPlan`;
-   executes steps in defined order;
-   delegates generator behavior to existing generator contracts;
-   delegates committed writes to the existing filesystem abstraction;
-   records observable execution results;
-   stops according to the defined failure model;
-   performs no undeclared network behavior.

Only `apply` may authorize the Bootstrap Framework's committed
project-state mutation.

## 6. Failure Model

Failure behavior is explicit and fail closed.

Baseline semantics are:

-   planning failure produces no mutation;
-   dry-run failure produces no committed mutation;
-   apply stops at the first non-recoverable step failure;
-   the result identifies completed work and the failed step;
-   successful earlier mutations are not assumed to be automatically
    reversible.

Generalized transactional rollback is outside the v1.2.1 scope.

The framework must not claim atomicity unless a later accepted
architecture defines and tests that guarantee.

## 7. Validation Model

Validation inspects observable project state after apply or when
explicitly requested.

Validation must:

-   inspect rather than silently repair project state;
-   produce explicit success or failure evidence;
-   avoid hidden filesystem mutation;
-   remain deterministic and offline-capable where the underlying
    contracts are offline-capable.

**Validation failure does not imply automatic rollback.**

A future repair workflow, if required, must be designed as an explicit
operation rather than embedded in validation.

## 8. Compatibility Guarantees

The v1.2.1 architecture preserves Stable v1.x boundaries.

Unless separately approved, Bootstrap Framework work must preserve:

-   existing generator public contracts;
-   existing bootstrap entry points;
-   existing filesystem abstraction;
-   deterministic local behavior;
-   existing plugin activation boundaries.

No Stable CLI syntax is accepted by this architecture document.

Illustrative concepts such as:

``` text
opl bootstrap plan
opl bootstrap --dry-run
opl bootstrap apply
```

are architectural examples only and are not accepted public CLI
contracts.

## 9. Deferred Scope

The following capabilities are explicitly deferred:

### 9.1 Checkpoint / resume

``` text
Checkpoint / Resume — Deferred
```

Checkpoint/resume may be proposed later only after its identity,
compatibility, partial-state, and deterministic-resume semantics are
designed and tested.

### 9.2 Generalized rollback

``` text
Generalized Rollback — Deferred
```

The initial architecture does not promise transaction-wide rollback.

### 9.3 Stable CLI surface

``` text
CLI Boundary — Not Accepted
```

A Stable CLI surface requires a separate public-contract slice.

### 9.4 Other non-goals

The v1.2.1 architecture does not approve:

-   a second filesystem mutation pipeline;
-   a second generator lifecycle;
-   remote bootstrap orchestration;
-   silent network access;
-   automatic plugin activation;
-   AI-driven arbitrary repository mutation;
-   generalized dependency resolution.

## 10. Testing Strategy

Architecture tests should encode the design contract before
implementation.

Required coverage includes:

1.  `BootstrapPlan`, `BootstrapStep`, and `BootstrapResult` are
    explicitly defined.
2.  `plan` is mutation-free.
3.  `dry-run` is mutation-free.
4.  `apply` is the only explicit committed-mutation phase.
5.  bootstrap composition reuses the existing generator lifecycle.
6.  committed writes reuse the existing filesystem abstraction.
7.  step ordering and planning behavior are deterministic.
8.  planning and dry-run failures leave no committed mutation.
9.  apply failure stops according to documented semantics.
10. validation performs inspection without hidden repair.
11. validation failure does not imply rollback.
12. checkpoint/resume remains deferred.
13. Stable CLI syntax remains unaccepted.
14. implementation remains blocked until design acceptance.

Implementation tests added in later slices should extend these contracts
rather than weaken or replace them.

## 11. Architectural Invariants

The following invariants are intended to remain machine-verifiable:

``` text
Generator Lifecycle — Reused
Filesystem Abstraction — Reused
Parallel Mutation Pipeline — Forbidden
plan — Mutation Free
dry-run — Mutation Free
apply — Explicit Mutation
Validation — Inspection Only
Automatic Rollback — Not Guaranteed
Checkpoint / Resume — Deferred
CLI Boundary — Not Accepted
v1.2 Implementation — Not Started
```

A future design that changes an invariant must explicitly document the
compatibility impact and update the governing tests.

## 12. Code Review Checklist

### Architecture

-   [ ] `BootstrapPlan` is deterministic and inspectable.
-   [ ] `BootstrapStep` reuses existing generator/service boundaries.
-   [ ] `BootstrapResult` exposes observable execution evidence.
-   [ ] Existing generator lifecycle remains authoritative.
-   [ ] Existing filesystem abstraction remains authoritative.
-   [ ] No parallel filesystem mutation pipeline is introduced.
-   [ ] No alternative generator registry is introduced.

### Execution

-   [ ] `plan` performs no filesystem mutation.
-   [ ] `dry-run` performs no committed filesystem mutation.
-   [ ] `apply` is the explicit mutation phase.
-   [ ] Step ordering is deterministic.
-   [ ] No implicit network behavior is introduced.
-   [ ] No implicit plugin activation is introduced.

### Failure and validation

-   [ ] Planning and dry-run failures are mutation-free.
-   [ ] Apply failure semantics are explicit.
-   [ ] Generalized rollback is not implied.
-   [ ] Validation is inspection-only.
-   [ ] Validation failure does not imply automatic rollback.

### Compatibility and scope

-   [ ] Stable v1.x contracts remain compatible.
-   [ ] Checkpoint/resume remains deferred.
-   [ ] Stable CLI syntax remains unaccepted.
-   [ ] Deferred capabilities are not accidentally implemented.
-   [ ] v1.2 implementation remains `Not Started`.

### Documentation and automation

-   [ ] Governing release design and architecture document agree.
-   [ ] Executable design tests encode the architecture boundaries.
-   [ ] Roadmap, HISTORY, and CHANGELOG are aligned without rewriting
    historical evidence.
-   [ ] Full regression and coverage gates pass before design
    acceptance.
-   [ ] Post-merge consistency verification is required before terminal
    acceptance.

## 13. Current Architecture State

``` text
v1.2 Planning Baseline — Accepted
Bootstrap Framework maturity — Priority 1
v1.2.1 Bootstrap Framework Design Baseline — In Progress
Architecture Contract — Defined
BootstrapPlan / BootstrapStep / BootstrapResult — Proposed
plan / dry-run / apply semantics — Defined
Filesystem Boundary — Defined
Generator Composition Boundary — Defined
Failure Semantics — Defined
Validation Semantics — Defined
Checkpoint / Resume — Deferred
CLI Boundary — Not Accepted
v1.2.1 Bootstrap Framework Design Baseline — Not Accepted
v1.2 Implementation — Not Started
Next — Focused design verification / lifecycle alignment
```
