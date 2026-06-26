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
and `target`. Run `shellcheck` on every `.sh` file found. Check script naming
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

- Conventional Commits: https://www.conventionalcommits.org/
- Keep a Changelog: https://keepachangelog.com/
- Semantic Versioning: https://semver.org/
- Shellcheck: https://www.shellcheck.net/
- GitHub CLI release docs: `gh help release`
