---
name: repo-health-and-sync-skill
description: >-
  Generic two-phase procedure: project health baseline (Phase B) and runtime
  reverse sync (Phase C). Uses heuristics to discover a repo's scripts,
  manifests, consistency checks, sync targets, and version sources at runtime.
  No hardcoded project metadata — works for any repo the agent is dropped into.
  Per-project configuration belongs in each repo's own .repo-health.json,
  not in this skill.
license: MIT
compatibility: hermes
metadata:
  author: CodeSigils
  version: "1.1.0"
  purpose: project-governance
  tags:
    - git-hygiene
    - release-automation
    - shellcheck
    - reverse-sync
    - health-audit
    - cross-project
---

# Repo Health Audit and Reverse Sync

Two-phase procedure designed for any git repository. Phase B establishes a
health baseline. Phase C synchronizes changes to deployed runtime targets.
Phase B gates Phase C — never sync a broken repo.

The skill discovers everything it needs by inspecting the repo at runtime.
It does not hardcode project names, paths, or commands. If a repo includes
a `.repo-health.json` at its root, that file overrides heuristics with
explicit declarations.

---

## Overview — How to use this skill

1. Confirm you're inside the repo root (`git rev-parse --show-toplevel`).
2. Run Phase B phases in order (B1 through B6).
3. If any BLOCKING item, stop and fix before continuing.
4. If the repo has a runtime target, run Phase C (C1 through C4).

Each phase section lists: **why** it matters, **how** to discover the
relevant files/config at runtime, **severity** when it fails, and
**remediation** when it fails.

### B0: Design principles (read before Phase B)

These principles govern all checks below. The agent should internalise them
before running any phase.

**Commit log vs CHANGELOG.** Some projects produce well-structured commit
messages that serve as their own release documentation (what: + why: per
commit, conventional format, clear scopes). For those projects, requiring a
`CHANGELOG.md` creates a duplicate drift surface (AP1) rather than tightening
it. The skill's CHANGELOG checks (B4, planned B7c) should defer to the commit
log when:
- Project uses conventional commits or a consistent structured format
- 90%+ of recent commits have descriptive bodies (not just one-line subjects)
- Release notes can be generated from `git log tag..tag --format`

When these conditions hold, CHANGELOG absence should be INFO, not WARNING.
The agent checks commit log quality first, then decides whether CHANGELOG
enforcement is proportionate. This honours the principle that `git log` is
the authoritative historical record.

**Detect, don't enforce.** No convention is universal across ecosystems.
The skill discovers the project's existing patterns before imposing rules.

**Zero tags is valid.** ohmyzsh (188k stars) proves a project can thrive
without formal releases. Only stale tags matter, not absence of tags.

**Proportionate anti-drift.** Every check should trace to a specific observed
failure mode. Speculative checks accumulate maintenance debt before they
create value. If a check fires and you haven't seen this failure before,
consider disabling it rather than patching around it. See
`references/anti-drift-proportionality.md` once created.

**Forge-awareness.** These checks work on any git repo. The skill activation
mechanism (`SKILL.md`, `hermes skills install`) is Hermes-specific. To port
to another agent runtime (Claude Code, Codex, Cursor, Copilot), create a
forge-specific adapter in `forge-adapters/` or rewrite the frontmatter for
that forge. The detection logic in B1-B6 and C1-C4 is agent-agnostic.

---

## Phase B — Project Health Baseline

### B1: Git hygiene

**Why:** Git history is the durable record. Dirty trees, orphan tags, and
un-pushed commits accumulate into context that misleads both humans and agents.

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
- Stale branches: `git push <remote> --delete <branch>` after confirming it's
  safe to remove.

---

### B2: Shellcheck shell scripts

**Why:** Shell scripts are the most common source of uncaught defects in
project automation — unquoted variables, missing `set -e`, backslash mangling,
and globbing cause silent CI or local failures. Shell scripts can be potentially
fragile and dangerous. The inclusion of code inside markdown files, makes the
use of checking and testing the scripts nearly impossible suggesting the rise
of an anti-pattern, unless they are simple one-liners.

**Discovery (runtime):** Walk the repo with `find . -name '*.sh'`, excluding
directories like `.git`, `node_modules`, `__pycache__`, `.venv`, `venv`,
`dist`, `build`, `output`, and `target`. Check `.repo-health.json` for
additional `skip_shellcheck_paths`. Run `shellcheck` on every `.sh` file
found.

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
- SC2295 (quoted expansion in prefix removal): use
  `"${file#"prefix"}"` instead of `${file#prefix}`.
- SC2046 (word splitting): use an array or explicit quoting.

If no `.sh` files are found, skip this step.

---

### B3: Consistency check

**Why:** Every project encodes its own invariants — version alignment, file
shape, CI structure. A generic procedure cannot know these a priori. The
project's own check script (if one exists) is the authority.

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

### B4: Version alignment

**Why:** Version skew between manifests is the leading cause of stale-release
bugs. Industry practice from semver + Keep a Changelog.

**Discovery (runtime) — inspect these files in order:**

Look for version information in these sources, using the extraction method
noted for each:

- `package.json`: read the `version` field via `node -p`.
- `Cargo.toml`: grep for `^version =`.
- `pyproject.toml`: grep for the `version` line under `[project]`.
- `SKILL.md` (or `skills/*/SKILL.md`): read the `version:` field from YAML
  frontmatter via `awk`.
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

### B5: Tag vs Release integrity

**Why:** A git tag and a GitHub Release are two separate artifacts. Tags can
be orphaned. Releases carry changelogs and are discoverable. Industry practice:
every runtime tag should have a corresponding GitHub Release, and annotated
tags are preferred over lightweight.

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

- Create a missing release from an existing annotated tag:
  `gh release create vX.Y.Z --title "vX.Y.Z" --notes-file ...` using the tag's
  annotation for body content.
- Delete an orphan tag both locally and on remote:
  `git tag -d vX.Y.Z` then `git push --delete origin vX.Y.Z`.
- Convert a lightweight tag to annotated:
  `git tag -d vX.Y.Z`, `git tag -a vX.Y.Z -m "vX.Y.Z"`, then
  `git push origin vX.Y.Z --force-with-lease` (only if no one else has pulled it).

If the project has no v\* tags, skip this step.

**Improvement:**

Also any other official CLI like the GitLab CLI for example should be taken
in consideration.

---

### B6: Format and lint check

**Why:** Consistent formatting across docs reduces noise in diffs and prevents
formatting-only commits. Run what the project defines.

**Discovery (runtime) — detect formatter config files:**

Check for these indicators in precedence order:

- `.oxfmtrc.json` or `oxfmt` in `package.json` dependencies → then check if
  `npm run format:check` is defined in `package.json` scripts.
- `.prettierrc*`, `.prettierignore`, or `prettier` in `package.json` →
  `npx prettier --check .`.
- `Cargo.toml` → `cargo fmt --check`.
- `pyproject.toml` with `[tool.ruff]` section → `ruff format --check .`;
  with `[tool.black]` section → `black --check .`.
- `Makefile` with `format-check` or `format:check` target → `make format-check`.

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

## Phase C — Reverse Sync

**Why:** Many projects produce runtime artifacts deployed to system directories
(Hermes skills, config mirrors, HQ clones, build outputs). The repo is source
of truth; the installed copy is the deployed target. After pushing to the repo,
the runtime must be updated. This is the CI/CD deploy stage.

### C1: Detect sync targets

**Discovery (runtime) — look for clues in the repo:**

- **Hermes skill**: any `SKILL.md` with `compatibility: hermes` in frontmatter.
  The skill name is in the `name:` frontmatter field.
- **HQ directory**: presence of `scripts/hq-sync.sh` or an `INDEX.md` at root.
- **Directory mirror**: presence of `scripts/sync-*.sh` or `scripts/*-sync-*.sh`.
- **Build package**: presence of `Containerfile`, `Dockerfile`, `build.sh`, or
  `release.sh`.

Priority order: `.repo-health.json` overrides all heuristics. If it declares
a `sync_target`, use that directly.

**Sync target types:**

| Type               | Meaning                                  | Heuristic clue                            |
| :----------------- | :--------------------------------------- | :---------------------------------------- |
| `hermes-skill`     | Installable Hermes Agent skill           | `SKILL.md` with `compatibility: hermes`   |
| `directory-mirror` | Config/tool directory with a sync script | `scripts/sync-*.sh`                       |
| `hq-directory`     | Hermes skill HQ clone                    | `INDEX.md` or `hq-sync.sh`                |
| `build-package`    | CI-built artifact (deb, binary, etc.)    | `build.sh`, `Containerfile`, `release.sh` |
| `none`             | No runtime target                        | None of the above                         |

### C2: Verify pre-sync state

Confirm Phase B completed without any BLOCKING items. If any BLOCKING issue
remains, report it and stop. Syncing a broken repo to a runtime target makes
the broken state durable.

### C3: Execute sync

Heuristic action per target type:

| Type               | Default action                                      | Preferred if sync script exists                  |
| :----------------- | :-------------------------------------------------- | :----------------------------------------------- |
| `hermes-skill`     | `hermes skills install --force --yes <hub-ref>`     | Use the install script in the repo if one exists |
| `directory-mirror` | Find and run `scripts/sync-*` or `scripts/*-sync-*` | Same default                                     |
| `hq-directory`     | `bash scripts/hq-sync.sh`                           | Uses it                                          |
| `build-package`    | Push a version tag and let CI handle the build      | Notify the user                                  |

For Hermes skills: if the hub hasn't indexed the latest push, fall back to
installing from a local path. Find the skill directory in the repo (the
directory containing `SKILL.md`), then run
`hermes skills install "$(pwd)/<skill-dir>" --force --yes`.

### C4: Verify post-sync

**Runtime check** — confirm the installed CLI or tool actually works:

| Type             | Runtime verification                                           |
| :--------------- | :------------------------------------------------------------- |
| hermes-skill     | Run `node <installed-path>/src/index.js --help` or `--version` |
| directory-mirror | Re-run the project's precheck script (should now pass)         |
| hq-directory     | Confirm key files exist under `~/.hermes/hq/`                  |
| build-package    | Confirm CI pipeline triggered from tag push                    |

**Drift check** — compare the installed files against the repo source.
This verifies that what was synced actually matches what's in the repo.
Drift here means the sync was incomplete, stale, or corrupted.

The strategy depends on sync target type:

- **Hermes skill**: Determine the skill directory in the repo (the directory
  containing `SKILL.md`). Read the skill name from the `name:` frontmatter
  field, then locate the installed path at `~/.hermes/skills/<name>/`.
  Walk all files under the repo's skill directory (excluding `node_modules/`)
  and check that each exists at the same relative path under the installed
  directory. Any file present in repo but missing from the installed copy is
  a drift warning.

- **Directory mirror**: If `.repo-health.json` declares a `sync_target.path`,
  run `diff -rq` between the repo root and that path, excluding `.git` and
  `node_modules`. Report any differing or missing files up to the first 20
  lines of diff output.

- **HQ directory**: Check that key files (`INDEX.md`, `SKILL.md`) exist in
  both the repo and `~/.hermes/hq/` and have identical content. Any
  difference is a drift warning.

**Severity:**

- Runtime check fails (CLI exits non-zero, precheck fails, key file
  missing) → BLOCKING. Fix the sync immediately.
- Drift findings (files differ between repo and installed target) →
  WARNING. Some differences are expected — file permissions, `.gitignore`d
  artifacts, platform-specific paths. If every key file matches and the
  runtime check passes, the sync is clean.

---

## `.repo-health.json` — Per-project overrides

Projects that want explicit configuration (rather than heuristic detection)
can add a `.repo-health.json` at their root. The skill checks for this file
at the start of each phase and uses its values when present.

Schema:

```json
{
  "version": 1,
  "remotes": ["origin", "ssh-origin"],
  "expected_branch": "main",
  "skip_shellcheck_paths": ["output/**"],
  "skip_version_alignment": false,
  "skip_releases": false,
  "version_files": [
    {
      "path": "package.json",
      "extract": "node -p \"require('./package.json').version\""
    }
  ],
  "consistency_check": "node scripts/check-consistency.js",
  "format_check": "npm run format:check",
  "format_fix": "npm run format",
  "sync_target": {
    "type": "hermes-skill",
    "name": "markdown-formatter",
    "install_cmd": "hermes skills install --force --yes CodeSigils/agents-markdown-formatter/markdown-formatter",
    "post_verify": "node ~/.hermes/skills/markdown-formatter/src/index.js --help"
  }
}
```

The schema is versioned to allow evolution. When a `.repo-health.json`
exists, its values take precedence over heuristics. Partial overrides are
supported — missing fields fall back to heuristic detection.

---

## Real-world heuristic examples

The table below shows how the heuristic detection resolves for five surveyed
projects. It demonstrates that the generic approach works without hardcoding.

| Signal                | agents-markdown-formatter                        | hermes-skill-hq            | hermes-doom-config | neovim-latest-ubuntu                     | agent-concepts-study |
| :-------------------- | :----------------------------------------------- | :------------------------- | :----------------- | :--------------------------------------- | :------------------- |
| B1: Branch            | main                                             | master                     | main               | main                                     | main                 |
| B1: Remotes           | 1                                                | 1                          | 1                  | 2 (origin, ssh-origin)                   | 1                    |
| B2: Shell scripts     | `scripts/release.sh`, `staged-install-verify.sh` | 13 across dev/ + scripts/  | 9 scripts          | `build.sh`, `test.sh`, `scripts/check-*` | 0                    |
| B3: Consistency check | `check-consistency.js`                           | `run-offline-contracts.sh` | `check-*` scripts  | `check-release-readiness.sh`             | `verify.py`          |
| B4: Version sources   | `package.json`, `SKILL.md`, README badge         | SKILL.md only              | none               | CHANGELOG only                           | none                 |
| B5: Tag/Release       | 5 tags, 3 releases (2 orphans)                   | 33 tags, 0 releases        | N/A (no tags)      | 2 tags, 2 releases                       | N/A (no tags)        |
| C1: Sync target       | Hermes skill                                     | HQ directory               | Doom mirror        | build-package (CI)                       | none                 |

Key observation: **hermes-skill-hq has 33+ version tags and zero GitHub
Releases** — the same category of gap that was recently fixed in
agents-markdown-formatter. A run of this skill against hermes-skill-hq would
flag B5 as WARNING and prompt 33 release creations or tag deletions.

---

## Common pitfalls

1. **GitHub Releases are not created from git tags automatically.** An
   annotated tag is a git object. `gh release create` is a separate step.

2. **Tags are not pushed with `git push` by default.** Use `git push --tags`
   or `git push --follow-tags` explicitly. Or push each tag individually
   with `git push origin <tag>`.

3. **Multiple remotes require multiple pushes.** `git push` only pushes to
   the default remote. Iterate all defined remotes.

4. **Shellcheck info-level findings are acceptable to defer**, but track
   them in a `.shellcheckrc` or `.repo-health.json` skip filter so they
   don't silently multiply.

5. **Hermes skill reinstall does not reload the current agent session.**
   After `hermes skills install --force`, run `/reset` or start a new
   session for the skill to take effect. Inform the user.

6. **Consistency checks vary widely in quality.** A check that exits 0
   for trivial reasons (empty script, always true) is worse than no check.
   Audit the actual coverage of each project's check script before trusting it.

7. **`.repo-health.json` is optional.** If absent, the heuristic fallback
   is used. If present with partial data, missing fields fall back to
   heuristics. A project should only add it when heuristics give wrong
   results or when explicit control is needed.

---

## References

- Conventional Commits: https://www.conventionalcommits.org/
- Keep a Changelog: https://keepachangelog.com/
- Semantic Versioning: https://semver.org/
- Shellcheck: https://www.shellcheck.net/
- GitHub CLI release docs: `gh help release`
