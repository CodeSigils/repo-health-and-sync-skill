---
title: Heuristic Discovery — B1-B6 Detection Patterns
description: Runtime detection patterns for Phase B project health baseline checks.
status: reference
supersedes: inline sections in SKILL.md B1-B6
---

# Heuristic Discovery — B1-B6 Detection Patterns

This file contains the detailed detection tables, severity mappings, and
remediation steps for Phase B checks. SKILL.md points here instead of
inlining the content — prevents duplication and drift.

---

## B1: Git hygiene

**Discovery (runtime):** Run `git status --porcelain` to check for a dirty
tree, `git branch --show-current` to confirm the expected branch is `main`,
`git remote -v` to list all remotes, and `git log origin/main..HEAD` to find
un-pushed commits. For stale tracking branches, run
`git branch -r --merged HEAD` and filter out main and HEAD.

**Heuristic table:**

| Signal                            | How to detect                                        | What it means                                 | Severity                                                       |
| :-------------------------------- | :--------------------------------------------------- | :-------------------------------------------- | :------------------------------------------------------------- |
| Dirty tree                        | `git status --porcelain` non-empty                   | Uncommitted changes                           | BLOCKING                                                       |
| Not on main                       | `git branch --show-current` not `main`               | Wrong base for release                        | BLOCKING                                                       |
| Multiple remotes                  | `git remote` count > 1                               | Must push to all                              | BLOCKING before sync                                           |
| Un-pushed commits                 | `git log origin/main..HEAD` non-empty                | Local-only changes                            | WARNING (elevates to BLOCKING before syncing a runtime target) |
| Branches merged to HEAD on origin | `git branch -r --merged HEAD` (excluding main, HEAD) | Stale tracking refs                           | INFO                                                           |
| Branch is `master`                | `git branch --show-current` shows `master`           | Legacy default — rename to `main` recommended | INFO                                                           |
| Commit message convention         | sample `git log --oneline -10`                       | Conventional Commits pattern                  | WARNING if inconsistent                                        |

**Remediation:**

- Dirty tree: `git stash` or commit+push.
- Wrong branch: `git merge` or `git rebase` into `main`.
- Un-pushed: `git push --all <remote>` followed by `git push --follow-tags <remote>`.
- Stale branches: `git push <remote> --delete <branch>` after confirming it's safe to remove.

---

## B2: Shellcheck shell scripts

**Discovery (runtime):** Walk the repo with `find . -name '*.sh'`, excluding
directories like `.git`, `node_modules`, `__pycache__`, `.venv`, `venv`,
`dist`, `build`, `output`, and `target`. Check `.repo-health.json` for
additional `skip_shellcheck_paths`. If `command -v shellcheck` fails, skip this
step and log the reason. Run `shellcheck` on every `.sh` file
found. Also verify script names follow a `verb-noun` pattern with standard
prefixes (`check-`, `build-`, `deploy-`, `test-`, `lint-`, `install-`,
`run-`, `release-`, `clean-`). Override expectations via `.repo-health.json`.

**Severity mapping:**

| shellcheck level | Project action                       |
| :--------------- | :----------------------------------- |
| error            | BLOCKING — fix before proceeding     |
| warning          | WARNING — fix when touching the file |
| style            | INFO — note but no block             |
| info             | INFO — note but no block             |

**Remediation:**

Run `shellcheck --shell=bash path/to/script.sh` for a specific file.

Common fixes by shellcheck rule:

- SC2086 (unquoted variable): use `"$var"` instead of `$var`.
- SC2162 (read -r): use `read -r var` instead of `read var`.
- SC2295 (quoted expansion in prefix removal): use `"${file#"prefix"}"` instead of `${file#prefix}`.
- SC2046 (word splitting): use an array or explicit quoting.

If no `.sh` files are found, skip this step.

---

## B3: Consistency check

**Discovery (runtime) — try these in precedence order:**

1. `.repo-health.json` → `consistency_check` value.
2. `check-consistency.js` → run with `node`.
3. `check-all.js` → run with `node`.
4. `check-release-readiness.sh` → run with `bash`.
5. `run-offline-contracts.sh` → run with `bash`.
6. `verify.py` → run with `python3`.
7. `verify-release.sh` → run with `bash`.
8. `Makefile test target` → `make test`.
9. Any `scripts/check-*.sh` file → run the first one found.

Heuristic: look for files named `check-*`, `verify-*`, or `consistency-*`
under `scripts/`, `dev/`, or the repo root. Prefer the most specific match
(longest filename) over a generic `check.sh`.

**Severity:**

| Outcome                    | Severity                      |
| :------------------------- | :---------------------------- |
| No consistency check found | WARNING — consider adding one |
| Found and exits 0          | OK                            |
| Found and exits non-zero   | BLOCKING — inspect output     |

**Remediation:**

If missing, add a trivial consistency check that at minimum confirms the
working tree is clean and version sources align (see B4).

---

## B4: Version alignment

**Discovery (runtime) — inspect these files in order:**

- `package.json`: read the `version` field via `node -p`.
- `Cargo.toml`: grep for `^version =`.
- `pyproject.toml`: grep for the `version` line under `[project]`.
- `SKILL.md` (or `skills/*/SKILL.md`): read the `version:` field from YAML frontmatter via `awk`.
- `CHANGELOG.md`: take the latest heading matching `## v*`.
- `README.md` badge: extract the version from any `vX.Y.Z-blue` badge URL.

Collect all found versions into a list.

**Evaluation:**

- If all found versions match → OK.
- If any mismatch → WARNING, list diverging sources and values.
- If no version source found → INFO (project may not be versioned).

**Remediation:**

Bump `package.json` version first, then update:

- `SKILL.md` frontmatter (if present)
- `README.md` badge URL (if present)
- `CHANGELOG.md` heading — move Unreleased entries under the new version heading
- Any other discovered manifest files

Run the project's own format check after bumping to confirm consistency.

For research repos, config repos, or tools without versioning: no version
sources found and no `.repo-health.json` declares versions → skip this step.

---

## B5: Tag vs Release integrity

**Discovery (runtime) — requires `gh` CLI:**

Fetch three sources:

- Local tags: `git tag -l 'v*' --sort=-version:refname`.
- Remote tags: `git ls-remote --tags origin`, filtered to `v*` refs.
- GitHub Releases: `gh release list --json tagName`.

Cross-reference all three. A tag that exists locally but has no corresponding
GitHub Release is orphaned. A tag that exists on remote but not locally was
pushed from another workstation (just `git fetch --tags`).

**Heuristic table:**

| Signal                                       | What it means                              | Severity    |
| :------------------------------------------- | :----------------------------------------- | :---------- |
| Tag exists locally but no GitHub Release     | Orphan tag — needs release or deletion     | WARNING     |
| Tag exists on remote but not locally         | Pushed from elsewhere — `git fetch --tags` | INFO        |
| Release marked Latest points to non-HEAD tag | Release status is stale                    | BLOCKING    |
| v\* tags exist but no GitHub Releases at all | Systematic release process gap             | WARNING     |
| No v\* tags at all                           | Project may not do versioned releases      | INFO — skip |
| Lightweight tag for a release                | `git tag` vs `git tag -a` check            | INFO        |

**Remediation:**

- Create a missing release from an existing annotated tag: `gh release create vX.Y.Z --title "vX.Y.Z" --notes-file ...` using the tag's annotation for body content.
- Delete an orphan tag both locally and on remote: `git tag -d vX.Y.Z` then `git push --delete origin vX.Y.Z`.
- Convert a lightweight tag to annotated: `git tag -d vX.Y.Z`, `git tag -a vX.Y.Z -m "vX.Y.Z"`, then `git push origin vX.Y.Z --force-with-lease` (only if no one else has pulled it).

If the project has no v\* tags, skip this step.

**Note:** Also consider the GitLab CLI (`glab`) for GitLab-hosted projects. Extend detection to check for `.gitlab-ci.yml` and use the appropriate platform CLI.

---

## B6: Format and lint check

**Discovery (runtime) — detect formatter config files in precedence order:**

1. `.oxfmtrc.json` or `oxfmt` in `package.json` dependencies → check if `npm run format:check` is defined in `package.json` scripts.
2. `.prettierrc*`, `.prettierignore`, or `prettier` in `package.json` → `npx prettier --check .`.
3. `Cargo.toml` → `cargo fmt --check`.
4. `pyproject.toml` with `[tool.ruff]` section → `ruff format --check .`; with `[tool.black]` section → `black --check .`.
5. `Makefile` with `format-check` or `format:check` target → `make format-check`.

Collect all detected formatter commands and run each. A project may have
multiple formatters (e.g., oxfmt for Markdown + prettier for JS).

**Severity:**

| Outcome                         | Severity                                                   |
| :------------------------------ | :--------------------------------------------------------- |
| No formatter config found       | INFO — suggest adding one                                  |
| All detected format checks pass | OK                                                         |
| Any detected format check fails | WARNING — run fix or update `.repo-health.json` to exclude |

**Remediation:**

Run the project's format-fix command, discovered analogously to the check
command above (e.g., `npm run format`, `prettier --write .`, `cargo fmt`,
`ruff format .`).

Format failures are WARNING, not BLOCKING, unless the project's own
consistency check (B3) also enforces them — in which case B3 already
catches it as BLOCKING.

---

## B8: Cross-platform shell audit

Scan `.sh` files for non-portable shell constructs. Runs after B2's file
discovery (same file walk, same exclusion rules).

### Detection patterns

| Pattern | Detection command | Portable replacement |
| :------ | :---------------- | :------------------- |
| `which` | `grep -rn '\bwhich\b' --include='*.sh' .` | `command -v` |
| `grep -P` | `grep -rn 'grep.*-P' --include='*.sh' .` | `grep -E` |
| `sed -i` without backup extension | `grep -rnE 'sed -i[^b ]' --include='*.sh' .` | `sed -i.bak` |
| `echo` with escape sequences | `grep -rn 'echo.*\\' --include='*.sh' .` | `printf '%s\n'` |
| Hardcoded `/bin/bash` shebang | `grep -rn '#!/bin/bash' --include='*.sh' .` | `#!/usr/bin/env bash` |
| Octal `\012` in printf/sed | `grep -rn '\\012' --include='*.sh' .` | `\n` |
| `find -exit` (non-POSIX) | `grep -rn 'find.*-exit' --include='*.sh' .` | `find ... -exec ... \;` |
| `flock` (Linux-only) | `grep -rn '\bflock\b' --include='*.sh' .` | `mkdir .lock || exit 1` |

### Remediation

For each match, replace with the portable alternative and re-run shellcheck
to confirm the fix didn't introduce new issues. If the project targets Linux
exclusively, add `skip_portability_check` to `.repo-health.json`:

```json
{
  "skip_portability_check": true
}
```

