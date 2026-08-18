# Generators

Generators are the primary content-production units in OpenProjectLab (OPL).
They convert validated requests into explicit generation plans and then execute
those plans through the shared framework lifecycle.

This chapter describes the user-facing Generator model and the built-in
Generator families exposed by the current CLI.

## 1. Canonical Lifecycle

Built-in Generators follow:

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

This lifecycle is framework-owned. A Generator supplies domain-specific
validation and planning behavior without replacing the common execution model.

## 2. Request Model

A generation request carries three main categories of information:

```text
generator_name
target
values
options
```

`values` contains Generator-specific structured input.

Runtime options include the shared behaviors represented by CLI flags such as:

```text
--dry-run
--force
```

Manifest recording is passed as generation context by the CLI for built-in
commands that support it.

## 3. Planning Before Execution

A valid request becomes a `GenerationPlan`.

Planning makes intended filesystem operations explicit before execution. This
supports deterministic tests and prevents Generator implementations from
silently creating their own unrelated write lifecycle.

A plan associates templates with destinations and the context required for
rendering.

## 4. Built-in Generator Identities

The current built-in Generator identities are:

```text
assignment
bootstrap
course
lab
quiz
slides
website
week
```

Use:

```console
opl list
```

to inspect the installed set.

## 5. Bootstrap Generator

Identity:

```text
bootstrap
```

Purpose: create the broader project/course skeleton.

Typical user input includes:

```text
project slug
project/course name
language
license
optional copyright metadata
```

CLI example:

```console
opl --output-root ./output bootstrap modern-java --name "Modern Java"
```

Bootstrap uses the same validation, planning, execution, dry-run, overwrite,
and result boundaries as other built-in Generators.

## 6. Course Generator

Identity:

```text
course
```

Purpose: generate the course-level README artifact.

Typical input includes:

```text
course name
language
weeks
license
optional textbook
optional instructor
optional description
```

Representative target:

```text
<output-root>/<project-slug>/README.md
```

CLI example:

```console
opl --output-root ./output course demo-course --name "Demo Course" --weeks 4 --language en
```

This Generator is used by the First 15 Minutes executable documentation smoke
test because it provides a small end-to-end installed-artifact workflow.

## 7. Week Generator

Identity:

```text
week
```

Purpose: generate a weekly courseware README.

Typical input includes:

```text
week number
title
course name
language
optional textbook chapter
directory pattern
```

The default CLI directory pattern is:

```text
week-{week:02d}
```

CLI example:

```console
opl --output-root ./output week demo-course --week 1 --title "Introduction"
```

## 8. Lab Generator

Identity:

```text
lab
```

Purpose: generate weekly Lab material.

Required CLI concepts include:

```text
week
lab-id
title
```

Example:

```console
opl --output-root ./output lab demo-course --week 1 --lab-id hello-lab --title "Hello Lab"
```

## 9. Assignment Generator

Identity:

```text
assignment
```

Purpose: generate Assignment material from structured content.

The CLI loads a UTF-8 JSON object from:

```text
--content-file FILE
```

and passes the structured values into the Generator contract.

Example command shape:

```console
opl --output-root ./output assignment demo-course --week 1 --assignment-id assignment-01 --title "Assignment 01" --content-file ./assignment.json
```

Do not infer the complete Assignment JSON schema from this chapter. Use the
Assignment contract and examples that correspond to the installed version.

## 10. Quiz Generator

Identity:

```text
quiz
```

Purpose: generate Quiz material from structured questions.

The CLI loads UTF-8 JSON through:

```text
--questions-file FILE
```

Example command shape:

```console
opl --output-root ./output quiz demo-course --week 1 --quiz-id quiz-01 --title "Quiz 01" --questions-file ./questions.json
```

Generator validation determines whether the loaded question structure satisfies
the Quiz contract.

## 11. Slides Generator

Identity:

```text
slides
```

Purpose: generate Markdown slide material from structured slide content.

Input is loaded from:

```text
--slides-file FILE
```

Example command shape:

```console
opl --output-root ./output slides demo-course --title "Week 01 Slides" --slides-file ./slides.json
```

## 12. Website Generator

Identity:

```text
website
```

Purpose: generate static course website output from structured page content.

Input is loaded from:

```text
--pages-file FILE
```

Example command shape:

```console
opl --output-root ./output website demo-course --title "Demo Course" --pages-file ./pages.json
```

## 13. Package-Owned Templates

Built-in Generators normally resolve templates from the installed
`generator.resources` package boundary.

This is essential to the v1.0 installed-user contract:

```text
installed wheel
    ↓
package-owned template
    ↓
Generator plan
    ↓
generated artifact
```

Normal use must not require the repository-level template tree.

An explicit `--template-root` override is available for intentional custom
template use.

## 14. Dry Run

Use:

```text
--dry-run
```

to validate and plan without performing normal persisted generation.

Example:

```console
opl --output-root ./output course demo-course --name "Demo Course" --dry-run
```

The First 15 Minutes smoke test verifies that the representative Course
`README.md` is not persisted by this dry-run workflow.

## 15. Overwrite Behavior

Use:

```text
--force
```

only when overwrite is intentional.

Without overwrite permission, existing destinations are protected according to
the established filesystem/Generator contract.

Do not design automation that routinely relies on `--force` to hide stale or
unexpected output.

## 16. Manifest Recording

Built-in CLI generation requests normally enable manifest recording.

Use:

```text
--no-manifest
```

to disable the manifest update for a request.

The manifest is OPL-owned metadata; it should not be confused with the
Generator's primary authored artifact.

## 17. Validation and Failure

Generators validate domain input before avoidable write effects.

Examples of invalid input can include:

- non-positive week counts or week numbers;
- missing required identifiers;
- invalid structured JSON content after loading;
- Generator-specific schema violations;
- unsafe or conflicting filesystem operations.

The CLI converts handled validation/configuration/value/file failures into a
non-zero exit status.

## 18. Determinism

Generators should produce predictable plans for equivalent inputs and relevant
configuration.

Determinism supports:

```text
contract tests
integration tests
documentation smoke tests
CI
reviewable generated artifacts
```

A Generator should not introduce hidden network calls or other uncontrolled
external behavior into the canonical lifecycle without an explicit contract.

## 19. Generators and Courseware Composition

Courseware Composition coordinates existing Generators.

Conceptually:

```text
courseware intent
    ↓
ordered Generator requests
    ↓
canonical lifecycle for each Generator
    ↓
composed courseware artifacts
```

Composition does not create a second Generator framework and does not imply
generalized rollback across already successful Generator executions.

See [Courseware](courseware.md) for the higher-level domain model.

## 20. Third-Party Generators

Third-party Generators integrate through the Plugin SDK and canonical Entry
Point group:

```text
openprojectlab.generators
```

They are expected to participate in the same public Generator contracts rather
than bypassing validation, planning, or registration.

See [Plugins](plugins.md).

## 21. Generator Checklist

Before running a Generator:

```text
[ ] Confirm the Generator identity with opl list.
[ ] Review opl <command> --help.
[ ] Supply all required domain input.
[ ] Use an explicit output root when location matters.
[ ] Use package-owned templates unless intentionally overriding them.
[ ] Consider --dry-run before writing.
[ ] Use --force only for intentional overwrite.
[ ] Decide whether manifest recording should remain enabled.
[ ] Treat structured JSON files as validated Generator inputs.
```

## Next Step

Continue with [Courseware](courseware.md) to understand how Generator outputs
participate in the larger courseware model.
