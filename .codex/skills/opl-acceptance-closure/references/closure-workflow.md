# Closure workflow

## Evidence boundary

- Require the alignment PR to be `MERGED` and required checks to pass.
- Synchronize clean `main` with `origin/main` using fast-forward only.
- Require both identities to equal the alignment PR merge commit when it is the
  latest mainline change.
- Execute the documented focused post-merge tests with the OPL virtual-environment
  Python. Record only observed results.
- Treat the collector JSON as input evidence, not permission to merge.

## Repository-driven generation

Read the actual implementation record, alignment record, governance surfaces, and
their tests before editing. Derive replacements from the current text.

- Change only the current pending terminal states required by closure.
- Preserve historical records and prior evidence.
- Add a distinct acceptance record and distinct exact marker for each governance
  surface.
- Test complete HTML markers such as `<!-- marker-changelog -->`; never count a
  prefix that is also contained in another marker.
- Assert semantic fragments independently when Markdown wrapping can change.
- Before delivery, apply the generated changes in an isolated copy or validate every
  exact replacement against the current repository.
- Never weaken a genuine contract merely to make a generated test pass.

## Reliable runner requirements

- Print every native command before execution with a `>>>` prefix.
- Pin `F:\OpenProjectLab\.venv\Scripts\python.exe` and `pre-commit.exe`.
- If mixed-line-ending or Ruff modifies files, rerun focused tests and pre-commit,
  restage explicit paths, and retry the commit once.
- If a commit already exists with the expected subject and no staged changes remain,
  resume from push rather than treating `nothing to commit` as failure.
- Quarantine only positively identified `gcm.cache/std.gcm` and `std.o` artifacts;
  stop on any other unexpected change.
- Run `gh auth status` and `gh auth setup-git`, then use this per-command rewrite for
  push and pull without changing the stored remote:

  ```powershell
  git -c "url.https://github.com/.insteadOf=git@github.com:" push -u origin $Branch
  ```

## Authorization and completion

Creating a branch, commit, push, PR, or monitoring CI does not authorize merge.
Stop at a visible merge gate containing PR number, URL, head SHA, CI status, and a
request for explicit `merge` authorization. After an authorized merge, synchronize
main and run the final documented lightweight consistency check.
