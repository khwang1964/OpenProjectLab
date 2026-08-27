# Bootstrap CLI Public Contract Architecture

> **Status:** Accepted --- Terminally Closed

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
Design Contract --- Accepted
Production Stabilization --- Not Started
v1.2.8 Acceptance --- Accepted
```

<!-- v1.2.8-bootstrap-cli-public-contract-terminal-alignment-architecture -->

## Minimum Implementation Alignment

``` text
Implementation PR #254 / merge 1d36d568ca0b09cde2f8e12418bfdb63e72f14e2 --- Verified
Stable parser alias and normalization --- Implemented
Bootstrap runtime failure mapping --- exit 1
Legacy command failure mapping --- exit 2
Deterministic result / diagnostic channels --- Preserved
Core runtime lifecycle ownership --- Unchanged
Deferred architecture --- Unchanged
Implementation acceptance --- Pending terminal-alignment merge
```
