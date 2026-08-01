# Changelog

## Unreleased

### Changed

- Completed the migration of `BootstrapGenerator`, `CourseGenerator`, and
  `WeekGenerator` to the shared `GenerationResult` contract.
- Standardized `generate()` and `run()` result semantics across all core generators.
- Preserved `BootstrapResult`, `CourseResult`, and `WeekResult` as temporary
  compatibility layers for generator-specific metadata.

### Added

- Added focused tests for `GenerationResult`.
- Added parameterized cross-generator contract tests for result type, immutable
  writes, affected-path ordering, dry-run behavior, run aliases, and Manifest state.
- Documented the Generator Framework contract and the recommended Milestone 3
  migration sequence.

### Verification

- Run the focused `GenerationResult` and all core Generator tests.
- Run the cross-generator result contract tests.
- Run the complete test suite to satisfy the repository coverage threshold.
- Run all pre-commit hooks before committing the refactor.

## Step 12 - 2026-07-26

### Added

- `UpgradeManifest`
- `PatchEntry`
- `UpgradePlan`
- `UpgradeResult`
- `UpgradeManager`
- `opl upgrade` 子命令
- Preview-only default mode
- Add/modify/delete operations
- SHA256 payload validation
- Optional source SHA256 conflict protection
- Safe relative path validation
- Automatic backup
- Automatic rollback on failure
- Upgrade report
- Core and CLI integration tests
- Upgrade system documentation
- Upgrade Manifest schema documentation
- Example upgrade patch
- Code Review Checklist

## Pre-commit repair - 2026-07-26

### Fixed

- Corrected mixed tab/space indentation in `GeneratorContext`.
- Reworked optional `BaseGenerator` lifecycle hooks to satisfy Ruff `B027`.
- Added explicit lifecycle type annotations and documentation.
- Normalized UTF-8/LF text files and removed trailing whitespace.
- Added a transitional Ruff docstring policy for legacy public APIs.
- Verified 210 tests with 78.79% coverage.
