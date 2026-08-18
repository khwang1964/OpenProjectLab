# Troubleshooting

This chapter provides a systematic troubleshooting path for the documented OpenProjectLab (OPL) v1.0 installed-user workflows. Start by identifying the failing boundary instead of immediately changing files or using `--force`.

## 1. Establish the Environment

Confirm that you are using the intended Python environment:

```console
python --version
python -c "import generator; print(generator.__file__)"
opl --help
opl list
```

The package metadata currently requires Python 3.12 or later. For an installed-user verification, `generator.__file__` should resolve inside the installed environment rather than an OpenProjectLab source checkout.

If `opl` is not found but `python -c "import generator"` succeeds, verify that the environment's scripts directory is on `PATH` and that the same environment was used to install the wheel.

## 2. `opl` Is Not Found

Check the active environment and package installation:

```console
python -m pip show openprojectlab
python -m pip --version
```

If the package is missing, install the intended wheel into the active environment.

Avoid using editable installation as evidence that a release artifact works. Editable installs can expose repository files and hide packaging defects.

## 3. `opl list` Does Not Show the Expected Built-ins

The documented built-in Generator identities are:

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

If the list differs, first confirm which OPL installation is being executed. Do not assume that an unrelated plugin or a different environment changes the built-in contract.

## 4. Configuration Errors

The CLI accepts the global options:

```text
--config FILE
--template-root DIR
--output-root DIR
```

If an explicitly supplied configuration file is missing or invalid, configuration loading fails. Check the path, YAML syntax, and the documented configuration structure.

For path problems, prefer an explicit `--output-root` or `--template-root` while diagnosing the issue.

## 5. Template Errors

Built-in installed-user workflows normally use package-owned runtime templates.

If generation reports a template loading, validation, or rendering problem:

1. Confirm that you are testing an installed wheel rather than relying on a repository `templates/` directory.
2. Remove a custom `--template-root` override unless it is intentionally under test.
3. Re-run a representative command with package-owned templates.
4. If a custom template root is required, confirm that its directory structure and expected template files match the Generator contract.

A custom template tree can change generated content and is therefore an advanced override.

## 6. Generator Validation Errors

Generation commands validate required arguments and structured content before writing.

Typical causes include:

- missing required command options;
- non-positive week/count values;
- malformed JSON input for assignment, quiz, slides, or website commands;
- structured content that violates the Generator contract;
- an existing output file when overwrite is not allowed.

Use `--dry-run` where available to validate and inspect planned output without modifying files.

Do not use `--force` as the first troubleshooting step. First determine why the existing target conflicts with the requested generation.

## 7. Output Is Written to an Unexpected Location

For onboarding and reproducible automation, specify an output root explicitly:

```console
opl --output-root ./opl-output course demo-course --name "Demo Course"
```

Remember that global options appear before the subcommand.

If configuration also supplies output paths, an explicit CLI override is the clearest diagnostic tool.

## 8. Structured JSON Files Fail to Load

`assignment`, `quiz`, `slides`, and `website` accept structured JSON files.

Check that:

- the file exists;
- it is UTF-8 JSON;
- the top-level shape matches the command's documented contract;
- required fields are present;
- values use the expected types.

A syntactically valid JSON document can still fail Generator validation.

## 9. Existing Files and `--force`

The shared write options are:

```text
--dry-run
--force
--no-manifest
```

`--force` permits overwrite behavior where supported; it is not a repair operation.

Before using it, inspect the existing output and confirm that replacement is intentional. If the existing files contain user edits, preserve or version-control them first.

## 10. Manifest Questions

By default, generation may update `.opl/manifest.yaml` according to the Generator lifecycle.

`--no-manifest` disables that recording for the command. Use it intentionally; do not disable the manifest merely to hide a manifest-related discrepancy.

If generated files and manifest state appear inconsistent, reproduce the operation with a clean output directory before editing manifest data manually.

## 11. Plugin Loading Problems

For a third-party Generator plugin, verify:

1. The plugin distribution is installed in the same Python environment as OPL.
2. It declares an Entry Point in `openprojectlab.generators`.
3. The Entry Point name equals the Generator's public `name`.
4. The exported object satisfies the Plugin SDK Generator contract.
5. Its name does not collide with an existing registry entry.

Installation alone does not mean a plugin has been discovered, validated, and registered.

## 12. AI Integration Problems

The documented v1.0 CLI does not expose a general `opl ai` command.

For programmatic AI integration, separate failures into:

```text
provider invocation
AIResponse production
response structure validation
domain mapping
downstream generation
```

Successful provider output is not automatically valid OPL courseware. Provider credentials and vendor-specific settings belong to the selected adapter/deployment boundary unless an explicit OPL contract says otherwise.

## 13. Marketplace Problems

Keep Marketplace stages separate:

```text
metadata lookup
→ acquisition
→ integrity verification
→ installation
→ optional later activation/integration
```

A SHA-256 mismatch means the acquired bytes do not match declared integrity metadata. Successful installation does not automatically activate a plugin or execute a Generator.

The baseline in-memory Marketplace components are deterministic and no-network; do not diagnose them as if they were a hosted marketplace service.

## 14. Upgrade Problems

Always inspect an upgrade package before applying it:

```console
opl upgrade <package.zip>
```

Inspection does not modify project files. A plan with conflicts returns a conflict status and should be reviewed before any apply operation.

Common upgrade failures include:

- missing or invalid ZIP package;
- invalid `upgrade-manifest.yaml`;
- unsupported manifest schema;
- unsafe paths;
- missing payload files;
- SHA-256 mismatch;
- add/modify/delete conflicts with the current project state.

See [Upgrading](upgrading.md) before using `--apply` or `--allow-conflicts`.

## 15. Clean Reproduction

When a problem is unclear, create a minimal clean reproduction:

```text
fresh virtual environment
→ install the intended wheel
→ work outside the source repository
→ use package-owned templates
→ use an explicit output root
→ run opl list
→ run the smallest failing command
```

This separates packaging/runtime defects from repository-local state.

## 16. Information to Capture for a Bug Report

Capture:

```text
OPL package version/artifact
Python version
operating system
installation method
exact command
exit status
complete error message
whether the test is inside or outside the source repository
whether --config / --template-root / --output-root are used
minimal input files needed to reproduce
```

Do not include API keys, credentials, private course material, or other secrets.

## Troubleshooting Checklist

- Confirm the active Python environment.
- Confirm the installed OPL package and `opl` executable.
- Reproduce outside the source checkout when testing packaging.
- Use an explicit output root.
- Prefer `--dry-run` before destructive changes.
- Diagnose validation before using `--force`.
- Keep plugin installation separate from registration.
- Keep Marketplace installation separate from activation.
- Inspect upgrade packages before applying them.
- Preserve the exact error and minimal reproduction.

## Next Step

Continue with [Upgrading](upgrading.md).
