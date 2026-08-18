# Quick Start: Your First 15 Minutes with OpenProjectLab

This Quick Start gives you one small, representative installed-user workflow.

The goal is to verify the full path:

```text
installed OPL
    ↓
working CLI
    ↓
package-owned runtime templates
    ↓
Course Generator
    ↓
generated README.md
```

This workflow deliberately avoids editable installation, `PYTHONPATH`, and
repository-only templates.

## Before You Begin

Complete [Installation](installation.md) first.

You should have:

- an active Python environment containing the installed `openprojectlab`
  distribution;
- the `opl` command available;
- a writable working directory.

The examples below use:

```text
opl-quick-start/
```

as a temporary working location.

## 1. Create a Clean Working Directory

### Windows PowerShell

```powershell
New-Item -ItemType Directory -Force opl-quick-start | Out-Null
Set-Location opl-quick-start
```

### POSIX shells

```bash
mkdir -p opl-quick-start
cd opl-quick-start
```

You do not need an OpenProjectLab source checkout in this directory.

## 2. Verify the CLI

Run:

```console
opl --help
```

You should see the OpenProjectLab command-line help.

Next, inspect the built-in Generators:

```console
opl list
```

The current built-in identities are:

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

The command prints descriptions beside these names.

## 3. Preview a Course Generation with Dry Run

Use an explicit output root:

```console
opl --output-root ./output course demo-course --name "Demo Course" --weeks 4 --language en --dry-run
```

This request means:

- `./output` is the generation output root;
- `course` selects the Course Generator;
- `demo-course` is the project slug;
- `--name "Demo Course"` supplies the course name;
- `--weeks 4` supplies the course length metadata;
- `--language en` supplies the authored language value;
- `--dry-run` requests validation/planning without normal persisted output.

After the dry run, the normal generated course README should not have been
persisted at:

```text
output/demo-course/README.md
```

## 4. Generate the Course

Run the same request without `--dry-run`:

```console
opl --output-root ./output course demo-course --name "Demo Course" --weeks 4 --language en
```

The Course Generator targets:

```text
output/demo-course/
```

and generates the representative artifact:

```text
output/demo-course/README.md
```

By default, generation also participates in the existing manifest behavior
unless `--no-manifest` is supplied.

## 5. Inspect the Generated Artifact

### Windows PowerShell

```powershell
Get-Content .\output\demo-course\README.md
```

### POSIX shells

```bash
cat ./output/demo-course/README.md
```

You should see a rendered course README derived from the installed
package-owned Course template and the values supplied in the CLI request.

The exact authored Markdown belongs to the template contract and may evolve
within the applicable compatibility rules. The key Quick Start guarantee is
that the installed Course Generator resolves its packaged template and produces
the expected artifact path.

## 6. Inspect the Generated Tree

### Windows PowerShell

```powershell
Get-ChildItem .\output\demo-course -Recurse
```

### POSIX shells

```bash
find ./output/demo-course -maxdepth 3 -type f -print
```

At minimum, the representative Course artifact should include:

```text
output/
└── demo-course/
    └── README.md
```

OPL-owned manifest metadata may also be present because manifest recording is
enabled by default for this command.

## 7. Optional: Generate Without Manifest Recording

If you intentionally do not want the command to update the generation
manifest, use:

```console
opl --output-root ./output course no-manifest-course --name "No Manifest Course" --weeks 4 --language en --no-manifest
```

This changes manifest behavior; it does not change the Course Generator
identity or canonical lifecycle.

## 8. Optional: Test Overwrite Protection

Run the same normal generation command again:

```console
opl --output-root ./output course demo-course --name "Demo Course" --weeks 4 --language en
```

Because the target artifact already exists, the established write policy may
reject the operation instead of silently replacing user content.

If you intentionally want overwrite behavior, the CLI provides `--force`:

```console
opl --output-root ./output course demo-course --name "Demo Course" --weeks 4 --language en --force
```

Use overwrite deliberately. Do not make `--force` the default habit for
user-authored content.

## 9. What You Just Verified

This small workflow verifies several important v1.0 concepts:

```text
installed console entry point
        ↓
opl list
        ↓
global output-root resolution
        ↓
Course Generator request
        ↓
validation and planning
        ↓
package-owned template resolution
        ↓
filesystem write
        ↓
README.md artifact
```

It also demonstrates that the normal onboarding path does not require:

```text
source checkout
editable install
PYTHONPATH
repository-level templates
```

## 10. Common Problems

### `opl` is not found

Confirm that the environment where you installed OPL is active.

You can also check:

```console
python -m pip show openprojectlab
```

If the package is installed in a different environment, activate that
environment and retry.

### `python -c "import generator"` fails

Verify the installed package:

```console
python -m pip show openprojectlab
```

Then confirm that the Python executable and `pip` belong to the same
environment:

```console
python -c "import sys; print(sys.executable)"
python -m pip --version
```

### The output directory is not writable

Choose another explicit output root that your user account can write:

```console
opl --output-root <writable-directory> course demo-course --name "Demo Course"
```

### The target file already exists

Use another project slug, remove or relocate the existing output after
reviewing it, or intentionally use `--force` when overwrite is appropriate.

## 11. Clean Up the Tutorial Output

When you no longer need the Quick Start files, remove the `opl-quick-start`
working directory using your normal filesystem tools.

Do not automate deletion of unrelated paths.

## 12. Next Steps

After completing the First 15 Minutes workflow, continue with:

- [Configuration](configuration.md)
- [CLI](cli.md)
- [Generators](generators.md)
- [Courseware](courseware.md)

If you plan to extend OPL, continue later with [Plugins](plugins.md).

## Automation Note

The v1.0 documentation contract requires this representative onboarding path to
become an executable documentation smoke test. The prose in this chapter is
therefore intentionally written around commands and artifact expectations that
can be verified deterministically in CI.
