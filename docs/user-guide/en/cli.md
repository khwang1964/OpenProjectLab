# Command-Line Interface

The `opl` command is the installed command-line entry point for OpenProjectLab.

This chapter documents the current v1.0 release-readiness CLI surface. Use
`opl --help` and `opl <command> --help` as the executable source of truth for
the installed version.

## 1. Command Shape

The general form is:

```text
opl [global options] <command> [command options]
```

Current global options:

```text
--config FILE
--template-root DIR
--output-root DIR
```

Example:

```console
opl --output-root ./output course demo-course --name "Demo Course"
```

Global options belong before the subcommand.

## 2. Available Commands

The current CLI defines:

```text
list
bootstrap
course
week
lab
assignment
quiz
slides
website
upgrade
```

`list` reports built-in Generator identities. `upgrade` is a CLI operation but
is not a Generator identity.

A legacy hidden `--list` compatibility path also exists. New documentation and
automation should use:

```console
opl list
```

## 3. `list`

List the built-in Generators:

```console
opl list
```

Current identities:

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

This command is useful as a lightweight installation verification.

## 4. Shared Write Options

Generation commands expose these shared write options:

```text
--dry-run
--force
--no-manifest
```

### `--dry-run`

Validate and plan the operation without performing the normal persisted
generation.

### `--force`

Allow overwrite behavior where the Generator/filesystem contract permits it.

### `--no-manifest`

Do not update `.opl/manifest.yaml` for the generation request.

These options apply to the built-in generation commands described below.

## 5. `bootstrap`

Create a complete course-project skeleton.

Required input:

```text
project_slug
--name NAME
```

Optional input:

```text
--language LANGUAGE
--license LICENSE
--copyright-year YEAR
--copyright-holder HOLDER
--dry-run
--force
--no-manifest
```

Defaults include:

```text
--language zh-TW
--license "CC BY 4.0"
```

Example:

```console
opl --output-root ./output bootstrap modern-java --name "Modern Java"
```

## 6. `course`

Generate the course README.

Required input:

```text
project_slug
--name NAME
```

Optional input:

```text
--language LANGUAGE
--weeks N
--textbook TEXT
--instructor TEXT
--description TEXT
--license LICENSE
--dry-run
--force
--no-manifest
```

Defaults include:

```text
--language zh-TW
--weeks 16
--license "CC BY 4.0"
```

`--weeks` must be an integer greater than zero.

Example:

```console
opl --output-root ./output course demo-course --name "Demo Course" --weeks 4 --language en
```

## 7. `week`

Generate a weekly courseware README.

Required input:

```text
project_slug
--week N
--title TITLE
```

Optional input:

```text
--course-name NAME
--language LANGUAGE
--textbook-chapter TEXT
--directory-pattern PATTERN
--dry-run
--force
--no-manifest
```

Defaults include:

```text
--language zh-TW
--directory-pattern "week-{week:02d}"
```

`--week` must be greater than zero.

Example:

```console
opl --output-root ./output week demo-course --week 1 --title "Introduction"
```

## 8. `lab`

Generate a weekly Lab README.

Required input:

```text
project_slug
--week N
--lab-id ID
--title TITLE
```

Optional input:

```text
--course-name NAME
--dry-run
--force
--no-manifest
```

Example:

```console
opl --output-root ./output lab demo-course --week 1 --lab-id hello-lab --title "Hello Lab"
```

## 9. `assignment`

Generate a weekly Assignment README from structured JSON content.

Required input:

```text
project_slug
--week N
--assignment-id ID
--title TITLE
--content-file FILE
```

Optional input:

```text
--course-name NAME
--dry-run
--force
--no-manifest
```

The content file is loaded as UTF-8 JSON and must have a JSON object at its
root.

Example command shape:

```console
opl --output-root ./output assignment demo-course --week 1 --assignment-id assignment-01 --title "Assignment 01" --content-file ./assignment.json
```

The exact domain schema of the structured content is documented with the
Assignment Generator contract rather than invented here.

## 10. `quiz`

Generate a weekly Quiz README from a structured questions JSON file.

Required input:

```text
project_slug
--week N
--quiz-id ID
--title TITLE
--questions-file FILE
```

Optional input:

```text
--course-name NAME
--dry-run
--force
--no-manifest
```

Example command shape:

```console
opl --output-root ./output quiz demo-course --week 1 --quiz-id quiz-01 --title "Quiz 01" --questions-file ./questions.json
```

The file is parsed as UTF-8 JSON. Generator validation determines whether the
loaded question structure satisfies the Quiz contract.

## 11. `slides`

Generate Markdown slides from structured JSON content.

Required input:

```text
project_slug
--title TITLE
--slides-file FILE
```

Optional input:

```text
--course-name NAME
--dry-run
--force
--no-manifest
```

Example command shape:

```console
opl --output-root ./output slides demo-course --title "Week 01 Slides" --slides-file ./slides.json
```

## 12. `website`

Generate a static course website from structured pages JSON.

Required input:

```text
project_slug
--title TITLE
--pages-file FILE
```

Optional input:

```text
--course-name NAME
--dry-run
--force
--no-manifest
```

Example command shape:

```console
opl --output-root ./output website demo-course --title "Demo Course" --pages-file ./pages.json
```

## 13. `upgrade`

The CLI also registers an `upgrade` command.

Upgrade behavior has its own contract and should be used according to the
installed command help and the [Upgrading](upgrading.md) chapter.

Inspect the installed surface with:

```console
opl upgrade --help
```

This chapter does not invent upgrade options that are not established by the
upgrade command itself.

## 14. Exit Codes

The CLI returns:

```text
0
```

for successful command execution.

Handled OPL/configuration/value/JSON/file errors are reported to standard error
and return:

```text
2
```

Scripts should check the process exit status instead of parsing localized human
error messages.

## 15. JSON Input Files

`assignment`, `quiz`, `slides`, and `website` accept structured UTF-8 JSON
files.

The CLI is responsible for loading the JSON. The corresponding Generator
contract is responsible for validating the loaded structure.

Malformed JSON, missing files, or invalid values result in a non-zero CLI
outcome.

## 16. Installed-User Examples

Verify the installation:

```console
opl --help
opl list
```

Preview generation:

```console
opl --output-root ./output course demo-course --name "Demo Course" --dry-run
```

Generate:

```console
opl --output-root ./output course demo-course --name "Demo Course"
```

These examples intentionally use an explicit output root and package-owned
templates.

## 17. CLI Automation Guidance

For scripts and CI:

- use explicit global path options;
- use exit codes as the primary success/failure signal;
- use `--dry-run` before writes when appropriate;
- do not depend on hidden `--list`;
- do not depend on localized human-readable output;
- do not require the repository checkout for installed-user workflows;
- treat JSON input files as versioned inputs to the corresponding Generator
  contract.

## 18. Marketplace Commands

The additive `marketplace` family provides exactly `versions`, `inspect`,
`verify`, and `install`. It uses explicit local `--catalog` and
`--payload-root` inputs, supports deterministic `--json` success output, and
supports installation preview through `--dry-run`.

It does not add `opl marketplace list`, remote access, automatic activation,
or persistent package installation. See [Marketplace CLI](marketplace.md) for
the complete command shapes, catalog example, safety rules, and failure
boundaries.

## Next Step

Continue with [Generators](generators.md) for the generation model behind these
commands.

## 19. AI CLI

The production `ai` command family exposes exactly four governed subcommands:

```text
opl ai course
opl ai review
opl ai document
opl ai template
```

The **Stable** execution path is deterministic `local-response` execution. It
does not require a network connection, credential, paid account, provider SDK,
or provider client.

The **Experimental** provider path is explicit, injection-only, and fail-closed.
Provider execution requires explicit provider selection together with an
injected client factory. The AI CLI does not perform automatic SDK import,
does not perform automatic credential lookup, does not perform implicit provider selection,
and does not perform network fallback.

Validation and failure handling preserve the established CLI boundary. A
handled AI CLI failure uses exit code 2, writes its diagnostic to stderr, and
produces no success output on stdout.

AI CLI behavior is non-mutating with respect to the filesystem and repository.
The `course`, `review`, `document`, and `template` handlers return projected
content/results but do not write generated AI output into the project,
repository, manifests, registries, or Marketplace state.

This documentation does not mark the broader implementation or release as
accepted:

```text
AI CLI Implementation Acceptance --- Not Accepted
Formal v1.1 Acceptance --- Not Accepted
```

<!-- v1.3.10-stable-release-evidence-cli-en -->
## 20. Release Evidence CLI

The stable read-only family exposes exactly:

```text
opl release-evidence verify --request FILE --format json|text
opl release-evidence request validate --request FILE --format json|text
```

`request validate` is offline and never executes Git, GitHub, tests, or a runtime.
`verify` uses only the accepted read-only command allowlist. Exit `0` means valid
success output, exit `1` means a complete verification report has findings, and exit
`2` means accepted output could not be produced. Success uses stdout; diagnostics use
stderr. There is no stdin, output file, discovery, repair, retry, polling, or mutation.
