# Bootstrap SDK Runtime Public Contract Architecture

## Dependency direction

```text
CLI adapter --- core bootstrap runtime
SDK adapter --- core bootstrap runtime
CLI adapter -/-> SDK adapter
SDK adapter -/-> CLI adapter
```

`generator.sdk.bootstrap_runtime` is a library-facing sibling of the command-line
adapter. It translates immutable SDK requests into existing core runtime requests and
translates core evidence into immutable SDK results. It does not parse arguments,
render messages, write streams, or choose exit codes.

## Contract mapping

```text
BootstrapSdkMode.preview --- plan / dry-run
BootstrapSdkMode.apply --- apply
BootstrapSdkMode.apply-and-validate --- apply / validate
invalid request --- BootstrapSdkUsageError
runtime or check failure --- BootstrapSdkExecutionError
validation findings --- BootstrapSdkResult with invalid validation state
```

All observable collections preserve deterministic core ordering. Failure translation
preserves phase identity, failed check identity, and already completed evidence.

## Filesystem boundary

Preview and validation are inspection-only. Apply is the sole mutation boundary.
The SDK adds no repair, rollback, hidden retry, or compensating write path.

## Deferred architecture

Serialization schemas, asynchronous execution, concurrency, remote execution,
plugin-provided checks, automatic recovery, and a public extension protocol remain
outside the v1.2.9 contract.

## Terminal design acceptance

The architecture contract was accepted after PR #257 merged as
`28cd71b1a415e876a09fcac15c9fd2e9dc5d8f93` and synchronized-main verification completed with 11 focused tests.
Production implementation remains Not Started.
