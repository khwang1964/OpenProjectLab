# Installing OpenProjectLab

This chapter describes the normal installed-user path for OpenProjectLab (OPL).

The v1.0 documentation is being prepared during release stabilization. The
current project metadata identifies the package as `openprojectlab` and requires
Python 3.12 or later. During the current stabilization baseline, the package
version is `0.6.0`; the final v1.0 release process will establish the final
v1.0 artifact/version relationship.

This chapter intentionally does not claim that a v1.0 package has already been
published to a public package index.

## 1. Requirements

The package metadata currently requires:

```text
Python >= 3.12
```

Runtime Python dependencies are:

```text
Jinja2 >= 3.1
PyYAML >= 6.0
```

The console entry point installed by the package is:

```text
opl
```

Environment support claims are owned by the later v1.0 Support Matrix work.
The Python metadata above describes package requirements; it should not be read
as a broader operating-system support guarantee.

## 2. Recommended: Use an Isolated Virtual Environment

Create a virtual environment with a suitable Python interpreter.

### Windows PowerShell

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

If Python 3.14 is not the interpreter you intend to use, select another
installed Python version that satisfies the package requirement.

### POSIX shells

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
```

## 3. Install a Built Wheel

Step 8.4 verifies OPL through the artifact users actually install.

Given a locally available wheel:

```text
<distribution-directory>/openprojectlab-<version>-py3-none-any.whl
```

install it with:

```console
python -m pip install <wheel-path>
```

For example, the Step 8.4 stabilization artifact was:

```text
openprojectlab-0.6.0-py3-none-any.whl
```

so a local verification command may look like:

```console
python -m pip install ./dist/openprojectlab-0.6.0-py3-none-any.whl
```

The exact path depends on where you obtained the artifact.

Do not treat that stabilization filename as a promise about the final v1.0
version number.

## 4. Verify the Installation

First verify that the Python package imports:

```console
python -c "import generator; print(generator.__file__)"
```

The reported path should resolve to the installed environment, not to an
OpenProjectLab source checkout.

Then verify the CLI:

```console
opl --help
```

and list the installed built-in Generators:

```console
opl list
```

The current built-in list includes:

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

Descriptions may appear beside the Generator identities.

## 5. Verify Package-Owned Runtime Resources

Normal installed use should not depend on a repository-level `templates/`
directory.

Built-in runtime templates are packaged through the `generator.resources`
boundary.

You normally do not need to inspect this path directly. The user-facing
verification is to run a built-in Generator successfully outside the source
repository.

The [Quick Start](quick-start.md) performs that representative verification.

## 6. Choosing an Output Directory

For installed-user workflows, specify an output root explicitly.

For example:

```console
opl --output-root ./opl-output list
```

`list` does not generate output, but the example demonstrates the location of
the global option.

For generation commands, use a writable location owned by you:

```console
opl --output-root ./opl-output course demo-course --name "Demo Course"
```

Using an explicit output root is preferable for onboarding because it avoids
depending on implementation-derived default paths.

## 7. Template Root Override

Built-in Generators normally use package-owned templates.

If you intentionally need a different template tree, the CLI exposes:

```text
--template-root DIR
```

For example:

```console
opl --template-root ./custom-templates --output-root ./opl-output course demo-course --name "Demo Course"
```

A custom template root is an advanced override. It changes the templates used
by the Generator and therefore can change output content.

For the normal v1.0 onboarding path, use the package-owned templates.

## 8. Configuration File Override

The CLI exposes:

```text
--config FILE
```

A user-supplied configuration file can provide path-related configuration.

If the built-in default configuration file is not present in an installed
environment, the CLI continues without loading that default file. Explicitly
supplied configuration files, however, are loaded and validated.

The dedicated [Configuration](configuration.md) chapter will document the
verified configuration surface in detail.

## 9. Do Not Use Editable Installation as the Normal User Path

This command is useful for development:

```console
python -m pip install -e .
```

but it is **not** the primary v1.0 user-installation workflow.

Editable installation can accidentally make repository files available and
therefore hide packaging defects.

The v1.0 release-readiness path verifies:

```text
build artifact
    ↓
install wheel in a clean environment
    ↓
import installed package
    ↓
resolve package resources
    ↓
run installed opl command
    ↓
generate representative artifact
```

## 10. Developer Installation

If you are contributing to OPL itself, a development installation may be
appropriate. That workflow belongs to contributor/development documentation,
not the normal installed-user Quick Start.

The project defines development extras containing tools such as `build`,
`pytest`, `pytest-cov`, `ruff`, `pre-commit`, `mypy`, and `twine`.

Do not infer user requirements from development-only dependencies.

## 11. Installation Verification Checklist

After installation, verify:

```text
[ ] Python environment satisfies the package requirement.
[ ] openprojectlab wheel installs successfully.
[ ] import generator succeeds outside the repository.
[ ] opl --help succeeds.
[ ] opl list succeeds.
[ ] a writable output directory is available.
[ ] the Quick Start representative generation succeeds.
```

## 12. What This Chapter Does Not Promise

This chapter does not define:

- the final v1.0 publication location;
- the final v1.0 release filename;
- operating-system support guarantees;
- long-term compatibility/deprecation policy;
- release signing policy;
- upgrade guarantees between future versions.

Those items belong to later Milestone 8 release-readiness gates.

## Next Step

Continue with [Quick Start](quick-start.md).
