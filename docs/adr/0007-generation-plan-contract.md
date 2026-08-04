# ADR 0007: Define the Generation Plan Contract

- Status: Proposed
- Date: 2026-08-04
- Decision owners: OpenProjectLab maintainers
- Related: ADR 0002, ADR 0004, ADR 0005, ADR 0006

## Context

OpenProjectLab has converged on shared generator boundaries:

- ADR 0004 defines `GenerationResult` as the common output contract.
- ADR 0005 defines `GenerateRequest` and `RuntimeOptions` as the common input
  contract.
- ADR 0006 defines structured generator validation and requires validation to
  complete before side effects.

The remaining gap is the boundary between validated input and filesystem or
manifest effects. Bootstrap, Course, and Week generators currently coordinate
rendering and writing directly. Dry-run suppresses physical writes through the
existing write path, but callers cannot inspect one authoritative description
of the work before execution.

`GenerationOperation` and `GenerationPlan` already exist in
`generator/core/models.py`. They were introduced by commit `cc7cac7` with the
result-contract work and have focused core unit tests. The current models are
immutable, preserve operation order, normalize paths and context values, reject
duplicate destinations, and expose ordered destinations.

However, these models are not yet integrated into the generator lifecycle:

- the built-in generators do not construct or execute a `GenerationPlan`;
- `normalize_operations()` has no production call site;
- the public SDK does not export the plan types;
- the CLI has no plan-preview contract;
- dry-run does not expose the plan it evaluates;
- no cross-generator contract test proves that planned operations correspond
  to execution results.

Architecture documents describe a future Generation Plan, but some examples
use names or fields that differ from the existing model. Without a decision,
implementation could create a competing plan type or allow normal execution,
dry-run, and preview to calculate different work.

## Decision drivers

- Formalize the existing model skeleton instead of introducing a second plan
  representation.
- Establish a side-effect-free boundary after validation and before execution.
- Make normal execution and dry-run evaluate the same ordered operations.
- Preserve the ordering guarantees already provided by `GenerationResult`.
- Keep planning distinct from execution outcomes and manifest persistence.
- Support deterministic inspection, testing, CLI preview, and plugin behavior.
- Allow a staged migration of built-in and third-party generators.

## Decision

### 1. The existing plan models are canonical

OpenProjectLab adopts the existing `GenerationOperation` and `GenerationPlan`
names as the canonical core models. Implementation may harden their validation,
but must not introduce parallel public models such as `PlannedFile` or
`PlannedOutput` for the same responsibility.

The minimum conceptual contract is:

```python
@dataclass(frozen=True, slots=True)
class GenerationOperation:
    template_name: str
    destination: Path
    context: Mapping[str, Any]
    write_policy: WritePolicy


@dataclass(frozen=True, slots=True)
class GenerationPlan:
    generator_name: str
    operations: tuple[GenerationOperation, ...]
```

The implementation remains authoritative for constructor defaults and
normalization details. Public compatibility covers the documented field names,
their meanings, immutability, and ordering guarantees.

### 2. A plan is immutable, deterministic, and side-effect-free

Constructing or validating a plan must not create, update, or delete files and
must not mutate the generation manifest. For the same validated request and the
same relevant source state, planning must produce operations in the same order.

The plan owns the ordered intent to render and write generated files:

- `template_name` identifies the template source;
- `destination` identifies the intended output path;
- `context` contains the immutable values used to render that operation;
- `write_policy` declares how the filesystem layer handles an existing target.

Operation order is semantically significant. Implementations must not derive
public output order from an unordered mapping or set.

### 3. The standard lifecycle is validate, plan, execute or simulate, result

The generator lifecycle becomes:

1. accept a `GenerateRequest`;
2. validate shared and generator-specific input;
3. build and validate one `GenerationPlan`;
4. execute or simulate that same plan;
5. perform any permitted manifest update;
6. return one `GenerationResult`.

Conceptually:

```python
def plan(self, request: GenerateRequest) -> GenerationPlan: ...

def execute(
    self,
    request: GenerateRequest,
    plan: GenerationPlan,
) -> GenerationResult: ...
```

The final implementation may keep these as protected lifecycle hooks while the
public API remains `run(request)` and supported `generate(request)` calls.
Method visibility is less important than maintaining one plan and one execution
path. A generator must not rebuild materially different operations during
execution.

### 4. Plan validation precedes all physical writes

A valid plan guarantees at least:

- a non-empty canonical `generator_name` matching the selected generator;
- normalized, ordered operations;
- no duplicate destinations;
- destinations constrained to the request target or another explicitly
  documented allowed root;
- valid template identifiers and resolvable templates;
- immutable rendering context;
- a defined `WritePolicy` for every operation;
- no known file-versus-directory destination conflict;
- no operation that silently escapes the allowed output boundary.

Generator-specific planning rules remain owned by the generator. Template,
filesystem, and manifest subsystems retain their domain-specific validation and
exception boundaries.

Plan validation failures must occur before physical filesystem or manifest
mutation. A dedicated `GenerationPlanError` may be used for invalid plan
structure or invariants; invalid request values continue to use the validation
contract defined by ADR 0006.

### 5. Dry-run evaluates the same plan

`RuntimeOptions.dry_run` selects simulation rather than an alternative planning
algorithm. Normal execution and dry-run must consume the same validated plan in
the same operation order.

Dry-run must perform every pre-write check that can be evaluated without
committing changes, including template resolution, rendering, destination
safety, write-policy evaluation, and known conflicts. It must not mutate the
filesystem or generation manifest.

Dry-run returns `GenerationResult` with `dry_run=True`. Its `writes` describe
the simulated outcome using the existing `WriteResult` and `WriteStatus`
contract; they are not evidence that a physical write occurred.

### 6. Plan operations map predictably to result writes

Each file-producing `GenerationOperation` yields exactly one corresponding
`WriteResult`, in the same relative order, after execution or simulation. The
result records what happened; the plan records what was intended.

This decision does not require every internal directory creation or manifest
operation to become a `GenerationOperation` or `WriteResult`. Directory setup
and manifest persistence have different semantics and remain coordinated by the
lifecycle until a separate ADR defines a broader operation model.

Consequently:

- `GenerationPlan.operations` is not an execution log;
- `GenerationResult.writes` is not a replacement for the plan;
- `manifest_updated` continues to report committed manifest state;
- dry-run must keep `manifest_updated=False` because no manifest mutation was
  committed;
- warnings belong to the result unless they are necessary to make the plan
  valid or interpretable before execution.

### 7. Write policy is explicit per operation

Every operation carries a `WritePolicy`. The generator derives it from
`RuntimeOptions` and any documented ownership rules before execution. The
filesystem layer applies the policy; it does not infer policy from the CLI or
template context.

Planning may identify an existing destination without mutating it. A conflict
that is deterministically incompatible with the selected policy must fail
before the first write. Runtime races or failures that arise only while applying
the plan remain execution errors.

### 8. CLI preview is a presentation of the plan

A future CLI preview command or option must render the canonical
`GenerationPlan`; it must not reproduce generator-specific path calculation.
Preview output is a presentation contract, not a second plan model.

The initial lifecycle implementation does not require a public preview command.
CLI preview may be added in a later, independently reviewed slice after the
plan lifecycle is stable. Existing dry-run behavior remains supported during
that migration.

### 9. SDK and plugin compatibility use a staged boundary

The supported SDK will export `GenerationPlan` and `GenerationOperation` from a
documented import boundary when lifecycle integration is implemented. Plugin
authors must be able to construct plans using the same core types as built-in
generators.

Migration is staged:

1. `BaseGenerator` provides the common planning and execution lifecycle.
2. Bootstrap migrates first as the reference vertical slice.
3. Course and Week migrate after the contract suite proves the slice.
4. Existing plugins that implement only the current generation hook continue
   through one documented compatibility adapter for a deprecation period.
5. New or migrated plugins implement the plan boundary and receive the same
   validation, dry-run, ordering, and result guarantees.
6. Removal of the legacy plugin adapter requires a separate compatibility
   decision and release note.

Compatibility normalization must exist in one base or SDK boundary. It must not
be duplicated in individual built-in generators.

## Alternatives considered

### Introduce `PlannedFile` or `PlannedOutput`

Rejected. The repository already contains suitable immutable plan models.
Adding another representation would create competing contracts and another
migration target.

### Treat `GenerationResult` as the plan

Rejected. A result describes observed or simulated outcomes, including write
statuses, warnings, dry-run state, and manifest state. It cannot serve as a
side-effect-free statement of intent without confusing planned work with
execution evidence.

### Let dry-run independently rediscover operations

Rejected. Separate calculation paths can drift, making dry-run an unreliable
predictor of normal execution. Both modes must consume the same plan.

### Make every directory and manifest action a plan operation now

Rejected for this slice. The existing operation model describes template-to-file
work. Expanding it before directory and manifest semantics are designed would
delay the core lifecycle and risk false one-to-one claims with `WriteResult`.

### Require every plugin to adopt `plan()` immediately

Rejected for the initial implementation. An immediate break would combine the
new lifecycle with a plugin API migration. A single temporary adapter preserves
compatibility while making the target contract explicit.

### Keep plans internal forever

Rejected. Stable SDK types are required for third-party generators, contract
tests, service integrations, and future CLI preview without duplicating
generator logic.

## Consequences

### Positive

- Generator intent becomes inspectable before side effects.
- Normal execution, dry-run, tests, and future preview share one source of
  truth.
- Deterministic ordering can be preserved from plan operations to result
  writes.
- Built-in and plugin generators converge on the same lifecycle boundary.
- Conflict and path-safety checks can fail before partial output is created.
- Existing core models and tests are reused instead of replaced.

### Negative

- Built-in generators require coordinated lifecycle refactoring.
- A temporary plugin compatibility adapter increases short-term complexity.
- Planning may perform template resolution or rendering work that was formerly
  interleaved with writes.
- Some execution-time races cannot be eliminated by plan validation.
- CLI preview and full SDK exposure require later implementation slices.

## Migration plan

### Phase 1: model hardening and contract tests

- Confirm and document existing field normalization and immutability.
- Add tests for empty generator names, invalid template identifiers, duplicate
  destinations, path containment, context immutability, and operation order.
- Define `GenerationPlanError` ownership without wrapping unrelated domain
  errors.
- Add a parameterized plan-contract suite for built-in generators.

### Phase 2: Bootstrap vertical slice

- Add one lifecycle planning boundary to `BaseGenerator`.
- Make Bootstrap build one plan before applying any operation.
- Execute and simulate the same plan.
- Prove ordered one-to-one mapping from file operations to result writes.
- Preserve successful output, dry-run, manifest, and validation behavior.

### Phase 3: Course and Week migration

- Migrate Course and Week to the same lifecycle.
- Remove duplicated path, policy, or dry-run calculations from their execution
  paths.
- Run the shared cross-generator plan contract against all built-ins.

### Phase 4: SDK, plugins, and preview

- Export the plan types from the supported SDK boundary.
- Document plugin construction, compatibility, and deprecation behavior.
- Add a plugin fixture that plans and executes one generated file.
- Add CLI plan preview only from the canonical plan representation.

### Phase 5: compatibility removal

- Remove the legacy plugin adapter in a separately approved breaking-change
  slice.
- Remove dead normalization helpers or legacy execution paths.
- Update architecture status, reference documentation, roadmap, and changelog.

Each phase must remain independently reviewable and keep the complete quality
gate green.

## Test strategy

The Generation Plan contract requires:

- unit tests for both plan models, normalization, immutability, and validation;
- deterministic-order and duplicate-destination tests;
- path-containment and file-versus-directory conflict tests;
- parameterized plan-contract tests across Bootstrap, Course, and Week;
- tests proving planning has no filesystem or manifest side effects;
- tests proving validation and plan validation precede the first write;
- tests proving normal execution and dry-run consume equivalent operations;
- ordered mapping tests from file operations to `GenerationResult.writes`;
- result tests for `dry_run`, warnings, write statuses, and
  `manifest_updated`;
- failure-injection tests ensuring pre-write failures leave no partial output;
- SDK import-contract tests for public plan types;
- plugin compatibility and migrated-plugin fixture tests;
- CLI preview tests when preview becomes part of the supported interface.

All Python changes must satisfy Ruff linting and formatting, the complete pytest
suite, the configured coverage threshold, pre-commit hooks, and documentation
checks.

## Documentation requirements

Implementation of this ADR requires synchronized updates to:

- `docs/architecture/generator.md`;
- `docs/architecture/core-contract.md`;
- Generator, SDK, CLI, and plugin-author reference documentation;
- `docs/adr/README.md`;
- `docs/ROADMAP.md`;
- `CHANGELOG.md`.

Architecture documents must distinguish accepted design from implementation
status. Reference documentation must not present plan lifecycle or CLI preview
as available until the corresponding implementation and tests are merged.

## Rollback plan

Because the ADR branch contains documentation only, it can be reverted before
implementation without changing runtime behavior.

After implementation begins, rollback follows the migration boundary:

1. retain the existing plan models because they predate this ADR and may have
   external consumers;
2. restore the previous built-in execution hook through the single
   compatibility adapter;
3. retain the shared input, validation, and result contracts established by
   ADRs 0004 through 0006;
4. remove SDK exports or preview behavior only with corresponding compatibility
   documentation;
5. rerun validation, dry-run, manifest, result, and plugin compatibility tests;
6. record a permanent redesign in a superseding ADR rather than rewriting this
   decision's history.

## Code Review Checklist

- [ ] Existing `GenerationPlan` and `GenerationOperation` models are reused;
      no parallel plan model is introduced.
- [ ] Planning is deterministic, immutable, and free of filesystem and manifest
      side effects.
- [ ] The lifecycle follows `validate -> plan -> execute/simulate -> result`.
- [ ] Plan validation completes before the first physical write.
- [ ] Normal execution and dry-run consume the same ordered plan.
- [ ] Every file-producing operation maps to one ordered `WriteResult`.
- [ ] Directory and manifest operations are not falsely modeled as file-write
      results.
- [ ] Write policy is explicit and derived before execution.
- [ ] Generator validation and downstream domain exception boundaries remain
      intact.
- [ ] Bootstrap is migrated and reviewed as the first vertical slice.
- [ ] Course and Week pass the shared plan-contract suite before migration is
      declared complete.
- [ ] SDK exports, plugin compatibility, and deprecation behavior are tested and
      documented.
- [ ] CLI preview, if included, renders the canonical plan instead of rebuilding
      generator logic.
- [ ] Architecture, reference, ADR index, roadmap, and changelog agree with the
      actual implementation status.
- [ ] Ruff, formatting, pytest, coverage, pre-commit, and documentation checks
      pass.

## Implementation boundary

This ADR is a design artifact only. No Python, SDK, Generator, CLI, or test
implementation changes belong in the ADR branch. Implementation begins only
after the decision is reviewed and accepted.
