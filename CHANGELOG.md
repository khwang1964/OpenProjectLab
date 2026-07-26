# Changelog

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
