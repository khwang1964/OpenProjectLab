# Configuration

OpenProjectLab (OPL) exposes a small YAML configuration model and three global
CLI path overrides. This chapter documents the configuration behavior that is
implemented by the current v1.0 release-readiness baseline.

The configuration file is not a second command language. Generator-specific
inputs still belong to their CLI commands or programmatic requests.

## 1. Configuration Model

`ProjectConfig` recognizes four top-level YAML sections:

```yaml
project: {}
paths: {}
generator: {}
plugins: {}
```

Each section must be a YAML mapping when present. A missing section, or a
section explicitly set to `null`, is treated as an empty mapping.

The loader rejects:

- a missing explicitly requested configuration file;
- malformed YAML;
- a non-mapping YAML document root;
- a recognized section whose value is not a mapping.

Unknown top-level keys are not part of the documented configuration contract.

## 2. Example Configuration

The repository's development default currently has this shape:

```yaml
project:
  name: OpenProjectLab
  version: 0.6.0
  locale: zh-TW

paths:
  templates: templates
  courses: courses
  docs: docs

generator:
  overwrite: false
  dry_run: false

plugins:
  enabled: true
```

This example shows the accepted section structure. Do not assume that every
value shown above is consumed by every CLI command.

For the current CLI root resolution, the `paths` section is the relevant
configuration surface.

## 3. Selecting a Configuration File

The global option is:

```text
--config FILE
```

Example:

```console
opl --config ./opl.yaml list
```

An explicitly supplied configuration file must exist and contain valid YAML.

The CLI also has a built-in development default path. In an installed
distribution that repository-oriented default file may not exist; when the
missing path is exactly the built-in default, the CLI continues without loading
it. This allows normal installed use to rely on package-owned templates and an
explicit output root instead of a source checkout.

## 4. Template Root Resolution

The CLI resolves the template root in this precedence order:

```text
--template-root
    ↓
paths.template_root
    ↓
paths.templates
    ↓
package-owned default template root
```

The global override is:

```text
--template-root DIR
```

Example:

```console
opl --template-root ./custom-templates course demo-course --name "Demo Course"
```

For normal installed-user workflows, omit this option and use the package-owned
runtime templates.

A custom template root is an advanced override. OPL does not promise that an
arbitrary external template tree is compatible with every built-in Generator.

## 5. Output Root Resolution

The CLI resolves the output root in this precedence order:

```text
--output-root
    ↓
paths.course_root
    ↓
paths.courses
    ↓
paths.output_root
    ↓
built-in default output root
```

The global override is:

```text
--output-root DIR
```

Example:

```console
opl --output-root ./output course demo-course --name "Demo Course"
```

For reproducible user documentation and automation, prefer an explicit
`--output-root`.

## 6. Relative Path Behavior

Path values are expanded and resolved by the CLI.

The current CLI treats a relative configured or command-line root as relative
to its internal project-root resolution boundary, not necessarily to the
shell's current working directory.

For that reason, automation that requires an exact filesystem location should
prefer an absolute path. The First 15 Minutes smoke test does this
programmatically when executing the installed artifact.

Do not build scripts that depend on undocumented assumptions about the
repository checkout location.

## 7. Project Section

The loader accepts a `project` mapping.

For example:

```yaml
project:
  name: Example Courseware Project
  locale: en
```

The generic configuration loader preserves this mapping, but the current CLI
does not automatically translate arbitrary `project` values into every
Generator's command arguments.

If a Generator command requires `--name`, `--week`, `--title`, or another
explicit argument, provide that argument unless the command documentation says
otherwise.

## 8. Generator Section

The loader accepts a `generator` mapping.

For example:

```yaml
generator:
  overwrite: false
  dry_run: false
```

The current CLI write behavior is controlled by command options:

```text
--dry-run
--force
--no-manifest
```

Do not assume that arbitrary values in the generic `generator` mapping override
those CLI options unless that behavior is explicitly documented and tested.

## 9. Plugins Section

The loader accepts a `plugins` mapping.

For example:

```yaml
plugins:
  enabled: true
```

Plugin discovery, validation, loading, and registration have their own public
contracts. The presence of a configuration key does not by itself define a
complete plugin-management interface.

See [Plugins](plugins.md) for the user-facing plugin model.

## 10. Configuration Errors

Configuration failures are reported when OPL cannot safely interpret an
explicit configuration file.

Typical causes include:

```text
file does not exist
invalid YAML
document root is not a mapping
project is not a mapping
paths is not a mapping
generator is not a mapping
plugins is not a mapping
```

When troubleshooting, first reduce the file to the smallest valid mapping:

```yaml
paths: {}
```

Then add only the settings required by your workflow.

## 11. Recommended Installed-User Configuration

For a simple installed-user workflow, configuration can remain minimal.

Example:

```yaml
paths:
  courses: C:/Users/example/opl-output
```

Or avoid a persistent configuration file and specify the output root directly:

```console
opl --output-root <output-directory> course demo-course --name "Demo Course"
```

The latter is especially useful in CI and tutorials because the path is visible
in the command itself.

## 12. Configuration Checklist

Before relying on a configuration file, verify:

```text
[ ] The file is UTF-8 YAML.
[ ] The YAML root is a mapping.
[ ] project, paths, generator, and plugins are mappings when present.
[ ] Path overrides point to locations you intend to use.
[ ] Automation uses explicit or absolute paths when location matters.
[ ] Generator-specific required CLI arguments are still supplied.
[ ] Custom template roots are intentional.
```

## Next Step

Continue with [CLI](cli.md) for the complete command-line surface.
