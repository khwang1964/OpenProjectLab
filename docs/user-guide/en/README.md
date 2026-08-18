# OpenProjectLab v1.0 User Manual

> **Language:** English
> **Audience:** OpenProjectLab users, educators, courseware authors, and extension users
> **Status:** v1.0 documentation baseline

OpenProjectLab (OPL) is a project engineering and content-generation platform
built around explicit contracts, deterministic generation, package-owned
runtime resources, extension boundaries, and automated verification.

This manual explains the user-facing v1.0 surface. It is intentionally focused
on behavior that is implemented, tested, and part of the current v1.0
release-readiness work. It does not promote proposed or deferred capabilities
into Stable v1.0 guarantees.

## Start Here

If you are new to OPL, read these chapters first:

1. [Concepts](concepts.md) — understand the OPL mental model.
2. [Installation](installation.md) — install and verify an OPL artifact.
3. [Quick Start](quick-start.md) — complete a representative first workflow.
4. [CLI](cli.md) — learn the command-line surface in detail.

## Manual Contents

- [Concepts](concepts.md)
- [Installation](installation.md)
- [Quick Start](quick-start.md)
- [Configuration](configuration.md)
- [CLI](cli.md)
- [Generators](generators.md)
- [Courseware](courseware.md)
- [Plugins](plugins.md)
- [AI Integration](ai-integration.md)
- [Marketplace](marketplace.md)
- [Troubleshooting](troubleshooting.md)
- [Upgrading](upgrading.md)

The Traditional Chinese (Taiwan) manual is maintained in parallel under
`docs/user-guide/zh-TW/`.

## What This Manual Covers

The v1.0 manual covers the verified user-facing boundaries of OPL:

- the `opl` command-line interface;
- built-in Generators;
- deterministic generation behavior;
- package-owned runtime templates;
- Course and Week courseware concepts;
- courseware composition;
- the Plugin SDK and canonical Generator Entry Point boundary;
- provider-independent AI integration concepts;
- Marketplace artifact and installation concepts;
- troubleshooting and upgrading guidance.

Some capabilities are intentionally outside the scope of this manual until
their own release-readiness gates are accepted. In particular, this manual does
not define future compatibility/deprecation policy, environment support claims,
or release-publication semantics ahead of Milestone 8 Steps 8.6–8.8.

## Core User Workflow

At a high level, OPL follows this model:

```text
user intent / CLI input
        ↓
Generator request
        ↓
validation
        ↓
generation plan
        ↓
execution
        ↓
generated artifacts
        ↓
GenerationResult
```

The framework owns this lifecycle so that built-in and extension Generators can
share predictable behavior.

## Built-in Generator Families

The current CLI exposes these built-in Generator identities:

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

Use:

```console
opl list
```

to inspect the installed command surface.

## Installed-User Principle

The v1.0 documentation assumes normal use from an installed distribution.

The primary user workflow must not require:

- an editable installation;
- `PYTHONPATH`;
- repository-only templates;
- untracked local files;
- running from the OpenProjectLab source checkout.

Development workflows may use a source checkout, but they are separate from the
normal user path documented here.

## Documentation Conventions

Commands appear in fenced blocks such as:

```console
opl list
```

Placeholder values use angle brackets when they are not literal input:

```text
<output-directory>
<wheel-path>
```

Canonical identifiers such as command names, option names, Python modules,
Entry Point names, configuration keys, and artifact paths are shown exactly as
the product expects them.

## Documentation Accuracy

This manual is governed by the v1.0 documentation contract. When a statement in
the manual conflicts with an accepted v1.0 contract or verified production
behavior, the manual must be corrected.

Documentation is part of release readiness: instructions that users are
expected to execute should be tested where practical.

## Next Step

Continue with [Concepts](concepts.md), then follow
[Installation](installation.md) and [Quick Start](quick-start.md).
