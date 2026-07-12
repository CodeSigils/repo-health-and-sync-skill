# portability: allow-platform-ref
---
title: Heuristic Discovery — B1-B9 Detection Patterns
description: Runtime detection patterns for Phase B project health baseline checks (B1-B9).
status: reference
supersedes: inline sections in SKILL.md B1-B9
---

# Heuristic Discovery — B1-B9 Detection Patterns

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
2. `package.json` scripts, in this order: `check`, `test`, `lint`, then
   package-manager-specific equivalents (`npm`, `pnpm`, or `yarn` based on
   lockfile).
3. `pyproject.toml`, `tox.ini`, or `noxfile.py` → prefer `tox`, then `nox`,
   then configured tool checks such as `pytest`, `ruff check .`, `mypy .`,
   or `hatch run test`.
4. `Cargo.toml` → `cargo test`; also run `cargo clippy -- -D warnings` when
   Clippy is installed or configured.
5. `go.mod` → `go test ./...`.
6. `composer.json` with `scripts.test` or `scripts.check` → `composer test`
   or `composer check`.
7. `mix.exs` → `mix test`.
8. `build.gradle`, `build.gradle.kts`, or `pom.xml` → `./gradlew test` when
   the wrapper exists, otherwise `gradle test` or `mvn test`.
9. `Makefile` test/check target → `make test` or `make check`.
10. Project-specific scripts: `check-consistency.js`, `check-all.js`,
    `check-release-readiness.sh`, `run-offline-contracts.sh`, `verify.py`,
    `verify-release.sh`, or files named `check-*`, `verify-*`, or
    `consistency-*` under `scripts/`, `dev/`, or the repo root. Prefer the
    most specific match (longest filename) over a generic `check.sh`.

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
- `setup.py`: grep for `version=` in `setup()` call.
- `setup.cfg`: grep for `version =` under `[metadata]`.
- `go.mod`: record the module path and Go directive. Go modules often do not
  carry an application version, so do not compare this to semver sources
  unless `.repo-health.json` declares it version-bearing.
- `composer.json`: read the `version` field.
- `mix.exs`: grep for `@version`.
- `build.gradle` / `build.gradle.kts`: grep for `version =`.
- `pom.xml`: grep for `<version>`.
- `CMakeLists.txt`: grep for `VERSION`.
- `meson.build`: grep for `version:`.
- `SKILL.md` (or `skills/*/SKILL.md`): read the `version:` field from YAML frontmatter via `awk`.
- `CHANGELOG.md`: take the latest heading matching `## v*`.
- `README.md` badge: extract the version from any `vX.Y.Z-blue` badge URL.

Collect all found versions into a list. Compare semver-bearing sources only;
some ecosystem manifests identify the module/package without declaring a
release version.

**Evaluation:**

- If all found versions match → OK.
- If any mismatch → WARNING, list diverging sources and values.
- If no version source found → INFO (project may not be versioned).

**Remediation:**

When the README badge is a hardcoded version (e.g. `vX.Y.Z-blue.svg`), consider
replacing it with a **dynamic GitHub Release badge** that auto-fetches the latest
tag: `https://img.shields.io/github/v/release/user/repo`. This eliminates the
manual bump step and removes a common drift surface entirely.

For manual bumps: bump `package.json` version first, then update:

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
4. `pyproject.toml` with `[tool.ruff]` section → `ruff format --check .` and
   `ruff check .`; with `[tool.black]` section → `black --check .`.
5. `Makefile` with `format-check` or `format:check` target → `make format-check`.
6. `package.json` `scripts` field with `format:check` or `format-check` key
   → `npm run format:check`. Catches projects that bundle their own formatter
   (e.g. skill repos with a custom CLI) rather than using a standard external tool.
7. `.ruff.toml` or `ruff.toml` → `ruff check .` and `ruff format --check .`.
8. `pyproject.toml` with `[tool.mypy]` or `[tool.pyright]` → `mypy .` or
   `pyright` (lint).
9. `.eslintrc*`, `eslint.config.js`, or `eslint` in `package.json` →
   `npx eslint .`.
10. `.stylelintrc*`, `stylelint` in `package.json` →
    `npx stylelint "**/*.{css,scss}"`.
11. `gofmt` sources plus Go files → `gofmt -w` only as a fix command;
    use `gofmt -l .` for checking. `golangci-lint` config
    (`.golangci.yml`, `.golangci.yaml`, `.golangci.toml`) →
    `golangci-lint run`.
12. `ktlint` / `detekt` config → `ktlint` / `detekt`.
13. `php-cs-fixer` (`.php-cs-fixer.php` / `.php-cs-fixer.dist.php`) →
    `php-cs-fixer fix --dry-run --diff`.
14. `phpstan` (`phpstan.neon`) → `phpstan analyse`.
15. `.rubocop.yml` → `rubocop`.
16. `.clang-format` → `clang-format --dry-run --Werror`.
17. `buf.yaml` / `buf.gen.yaml` → `buf format --diff` (protobuf).

Collect all detected formatter/linter commands and run each. A project may have
multiple formatters/linters (e.g., oxfmt for Markdown + prettier for JS + ruff for Python).

**Severity:**

| Outcome                             | Severity                                                   |
| :---------------------------------- | :--------------------------------------------------------- |
| No formatter/lint config found      | INFO — suggest adding one                                  |
| All detected format/lint checks pass | OK                                                        |
| Any detected format/lint check fails | WARNING — run fix or update `.repo-health.json` to exclude |

**Remediation:**

Run the project's format-fix command, discovered analogously to the check
command above (e.g., `npm run format`, `prettier --write .`, `cargo fmt`,
`ruff format .`, `eslint --fix .`, `golangci-lint run --fix`).

Format/lint failures are WARNING, not BLOCKING, unless the project's own
consistency check (B3) also enforces them — in which case B3 already
catches it as BLOCKING.

---

## B7: Commit audit

**Discovery (runtime):** Sample the last 10 commits with `git log --oneline -10` for format classification (B7a). For drift checks (B7b-B7e), use `git diff --name-only` between baseline (latest tag or `origin/main`) and HEAD.

**Severity mapping:**

| Sub-step | What it checks | Severity |
| :------- | :------------- | :------- |
| B7a      | Commit message subject format consistency | WARNING |
| B7b      | Runtime files changed but CHANGELOG didn't | Depends on commit quality (see below) |
| B7c      | No `## Unreleased` section despite commits since last tag | Depends on commit quality (see below) |
| B7d      | Source files changed but version unchanged | INFO (advisory) |
| B7e      | Commit body missing required fields (what:/why:) | WARNING |

#### B7a: Commit message subject audit

Sample the last 10 commits with `git log --oneline -10` and classify each
by format:

- `type(scope): message` — Conventional Commits (preferred)
- `type: message` — Conventional Commits, no scope
- `topic: message` — structured (noun phrase before colon)
- `message` — unstructured (no colon prefix)

Count how many follow a structured format (conventional commits + topic-style).
If fewer than 7/10 are structured, emit a WARNING. The agent logs the sample and the ratio,
but does NOT require retroactive fixes — this is a culture signal, not a
block.

**Remediation:** Suggest adopting Conventional Commits for new commits.
For the current batch, consider whether to squash-merge into a single
well-formed commit before release.

#### B7b: Cross-commit drift

Detect when runtime source files (under `skills/`, `src/`, `lib/`, `app/`)
were modified but `CHANGELOG.md` was not. Severity depends on whether the
repo's commit log already serves as its release record:

1. **Check if CHANGELOG.md exists** — if not, proceed to commit quality gate
2. **If CHANGELOG.md exists:** Run `git diff --name-only` between the
   baseline (latest tag or `origin/main`) and HEAD. If runtime paths
   changed but CHANGELOG.md didn't, emit BLOCKING.
3. **If no CHANGELOG.md:** Sample the last 10 commits (same method as B7a).
   If ≥7/10 have structured what/why bodies → emit INFO
   ("No CHANGELOG; commit log serves as release record").
   If <7/10 → emit WARNING
   ("No CHANGELOG and commit messages are unstructured — consider
   either improving commit quality or adding a CHANGELOG").

Per B0, git log is authoritative — skip CHANGELOG enforcement when
commit quality is high.

See [references/drift-pairs.md](references/drift-pairs.md) for the full
detection script and `.repo-health.json` configuration options.

#### B7c: CHANGELOG completeness

Check that `## Unreleased` exists in CHANGELOG.md when there are commits
since the last release tag. Same commit-quality gating as B7b:

1. **If CHANGELOG.md exists** — check for `## Unreleased` when there are
   commits since the latest tag. Missing section → WARNING.
2. **If no CHANGELOG.md** — rely on commit quality assessment from B7b.
   If commit quality is high → skip silently (commit log is the record).
   If commit quality is low → INFO ("consider adding a CHANGELOG or
   improving commit message structure").

**How:** Determine the latest `v*` tag, count commits since it, then check
CHANGELOG.md for `## Unreleased`. If no tags exist but a CHANGELOG.md does,
check it has an Unreleased section as a hygiene signal.

#### B7d: Version-bump awareness (advisory)

Emit INFO when source files changed but the version field in `package.json`
(or whatever version source the project uses) did not. This is advisory only
— many commits are not releases — but it alerts the agent to consider
whether a version bump is warranted.

**How:** Count source file changes between baseline and HEAD via
`git diff --name-only`, compare against version field changes in the
primary manifest.

#### B7e: Commit body format

Check that commit messages in the range have required body fields
(e.g., `what:` and `why:`). Configured via `.repo-health.json` →
`commit_body_format.required_fields` (default: `["what", "why"]`).

**How:** Run `python3 scripts/check-commit-body.py --range origin/main..HEAD`
(or the configured baseline). The checker reads `.repo-health.json` for
`required_fields` and `pattern`. Violations are WARNING by default
(configurable via `.repo-health.json`).

**Remediation:** Add the required fields to commit bodies. Bypass with
`ALLOW_ATTRIBUTION_TRAILERS=1` if needed.

**Configuration via `.repo-health.json`:**

```json
{
  "commit_body_format": {
    "required_fields": ["what", "why"],
    "pattern": "^what: .+\\nwhy:  .+$"
  }
}
```

If `commit_body_format` is absent, the default is `["what", "why"]` with no
extra regex pattern. To disable, explicitly set `required_fields: []` in
`.repo-health.json`.

---

## B8: Cross-platform shell audit

### Detection patterns

| Pattern | Detection command | Portable replacement |
| :------ | :---------------- | :------------------- |
| `$(which ...)` | `grep -rnE` with `$(which` on `.sh` files | `command -v` |
| `grep -P` | `grep -rn 'grep.*-P' --include='*.sh' .` | `grep -E` |
| `sed -i` without backup extension | `grep -rnE 'sed -i[^b ]' --include='*.sh' .` | `sed -i.bak` |
| `echo` with escape sequences | `grep -rn 'echo.*\\' --include='*.sh' .` | `printf '%s\n'` |
| Hardcoded `/bin/bash` shebang | `grep -rn '#!/bin/bash' --include='*.sh' .` | `#!/usr/bin/env bash` |
| Octal `\012` in printf/sed | `grep -rn '\\012' --include='*.sh' .` | `\n` |
| `find -exit` (non-POSIX) | `grep -rn 'find.*-exit' --include='*.sh' .` | `find ... -exec ... \;` |
| `flock` (Linux-only) | `grep -rn '\bflock\b' --include='*.sh' .` | `mkdir .lock || exit 1` |

### B8b: CI cross-platform guard

When `.sh` files exist and CI is configured, check whether at least one
workflow/job exercises a non-Linux runner (`macos-latest`) or both Linux and
Windows runners (`ubuntu-latest` plus `windows-latest`). This is a guard
against "looks portable" scripts that only ever run on Linux.

**Severity:** INFO by default. Elevate to WARNING only when the project
declares cross-platform support or `.repo-health.json` sets
`require_cross_platform_ci: true`.

**Skip conditions:** no shell scripts, no CI config, or an explicitly
Linux-only project.

### Remediation

For each match, replace with the portable alternative and re-run shellcheck
to confirm the fix didn't introduce new issues. If the project targets Linux
exclusively, add `skip_portability_check` to `.repo-health.json`:

```json
{
  "skip_portability_check": true
}
```

---

## B9: CI efficiency and coverage audit

**Discovery (runtime):** Detect CI configuration across common forges:

| Forge | Config path |
| :---- | :---------- |
| GitHub Actions | `.github/workflows/*.yml`, `.github/workflows/*.yaml` |
| GitLab CI | `.gitlab-ci.yml` |
| CircleCI | `.circleci/config.yml` |
| Azure Pipelines | `azure-pipelines.yml`, `.azure-pipelines/*.yml` |
| Bitbucket Pipelines | `bitbucket-pipelines.yml` |
| Drone | `.drone.yml` |
| Woodpecker | `.woodpecker.yml`, `.woodpecker/*.yml` |

Evaluate efficiency only for the CI system present. Do not require every
forge file. If no known CI config exists, skip with INFO.

**Signals:**

| Signal | Efficient | Inefficient |
| :----- | :-------- | :---------- |
| Trigger scoping | Separate docs/CI/release paths | Monolithic workflow for every change |
| Trigger path completeness | Validated files appear in trigger paths | Docs or metadata validated by CI are omitted |
| Tag handling | Tag pushes route to release workflow | Tag pushes rerun full branch CI |
| Dependency caching | Native cache for the forge/ecosystem | Fresh dependency install on every run |
| Guard independence | Commit/trailer guards run on all commit-bearing changes | Guards are hidden behind path filters |

**Severity:** WARNING for clear inefficiency or missing coverage in a present
CI config; INFO when no CI config exists or when the project intentionally
does not use hosted CI.
