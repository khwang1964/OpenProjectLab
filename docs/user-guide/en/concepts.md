# OpenProjectLab Concepts

This chapter introduces the mental model behind OpenProjectLab (OPL). You do not
need to know internal implementation details to use OPL, but understanding the
main boundaries makes the CLI, Generators, plugins, courseware, AI integration,
and Marketplace behavior easier to reason about.

## 1. OpenProjectLab as a Project Engineering Platform

OPL began as a project and content generator, but its design is broader than
template expansion alone.

The platform is organized around four engineering principles:

```text
Design First
Documentation First
Automation First
Testing First
```

For a user, the practical consequence is that important behavior is expressed
through explicit contracts and verified workflows instead of hidden
conventions.

## 2. Generators

A Generator is a component that turns structured input into one or more planned
artifacts.

Examples of built-in Generator identities include:

```text
bootstrap
course
week
lab
quiz
assignment
slides
website
```

Each Generator has its own user-facing input, but built-in Generators share the
same framework-controlled lifecycle.

## 3. Canonical Generation Lifecycle

The core lifecycle is:

```text
GenerateRequest
    ↓
validate_request
    ↓
plan
    ↓
execute
    ↓
GenerationResult
```

### Request

A request identifies:

- which Generator should run;
- the target location;
- the values needed by that Generator;
- runtime options such as overwrite or dry-run behavior.

### Validation

Validation rejects invalid input before avoidable side effects occur.

A Generator should not begin writing files merely to discover later that a
required input is invalid.

### Plan

Planning converts a valid request into an explicit `GenerationPlan`.

A plan describes the generation operations that are intended to happen,
including the template and destination for each planned artifact.

### Execution

Execution applies the plan through the existing rendering and filesystem
boundaries.

### Result

Execution returns a `GenerationResult` rather than inventing a separate
Generator-specific result model.

This shared lifecycle is a core architectural constraint: extensions should not
create a second execution framework.

## 4. Targets, Output Roots, and Generated Artifacts

The CLI resolves an output root and then derives Generator-specific targets
within it.

For example, a `course` command using a project slug such as `demo-course`
targets:

```text
<output-root>/demo-course/
```

The Course Generator produces:

```text
<output-root>/demo-course/README.md
```

unless the request explicitly changes the output name through lower-level
programmatic use.

Generation may also maintain OPL-owned metadata such as the project manifest
when that behavior is enabled.

## 5. Package-Owned Runtime Resources

Built-in Generators use runtime templates.

For v1.0 release readiness, those templates are owned by the installed Python
package under the package-resource boundary instead of depending on a
repository-level `templates/` directory.

Conceptually:

```text
installed openprojectlab distribution
        ↓
generator.resources
        ↓
package-owned templates
        ↓
built-in Generator
```

This matters because an installed user should be able to run OPL outside the
source repository.

The CLI still supports an explicit `--template-root` override when a user
intentionally wants a different template root.

## 6. Dry Run and Overwrite Behavior

Built-in generation commands share write-related runtime options.

### Dry Run

`--dry-run` validates and plans the operation without persisting the normal
generated output.

Use it when you want to inspect whether a generation request is valid before
writing files.

### Force / Overwrite

`--force` permits overwrite behavior where the underlying Generator and
filesystem contract allow it.

Without an explicit overwrite request, OPL preserves the established
write-conflict behavior rather than silently replacing user content.

### Manifest Control

`--no-manifest` disables manifest updates for commands that otherwise record
generation metadata.

## 7. Courseware Model

OPL includes an Open Courseware layer.

At its foundation are Course and Week concepts. Higher-level content can be
generated around them, including:

- Lab material;
- Quiz material;
- Assignment material;
- Slides source;
- static Website output.

Courseware Composition coordinates existing Generators rather than creating a
second generation lifecycle.

The established composition behavior is deterministic and fail-fast. It does
not promise generalized cross-Generator rollback.

## 8. Plugin Extension Model

Third-party Generator extensions use the stable Plugin SDK/public boundary and
the canonical Entry Point group:

```text
openprojectlab.generators
```

Conceptually:

```text
third-party installed distribution
        ↓
openprojectlab.generators Entry Point
        ↓
discovery / loading
        ↓
validation
        ↓
registry
        ↓
canonical Generator lifecycle
```

Installation and discovery do not justify bypassing validation or the shared
Generator lifecycle.

Plugin authors should depend on the public SDK boundary rather than internal
modules when the SDK provides the required contract.

## 9. AI Integration Boundary

OPL's AI architecture separates provider-specific behavior from the core
application contracts.

The provider-independent model is:

```text
application request
        ↓
AIProvider
        ↓
AIResponse
        ↓
structural validation
        ↓
domain mapping / application service
```

AI output is treated as external input and must be validated before it is used
to construct domain objects or participate in generation.

Normal deterministic tests do not require a real provider, public network
access, or paid invocation.

A concrete provider adapter may exist behind the provider-independent boundary,
but provider-specific SDK details are not the core AI contract.

## 10. Marketplace Boundary

The Marketplace layer models distributable artifacts and separates several
responsibilities:

```text
artifact lookup
    ↓
acquisition
    ↓
integrity verification
    ↓
installation
```

Installation is deliberately separate from activation.

The verified Marketplace core does not imply that v1.0 includes a public
remote Marketplace service, ratings, reviews, monetization, generalized
dependency solving, or other deferred platform capabilities.

## 11. Stable, Experimental, Internal, and Deferred Behavior

Milestone 8 audits the v1.0 surface so documentation does not accidentally
promise more than the project can maintain.

A useful reading rule is:

- **Stable** — part of the reviewed compatibility surface.
- **Experimental** — implemented but not promoted to the same compatibility
  commitment.
- **Internal** — implementation detail, not a user contract.
- **Deferred** — intentionally outside the v1.0 scope.

The exact compatibility/deprecation policy is owned by the later Milestone 8
policy step. This Concepts chapter does not pre-define that policy.

## 12. Determinism

Deterministic behavior is an important OPL property.

Given equivalent valid inputs and the same relevant configuration, OPL aims to
produce predictable plans and artifacts. This makes the system easier to test,
review, automate, and integrate into CI.

Sources of hidden nondeterminism should not be introduced into core generation
without an explicit contract.

## 13. Failure Boundaries

OPL generally follows these principles:

```text
validate before avoidable side effects
fail predictably
preserve existing state where the contract requires it
do not claim rollback that does not exist
```

For example:

- invalid Generator input should fail before generation;
- integrity verification should happen before Marketplace installation;
- invalid AI structured output should fail before downstream filesystem
  effects;
- composition stops on failure but does not claim to undo earlier successful
  Generators.

## 14. User Mental Model

A practical way to think about OPL is:

```text
CLI / application input
        ↓
verified public contracts
        ↓
Generator / Plugin / AI / Marketplace boundaries
        ↓
deterministic planning and validation
        ↓
filesystem or installation result
```

You do not need to use every subsystem. The shared contracts exist so that
simple workflows and larger composed workflows behave consistently.

## Next Step

Continue with [Installation](installation.md), then complete the
[Quick Start](quick-start.md).
