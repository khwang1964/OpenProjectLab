# Bootstrap CLI Public Contract Architecture

> **Status:** Proposed --- v1.2.8 Design First

## Boundary

The CLI adapter owns parsing, normalization, lifecycle invocation, output
rendering, and exit-status mapping. It does not own planning, apply execution,
validation checks, filesystem repair, or rollback.

``` text
argv
  -> side-effect-free parser
  -> immutable normalized request
  -> existing Bootstrap runtime lifecycle
  -> terminal result / failure evidence
  -> deterministic renderer and exit mapper
```

## Contract ownership

``` text
Parser --- syntax and option compatibility
CLI adapter --- normalization and lifecycle invocation
Runtime integration --- phase ordering and terminal evidence
Planner / executor / validator --- existing domain semantics
Renderer --- deterministic stdout / stderr projection
Exit mapper --- one terminal process status
```

## Failure preservation

Parser failures never invoke the runtime. Runtime and validation failures retain
their phase identity and failed-check identity. Completed evidence is preserved,
but success-shaped partial results are forbidden. Diagnostics must not expose
secrets or raw internal exception details.

## Deferred architecture

Stable SDK entrypoints, JSON schemas, plugin-defined checks, remote execution,
concurrency, automatic repair, retry policy, and rollback orchestration remain
deferred and require independent Design First contracts.

## Terminal state

``` text
Design Contract --- Proposed
Production Stabilization --- Not Started
v1.2.8 Acceptance --- Not Accepted
```
