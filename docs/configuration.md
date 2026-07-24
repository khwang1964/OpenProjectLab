# Configuration

OpenProjectLab uses a YAML configuration file to control project generation,
template locations, generators, and plugins.

---

# Configuration File

By default, OpenProjectLab loads

```text
config/default.yaml
```

A different configuration file may be specified from the command line.

Example:

```bash
opl --config myproject.yaml list
```

---

# File Format

Configuration files must be valid YAML documents.

The root node **must** be a mapping.

Example:

```yaml
project:
  name: Demo

paths:
  templates: templates

generator: {}

plugins: {}
```

Invalid example:

```yaml
- project
- paths
```

This will produce a `ConfigurationError`.

---

# Top-Level Sections

The following top-level sections are currently supported.

| Section | Description | Required |
|----------|-------------|----------|
| `project` | Project information | No |
| `paths` | File and directory locations | No |
| `generator` | Generator options | No |
| `plugins` | Plugin configuration | No |

Missing sections are treated as empty mappings.

For example,

```yaml
project:
  name: Demo
```

is equivalent to

```yaml
project:
  name: Demo

paths: {}

generator: {}

plugins: {}
```

---

# Section Validation

Every top-level section must be a YAML mapping.

Correct:

```yaml
project:
  name: OpenProjectLab
```

Incorrect:

```yaml
project:
  - OpenProjectLab
```

Incorrect:

```yaml
project: 123
```

Incorrect:

```yaml
project: hello
```

If a section is not a mapping,
OpenProjectLab raises

```text
ConfigurationError
```

---

# paths

The `paths` section defines important project directories.

Example:

```yaml
paths:
  templates: templates
```

---

## paths.templates

Specifies the root directory containing all templates.

### Relative Path

```yaml
paths:
  templates: templates
```

Resolved as

```text
<project_root>/templates
```

Example

```text
F:\OpenProjectLab
└── templates
```

---

### Absolute Path

```yaml
paths:
  templates: D:/Shared/Templates
```

or

```yaml
paths:
  templates: F:\Company\Templates
```

The configured path is used directly.

---

### Default Value

If omitted,

```yaml
paths: {}
```

or

```yaml
paths:
```

then

```text
templates
```

is used automatically.

Equivalent to

```yaml
paths:
  templates: templates
```

---

# project

Currently reserved for project metadata.

Example:

```yaml
project:
  name: Demo
  version: 1.0
```

Future releases may support additional metadata.

---

# generator

Reserved for generator-specific options.

Example:

```yaml
generator:
  overwrite: false
```

---

# plugins

Reserved for plugin configuration.

Example:

```yaml
plugins:
  java: {}
  python: {}
```

---

# Error Handling

The following situations raise `ConfigurationError`.

| Condition | Example |
|-----------|---------|
| File not found | Missing configuration file |
| Invalid YAML | YAML syntax error |
| Root node is not a mapping | Root is a list |
| Invalid section type | `project: []` |

---

# Best Practices

Recommended directory layout:

```text
OpenProjectLab/
│
├── config/
│   └── default.yaml
│
├── templates/
│
├── docs/
│
└── generator/
```

Use relative paths whenever possible to improve project portability.

---

# API Reference

Current `ProjectConfig` public interface:

```python
ProjectConfig.load(path: Path) -> ProjectConfig

ProjectConfig.template_root(project_root: Path) -> Path
```

---

# Version History

## v0.5

- Added YAML configuration loading
- Added configuration validation
- Added section validation
- Added template root resolution