# Marketplace

OpenProjectLab's Marketplace layer defines deterministic contracts for versioned artifact metadata, acquisition, integrity verification, and installation. It is intentionally narrower than a hosted public marketplace service.

## Domain scope

The Marketplace domain includes `ArtifactIdentity`, `ArtifactVersion`, `ArtifactCoordinate`, `ArtifactType`, `CompatibilityRequirement`, `DistributionMetadata`, `IntegrityMetadata`, and `MarketplaceArtifact`.

Exact coordinates identify exact versioned artifacts, supporting deterministic lookup and tests.

## Pipeline boundaries

Keep these stages distinct:

```text
metadata lookup
→ acquire exact payload bytes
→ verify integrity
→ install validated payload
```

Metadata lookup does not imply acquisition; acquisition does not imply verification; verification does not imply installation or activation.

## Acquisition

`ArtifactAcquirer.acquire(MarketplaceArtifact) -> bytes` returns payload bytes. The baseline in-memory acquirer performs no integrity verification, installation, activation, plugin registration, Generator execution, filesystem mutation, or network access.

## Integrity

The current verifier supports deterministic SHA-256 digest checking against `IntegrityMetadata`. A mismatch raises an integrity error; an unsupported algorithm raises a distinct error.

Digest integrity proves that bytes match the declared digest. It does **not** establish publisher identity, provenance, trust, or authenticity.

## Installation

`ArtifactInstaller` installs an artifact payload and returns `ArtifactInstallationResult`. The current in-memory implementation records bytes/metadata, reports `installed`, and rejects duplicate installation of the same exact coordinate.

Installation is intentionally separate from activation:

```text
artifact installed ≠ artifact activated
```

The installer does not access a package manager or network, discover Entry Points, register plugins, execute Generators, or write Courseware output.

## Plugins

Marketplace and Plugin SDK cover different stages:

```text
Marketplace → metadata / bytes / integrity / installation
Plugin SDK  → Entry Point discovery / validation / registry
```

A plugin artifact being installed therefore does not mean its Generator is registered.

## Public API boundary

Marketplace models are intentionally not part of `generator.sdk` merely because the modules exist. Their long-term public compatibility is a separate release decision.

## What v1.0 does not promise

The current Marketplace domain does not establish a public remote marketplace, browsing/search UI, publisher accounts, ratings/reviews, payments, automatic dependency resolution, package-manager installation, plugin activation, Generator execution, publisher-signature trust infrastructure, or baseline network acquisition.

### Checklist

- Resolve an exact versioned artifact.
- Keep metadata lookup and payload acquisition separate.
- Treat acquired bytes as unverified until integrity checking succeeds.
- Do not confuse SHA-256 integrity with publisher authenticity.
- Install only the payload you intended to verify.
- Do not assume installation activates plugins or executes Generators.
- Do not assume baseline Marketplace components use the network.
- Treat hosted marketplace features as outside v1.0 unless explicitly documented.

## Next step

Continue with [Troubleshooting](troubleshooting.md).
