# Changelog

## Unreleased

### Added

- Added ADR 0010 through ADR 0012 to define the Plugin SDK public contract,
  Plugin validation contract, and Python Entry Point contract.
- Added the `generator.sdk` public façade required by third-party-style
  Generator implementations.
- Added dedicated `tests/sdk/` public export and Plugin Generator contract tests.
- Added `generator.plugins` discovery, validation, registry, loader, and
  Entry Point runtime boundaries.
- Added `openprojectlab.generators` as the canonical third-party Generator
  Entry Point group.
- Added Plugin validation for concrete `BaseGenerator` subclasses, public
  naming, and zero-argument construction.
- Added transactional Entry Point loading with validate-all / preflight-all /
  register-all semantics.
- Added Plugin Registry membership query coverage and Entry Point integration
  contract tests.
- Added architecture tests protecting the removal of the legacy PluginManager
  runtime path.
- Added `docs/plugin-authoring.md` as the third-party Plugin development and
  packaging guide.

### Changed

- Standardized third-party Plugin dependencies on `generator.sdk` rather than
  internal `generator.core`, `generator.generators`, or `generator.plugins`
  namespaces.
- Standardized Plugin public names on `^[a-z][a-z0-9-]*$`.
- Required Python Entry Point metadata names to match the loaded Generator's
  public `name`.
- Changed Plugin loading to complete discovery/loading/validation/identity
  checks and registration preflight before mutating the Registry.
- Clarified Registry membership checks through an explicit `contains()` query
  rather than exception-driven `get()` control flow.
- Aligned Plugin SDK architecture, contract inventory, roadmap, history, and
  authoring documentation with the canonical Entry Point runtime.

### Removed

- Removed the legacy `generator.core.plugin.PluginManager`.
- Removed the legacy internal `PluginDescriptor` path together with the
  superseded PluginManager implementation.
- Removed the duplicate legacy Plugin runtime path after canonical Entry Point
  integration and architecture tests were established.

### Migration

- Third-party Plugin implementations should import lifecycle contracts only
  from `generator.sdk`.
- Declare Generator plugins under:
  `[project.entry-points."openprojectlab.generators"]`.
- Map one Entry Point to one concrete `BaseGenerator` subclass.
- Keep Entry Point metadata names identical to `generator.name`.
- Ensure Plugin Generator classes support zero-argument construction.
- Do not depend on the removed `generator.core.plugin.PluginManager`.

### Verification

- Verified Public SDK export and SDK-only Generator contract tests.
- Verified Plugin validation, Registry, loading, and Entry Point contract tests.
- Verified transactional Entry Point integration and no-partial-registration
  behavior.
- Verified legacy PluginManager removal architecture tests.
- Verified the complete repository test suite and coverage gate.
- Verified Ruff, pre-commit, GitHub Actions, and `git diff --check`.

---

### Milestone 3 Generator Framework

- Added ADR 0005 through ADR 0009 to define the shared Generator input,
  validation, planning, execution, and legacy lifecycle removal contracts.
- Added parameterized cross-generator contract tests for `GenerateRequest`,
  `GeneratorValidationError`, `GenerationPlan`, `GenerationResult`, dry-run,
  Manifest state, lifecycle ordering, and failure boundaries.
- Standardized Generator input validation on `GeneratorValidationError`.
- Established `BaseGenerator.run(GenerateRequest)` as the framework-controlled
  canonical execution entry point.
- Removed legacy `GeneratorContext` lifecycle hooks and Generator-specific
  result compatibility types.

## Step 12 - 2026-07-26

### Added

- `UpgradeManifest`
- `PatchEntry`
- `UpgradePlan`
- `UpgradeResult`
- `UpgradeManager`
- `opl upgrade` subcommand
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
