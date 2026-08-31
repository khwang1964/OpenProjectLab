---
name: opl-acceptance-closure
description: Complete an OpenProjectLab terminal-alignment post-merge verification and separate implementation-acceptance closure directly from the current repository. Use after an OPL implementation or terminal-alignment PR merges, when the user says next step, acceptance closure, post-merge verification, or asks to avoid uploading a context ZIP.
---

# OPL Acceptance Closure

Complete the strict second-PR acceptance closure without exporting repository
context. Work directly from the current OPL checkout and preserve the explicit
merge-authorization gate.

## Required workflow

1. Read `references/closure-workflow.md` before generating or applying a closure.
2. Run `scripts/collect_acceptance_evidence.ps1` with the merged alignment PR number
   and its actual focused test paths.
3. Read the current implementation/alignment records, governance marker blocks, and
   their contract tests from the repository. Never infer their exact wording from a
   previous release.
4. Generate the closure record and tests from current semantic states and exact HTML
   markers. Validate the generated changes before commit.
5. Run focused tests, pre-commit, and the required regression. Repair deterministic
   formatting failures, rerun affected checks, and restage.
6. Use authenticated HTTPS for Git network operations through the existing `gh auth`
   session. Do not depend on an SSH passphrase prompt.
7. Create or reuse the separate closure PR, monitor required CI, write merge-gate
   evidence, and stop. Merge only after the user explicitly says `merge`.

Do not create a context ZIP. Do not ask the user to paste evidence already available
from Git, GitHub CLI, the repository, or the collector output.
