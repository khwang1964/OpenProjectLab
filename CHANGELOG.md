# Changelog

## Unreleased

### Changed

-   Standardized Generator input validation on
    `GeneratorValidationError`, with stable `generator`, `field`, and
    `message` attributes for callers and tests.
-   Migrated `BootstrapGenerator`, `CourseGenerator`, and
    `WeekGenerator` away from validation-specific `ValueError` behavior.
-   Updated the CLI error boundary to report Generator validation
    failures on standard error and return exit code `2`.
-   Completed the migration of `BootstrapGenerator`, `CourseGenerator`,
    and `WeekGenerator` to the shared `GenerationResult` contract.
-   Standardized `generate()` and `run()` result semantics across all
    core generators.
-   Decoupled the CLI from generator-specific result types; Bootstrap,
    Course, and Week output now uses the ordered
    `GenerationResult.affected_paths` view.
-   Bootstrap project-root display is derived from the command input
    instead of a generator-specific result field.
-   Removed the temporary `BootstrapResult`, `CourseResult`, and
    `WeekResult` compatibility layers after completing downstream
    migration.

### Added

-   Added ADR 0009: Remove Legacy Generator Lifecycle.

-   Added Legacy Generator Lifecycle Removal Contract Tests.

-   Added parameterized cross-generator validation contract tests
    covering the shared `generator_name` and `template_root` fields,
    Bootstrap `project_slug`, and Week `week` and `directory_pattern`
    fields.

-   Added Generator validation architecture, ADR, and reference
    documentation, including a Code Review Checklist for validation
    changes.

-   Added focused tests for `GenerationResult`.

-   Added parameterized cross-generator contract tests for result type,
    immutable writes, affected-path ordering, dry-run behavior, run
    aliases, and Manifest state.

-   Documented the Generator Framework contract and the recommended
    Milestone 3 migration sequence.

-   Documented the Bootstrap result migration from `generated_files` to
    `affected_paths` and clarified that `created_directories` is not
    part of the shared result contract.

### Migration

-   Catch `GeneratorValidationError` when handling invalid Generator
    input; do not depend on the former validation-specific `ValueError`
    behavior.
-   Inspect the structured `generator` and `field` attributes instead of
    parsing validation message text.
-   Replace reads of `generated_files` or `output_path` with
    `GenerationResult.affected_paths`.
-   Preserve or derive Bootstrap's project root from the request or CLI
    input.
-   Do not infer created directories from `affected_paths`; directory
    creation is an implementation detail rather than a shared result
    field.
-   Stop importing `BootstrapResult`, `CourseResult`, and `WeekResult`
    in new code.

### Changed

-   Finalized the canonical Generator execution lifecycle around
    `BaseGenerator.run()`.
-   Clarified the framework-owned execution sequence:
    `validate_request() → plan() → execute() → GenerationResult`.
-   Documented validation, planning, execution, and dry-run side-effect
    boundaries.
-   Removed the legacy `GeneratorContext` lifecycle from
    `BaseGenerator`.
-   Simplified the canonical Generator execution lifecycle to:
    `run() → validate_request() → plan() → execute() → GenerationResult`.
-   Removed `GeneratorContext` from the public Generator SDK exports.

### Added

-   Added ADR 0008: Generator Execution Contract.
-   Added execution contract architecture documentation describing
    lifecycle ownership, immutable planning, and dry-run semantics.
-   Added shared execution contract tests covering lifecycle ordering,
    validation and planning failure boundaries, execution exception
    propagation, immutable `GenerationPlan` handoff, and dry-run
    behavior.

### Migration

-   Use `BaseGenerator.run(GenerateRequest)` as the canonical execution
    entry point.
-   Implement generator customization through `validate_request()`,
    `plan()`, and `execute()` rather than overriding lifecycle
    orchestration.
-   Do not implement or depend on the removed legacy lifecycle hooks.
-   Do not use `GeneratorContext` as part of the Generator execution
    API.

### Verification

-   Verified execution contract tests.
-   Verified all Generator tests (165 passed).
-   Verified repository test suite, Ruff, pre-commit, and
    `git diff --check`.

### Verification

-   Verified all 32 cross-generator validation contract cases.
-   Verified the complete suite: 332 tests passed with 80.79% coverage.
-   Verified all pre-commit hooks and `git diff --check` before
    documenting the completed validation contract.
-   Run the focused `GenerationResult` and all core Generator tests.
-   Run the cross-generator result contract tests.
-   Run the CLI integration tests for Bootstrap, Course, Week, and
    dry-run output.
-   Run the complete test suite to satisfy the repository coverage
    threshold.
-   Run all pre-commit hooks before committing the refactor.

## Step 12 - 2026-07-26

### Added

-   `UpgradeManifest`
-   `PatchEntry`
-   `UpgradePlan`
-   `UpgradeResult`
-   `UpgradeManager`
-   `opl upgrade` 子命令
-   Preview-only default mode
-   Add/modify/delete operations
-   SHA256 payload validation
-   Optional source SHA256 conflict protection
-   Safe relative path validation
-   Automatic backup
-   Automatic rollback on failure
-   Upgrade report
-   Core and CLI integration tests
-   Upgrade system documentation
-   Upgrade Manifest schema documentation
-   Example upgrade patch
-   Code Review Checklist

## Pre-commit repair - 2026-07-26

### Fixed

-   Corrected mixed tab/space indentation in `GeneratorContext`.
-   Reworked optional `BaseGenerator` lifecycle hooks to satisfy Ruff
    `B027`.
-   Added explicit lifecycle type annotations and documentation.
-   Normalized UTF-8/LF text files and removed trailing whitespace.
-   Added a transitional Ruff docstring policy for legacy public APIs.
-   Verified 210 tests with 78.79% coverage.
