# OpenProjectLab Maintainer Release Process

> **Audience:** OpenProjectLab maintainers\
> **Milestone:** 8 --- v1.0 Stabilization / Release Readiness\
> **Step:** 8.8.7 --- Maintainer Release Documentation\
> **Purpose:** Provide the executable, auditable maintainer runbook for
> preparing, verifying, drafting, publishing, and verifying an
> OpenProjectLab release.\
> **Governing design:**
> `docs/releases/v1.0-release-automation-reproducibility.md`

------------------------------------------------------------------------

## 1. Purpose

This runbook defines the maintainer-facing release procedure for
OpenProjectLab.

A release is not considered valid merely because a Git tag or GitHub
Release exists. The release identity is the coordinated set of:

``` text
canonical version
+ approved source commit SHA
+ release tag
+ wheel / sdist artifacts
+ artifact metadata
+ SHA-256 checksums
+ verification results
+ GitHub Release state
```

The process is designed around four principles:

1.  **Design First** --- release invariants are defined before
    publication.
2.  **Documentation First** --- the release procedure and evidence
    requirements are explicit.
3.  **Automation First** --- repeatable verification is encoded in
    repository-owned tests and workflows.
4.  **Fail Closed** --- identity, artifact, checksum, or verification
    conflicts stop publication.

------------------------------------------------------------------------

## 2. Scope and Boundaries

This runbook covers:

-   release preflight;
-   version / tag / commit-SHA verification;
-   clean artifact build;
-   wheel and source-distribution verification;
-   release contract tests;
-   wheel-backed installed-user verification;
-   checksum generation and verification;
-   release workflow dispatch;
-   draft GitHub Release inspection;
-   publication decision;
-   post-release verification;
-   abort and correction procedures;
-   evidence recording.

This runbook does **not** expand the v1.0 support matrix and does not
redefine compatibility or deprecation policy.

Step 8.8 currently treats GitHub Release publication as the publication
boundary described here. Package-index publication such as PyPI must not
be inferred from this procedure unless separately designed, reviewed,
automated, and accepted.

Semantic reproducibility is required. Byte-for-byte reproducibility is
**not** claimed unless separately demonstrated by automation and
evidence.

------------------------------------------------------------------------

## 3. Governing Sources

Before performing a release, maintainers should treat the following
repository documents as authoritative within their respective scopes:

``` text
docs/releases/v1.0-release-automation-reproducibility.md
docs/reference/support-matrix.md
docs/releases/v1.0-known-limitations.md
docs/releases/v1.0-compatibility-deprecation-policy.md
docs/roadmap.md
docs/HISTORY.md
CHANGELOG.md
```

The Step 8.8 governing document defines the release architecture and
invariants. This runbook translates those invariants into maintainer
actions.

If this runbook conflicts with an accepted governing contract, stop the
release and reconcile the documentation before publication.

------------------------------------------------------------------------

## 4. Required Release Inputs

The maintainer must know or resolve the following before publication:

  -----------------------------------------------------------------------
  Input                               Requirement
  ----------------------------------- -----------------------------------
  Canonical version                   Must resolve from the repository's
                                      canonical version source

  Approved release commit             Exact immutable Git commit SHA

  Expected release tag                Must be deterministically derived
                                      from the canonical version

  Release branch/source               Must contain the approved release
                                      state

  Wheel                               Must be built from the approved
                                      source state

  Source distribution                 Must be built from the same
                                      approved source state

  Checksums                           SHA-256 for the exact release
                                      artifacts

  Release notes                       Must describe the intended release

  Support/limitations docs            Must match the release's actual
                                      supported state

  GitHub permissions                  Maintainer must be authorized to
                                      dispatch/publish the release
  -----------------------------------------------------------------------

Do not proceed when any release input is ambiguous.

------------------------------------------------------------------------

## 5. Release Identity Contract

The release must preserve this relationship:

``` text
canonical version
        ==
tag-derived version

approved release SHA
        ==
tag target SHA

expected release tag
        ==
GitHub Release tag

verified artifact identity
        ==
canonical project/version

GitHub Release assets
        ==
verified release artifact set + checksum manifest
```

Any disagreement is a release blocker.

A maintainer must never silently move a public release tag to another
commit.

------------------------------------------------------------------------

## 6. Phase A --- Prepare

### 6.1 Synchronize `main`

Start from the approved repository state:

``` powershell
git switch main
git fetch origin --prune
git pull --ff-only
```

Verify synchronization:

``` powershell
git status
git rev-parse HEAD
git rev-parse main
git rev-parse origin/main
```

Expected state:

``` text
HEAD == main == origin/main
working tree clean
```

If the SHAs differ unexpectedly or the working tree is not clean, stop.

### 6.2 Verify repository state

Run:

``` powershell
git status --short
git log -5 --oneline
```

There must be no unreviewed local release changes.

Do not build a release from an accidental local modification.

### 6.3 Verify release documentation

Review at minimum:

``` text
CHANGELOG.md
docs/roadmap.md
docs/HISTORY.md
docs/reference/support-matrix.md
docs/releases/v1.0-known-limitations.md
docs/releases/v1.0-compatibility-deprecation-policy.md
docs/releases/v1.0-release-automation-reproducibility.md
```

Confirm that the release does not claim support beyond the tested
support matrix and that known limitations remain accurate.

### 6.4 Identify the approved release commit

Record:

``` powershell
git rev-parse HEAD
```

Treat this SHA as the candidate release source identity.

Do not substitute a later commit without restarting release
verification.

------------------------------------------------------------------------

## 7. Phase B --- Verify

### 7.1 Run repository quality gates

Before release publication, run the repository's normal quality gates:

``` powershell
git diff --check
ruff check .
ruff format --check .
pre-commit run --all-files
```

Any failure blocks the release.

### 7.2 Run release contract suites

Run:

``` powershell
python -m pytest tests\release -v --no-cov
```

The release contract suites should cover the implemented Step 8.8
release identity, artifact, workflow, GitHub Release consistency, and
reproducibility contracts.

A failure is a release blocker.

### 7.3 Clean previous build outputs

Stale artifacts must not enter the release set.

On PowerShell:

``` powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
```

Confirm:

``` powershell
Test-Path build
Test-Path dist
```

A new `dist` directory should be created only by the current build.

### 7.4 Build wheel and source distribution

Build from the approved source state:

``` powershell
python -m build
```

Inspect:

``` powershell
Get-ChildItem dist
```

The expected release set is one current wheel and one current source
distribution unless the accepted artifact contract explicitly says
otherwise.

Do not reuse artifacts from an earlier build.

### 7.5 Select the exact current wheel

The installed-user verification path must use the wheel built by this
release candidate.

Inspect:

``` powershell
Get-ChildItem dist\*.whl
```

There must be one unambiguous wheel matching the canonical
project/version identity.

If multiple current/stale wheels create ambiguity, clean `dist` and
rebuild.

### 7.6 Configure `OPL_TEST_WHEEL`

Resolve the current wheel:

``` powershell
$wheel = (Resolve-Path dist\*.whl).Path
$env:OPL_TEST_WHEEL = $wheel
$env:OPL_TEST_WHEEL
```

Verify:

``` powershell
Test-Path $env:OPL_TEST_WHEEL
```

`OPL_TEST_WHEEL` must point to the exact current release wheel, not an
older artifact.

### 7.7 Run wheel-backed packaging and onboarding verification

Run the installed-artifact suites with `OPL_TEST_WHEEL` set:

``` powershell
python -m pytest tests\packaging -v --no-cov
python -m pytest tests\documentation\test_first_15_minutes.py -v --no-cov
```

These tests must exercise the built artifact rather than substituting
the source checkout for installed-user behavior.

### 7.8 Run full regression

Run the full suite with the current release wheel available:

``` powershell
python -m pytest
```

The final Step 8.8 acceptance evidence must use fresh completion-state
results. Do not reuse earlier Milestone 8 regression numbers as the
final Step 8.8 result.

The configured coverage threshold must pass.

### 7.9 Re-run final static gates

After any test-driven correction:

``` powershell
git diff --check
ruff check .
ruff format --check .
pre-commit run --all-files
```

All must pass.

------------------------------------------------------------------------

## 8. Artifact Verification

Before publication, verify that:

-   the artifact set contains the expected wheel and source
    distribution;
-   filenames match the expected project/version;
-   wheel metadata matches the canonical project/version;
-   stale or duplicate release artifacts are absent;
-   the exact wheel used by installed-user verification belongs to this
    release;
-   artifacts came from the approved source state.

If artifact identity cannot be proven, stop.

------------------------------------------------------------------------

## 9. SHA-256 Checksums

Generate checksums for the exact release artifacts.

From PowerShell, one portable approach is:

``` powershell
Get-FileHash dist\*.whl -Algorithm SHA256
Get-FileHash dist\*.tar.gz -Algorithm SHA256
```

The automated release workflow is responsible for generating the release
checksum manifest used for publication.

The published checksum manifest must describe exactly the published
wheel and source distribution.

After artifact handoff, checksums must be re-verified before GitHub
Release creation.

Checksum mismatch is always a publication blocker.

------------------------------------------------------------------------

## 10. Semantic Reproducibility

Step 8.8 requires semantic reproducibility.

A clean rebuild must preserve the release's semantic identity,
including:

``` text
project identity
canonical version
artifact classes
wheel project metadata
wheel version metadata
```

Different artifact bytes or SHA-256 values do not, by themselves, prove
semantic non-reproducibility.

Therefore:

``` text
same semantic release identity
    required

same byte-for-byte artifact digest
    not required unless separately proven
```

Do not describe OpenProjectLab v1.0 artifacts as byte-for-byte
reproducible without dedicated evidence.

------------------------------------------------------------------------

## 11. Phase C --- Dispatch the Release Workflow

### 11.1 Preconditions

Do not dispatch the release workflow until:

-   release contract tests pass;
-   packaging tests pass;
-   wheel-backed First 15 Minutes tests pass;
-   full regression passes;
-   coverage gate passes;
-   Ruff / formatting / pre-commit pass;
-   release identity is known;
-   artifact and documentation review is complete;
-   the expected tag is known;
-   the release commit is approved.

### 11.2 Trigger policy

The release workflow must be maintainer-triggered.

It must not publish from:

``` text
pull_request
pull_request_target
```

The verification stage should remain read-only. Publication rights
belong only to the publication stage after verification succeeds.

### 11.3 Dispatch

Use the GitHub CLI to inspect available workflows:

``` powershell
gh workflow list
```

Dispatch the repository release workflow with the intended release tag:

``` powershell
gh workflow run release.yml -f tag=<EXPECTED_TAG>
```

Example shape only:

``` powershell
gh workflow run release.yml -f tag=v1.0.0
```

Use the actual canonical version-derived tag for the release.

### 11.4 Watch the workflow

Inspect recent runs:

``` powershell
gh run list --workflow release.yml --limit 5
```

Watch the selected run:

``` powershell
gh run watch <RUN_ID>
```

Inspect failures when necessary:

``` powershell
gh run view <RUN_ID> --log-failed
```

Do not bypass a failed verification job by manually publishing
equivalent-looking artifacts.

------------------------------------------------------------------------

## 12. Release Workflow Verification Boundary

The release workflow is expected to preserve this logical ordering:

``` text
checkout approved release source/tag
        ↓
resolve and verify release identity
        ↓
clean build outputs
        ↓
build wheel + sdist
        ↓
verify artifact metadata
        ↓
run release contract tests
        ↓
run wheel-backed installed-user verification
        ↓
generate + verify SHA-256 checksums
        ↓
upload verified release bundle
        ↓
publication job
        ↓
download exact verified bundle
        ↓
re-verify checksums
        ↓
create draft GitHub Release
```

Publication must depend on successful verification.

------------------------------------------------------------------------

## 13. Draft GitHub Release Verification

The release process is draft-first.

Before publishing the draft, verify all of the following:

### Identity

``` text
GitHub Release tag == expected release tag
tag target SHA == approved release SHA
release version == canonical version
```

### Assets

The draft must contain exactly the intended verified release assets,
including:

``` text
current wheel
current source distribution
SHA256SUMS.txt
```

There must be no stale artifact from another version/build.

### Classification

For a release candidate:

``` text
prerelease == true
```

For a general-availability release:

``` text
prerelease == false
```

### Draft boundary

The release must remain a draft until the maintainer has completed the
consistency review.

An already-published conflicting release must not be silently mutated by
automation.

------------------------------------------------------------------------

## 14. Publish Decision

Publish only when every required condition is true:

``` text
release identity consistent
AND
tag/commit binding correct
AND
artifact set correct
AND
artifact metadata correct
AND
checksums verified
AND
release tests passed
AND
packaging tests passed
AND
wheel-backed onboarding passed
AND
full regression passed
AND
coverage gate passed
AND
static/pre-commit gates passed
AND
draft GitHub Release reviewed
```

If any condition is uncertain, do not publish.

------------------------------------------------------------------------

## 15. Phase D --- Post-release Verification

Immediately after publication, verify the public state.

### 15.1 Verify repository tag

``` powershell
git fetch origin --tags --prune
git show <RELEASE_TAG> --no-patch
```

Confirm that the tag identifies the approved release commit.

### 15.2 Verify GitHub Release

Inspect the release:

``` powershell
gh release view <RELEASE_TAG>
```

Confirm:

-   tag;
-   title/version;
-   prerelease/GA classification;
-   expected assets;
-   checksum manifest;
-   publication state.

### 15.3 Verify downloadable assets

Download into a clean temporary directory:

``` powershell
New-Item -ItemType Directory -Force release-verification | Out-Null
gh release download <RELEASE_TAG> --dir release-verification
Get-ChildItem release-verification
```

Confirm that the downloaded asset set matches the reviewed release set.

### 15.4 Verify downloaded checksums

Use the checksum manifest to verify that downloaded artifact bytes agree
with the published checksums.

Any mismatch is a release incident and must be investigated immediately.

### 15.5 Optional/required installed-user smoke

Where the release acceptance procedure requires it, point
`OPL_TEST_WHEEL` at the downloaded release wheel and repeat the
clean-install / onboarding verification.

This provides evidence against accidental asset substitution between
verification and publication.

------------------------------------------------------------------------

## 16. Abort Conditions

Abort publication when any of the following occurs:

-   working tree/source state is not the approved state;
-   canonical version cannot be resolved;
-   expected tag cannot be derived;
-   tag/version disagree;
-   an existing tag points to a different commit;
-   artifact set is missing, stale, duplicated, or ambiguous;
-   wheel metadata disagrees with the expected project/version;
-   release tests fail;
-   packaging or installed-user verification fails;
-   full regression fails;
-   coverage falls below the configured threshold;
-   Ruff, formatting, `git diff --check`, or pre-commit fails;
-   checksum generation or verification fails;
-   GitHub Release state conflicts with expected identity;
-   release assets differ from the verified artifact set;
-   required release documentation is inconsistent;
-   the maintainer cannot establish the approved release SHA.

Fail closed. Do not publish first and repair evidence later.

------------------------------------------------------------------------

## 17. Correction Policy

### 17.1 Failure before tag creation

If verification fails before a tag exists:

``` text
abort
→ fix repository/workflow
→ review changes
→ rerun from clean state
```

No public correction is necessary.

### 17.2 Incorrect tag before public release

If a tag was created incorrectly but has **not** become part of a public
release:

1.  stop publication;
2.  verify whether correction is safe under the governing tag policy;
3.  document the correction;
4.  correct the unpublished state deliberately;
5.  restart verification from a clean state.

Do not silently conceal the correction.

### 17.3 Incorrect state after public release

If a materially incorrect release has already been published:

-   do not silently rewrite release history;
-   do not silently repoint the public tag;
-   preserve auditability;
-   document the issue;
-   use a corrective release/version when binary correction is required;
-   update release notes or Known Limitations for documentary
    corrections;
-   apply compatibility/deprecation policy to user-visible behavioral
    corrections.

When uncertain, stop and treat the situation as a release-governance
issue rather than improvising a destructive fix.

------------------------------------------------------------------------

## 18. RC versus GA Procedure

### Release Candidate

For an RC such as:

``` text
v1.0.0rc1
```

verify that:

-   canonical version includes the intended RC identifier;
-   expected tag includes the same RC identifier;
-   GitHub Release is marked prerelease;
-   artifacts contain the same canonical version;
-   RC evidence is not presented as GA acceptance.

### General Availability

For GA:

``` text
v1.0.0
```

verify that:

-   canonical version is the GA version;
-   GitHub Release is not marked prerelease;
-   support matrix and known limitations are final for the release;
-   Step 8.9 final release-readiness decision has been completed when
    required by the Milestone 8 plan.

RC success does not automatically imply GA approval.

------------------------------------------------------------------------

## 19. Evidence Recording

Every release candidate or accepted release should record enough
evidence to reconstruct what was released and why it was considered
valid.

Record at minimum:

``` text
canonical version
release tag
release commit SHA
tag target SHA
workflow run ID
wheel filename
sdist filename
SHA-256 checksums
release-suite result
packaging-suite result
wheel-backed onboarding result
full-regression result
coverage result
Ruff result
Ruff Format result
git diff --check result
pre-commit result
GitHub Release URL/identity
draft/publish outcome
post-release verification outcome
known exceptions, if any
```

Acceptance documentation must distinguish confirmed evidence from
assumptions.

Do not copy stale regression numbers from an earlier Step as if they
were fresh release evidence.

------------------------------------------------------------------------

## 20. Suggested Evidence Block

A maintainer may use the following structure in the relevant acceptance
record:

``` text
Release version:
Release tag:
Release SHA:
Tag target SHA:

Release contract suites:
Packaging suites:
Wheel-backed First 15 Minutes:
Full regression:
Coverage:
git diff --check:
Ruff:
Ruff Format:
pre-commit:

Wheel:
Source distribution:
SHA256SUMS:
Release workflow run:
GitHub Release:
Post-release verification:

Exceptions:
Final result:
```

------------------------------------------------------------------------

## 21. Troubleshooting

### `gh pr view --state merged` fails

`gh pr view` does not accept `--state`.

Use:

``` powershell
gh pr list --state merged --limit 10
```

or inspect a known PR directly:

``` powershell
gh pr view <PR_NUMBER>
```

### Release workflow remains pending

Inspect:

``` powershell
gh run list --workflow release.yml --limit 5
gh run view <RUN_ID>
```

For job-level state, inspect the run/jobs before assuming repository
code is at fault.

A GitHub Actions runner/service delay is not evidence that release
verification passed.

### `OPL_TEST_WHEEL` tests skip

Build the wheel first and set:

``` powershell
$env:OPL_TEST_WHEEL = (Resolve-Path dist\*.whl).Path
```

Then rerun the wheel-backed suites.

A skipped wheel-backed release test is not equivalent to a passed
installed-artifact verification.

### Multiple wheels exist in `dist`

Do not guess which one is current.

Clean:

``` powershell
Remove-Item -Recurse -Force build, dist -ErrorAction SilentlyContinue
python -m build
```

Then repeat artifact verification.

### Checksum mismatch

Stop publication.

Do not regenerate a checksum merely to make an unexplained artifact
mismatch disappear. Determine whether the artifact changed, the handoff
changed, or the wrong file was selected.

------------------------------------------------------------------------

## 22. Maintainer Release Checklist

### Prepare

-   [ ] `main` is synchronized with `origin/main`.
-   [ ] Working tree is clean.
-   [ ] Approved release commit SHA is recorded.
-   [ ] Canonical version is confirmed.
-   [ ] Expected release tag is confirmed.
-   [ ] CHANGELOG / roadmap / HISTORY are consistent.
-   [ ] Support matrix is accurate.
-   [ ] Known limitations are accurate.
-   [ ] Compatibility/deprecation policy remains satisfied.

### Verify

-   [ ] `git diff --check` passes.
-   [ ] Ruff passes.
-   [ ] Ruff Format passes.
-   [ ] Pre-commit passes.
-   [ ] Release contract suites pass.
-   [ ] Build outputs were cleaned before build.
-   [ ] Current wheel and sdist were built.
-   [ ] Artifact filenames match release identity.
-   [ ] Wheel metadata matches release identity.
-   [ ] `OPL_TEST_WHEEL` points to the exact current wheel.
-   [ ] Packaging tests pass against the current artifact.
-   [ ] First 15 Minutes tests pass against the current artifact.
-   [ ] Full regression passes.
-   [ ] Coverage threshold passes.
-   [ ] SHA-256 checksums are generated and verified.
-   [ ] Semantic reproducibility requirements are satisfied.
-   [ ] No byte-for-byte reproducibility claim is made without evidence.

### Publish

-   [ ] Release workflow is explicitly maintainer-dispatched.
-   [ ] Verification completes before publication.
-   [ ] Publication job receives only required write permission.
-   [ ] Expected tag points to the approved release SHA.
-   [ ] Verified artifact bundle is handed to publication unchanged.
-   [ ] Checksums are re-verified after handoff.
-   [ ] Draft GitHub Release tag is correct.
-   [ ] Draft GitHub Release assets are exact.
-   [ ] RC/GA classification is correct.
-   [ ] Draft has been manually reviewed.
-   [ ] All abort conditions are clear.
-   [ ] Publication is explicitly approved.

### Post-release

-   [ ] Public tag resolves to the approved SHA.
-   [ ] GitHub Release identity is correct.
-   [ ] Published asset set is correct.
-   [ ] Published checksums match downloadable artifacts.
-   [ ] Required installed-user smoke verification passes.
-   [ ] Release evidence is recorded.
-   [ ] Any exception is documented.
-   [ ] Repository documentation is synchronized with new release
    evidence.

------------------------------------------------------------------------

## 23. Code Review Checklist --- Step 8.8.7

### Architecture

-   [ ] The runbook follows verification-before-publication.
-   [ ] Verification and publication remain separate trust boundaries.
-   [ ] The procedure does not bypass repository-owned automation.
-   [ ] The runbook does not introduce an undocumented publication
    channel.
-   [ ] PyPI/package-index publication is not implied.

### Release Identity

-   [ ] Canonical version is explicit.
-   [ ] Release commit SHA is explicit.
-   [ ] Expected tag is deterministic.
-   [ ] Tag/version agreement is required.
-   [ ] Tag/SHA agreement is required.
-   [ ] Conflicting tags fail closed.
-   [ ] Public tags are never silently moved.

### Artifacts and Checksums

-   [ ] Build outputs are cleaned before build.
-   [ ] Wheel and sdist are verified as the current release artifacts.
-   [ ] Wheel metadata verification is documented.
-   [ ] Stale artifact handling is documented.
-   [ ] SHA-256 generation is documented.
-   [ ] Checksum re-verification after artifact handoff is documented.

### Installed-user Verification

-   [ ] `OPL_TEST_WHEEL` is documented.
-   [ ] It points to the exact current wheel.
-   [ ] Packaging verification is documented.
-   [ ] First 15 Minutes verification is documented.
-   [ ] Source checkout is not treated as a substitute for
    installed-artifact evidence.

### Reproducibility

-   [ ] Semantic reproducibility is defined.
-   [ ] Byte-for-byte reproducibility is not overclaimed.
-   [ ] Rebuild semantic drift is a blocker.

### GitHub Release

-   [ ] Workflow dispatch is explicit.
-   [ ] PR-triggered publication is prohibited.
-   [ ] Draft-first publication is documented.
-   [ ] Release tag / SHA / assets / checksums are checked.
-   [ ] RC versus GA classification is documented.
-   [ ] Existing conflicting published state fails closed.

### Failure Handling

-   [ ] Pre-tag abort procedure is documented.
-   [ ] Pre-publication tag correction is documented.
-   [ ] Post-publication correction preserves auditability.
-   [ ] Silent history rewriting is prohibited.
-   [ ] Checksum mismatch is a blocker.

### Evidence and Acceptance

-   [ ] Required release evidence is enumerated.
-   [ ] Fresh completion-state regression evidence is required.
-   [ ] Confirmed facts are distinguishable from assumptions.
-   [ ] Step 8.8.8 owns final full-regression quality-gate evidence.
-   [ ] Step 8.8.9 owns formal Step 8.8 acceptance.
-   [ ] Step 8.9 final release-readiness ownership is not pre-empted.

------------------------------------------------------------------------

## 24. Step 8.8.7 Completion Criteria

Step 8.8.7 may be considered complete when:

-   this maintainer runbook exists in
    `docs/maintainers/release-process.md`;
-   the procedure agrees with the accepted Step 8.8 governing design;
-   release identity, artifacts, checksums, workflow dispatch,
    draft/publish, abort, correction, and evidence procedures are
    documented;
-   commands are actionable for the supported maintainer environment;
-   the Step 8.8.7 Code Review Checklist is reviewed;
-   documentation quality gates pass;
-   the change passes PR/CI review.

Step 8.8.7 completion does **not** by itself accept Step 8.8.

After this documentation slice, the next planned work is:

``` text
Step 8.8.8 — Full Regression + Quality Gates
        ↓
Step 8.8.9 — Formal Acceptance
```

------------------------------------------------------------------------

## 25. Maintainer Summary

The release rule is:

> Build from one approved source identity, verify before publication,
> publish only the exact verified artifacts, and preserve enough
> evidence to prove what was released.

When evidence conflicts, **stop**.

When publication state is ambiguous, **stop**.

When a correction would rewrite public history silently, **do not do
it**.

A successful OpenProjectLab release is an auditable agreement between
source SHA, version, tag, artifacts, checksums, verification results,
and the published GitHub Release.
