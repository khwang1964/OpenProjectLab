# Opt-in Read-only Verification CLI Preview

> v1.3.7 Design First baseline — Proposed / Pending design review

## Context

v1.3.5 defines explicit invocation and v1.3.6 defines deterministic request and
report interchange. The final delivery-train capability is a narrow opt-in CLI
preview that exposes those accepted contracts without adding mutation authority.

## Command contract

Define one experimental command:

`opl release-evidence verify --request <path> --format json|text`

- `--request` is required and identifies one caller-selected UTF-8 JSON document.
- `--format` is explicit and accepts only `json` or `text`.
- Successful output is written only to standard output.
- Diagnostics are written only to standard error.
- No output file, repository discovery, interactive prompt, or implicit default.

## Execution lifecycle

1. parse the exact command and options
2. read one bounded request document
3. decode it using the v1.3.6 strict request contract
4. invoke the v1.3.5 service exactly once
5. render the report using the requested v1.3.6 format
6. return one stable exit status

Exit status `0` means the report is valid and accepted. Exit status `1` means a
complete verification report contains fail-closed findings. Exit status `2` means
command, request, configuration, or runtime execution could not produce a complete
report. Output and exit status must agree.

## Safety boundary

The preview can execute only the v1.3.4 accepted read commands. It cannot execute
tests or arbitrary commands and cannot commit, push, merge, tag, release, publish,
modify repository content, write reports, or prompt for credentials.

## Deferred

- production implementation and stable CLI status
- public SDK, HTTP, RPC, plugin, or marketplace exposure
- stdin requests, output files, globbing, batch, queue, watch, or interactive mode
- retry, polling, cache, persistence, telemetry, scheduling, or credential handling
- mutation, test execution, release, publication, and automatic evidence discovery

## Code Review Checklist

- [ ] The command is explicit, experimental, and opt-in.
- [ ] Request path and output format are mandatory and strictly validated.
- [ ] Exactly one bounded request document is decoded.
- [ ] Exactly one read-only invocation occurs.
- [ ] JSON and text output reuse v1.3.6 without modification.
- [ ] Exit statuses are stable, exhaustive, and agree with output.
- [ ] Standard output and standard error remain separated.
- [ ] No test execution, mutation, output file, prompt, or discovery is possible.
