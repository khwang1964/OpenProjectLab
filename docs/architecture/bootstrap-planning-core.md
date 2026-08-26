# Bootstrap Planning Core Architecture

> **Status:** Architecture Definition — In Progress
> **Target:** OpenProjectLab v1.2.2 — Bootstrap Planning Core
> **Predecessor:** v1.2.1 Bootstrap Framework Design Baseline — Accepted
> **Implementation:** Not Started

## 1. Purpose

The Bootstrap Planning Core is the first implementation-oriented architecture
slice under the accepted Bootstrap Framework design.

Its purpose is to construct a deterministic, inspectable `BootstrapPlan`
without performing execution, mutation, network access, or plugin activation.

## 2. Architectural Position

``` text
Bootstrap intent
      ↓
BootstrapPlanner
      ↓
normalize inputs
      ↓
GeneratorRegistry resolution
      ↓
ordered BootstrapStep values
      ↓
expected-effect data
      ↓
BootstrapPlan
```

The planning core remains above the existing Generator lifecycle and does not
enter generator execution.

## 3. Core Contracts

### BootstrapStep

Descriptive planning step containing:

- stable step identity;
- generator/service identity;
- normalized planning inputs;
- deterministic ordering information;
- expected outputs/effects;
- later apply-phase mutation intent, if relevant.

At v1.2.2 a BootstrapStep is data only.

### BootstrapPlan

Deterministic, inspectable planning result containing:

- normalized bootstrap intent;
- ordered BootstrapStep entries;
- ordered expected effects;
- reproducibility/traceability information;
- an equivalence basis suitable for executable tests.

### BootstrapPlanner

Planning service responsible for:

- normalizing supported bootstrap intent;
- resolving accepted generator identities;
- constructing deterministic steps;
- computing expected effects as data;
- returning BootstrapPlan.

BootstrapPlanner must not execute generators.

## 4. GeneratorRegistry Boundary

The existing GeneratorRegistry remains authoritative.

The planning core may resolve and validate generator identities through it, but
must not:

- create another registry;
- activate plugins;
- instantiate generators for execution;
- mutate global generator configuration.

## 5. Generator Lifecycle Boundary

The existing Generator lifecycle remains authoritative.

v1.2.2 must not call execution/mutation phases while planning. Metadata or
contract information may be inspected only where required to describe future
steps.

``` text
Generator Execution — Forbidden
```

## 6. Filesystem Boundary

The planning core may describe filesystem effects but must not commit them.

``` text
Filesystem Mutation — Forbidden
```

Forbidden behavior includes file/directory create, update, delete, backup,
manifest write, checkpoint write, or filesystem commit.

## 7. Determinism

Equivalent supported inputs and equivalent relevant repository state should
produce equivalent plans.

Required deterministic properties:

- stable step ordering;
- stable normalized input representation;
- stable generator identity resolution;
- stable expected-effect ordering;
- repeatable plan equivalence.

A cryptographic plan hash is not required in v1.2.2.

## 8. Expected Effects

Expected effects are descriptive data representing possible later apply-phase
intent, for example:

- create file;
- update file;
- create directory;
- generate artifact.

They are not executable commands and must remain separated from mutation.

## 9. Side-effect Boundary

``` text
Filesystem Mutation — Forbidden
Generator Execution — Forbidden
Network Access — Forbidden
Plugin Activation — Forbidden
```

Planning must remain safe to repeat.

## 10. Deferred / Closed Scope

``` text
dry-run execution — Not Started
apply execution — Not Started
validation runtime — Not Started
checkpoint / resume — Deferred
generalized rollback — Deferred
CLI Boundary — Not Accepted
```

Any expansion requires a later Design First contract.

## 11. Test Strategy

Executable contracts should verify:

1. core planning contracts are explicit;
2. planning is mutation-free;
3. generators are not executed;
4. GeneratorRegistry is reused;
5. generator lifecycle remains authoritative;
6. ordering is deterministic;
7. equivalent plans are reproducible;
8. expected effects remain data;
9. no network access occurs;
10. no plugin activation occurs;
11. dry-run/apply remain unimplemented;
12. CLI remains unaccepted.

## 12. Architectural Invariants

``` text
BootstrapStep — Descriptive Only
BootstrapPlan — Deterministic / Inspectable
BootstrapPlanner — Planning Only
GeneratorRegistry — Reused
Generator Lifecycle — Preserved
Filesystem Mutation — Forbidden
Generator Execution — Forbidden
Network Access — Forbidden
Plugin Activation — Forbidden
Expected Effects — Data Only
dry-run — Not Started
apply — Not Started
checkpoint / resume — Deferred
CLI Boundary — Not Accepted
v1.2 Implementation — Not Started
```

## 13. Code Review Checklist

- [ ] BootstrapStep remains descriptive only.
- [ ] BootstrapPlan remains deterministic and inspectable.
- [ ] BootstrapPlanner never executes generators.
- [ ] existing GeneratorRegistry is reused.
- [ ] existing Generator lifecycle remains authoritative.
- [ ] planning performs no filesystem mutation.
- [ ] planning performs no network access.
- [ ] planning performs no plugin activation.
- [ ] expected effects remain data only.
- [ ] deterministic ordering is explicit.
- [ ] equivalent-plan behavior is testable.
- [ ] dry-run/apply remain Not Started.
- [ ] checkpoint/resume remains Deferred.
- [ ] Stable CLI syntax remains Not Accepted.
- [ ] implementation remains Not Started.

## 14. Current Architecture State

``` text
v1.2.1 Bootstrap Framework Design Baseline — Accepted
v1.2.2 Bootstrap Planning Core — In Progress
Planning-core architecture — Defined
BootstrapStep / BootstrapPlan / BootstrapPlanner — Proposed
GeneratorRegistry reuse — Required
Generator lifecycle preservation — Required
Filesystem Mutation — Forbidden
Generator Execution — Forbidden
Network Access — Forbidden
Plugin Activation — Forbidden
dry-run execution — Not Started
apply execution — Not Started
checkpoint / resume — Deferred
CLI Boundary — Not Accepted
v1.2.2 Bootstrap Planning Core — Not Accepted
v1.2 Implementation — Not Started
```

------------------------------------------------------------------------

<!-- v1.2.2-bootstrap-planning-core-acceptance-architecture -->

## Design Acceptance Status

``` text
v1.2.2 Bootstrap Planning Core --- Accepted
Design PR #226 --- Merged
Design merge --- c76c1b931da7d0aaf13792546b451c46f4769fe0
Post-merge consistency verification --- Passed
Focused post-merge verification --- Passed
BootstrapStep / BootstrapPlan / BootstrapPlanner --- Accepted
GeneratorRegistry reuse --- Accepted
Generator lifecycle preservation --- Accepted
Deterministic ordering --- Accepted
Equivalent-plan behavior --- Accepted
Filesystem Mutation --- Forbidden
Generator Execution --- Forbidden
Network Access --- Forbidden
Plugin Activation --- Forbidden
dry-run execution --- Not Started
apply execution --- Not Started
checkpoint / resume --- Deferred
CLI Boundary --- Not Accepted
v1.2 Implementation --- Not Started
```

------------------------------------------------------------------------

<!-- v1.2.2.1-bootstrap-planning-core-terminal-architecture -->

## v1.2.2.1 Planning Core Implementation Status

``` text
BootstrapStep implementation --- Completed
BootstrapPlan implementation --- Completed
BootstrapPlanner implementation --- Completed
ExpectedEffect implementation --- Completed
Deterministic ordering implementation --- Completed
Equivalent-plan behavior --- Completed
GeneratorRegistry reuse --- Completed
Mutation-free planning --- Verified
Implementation PR #228 --- Merged
Implementation merge --- 528f356a3160af5445a9e4b4193ee5e62029653e
Post-merge consistency verification --- Passed
dry-run --- Not Started
apply --- Not Started
validation runtime --- Not Started
CLI Boundary --- Not Accepted
```

The implementation remains planning-only. It does not authorize dry-run,
apply, validation runtime, or Stable CLI behavior.
