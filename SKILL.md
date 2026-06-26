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
  version: "0.1.0"
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

**Repo as source.** The git repository is the authoritative copy of every
file it tracks. Deployed runtime targets (Hermes skill directories, config
mirrors, HQ clones, build artifacts) are derived copies. Never ship
maintainer tooling — CI scripts, release infra, development helpers — to a
user's machine. Phase C enforces this mechanically: sync goes repo→target,
not the reverse, and maintainer-only files stay in `scripts/`, `.github/`, and `docs/` —
these are never sync targets.

**Portable grep in skill code.** Every `grep` command in this SKILL.md and its
reference files must use POSIX-compatible flags. `-P` (PCRE) is GNU-only and
fails on BSD/macOS. Use `-E` for extended regex or POSIX basic regex by default.
For extraction logic that PCRE `\K` enables, use `awk` or `sed` instead. The
detection commands the agent runs (B8 heuristic-discovery table, drift-pairs
scripts) must work on any system where the repo builds.

**Forge-awareness.** These checks work on any git repo. The skill activation
mechanism (`SKILL.md`, `hermes skills install`) is Hermes-specific. To port
to another agent runtime, see
[references/agent-instruction-ecosystem.md](references/agent-instruction-ecosystem.md)
for the adaptation path and portability tiers. The detection logic in B1-B6
and C1-C4 is agent-agnostic.

**Quality-skill fallback (tri-layer probe).** Before running a B-phase check
that depends on an external quality tool (shellcheck, linters, formatters),
the agent runs a three-layer availability check:

1. `skill_view(name)` — verify a matching Hermes skill (e.g.
   `python-best-practices`) exists and loads
2. Frontmatter tags check — does the skill's declared language/scope match
   the repo being inspected?
3. Degraded mode — if neither resolves, skip the check and log which checks
   were skipped and why

Per-check degraded mode:

| Check | Depends on | Fallback when absent |
| :---- | :--------- | :------------------- |
| B2 Shellcheck | `shellcheck` binary | Skip, log reason |
| B3 Lint | equivalent language lint skill | Probe availability, then look for `.pylintrc`/`.flake8`/`.ruff.toml` / ecosystem-equivalent config file and run tool directly |
| B6 Format | `prettier` / `black` / `rustfmt` etc. | `command -v` probe — use whatever is available on PATH |

If the quality tool is genuinely unavailable (not installed, not on PATH),
skip the check. Do not fabricate a pass or a fail — log the skip clearly.

---

## Phase B — Project Health Baseline

### B1: Git hygiene

**Why:** Git history is the durable record. Dirty trees, orphan tags, and
un-pushed commits accumulate into context that misleads both humans and agents.

**How:** Run `git status --porcelain`, `git branch --show-current`,
`git remote -v`, `git log origin/main..HEAD`, and
`git branch -r --merged HEAD`.

See [references/heuristic-discovery.md](references/heuristic-discovery.md) for
the full signal table, severity mapping, and remediation steps.

---

### B2: Shellcheck shell scripts

**Why:** Shell scripts are the most common source of uncaught defects in
project automation — unquoted variables, missing `set -e`, backslash mangling,
and globbing cause silent CI or local failures. Code inside markdown files
cannot be shellchecked, suggesting an anti-pattern unless they are simple
one-liners.

**How:** Walk the repo with `find . -name '*.sh'`, excluding `.git`,
`node_modules`, `__pycache__`, `.venv`, `venv`, `dist`, `build`, `output`,
and `target`. If `command -v shellcheck` fails, skip this step and log the reason.
Run `shellcheck` on every `.sh` file found. Check script naming
follows a `verb-noun` pattern with standard prefixes.

See [references/heuristic-discovery.md](references/heuristic-discovery.md) for
severity mapping, common SC-rule fixes, and naming convention details.

If no `.sh` files are found, skip this step.

---

### B3: Consistency check

**Why:** Every project encodes its own invariants — version alignment, file
shape, CI structure. A generic procedure cannot know these a priori. The
project's own check script (if one exists) is the authority.

**How:** Try these in precedence order:
`.repo-health.json` → `check-consistency.js` → `check-all.js` →
`check-release-readiness.sh` → `run-offline-contracts.sh` → `verify.py` →
`verify-release.sh` → `make test` → any `scripts/check-*.sh`.

See [references/heuristic-discovery.md](references/heuristic-discovery.md) for
the full discovery order, severity table, and remediation.

If missing, add a trivial check that confirms the working tree is clean and
version sources align (see B4).

---

### B4: Version alignment

**Why:** Version skew between manifests is the leading cause of stale-release
bugs. Industry practice from semver + Keep a Changelog.

**How:** Inspect these files in order: `package.json`, `Cargo.toml`,
`pyproject.toml`, `SKILL.md` frontmatter, `CHANGELOG.md` latest heading,
`README.md` badge URL. Collect all found versions into a list.

See [references/heuristic-discovery.md](references/heuristic-discovery.md) for
extraction commands, evaluation criteria, and full remediation steps.

For research repos, config repos, or tools without versioning: no version
sources found and no `.repo-health.json` declares versions → skip this step.

---

### B5: Tag vs Release integrity

**Why:** A git tag and a GitHub Release are two separate artifacts. Tags can
be orphaned. Releases carry changelogs and are discoverable.

**How (requires `gh` CLI):** Fetch local tags, remote tags, and GitHub
Releases. Cross-reference all three.

See [references/heuristic-discovery.md](references/heuristic-discovery.md) for
the signal table, severity mapping, and remediation commands.

If the project has no v\* tags, skip this step.

---

### B6: Format and lint check

**Why:** Consistent formatting across docs reduces noise in diffs and prevents
formatting-only commits. Run what the project defines.

**How:** Detect formatter config files in precedence order: `.oxfmtrc.json`,
`.prettierrc*`, `Cargo.toml`, `pyproject.toml` (`[tool.ruff]` or
`[tool.black]`), `Makefile` with `format-check` target.

See [references/heuristic-discovery.md](references/heuristic-discovery.md) for
the full detection order, severity table, and format-fix commands.

Format failures are WARNING, not BLOCKING, unless the project's own
consistency check (B3) also enforces them — in which case B3 already
catches it as BLOCKING.

---

### B7: Commit audit

**Why:** Every commit traverses review, CI, and deployment pipelines. Unchecked
commits — inconsistent messages, missing CHANGELOG updates, stale versions —
accumulate silently until a release fails. B7 catches these per-commit gaps
before they compound.

**Severity for B7:**

| Sub-step | What it checks | Severity |
| :------- | :------------- | :------- |
| B7a      | Commit message format consistency | WARNING |
| B7b      | Runtime files changed but CHANGELOG didn't | BLOCKING |
| B7c      | No `## Unreleased` section despite commits since last tag | WARNING |
| B7d      | Source files changed but version unchanged | INFO (advisory) |

#### B7a: Commit message audit

Sample the last 10 commits with `git log --oneline -10` and classify each
by format:

- `type(scope): message` — Conventional Commits (preferred)
- `type: message` — Conventional Commits, no scope
- `message` — unstructured

Count how many match Conventional Commits. If fewer than 7/10 follow a
structured format, emit a WARNING. The agent logs the sample and the ratio,
but does NOT require retroactive fixes — this is a culture signal, not a
block.

**Remediation:** Suggest adopting Conventional Commits for new commits.
For the current batch, consider whether to squash-merge into a single
well-formed commit before release.

#### B7b: Cross-commit drift

Detect when runtime source files (under `skills/`, `src/`, `lib/`, `app/`)
were modified but `CHANGELOG.md` was not. This is the most common cause of
stale-release bugs after version skew.

**How:** Run `git diff --name-only` between the baseline (latest tag or
`origin/main`) and HEAD. If runtime paths changed but CHANGELOG.md didn't,
emit BLOCKING.

See [references/drift-pairs.md](references/drift-pairs.md) for the full
detection script and `.repo-health.json` configuration options.

#### B7c: CHANGELOG completeness

Check that `## Unreleased` exists in CHANGELOG.md when there are commits
since the last release tag. If there are tags but no Unreleased section,
emit WARNING with the count of un-released commits.

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

---

### B8: Cross-platform shell audit

**Why:** Shell scripts that work on Linux may silently fail on macOS, BSD,
or other Unix systems. Non-portable constructs (`which`, `grep -P`,
`sed -i` without backup, `echo` with escapes, hardcoded `/bin/bash`, etc.)
cause CI failures on non-Linux runners and frustrate cross-platform
contributors.

**How:** Scan all `.sh` files for non-portable patterns. Each `.sh` file
gets a pattern check; any match is flagged.

**Severity:** WARNING — portability is project-dependent. Projects that
target Linux exclusively may reject portable patterns that add complexity.

Detection patterns (grep each `.sh` file found by B2's walk):

| Pattern | How to detect | Portable replacement |
| :------ | :------------ | :------------------- |
| `which` | `grep '\bwhich\b'` | `command -v` |
| `grep -P` | `grep -n 'grep.*-P'` | `grep -E` |
| `sed -i` (no backup) | `sed -i[^b ]` | `sed -i.bak` |
| `echo` with escapes | `echo.*\\` | `printf '%s\n'` |
| Hardcoded `/bin/bash` | `#!/bin/bash` | `#!/usr/bin/env bash` |
| Octal `\012` | `\\012` | `\n` |
| `find -exit` | `find.*-exit` | `find ... -exec` |
| `flock` | `\bflock\b` | `mkdir .lock \|\| exit 1` |

See [references/heuristic-discovery.md](references/heuristic-discovery.md)
§ B8 for the full detection approach and per-pattern remediation.

If no `.sh` files are found, skip this step.

---

### B9: CI efficiency audit

**Why:** CI pipelines that run on every push regardless of scope waste
minutes, energy, and attention. Documentation-only changes should not
trigger full test suites. Tag pushes should not re-run branch CI.
Advisory only — every project's CI budget is different.

**How:** Inspect `.github/workflows/*.yml` for efficiency signals.

**Severity:** WARNING — advisory. CI efficiency is project-dependent and
there is no single correct configuration.

Signals evaluated:

| Signal | Efficient | Inefficient |
| :----- | :-------- | :---------- |
| Trigger scoping | Separate workflow for docs/CI/release | Monolithic workflow triggers on everything |
| `paths-ignore` | Excludes `*.md` (docs) from build triggers | No `paths-ignore` — docs trigger full CI |
| Tag handling | Tag pushes skip build (release is manual) | Tag pushes re-run the full pipeline |
| Caching | `actions/cache` for dependencies | No cache — fresh install every run |
| Guard workflow independence | Standalone guard workflow (e.g. trailer check) | Guard embedded in main build — doc-only pushes skip it |
| Artifact separation | Ship/release workflow separate from test | Tests and shipping in same workflow |

If no `.github/workflows/` directory exists, skip this step.

---

### B10: `.gitignore` + repository metadata audit

**Why:** Missing or incomplete `.gitignore` files let build artifacts,
OS junk, agent state, and credential-adjacent files leak into commits.
Undocumented instruction-file conflicts (e.g. `AGENTS.md` + `CLAUDE.md`
both present with no documented precedence) create invisible divergence
in agent behavior.

**How:** Check six categories:

| # | What it checks | If missing |
| :- | :------------- | :--------- |
| 1 | `.gitignore` exists at repo root | WARNING |
| 2 | Agent-artifact patterns covered | `.open-mem/`, `.omo/`, `.aider.*`, `CLAUDE.local.md`, `.claude/**/*.log`, `AGENT.md`, `GEMINI.md` |
| 3 | OS junk covered | `.DS_Store`, `Thumbs.db`, `*.swp`, `*.swo`, `*~` |
| 4 | Language build artifacts | `node_modules/`, `__pycache__/`, `*.pyc`, `target/`, `dist/` |
| 5 | IDE files covered | `.vscode/`, `.idea/`, `*.sublime-*` |
| 6 | Instruction-file conflicts | Flag if 2+ of `[AGENTS.md, WARP.md, .rules, CLAUDE.md, GEMINI.md, .github/copilot-instructions.md]` co-exist |

**Severity:** WARNING — missing `.gitignore` is advisory; incorrect
exclusions may block builds. Instruction-file conflicts are flagged for
manual review (no automated resolution).

**How to check each category:**

- **1:** `test -f .gitignore`
- **2-5:** If `.gitignore` exists, read it and grep for each pattern listed
  above. Emit the missing pattern names, not the entire file.
- **6:** Walk the repo root for the listed filenames. If any two are found,
  list them and suggest documenting precedence in one of them.

**Remediation:** For missing patterns, add them to `.gitignore`. See
[references/gitignore-templates.md](references/gitignore-templates.md) for
the recommended patterns from Agents.gitignore and per-language templates.
For instruction-file conflicts, pick one primary file and reference the
other from it, or document the precedence order in a comment.

If `.gitignore` already covers a pattern, skip that check silently.

---

### B11: Co-author guard

**Why:** Commit trailers (`Co-authored-by:`, `Signed-off-by:`,
`Helped-by:`, `Reviewed-by:`) encode attribution and responsibility.
Accidental or automated trailers create permanent history artifacts that
misrepresent who did what. Prevention is better than rewrite.

**Severity for B11:**

| Sub-step | What it does | Severity |
| :------- | :----------- | :------- |
| B11a     | Agent MUST NOT rule for attribution trailers | N/A (instruction) |
| B11b     | CONTRIBUTING.md policy documentation | N/A (documentation) |
| B11c     | Shared Python checker + commit-msg hook | BLOCKING |
| B11d     | CI enforcement over commit range | BLOCKING |

**How:** The enforcement is four-layer, from policy to automated blocking.
See [references/co-author-guard.md](references/co-author-guard.md) for the
full implementation, hook template, CI config, and counter-indications.

#### B11a: Agent instruction layer

Add a MUST NOT rule to the project's agent instruction file (AGENTS.md,
CLAUDE.md, or equivalent): agents must not include `*-by:` attribution
trailers in commit messages. The exact wording is in the reference file.

#### B11b: Policy layer

Add a "Commit trailers" section to CONTRIBUTING.md documenting the policy
and the `ALLOW_ATTRIBUTION_TRAILERS=1` bypass mechanism.

#### B11c: Technical layer (shared checker + hook)

A single Python script (`scripts/check-commit-trailers.py`) serves both
local commit hooks and CI. It uses a generic `*-by:` regex to catch all
attribution trailer variants without maintaining a blocklist.

Install the hook:

```bash
cat > .git/hooks/commit-msg << 'HOOK'
#!/usr/bin/env bash
set -euo pipefail
exec python3 "$(git rev-parse --show-toplevel)/scripts/check-commit-trailers.py" "$1"
HOOK
chmod +x .git/hooks/commit-msg
```

The checker has a `--self-test` mode for CI-verifiable integrity.

#### B11d: CI enforcement

Run the same checker over the commit range on every push or PR:

```bash
python3 scripts/check-commit-trailers.py --range origin/main..HEAD
```

The `--range` mode iterates each commit in the range and applies the same
detection logic as the local hook. Use the `ALLOW_ATTRIBUTION_TRAILERS=1`
env var for bypass at both hook and CI level.

**Counter-indications:** Pair-programming teams, mailing-list workflows,
and single-contributor repos may want to skip B11 entirely. See the
reference file for details and `.repo-health.json` skip configuration.

---

## Phase C — Reverse Sync

**Why:** Many projects produce runtime artifacts deployed to system directories
(Hermes skills, config mirrors, HQ clones, build outputs). The repo is source
of truth; the installed copy is the deployed target.

See [references/sync-targets.md](references/sync-targets.md) for the complete
C1-C4 procedures:

| Step | What it does                          | Key detail                              |
| :--- | :------------------------------------ | :-------------------------------------- |
| C1   | Detect sync targets (5 types)         | Heuristic clues + `.repo-health.json`   |
| C2   | Verify pre-sync state                 | No BLOCKING items from Phase B          |
| C3   | Execute sync per target type          | Default commands + local fallback       |
| C4   | Verify post-sync — runtime + drift    | File walk or `diff -rq` per target type |

Phase B gates Phase C: never sync a broken repo.

---

## `.repo-health.json` — Per-project overrides

Projects that want explicit configuration can add a `.repo-health.json` at
their root. The skill checks for this file at the start of each phase and
uses its values when present.

See [references/repo-health-json-schema.md](references/repo-health-json-schema.md)
for the full schema specification, field descriptions, and usage notes.

If absent → all heuristics used. If present with partial data → missing
fields fall back to heuristics. A project should only add this file when
heuristics give wrong results or when explicit control is needed.

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

- [Agent Instruction Ecosystem](references/agent-instruction-ecosystem.md) — Portability tiers and adaptation paths for multi-forge projects
- [Anti-Drift Proportionality](references/anti-drift-proportionality.md) — When to add a check vs when to wait
- [Co-Author Guard](references/co-author-guard.md) — Four-layer enforcement for attribution trailers
- [Drift Pairs](references/drift-pairs.md) — Reusable cross-commit detection patterns
- [Heuristic Discovery](references/heuristic-discovery.md) — B1-B6 and B8 detection tables, severity, remediation
- [.gitignore Templates](references/gitignore-templates.md) — Official templates, agent-artifact patterns, per-language recommendations
- [Repo Health JSON Schema](references/repo-health-json-schema.md) — Full schema specification and field documentation
- [Sync Targets](references/sync-targets.md) — C1-C4 procedures and target types
- Conventional Commits: https://www.conventionalcommits.org/
- Keep a Changelog: https://keepachangelog.com/
- Semantic Versioning: https://semver.org/
- Shellcheck: https://www.shellcheck.net/
- GitHub CLI release docs: `gh help release`
