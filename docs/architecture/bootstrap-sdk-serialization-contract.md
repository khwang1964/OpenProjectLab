# Bootstrap SDK Serialization Contract Architecture

## Dependency direction

```text
serialization DTOs --- bootstrap SDK public contract models
bootstrap SDK runtime -/-> serialization execution
serialization decoder -/-> CLI adapter
serialization decoder -/-> filesystem / plugins / network
```

Serialization is an inspection and interchange boundary, not a runtime adapter. Encoding
projects accepted immutable SDK values into a closed JSON envelope. Decoding validates a
closed schema and constructs immutable DTOs without invoking production lifecycle code.

## Schema identity

```text
schema --- opl.bootstrap/1.0
document_type --- bootstrap-request | bootstrap-result
payload --- closed type-specific object
```

Version dispatch is explicit and fail closed. A decoder never guesses a schema, silently
drops fields, or upgrades documents. Future migration requires an independent contract.

## Determinism and evidence

Object keys are canonicalized only for encoding. Every evidence sequence remains an array
in authoritative runtime order. Optional phases distinguish absent evidence from present
empty evidence. Paths are inert forward-slash lexical strings and are never resolved.

## Security boundary

Duplicate keys, non-finite numbers, executable metadata, arbitrary object hooks, unknown
fields, and unsupported versions are rejected. Decode performs no filesystem, plugin,
network, CLI, runtime, repair, retry, or rollback action.
