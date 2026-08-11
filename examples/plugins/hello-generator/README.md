# OPL Hello Plugin

`opl-hello-plugin` is the minimal third-party Generator Plugin example for
OpenProjectLab.

It exists to demonstrate the Plugin SDK v1 authoring contract end to end:

```text
third-party distribution
    -> generator.sdk
    -> BaseGenerator subclass
    -> openprojectlab.generators
    -> Entry Point metadata
```

The example intentionally contains no filesystem, template, network, or
subprocess behavior. Its purpose is to validate the public SDK and packaging
boundary rather than demonstrate application-specific generation logic.

## Requirements

The package uses the same Python minimum as OpenProjectLab:

```text
Python >= 3.12
```

OpenProjectLab must be available in the environment because the Plugin imports
its public contracts from:

```python
from generator.sdk import ...
```

## Package Structure

```text
hello-generator/
├── pyproject.toml
├── README.md
├── src/
│   └── opl_hello_plugin/
│       ├── __init__.py
│       └── generator.py
└── tests/
    └── test_plugin.py
```

## Generator Contract

`HelloGenerator`:

* subclasses `BaseGenerator`;
* has the public name `hello-plugin`;
* supports zero-argument construction;
* implements `plan()`;
* implements `execute()`;
* returns `GenerationPlan` and `GenerationResult`;
* imports OpenProjectLab contracts only through `generator.sdk`.

## Entry Point

`pyproject.toml` declares:

```toml
[project.entry-points."openprojectlab.generators"]
hello-plugin = "opl_hello_plugin.generator:HelloGenerator"
```

The Entry Point name and runtime Generator name are intentionally identical:

```text
hello-plugin == HelloGenerator.name
```

## Install for Development

From this directory, with OpenProjectLab already installed in the active
environment:

```bash
python -m pip install -e .
```

## Run the Example Tests

```bash
python -m pytest -v
```

From the OpenProjectLab repository root, the host-side contract test is:

```bash
python -m pytest tests/plugins/test_example_third_party_plugin.py -v --no-cov
```

## Public API Rule

Third-party Plugin implementation code must not import:

```text
generator.core.*
generator.generators.*
generator.plugins.*
```

Those namespaces are host implementation details.

For the full authoring contract, see:

```text
docs/plugin-authoring.md
```
