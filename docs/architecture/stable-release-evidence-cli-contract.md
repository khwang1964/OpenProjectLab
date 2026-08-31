# Stable Release Evidence CLI Public Contract

> v1.3.10 Design First baseline — Proposed / Pending design review

## Context

The v1.3.7 opt-in preview has an accepted implementation and terminal evidence. The
v1.3.8 and v1.3.9 contracts can complete a narrow user-facing request workflow without
expanding the underlying read-only verification authority.

## Stable command inventory

The `release-evidence` family becomes a reviewed stable additive CLI family with two
exact command shapes:

- `opl release-evidence verify --request <path> --format json|text`
- `opl release-evidence request validate --request <path> --format json|text`

Both require an explicit bounded UTF-8 request and explicit output format. There is
no implicit repository selection, stdin, output file, interactive prompt, or default
format. Existing v1 and reviewed v1.1 command families remain unchanged.

## Public behavior

- installed-package and source-tree invocation expose the same parser contract
- JSON and text outputs reuse accepted deterministic renderers
- exit `0` means successful valid output
- exit `1` remains exclusive to a complete verification report with findings
- exit `2` means command/request/runtime failure prevented accepted success output
- stdout contains only successful structured output; stderr contains diagnostics
- English and zh-TW manuals document identical command and safety boundaries

## Authority boundary

Stable status does not authorize tests, discovery, arbitrary commands, mutation,
retry, polling, persistence, release, or publication. `verify` retains the v1.3.4
read-only allowlist; `request validate` remains fully offline.

## Deferred

- production implementation and stable registration
- public Python SDK, HTTP, RPC, plugin, marketplace, and remote service exposure
- stdin, output files, batch, queue, watch, retry, polling, and scheduling
- automatic evidence discovery, repair, enrichment, and credential management
- test execution, mutation, commit, push, merge, tag, release, and publication

## Code Review Checklist

- [ ] Both stable command shapes are exact and independently tested.
- [ ] Existing CLI inventory and legacy command behavior remain unchanged.
- [ ] Source-tree, installed-package, English, and zh-TW contracts agree.
- [ ] Output streams, formats, and exit statuses remain deterministic.
- [ ] Offline validation cannot reach runtime or command execution.
- [ ] Verification cannot exceed the accepted read-only allowlist.
- [ ] No mutation, discovery, retry, persistence, or publication is added.
