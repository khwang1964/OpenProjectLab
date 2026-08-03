# ADR 0005: Unify the Generator Input Contract

- Status: Accepted
- Date: 2026-08-03
- Decision owners: OpenProjectLab maintainers
- Related: ADR 0002, ADR 0004

## Context

OpenProjectLab has unified built-in generator outputs around `GenerationResult`,
but generator inputs still use overlapping contracts.

- `GenerateRequest` and `RuntimeOptions` already provide immutable runtime
  models in `generator/core/models.py`.
- `BaseGenerator` accepts the mutable `GeneratorContext` model and returns
  `None` from `run()` and `generate()`.
- `BootstrapGenerator`, `CourseGenerator`, and `WeekGenerator` accept an output
  path, an optional `Mapping[str, Any]`, and arbitrary keyword values.
- Built-in generators allow keyword values to override values supplied through
  the mapping. Tests currently protect this behavior.
- `generator/sdk/generator.py` exports `GeneratorContext` as though it were the
  public generator input contract.

These contracts duplicate the target path, template values, and execution
options. They also leave extension authors without one authoritative API and
make it harder for the CLI, SDK, built-in generators, and contract tests to
share the same lifecycle.

## Decision drivers

- Expose one stable input model to the CLI, SDK, built-in generators, and
  third-party generators.
- Preserve immutable request data throughout a generation run.
- Keep runtime options separate from template values.
- Align `BaseGenerator` with the existing `GenerationResult` output contract.
- Provide a measured migration path for existing callers.
- Avoid introducing a third context or request model.

## Decision

### Public request contract

`GenerateRequest` is the only public input contract for generator execution.
Its fields have the following meanings:

- `generator_name`: the registered generator identifier.
- `target`: the root path affected by the generation request.
- `values`: immutable template and generator-specific values.
- `options`: a `RuntimeOptions` instance containing execution behavior.

Generator-specific data belongs in `GenerateRequest.values`. Execution controls
such as `dry_run`, `overwrite`, `verbose`, and `force` belong only in
`GenerateRequest.options` and must not be duplicated in `values`.

The request remains immutable after construction. Generators may derive local
mutable dictionaries for rendering, but must not mutate the caller's data.

### Generator execution contract

The canonical public signatures become conceptually:

```python
def run(self, request: GenerateRequest) -> GenerationResult: ...

def generate(self, request: GenerateRequest) -> GenerationResult: ...
```

`run()` owns the complete lifecycle. `generate()` performs the generator's main
work within that lifecycle. Both return `GenerationResult`; neither returns a
generator-specific result type.

Every generator must validate that `request.generator_name` identifies the
generator being invoked. The exact registry alias policy will be documented by
the SDK reference before implementation is considered complete.

### Runtime options

`RuntimeOptions` is the authoritative source of cross-generator execution
behavior.

- `dry_run=True` validates and plans work without changing the filesystem.
- `overwrite=True` selects `WritePolicy.OVERWRITE`.
- `force=True` permits explicitly documented safety bypasses; it does not
  silently imply overwrite unless a later ADR changes that rule.
- `verbose=True` affects diagnostics only and must not change generation
  results.

Invalid or contradictory combinations must be rejected when a clear invariant
exists. Any new validation belongs in the immutable model and requires focused
unit tests.

### `GeneratorContext`

`GeneratorContext` is not a second public input contract.

During migration it may remain as a private lifecycle adapter if internal hooks
still require derived state such as resolved paths or loaded configuration. It
must not be exported from the public SDK after the migration. Once all internal
consumers accept `GenerateRequest` or a deliberately private runtime structure,
`generator/core/context.py` will be removed.

If derived mutable execution state proves necessary, it must have a private
name and must be created from—not accepted instead of—`GenerateRequest`.

### Compatibility policy

Migration is staged to avoid combining an API break with the initial contract
implementation.

1. Add canonical `GenerateRequest` support to the base class and built-in
   generators.
2. Adapt the CLI to construct one request before invoking a generator.
3. Temporarily retain the legacy output-root, mapping, and keyword forms at a
   single compatibility boundary.
4. Preserve the existing precedence rule while compatibility remains:
   explicit keyword context values override values from the legacy mapping.
5. Emit a documented deprecation warning for legacy calls.
6. Remove legacy signatures and the compatibility adapter in a separately
   reviewed breaking-change slice.

Compatibility normalization must not be duplicated across the three built-in
generators. One adapter converts legacy inputs into a `GenerateRequest`, after
which all execution follows the canonical path.

## Alternatives considered

### Keep `GeneratorContext` as the public contract

Rejected. It is mutable, duplicates fields already modeled by
`GenerateRequest` and `RuntimeOptions`, exposes `ProjectConfig` directly, and
does not match the input style used by built-in generators.

### Create a new input model

Rejected. `GenerateRequest` already represents the required public data. A new
model would create another migration target without resolving the duplication.

### Keep mapping and keyword arguments as the permanent API

Rejected. They provide weak discoverability and validation, mix template values
with execution options, and prevent a consistent SDK contract.

### Remove all legacy inputs immediately

Rejected for the first implementation slice. A staged transition makes the
behavioral change observable and testable while isolating the eventual breaking
change.

## Consequences

### Positive

- CLI, SDK, built-in generators, and plugins share one immutable request model.
- Input and output contracts become symmetrical: `GenerateRequest` in and
  `GenerationResult` out.
- Cross-generator behavior can be tested once through a contract suite.
- Execution options no longer leak into template values.
- Future lifecycle and plugin work gains a stable boundary.

### Negative

- A temporary compatibility adapter and deprecation tests are required.
- `BaseGenerator` and its lifecycle hooks need coordinated changes.
- SDK users must migrate from `GeneratorContext` and legacy call signatures.
- Documentation must clearly distinguish request data from derived runtime
  state.

## Migration plan

### Phase 1: contract tests and model hardening

- Add focused tests for `GenerateRequest` normalization and immutability.
- Add tests for `RuntimeOptions` and write-policy semantics.
- Add a parameterized input-contract suite for all built-in generators.
- Define expected errors for generator-name mismatches and invalid options.

### Phase 2: base and built-in generators

- Update `BaseGenerator` to consume `GenerateRequest` and return
  `GenerationResult`.
- Add one legacy-input adapter.
- Migrate Bootstrap, Course, and Week generators to the canonical request path.
- Preserve dry-run, manifest, affected-path ordering, and context precedence.

### Phase 3: CLI and SDK

- Build `GenerateRequest` in `generator/cli/main.py`.
- Export `GenerateRequest`, `RuntimeOptions`, and `GenerationResult` from the
  SDK surface.
- Stop exporting `GeneratorContext` as a public contract.
- Document deprecation behavior and migration examples.

### Phase 4: legacy removal

- Remove mapping and keyword compatibility in a dedicated breaking-change PR.
- Remove `GeneratorContext` when it has no internal consumers.
- Remove deprecation tests and replace them with rejection tests.

## Test matrix

| Area | Required behavior |
| --- | --- |
| Request model | Name normalization, empty-name rejection, `Path` normalization, immutable copied values |
| Runtime options | Default policy, overwrite policy, dry-run semantics, option validation |
| Built-in generators | Bootstrap, Course, and Week accept the same request shape |
| Result contract | `run()` and `generate()` return `GenerationResult` |
| Identity | A request for another generator is rejected |
| Compatibility | Legacy mapping and keyword calls normalize through one adapter |
| Precedence | Legacy keyword values override mapping values during the deprecation period |
| Dry run | Full validation with no filesystem or manifest mutation |
| CLI integration | CLI arguments produce the expected request and output |
| SDK | Public exports expose request, options, base generator, and result contracts |

## Documentation requirements

The implementation PR must update:

- `docs/architecture/generator.md`
- the Generator and SDK reference documentation
- CLI reference examples that invoke generators
- migration or deprecation guidance
- `CHANGELOG.md`

Documentation examples must use `GenerateRequest` as the primary API. Legacy
forms may appear only in migration guidance.

## Rollback plan

Because this ADR branch changes documentation only, it can be rolled back by
reverting the ADR and index commit before implementation begins.

After implementation starts, rollback must happen at the migration boundary:

1. Keep or restore the single legacy-input adapter so existing output-root,
   mapping, and keyword callers continue to work.
2. Revert CLI and SDK call sites to the last accepted public contract without
   reintroducing generator-specific result types.
3. Retain `GenerateRequest` and `RuntimeOptions` as unused internal models if
   removing them would create additional compatibility risk.
4. Re-run the legacy compatibility, dry-run, manifest, and result-contract
   suites before releasing the rollback.
5. Record any permanent reversal or replacement of this decision in a new ADR;
   do not rewrite an accepted ADR's history.

The legacy compatibility boundary must remain independently removable so a
failed generator migration does not require reverting unrelated result-contract
work completed under ADR 0004.

## Code Review Checklist

- [ ] Public execution accepts `GenerateRequest` as the canonical input.
- [ ] `RuntimeOptions` is the only source of cross-generator execution options.
- [ ] Request values are copied and remain immutable to callers.
- [ ] `run()` and `generate()` return `GenerationResult` consistently.
- [ ] Bootstrap, Course, and Week pass the same parameterized contract tests.
- [ ] Legacy normalization exists in one compatibility boundary only.
- [ ] Legacy keyword-over-mapping precedence remains covered by tests.
- [ ] Dry-run performs validation without filesystem or manifest mutation.
- [ ] `GeneratorContext` is not exported as a competing public contract.
- [ ] CLI and SDK documentation use the canonical request form.
- [ ] Architecture, reference, migration, and changelog documentation agree.
- [ ] Ruff, formatting, pytest, coverage, and pre-commit checks pass.

## Implementation boundary

This ADR is a design artifact only. No Python implementation changes belong in
the ADR branch. Implementation begins after this ADR is reviewed and accepted.
