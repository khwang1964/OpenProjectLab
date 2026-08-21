# Marketplace CLI

OpenProjectLab provides a deterministic, local-only Marketplace CLI for
inspecting versioned artifacts, verifying exact payload bytes, and performing a
process-local, non-activating installation.

## Command inventory

The exact production command family is:

```text
opl marketplace versions IDENTITY --catalog FILE [--json]
opl marketplace inspect COORDINATE --catalog FILE [--json]
opl marketplace verify COORDINATE --catalog FILE --payload-root DIR [--json]
opl marketplace install COORDINATE --catalog FILE --payload-root DIR [--dry-run] [--json]
```

`IDENTITY` is `namespace/name`. `COORDINATE` is
`namespace/name@MAJOR.MINOR.PATCH`.

There is no `opl marketplace list` command. Use `versions` for one exact
identity.

## Local catalog

Every command requires one explicit UTF-8 JSON catalog. A minimal catalog is:

```json
{
  "schema_version": 1,
  "artifacts": [
    {
      "schema_version": 1,
      "identity": {
        "namespace": "community",
        "name": "demo"
      },
      "version": "1.2.3",
      "artifact_type": "template",
      "description": "Local demo artifact",
      "compatibility": ">=1.0,<2.0",
      "distribution": {
        "kind": "file",
        "reference": "packages/demo.opl"
      },
      "integrity": {
        "algorithm": "sha256",
        "digest": "<64 lowercase hexadecimal characters>"
      }
    }
  ]
}
```

Catalog parsing fails closed on malformed UTF-8 JSON, unsupported schema
versions, wrong field types, unknown fields, invalid identities or coordinates,
and duplicate exact coordinates.

## Payload root and safety

`verify` and `install` require `--payload-root DIR`. The artifact
`distribution.reference` is resolved below this root.

The CLI rejects absolute paths, drive-prefixed paths, parent traversal, missing
files, directories, escaping symlinks, unsupported distribution kinds, and any
network fallback. Lookup, containment, acquisition, and SHA-256 verification
complete before installation.

## Examples

List deterministic semantic versions:

```powershell
python -m generator.cli.main marketplace versions community/demo `
  --catalog .\examples\marketplace\catalog.json
```

Inspect one exact artifact as JSON:

```powershell
python -m generator.cli.main marketplace inspect community/demo@1.2.3 `
  --catalog .\examples\marketplace\catalog.json `
  --json
```

Verify local payload bytes without installation:

```powershell
python -m generator.cli.main marketplace verify community/demo@1.2.3 `
  --catalog .\examples\marketplace\catalog.json `
  --payload-root .\examples\marketplace\payloads `
  --json
```

Preview installation without calling the installer:

```powershell
python -m generator.cli.main marketplace install community/demo@1.2.3 `
  --catalog .\examples\marketplace\catalog.json `
  --payload-root .\examples\marketplace\payloads `
  --dry-run `
  --json
```

Perform process-local installation:

```powershell
python -m generator.cli.main marketplace install community/demo@1.2.3 `
  --catalog .\examples\marketplace\catalog.json `
  --payload-root .\examples\marketplace\payloads
```

## Output and failures

Human-readable success output is written to stdout. With `--json`, success
emits exactly one compact UTF-8 JSON object with `schema_version: 1`.
Diagnostics are written to stderr.

The broad exit contract is:

- `0`: successful Marketplace operation;
- `2`: usage error or handled catalog, lookup, payload, integrity,
  installation, or filesystem failure.

A handled failure emits no success JSON document and leaves installer state
unchanged when failure occurs before installation.

## Installation is not activation

Marketplace installation is process-local, non-persistent, and non-activating:

```text
artifact installed != artifact activated
```

It does not register plugins, execute Generators, write Courseware output, or
modify a package manager environment.

## Deferred capabilities

The current CLI does not provide remote Marketplace access, implicit network
fallback, global browsing/search, dependency resolution, lockfiles, caches,
publisher signing or trust, ratings/reviews, payments, automatic activation,
plugin execution, or AI CLI behavior.

## Checklist

- Use an exact identity or coordinate.
- Supply an explicit local catalog.
- Supply an explicit payload root for `verify` and `install`.
- Use `--dry-run` to verify installation inputs without installer effects.
- Use `--json` for deterministic machine-readable success output.
- Treat SHA-256 integrity as byte matching, not publisher authenticity.
- Do not assume installation activates or persists an artifact.

## Next step

Continue with [Troubleshooting](troubleshooting.md).
