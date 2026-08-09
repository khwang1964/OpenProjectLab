# Changelog

## Unreleased

### Added

- Added ADR 0005 through ADR 0009 to define the shared Generator input,
  validation, planning, execution, and legacy lifecycle removal contracts.
- Added parameterized cross-generator contract tests for `GenerateRequest`,
  `GeneratorValidationError`, `GenerationPlan`, `GenerationResult`, dry-run,
  Manifest state, lifecycle ordering, and failure boundaries.
- Added Legacy Generator Lifecycle Removal Contract Tests.
- Added built-in Generator lifecycle contract tests enforcing `BaseGenerator`
  inheritance and framework ownership of `run()`.
- Added Generator architecture, reference, migration, and Code Review Checklist
  documentation for the completed Milestone 3 framework contracts.

### Changed

- Standardized Generator input validation on `GeneratorValidationError`, with
  stable `generator`, `field`, and `message` attributes.
- Migrated `BootstrapGenerator`, `CourseGenerator`, and `WeekGenerator` to the
  shared `GenerateRequest`, `RuntimeOptions`, `GenerationPlan`, and
  `GenerationResult` contracts.
- Migrated `BootstrapGenerator`, `CourseGenerator`, and `WeekGenerator` to
  inherit the shared `BaseGenerator` canonical lifecycle.
- Removed built-in `run()` overrides so lifecycle ownership remains with
  `BaseGenerator.run()`.
- Changed built-in `generate(request)` methods to compatibility wrappers
  delegating to the canonical `run(request)` entry point.
- Made built-in execution consume the `GenerationPlan` produced by
  `plan(request)` instead of bypassing the planning lifecycle.
- Established `BaseGenerator.run(GenerateRequest)` as the framework-controlled
  canonical execution entry point.
- Fixed the canonical execution order as:
  `validate_request() → plan() → execute() → GenerationResult`.
- Documented validation, planning, execution, dry-run, and side-effect
  boundaries.
- Decoupled the CLI from Generator-specific result types and standardized output
  formatting around `GenerationResult.affected_paths`.
- Removed the temporary `BootstrapResult`, `CourseResult`, and `WeekResult`
  compatibility layers.

### Removed

- Removed the legacy `GeneratorContext` lifecycle hooks from `BaseGenerator`:
  `validate()`, `prepare()`, `generate()`, `post_generate()`, and `cleanup()`.
- Removed `GeneratorContext` from the public Generator SDK exports.
- Removed Generator-specific result compatibility types after downstream
  migration completed.

### Migration

- Catch `GeneratorValidationError` instead of depending on validation-specific
  `ValueError` behavior.
- Inspect structured `generator` and `field` attributes rather than parsing
  validation message text.
- Use `BaseGenerator.run(GenerateRequest)` as the canonical execution entry
  point.
- Implement Generator behavior through `validate_request()`, `plan()`, and
  `execute()`.
- Do not implement or depend on the removed legacy lifecycle hooks.
- Do not use `GeneratorContext` as part of the public Generator execution API.
- Replace `generated_files` and `output_path` reads with
  `GenerationResult.affected_paths`.
- Stop importing `BootstrapResult`, `CourseResult`, and `WeekResult`.

### Verification

- Verified the complete Generator test suite.
- Verified Legacy Lifecycle Removal Contract Tests without `xfail`.
- Verified Generator Validation, Planning, Execution, and Result Contract Tests.
- Verified CLI integration tests for Bootstrap, Course, Week, validation
  failures, and dry-run behavior.
- Verified the complete repository test suite and coverage gate.
- Verified Ruff, pre-commit, GitHub Actions, and `git diff --check`.

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
