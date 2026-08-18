# Upgrading

OpenProjectLab provides an explicit upgrade-package mechanism for previewing and applying controlled project changes. This command updates project content from an OPL upgrade ZIP; it is not a replacement for upgrading the installed `openprojectlab` Python distribution with `pip`.

## 1. Two Different Kinds of Upgrade

Keep these operations separate:

```text
Python package upgrade
→ changes the installed OPL software

opl upgrade <package.zip>
→ inspects/applies an OPL project upgrade package
```

To change the installed Python distribution, use the package installation/release procedure appropriate to the artifact you obtained.

This chapter documents the second operation.

## 2. Safe Default: Inspect First

The `upgrade` command requires a ZIP package:

```console
opl upgrade <package.zip>
```

Without `--apply`, OPL only inspects the package and project state. It prints:

```text
package/version
number of added paths
number of modified paths
number of deleted paths
number of unchanged paths
conflicts, if any
```

It then reports that no files have been changed.

This preview-first behavior is the normal workflow.

## 3. Exit Status During Inspection

Inspection returns success when the plan has no conflicts.

If the plan contains conflicts, the CLI reports them and returns a conflict status rather than modifying the project.

Use the conflict list to decide whether the current project matches the upgrade package's assumptions.

## 4. Applying an Upgrade

After reviewing a clean plan:

```console
opl upgrade <package.zip> --apply
```

The upgrade manager verifies the package again, creates a backup, and applies the declared operations.

On success it reports the package/version, number of changed paths, and backup directory.

## 5. Upgrade Package Structure

The ZIP contains:

```text
upgrade-manifest.yaml
payload/
```

The manifest schema currently requires:

```text
schema_version: "1.0"
package: <non-empty string>
version: <non-empty string>
description: <string>
entries: <non-empty list>
```

Each entry declares:

```text
path
operation
sha256            # required for add/modify
source_sha256     # optional current-state guard
```

Supported operations are:

```text
add
modify
delete
```

Duplicate manifest paths are rejected.

## 6. Path Safety

Manifest paths must be safe relative POSIX-style paths.

OPL rejects paths that are absolute, contain `..` or `.` path components, use backslashes, are empty, or use Windows reserved device names.

Extracted ZIP member paths are validated before extraction, and final target paths are checked to remain inside the project root.

These checks reduce path-traversal and unsafe-target risk.

## 7. Payload Integrity

Every `add` or `modify` entry requires a 64-character SHA-256 digest.

Before planning or applying changes, OPL verifies that the corresponding file exists under `payload/` and matches the declared digest.

A missing payload or digest mismatch fails the upgrade.

## 8. Conflict Detection

The plan checks the current project state.

### `add`

Conflict if the target already exists.

### `modify`

Conflict if the target does not exist.

If `source_sha256` is provided, the current target must match that digest. A mismatch is a conflict.

If the current file already equals the new payload digest, it is classified as unchanged.

### `delete`

A missing target is unchanged.

If `source_sha256` is provided, an existing target must match it before deletion; otherwise the plan records a conflict.

## 9. `--allow-conflicts`

The CLI exposes:

```text
--allow-conflicts
```

This option is only relevant when applying:

```console
opl upgrade <package.zip> --apply --allow-conflicts
```

It permits application even when the inspection plan contains add/modify/delete state conflicts.

Use it only after understanding each conflict. It does not disable manifest validation, path safety, or payload integrity checks.

Because conflicts indicate that the project differs from the package's expected source state, version-control or external backups are strongly recommended before overriding them.

## 10. Backups

Before changing an existing path, OPL copies its previous state into a timestamped backup directory.

By default backups are created under:

```text
.opl/backups/
```

The successful result reports the exact backup directory.

An `upgrade-report.yaml` is also written there, recording the package/version and the plan's added, modified, deleted, unchanged, and conflict lists.

Do not delete the backup until the upgraded project has been validated.

## 11. Rollback on Apply Failure

The upgrade manager maintains an operation journal while applying changes.

If an exception occurs during application, it attempts to restore previously existing paths from the backup and remove paths created during the failed operation.

This rollback applies to the upgrade manager's controlled apply operation. Do not generalize it to Generator execution or Courseware composition, which have different failure semantics.

## 12. Project Root

The CLI upgrade handler uses the current working directory as the project root unless calling code supplies another project root.

Therefore run the command from the project you intend to inspect or update:

```console
cd <project-root>
opl upgrade <path-to-package.zip>
```

Confirm the current directory before using `--apply`.

## 13. Recommended Workflow

```text
1. Commit or back up current project work.
2. Change to the intended project root.
3. Run opl upgrade <package.zip>.
4. Review add/modify/delete/unchanged/conflict counts.
5. Resolve unexpected conflicts.
6. Run normal project tests/checks before deciding to override conflicts.
7. Apply with --apply only after review.
8. Validate the upgraded project.
9. Keep the reported .opl/backups directory until validation is complete.
10. Commit the resulting project changes separately.
```

## 14. What `opl upgrade` Does Not Do

The command does not automatically:

- download an upgrade package from the network;
- upgrade the installed Python package;
- resolve Marketplace dependencies;
- activate plugins;
- execute Generators;
- merge arbitrary user edits;
- treat `--allow-conflicts` as a guarantee that the resulting project is semantically correct.

## 15. Recovery Guidance

If apply reports failure, preserve the error and inspect the backup directory before attempting another apply.

If you use version control, also inspect:

```console
git status
git diff
```

Do not repeatedly apply the same package with `--allow-conflicts` until the project state is understood.

## Upgrade Checklist

- Back up or commit current work.
- Confirm the intended project root.
- Inspect before applying.
- Review every conflict.
- Verify package integrity errors instead of bypassing them.
- Use `--allow-conflicts` only intentionally.
- Validate the project after apply.
- Retain `.opl/backups` until validation succeeds.
- Keep project upgrade separate from Python package upgrade.

## Next Step

Return to [README](README.md) or consult [Troubleshooting](troubleshooting.md) if an upgrade fails.
