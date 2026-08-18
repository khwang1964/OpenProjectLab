# Courseware

OpenProjectLab (OPL) models courseware separately from file rendering. The current layer provides immutable `Course` and `Week` domain models plus `CoursewareComposer`, which coordinates ordered Generator requests through the shared `GeneratorRegistry`.

## Domain model

`Week(number, title)` represents one teaching unit. `number` must be an integer greater than zero.

`Course(course_id, title, language, weeks=())` is the root aggregate. It trims `course_id`, rejects an empty ID and duplicate week numbers, converts weeks to a tuple, and stores them ordered by week number.

```python
from generator.courseware import Course, Week

course = Course(
    course_id="modern-java",
    title="Modern Java",
    language="en",
    weeks=(Week(2, "Streams"), Week(1, "Introduction")),
)
```

The resulting weeks are ordered 1, then 2.

## Composition architecture

Courseware composition reuses the Generator framework:

```text
ordered GenerateRequest values
→ validate sequence
→ resolve every required Generator
→ execute sequentially
→ tuple[GenerationResult, ...]
```

`CoursewareComposer.plan()` preserves authored order and returns an immutable tuple. Input must be an ordered `Sequence` containing only `GenerateRequest` values; strings, bytes, mappings, non-sequences, and mixed-value sequences are rejected.

## Fail-fast preflight

`run()` resolves **all** required Generators before executing any of them. If a later request names an unavailable Generator, composition fails before earlier requests can create filesystem effects.

After preflight, execution is sequential. If a Generator then fails, subsequent requests are not run. Earlier successful writes are **not** automatically reversed. This is fail-fast orchestration, not an ACID transaction or generalized rollback facility.

## CLI boundary

The documented v1.0 CLI remains Generator-oriented (`course`, `week`, `lab`, `assignment`, `quiz`, `slides`, `website`). There is no documented general-purpose `courseware compose` command. Programmatic composition is therefore a framework/domain capability unless a later release establishes a CLI contract.

## AI relationship

AI-assisted course generation maps provider-independent AI output into the same `Course` / `Week` domain model:

```text
AIResponse → validated mapping → Course / Week
```

AI does not define a parallel courseware representation.

## Design boundaries

```text
Course / Week        domain model
Generators           artifact planning/execution
CoursewareComposer   ordered orchestration
Plugin SDK           Generator discovery/registration
AI                   provider-independent assistance
Marketplace          artifact distribution contracts
```

### Checklist

- Use positive, unique Week numbers.
- Provide a non-empty `course_id`.
- Treat Course and Week as immutable values.
- Supply ordered `GenerateRequest` values.
- Register every required Generator before composition.
- Expect unresolved Generators to fail during preflight.
- Do not assume rollback of already completed Generator writes.

## Next step

Continue with [Plugins](plugins.md).
