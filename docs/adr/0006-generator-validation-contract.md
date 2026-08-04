# ADR 0006: Define the Generator Validation Contract

- Status: Proposed
- Date: 2026-08-04
- Decision owners: OpenProjectLab maintainers
- Related: ADR 0002, ADR 0005

## Context

ADR 0005 established `GenerateRequest` and `RuntimeOptions` as the shared input
contract for built-in generators. Bootstrap, Course, and Week generators now
consume that contract, but validation behavior is not yet governed by a shared
contract.

Validation is currently distributed across several layers:

- `GenerateRequest.__post_init__()` checks shared input invariants.
- Each built-in generator validates its name and generator-specific values.
- `TemplateRenderer`, `FileSystem`, and `GenerationManifest` validate their own
  domain constraints.
- The generator registry uses `ValidationError`, while built-in generators
  commonly raise `ValueError`.
- The CLI catches broad `ValueError` and `RuntimeError` groups and translates
  them into user-facing failures.

This distribution is reasonable, but the ownership and public behavior are not
explicit. Callers cannot reliably distinguish an invalid generator request from
a programming error or a template, filesystem, or manifest failure. Error
messages also carry no stable generator or field metadata.

The existing `BaseGenerator` lifecycle models `validate -> generate ->
completed`, while built-in generators validate directly inside `generate()`.
Without a defined entry point, introducing validation risks duplicate checks or
different behavior between `run()` and `generate()`.

Dry-run already performs input, template, and path validation before suppressing
physical writes. This behavior must remain part of the public contract.

## Decision

### 1. Validation is layered by ownership

Each layer validates only the invariants it owns:

| Layer | Responsibility |
| --- | --- |
| `GenerateRequest` | Shared structure, normalization, and type-independent request invariants |
| Generator | Generator identity and generator-specific business values |
| Template subsystem | Template existence, required variables, rendering, and template paths |
| Filesystem subsystem | Destination safety and filesystem operation constraints |
| Manifest subsystem | Manifest schema, entries, and persistence constraints |
| CLI | Parse command-line syntax and present domain failures; it does not duplicate domain validation |

`GenerateRequest` does not know the accepted fields or business rules of a
specific generator. Generators do not wrap unrelated template, filesystem, or
manifest failures as validation errors.

### 2. Generator business validation uses a dedicated exception

Introduce `GeneratorValidationError` as a subclass of
`OPLGeneratorError`. It represents a structurally valid `GenerateRequest` that
cannot be accepted by the selected generator.

The exception exposes stable machine-readable attributes:

- `generator`: the canonical generator name;
- `field`: the invalid field name, or `None` when the failure concerns the
  request as a whole;
- `message`: a concise human-readable explanation.

The attributes form the compatibility contract. Exact rendered sentence
wording is not a stable API unless a test explicitly declares it so.

Shared model construction may continue to raise `ValueError` for invalid model
invariants. This preserves normal Python value-object semantics and keeps
generator business validation distinct from model construction.

### 3. Validation occurs before planning or side effects

The standard generator execution lifecycle is:

1. confirm that `request.generator_name` identifies the selected generator;
2. validate and normalize generator-specific values;
3. build and validate the generation plan;
4. render templates and perform domain checks;
5. execute or simulate writes;
6. return `GenerationResult`.

Validation must complete before any physical write or manifest mutation. A
failed request returns no `GenerationResult` and leaves the destination
unchanged.

### 4. `run()` is the standard lifecycle boundary

`run(request)` is the preferred public execution entry point. It coordinates
validation and generation exactly once. The internal generation step consumes
validated values and must not establish a second, divergent contract.

During migration, existing `generate(request)` call sites remain supported.
They must preserve the same validation behavior and exception semantics as
`run(request)`. Removal or restriction of `generate()` as a public entry point
requires a separate compatibility decision.

### 5. Dry-run performs complete validation

`RuntimeOptions.dry_run` changes write execution, not validation. A dry-run must
perform all validation, planning, template rendering, required-variable checks,
and path-safety checks that can be performed without committing changes.

A request that fails during a normal run must also fail during dry-run when the
same pre-write information is available. Dry-run must not create, update, or
delete files or mutate the generation manifest.

### 6. CLI translation is explicit

The CLI catches `OPLGeneratorError` at its application boundary and converts it
to a concise user-facing error with a non-zero exit status. For
`GeneratorValidationError`, output may include the generator and field metadata
without exposing a traceback during normal operation.

Argument-parser errors remain parser errors. Unexpected exceptions are not
reclassified as validation failures and remain visible to diagnostics and test
infrastructure.

### 7. The SDK exposes the shared contract

The supported generator SDK surface will expose the shared request, runtime,
result, and generator-validation types from one documented import boundary.
The exact re-export module is finalized during implementation, but callers
must not need to import a built-in generator to handle validation consistently.

## Error contract

Generator validation errors follow these rules:

- `generator` uses the canonical registered name.
- `field` uses the public `GenerateRequest` field name or a key from
  `GenerateRequest.values`.
- Missing, invalid-type, out-of-range, malformed-pattern, and unsafe
  generator-specific values use `GeneratorValidationError`.
- Template, filesystem, configuration, manifest, and upgrade failures retain
  their existing domain exception types.
- Validation order is deterministic so that the first reported error is stable
  for the same request.

## Alternatives considered

### Continue using `ValueError` everywhere

Rejected. It is idiomatic for isolated value checks but cannot reliably
separate user-correctable generator input from unrelated programming and
library errors at the CLI or SDK boundary.

### Put every validation rule in `GenerateRequest`

Rejected. The shared model would need knowledge of every built-in and plugin
generator, coupling the core input contract to generator-specific fields and
preventing independent extension.

### Wrap all downstream errors as generator validation errors

Rejected. It would erase useful domain boundaries, make operational failures
look like user input mistakes, and complicate diagnostics.

### Validate only in the CLI

Rejected. SDK and programmatic callers must receive the same guarantees, and
plugins must not depend on one presentation layer.

### Skip expensive checks during dry-run

Rejected as a general rule. It would make dry-run an unreliable predictor of a
real execution. Checks that intrinsically require a committed write may remain
execution-time failures, but this exception must be documented and tested.

## Consequences

### Positive

- CLI and SDK callers can identify user-correctable validation failures.
- Built-in and plugin generators share a stable error shape.
- Validation ownership becomes explicit and avoids cross-layer duplication.
- Dry-run remains a trustworthy preflight operation.
- Domain failures preserve their diagnostic precision.

### Negative

- Existing tests that assert `ValueError` for generator business rules require
  migration.
- `run()` and `generate()` need temporary compatibility coverage.
- Plugin authors must adopt the new exception contract for consistent CLI
  behavior.
- Structured error fields add a compatibility surface that maintainers must
  preserve.

## Migration plan

1. Add contract tests for Bootstrap, Course, and Week generators before
   changing production behavior.
2. Introduce `GeneratorValidationError` and unit tests for its stable
   attributes and rendering.
3. Add or consolidate the standard validation/lifecycle entry point without
   changing successful generation results.
4. Migrate built-in generator name and business-value checks from
   `ValueError` to `GeneratorValidationError`.
5. Preserve template, filesystem, manifest, and configuration exception
   boundaries.
6. Update the CLI to catch `OPLGeneratorError` explicitly and test its exit
   status and user-facing output.
7. Export and document the supported SDK validation types.
8. Update architecture, reference, changelog, and plugin-author documentation.
9. Remove broad compatibility catches only after the full suite confirms that
   no supported path depends on them.

Each implementation step should be independently reviewable and keep the test
suite green.

## Test strategy

The validation contract requires:

- unit tests for `GeneratorValidationError` attributes and string rendering;
- parameterized contract tests across all built-in generators;
- tests for generator-name mismatch, missing values, invalid types, invalid
  ranges, malformed patterns, and unsafe paths where applicable;
- tests proving validation precedes filesystem and manifest side effects;
- tests proving dry-run performs the same pre-write validation and has no
  physical side effects;
- tests preserving template, filesystem, and manifest exception types;
- lifecycle tests proving `run()` and supported `generate()` calls validate
  exactly once with equivalent outcomes;
- CLI integration tests for message shape, non-zero exit status, and absence of
  normal-operation tracebacks;
- SDK import-contract tests for documented public exports;
- plugin fixture tests demonstrating adoption by a non-built-in generator.

All Python changes must pass Ruff formatting and linting, the full pytest suite,
coverage thresholds, and all pre-commit hooks.

## Documentation changes

Implementation of this ADR requires updates to:

- the generator architecture and lifecycle documentation;
- the generator SDK/reference documentation;
- CLI error-handling documentation and examples;
- plugin author guidance;
- the changelog and roadmap or milestone status;
- this ADR index when the decision is accepted.

## Rollback plan

Before release, individual migration commits can be reverted while retaining
the ADR as `Proposed`. If compatibility problems appear after release, retain
`GeneratorValidationError` but temporarily restore legacy `ValueError` handling
at the CLI boundary and in supported `generate()` adapters. Do not reclassify
downstream domain errors.

If the contract itself is abandoned or materially redesigned, mark this ADR
`Superseded` and record the replacement decision in a new ADR rather than
rewriting this document's history.

## Code Review Checklist

- [ ] Validation ownership follows the layer table in this ADR.
- [ ] Generator business failures use `GeneratorValidationError`.
- [ ] Stable `generator` and `field` metadata are populated correctly.
- [ ] Shared model invariant failures retain their documented semantics.
- [ ] Template, filesystem, manifest, configuration, and upgrade errors are not
      incorrectly wrapped.
- [ ] Validation completes before any physical write or manifest mutation.
- [ ] Dry-run performs complete pre-write validation and has no side effects.
- [ ] `run()` and supported `generate()` paths produce equivalent validation
      outcomes without duplicate validation.
- [ ] CLI output and exit behavior are covered by integration tests.
- [ ] Built-in generators share parameterized contract tests.
- [ ] SDK exports and plugin behavior are documented and tested.
- [ ] Ruff, pytest, coverage, pre-commit, and documentation checks pass.
- [ ] Architecture, reference, changelog, roadmap, and ADR index updates are
      included where applicable.
