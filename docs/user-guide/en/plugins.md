# Plugins

OpenProjectLab supports third-party Generator extensions through its Plugin SDK and Python Entry Points. Plugins participate in the same Generator lifecycle as built-in Generators.

## Architecture

```text
installed Python distribution
→ Entry Point discovery
→ load candidate
→ validate Generator contract
→ validate identity
→ preflight collisions
→ GeneratorRegistry
```

The canonical Entry Point group is:

```text
openprojectlab.generators
```

Plugin authors should depend on the public Plugin SDK rather than private implementation modules.

## Packaging and discovery

A distribution advertises a Generator with packaging metadata such as:

```toml
[project.entry-points."openprojectlab.generators"]
hello = "example_plugin:HelloGenerator"
```

Discovery uses installed Python distribution metadata; an arbitrary source directory is not an installed plugin.

## Loading and validation

OPL loads the Entry Point object and validates it against the shared Plugin SDK Generator contract. Successful Python import alone does not make an object a valid plugin.

The Entry Point metadata name must equal the Generator's public runtime `name`:

```text
EntryPoint.name == Generator.name
```

A mismatch is rejected.

## Atomic batch registration

For a batch, OPL loads and validates all candidates and preflights registration before mutating the registry. It rejects duplicate names inside the batch and names already present in the target registry. A later failure therefore does not leave earlier batch members partially registered.

`GeneratorRegistry` remains the shared lookup boundary used by plugin loading and courseware orchestration.

## Lifecycle

```text
package plugin
→ install distribution
→ discover Entry Point
→ load
→ validate
→ register
→ resolve through shared Generator framework
```

Installation and activation/registration are separate concepts.

## Marketplace relationship

Marketplace installation does **not** automatically discover or register plugin Entry Points:

```text
Marketplace artifact installed ≠ plugin activated
```

See [Marketplace](marketplace.md).

## Troubleshooting

If a plugin does not load, verify that it is installed in the same Python environment as OPL, declares `openprojectlab.generators`, exports a valid Plugin SDK Generator, uses an Entry Point name equal to `Generator.name`, and does not collide with an existing registry name.

### Plugin author checklist

- Depend on the public Plugin SDK.
- Implement the canonical Generator contract.
- Package an installable Python distribution.
- Declare `openprojectlab.generators`.
- Keep Entry Point name equal to `Generator.name`.
- Avoid private OPL dependencies.
- Test clean-environment installation and discovery.
- Test validation and collision failures.
- Do not assume Marketplace installation means activation.

## Next step

Continue with [AI Integration](ai-integration.md).
