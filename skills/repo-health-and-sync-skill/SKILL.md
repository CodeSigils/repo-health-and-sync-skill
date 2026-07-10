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
2. Run Phase B phases in order (B1 through B11).
3. If any BLOCKING item, stop and fix before continuing.
4. If the repo has a runtime target, run Phase C (C1 through C4).

Each phase section lists: **why** it matters, **how** to discover the
relevant files/config at runtime, **severity** when it fails, and
**remediation** when it fails.

### B0: Design principles (read before Phase B)

These principles govern all checks below. The agent should internalise them
before running any phase.

**Commit log vs CHANGELOG.** The git log is the authoritative historical
record. Some projects produce well-structured commits that serve as their
own release documentation. For those, requiring a CHANGELOG creates a
duplicate drift surface (AP1). The agent checks three conditions:
- Project uses conventional commits or a consistent structured format
- 90%+ of recent commits have descriptive bodies (not just one-line subjects)
- Release notes can be generated from `git log tag..tag --format`

When all three hold, CHANGELOG absence should be INFO, not WARNING.
B7b and B7c apply this gate.

**Detect, don't enforce.** No convention is universal across ecosystems.
The skill discovers the project's existing patterns before imposing rules.

**Zero tags is valid.** ohmyzsh (188k stars) proves a project can thrive
without formal releases. Only stale tags matter, not absence of tags.

**Proportionate anti-drift.** Every check should trace to a specific observed
failure mode. Speculative checks accumulate maintenance debt before they
create value. If a check fires and you haven't seen this failure before,
consider disabling it rather than patching around it. See
`references/anti-drift-proportionality.md`.

The **two-question test** operationalises this principle before adding any
new check: (1) "What evidence says this check is necessary at our scale?"
and (2) "Will a human or runtime catch this failure faster than our CI?"
If a runtime or human would catch the failure before it causes harm, do not
add CI for it. Reserve CI for failure modes that have no cheaper validator.
This prevents infrastructure accretion — each proposed check must justify
itself against observed failure, not hypothetical risk.

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
for the adaptation path and portability tiers. The detection logic in B1-B11
and C1-C4 is agent-agnostic.

**Quality-skill fallback (quad-layer probe).** Before running a B-phase check
that depends on an external quality tool (shellcheck, linters, formatters),
the agent runs a cross-platform availability check:

1. `command -v <tool>` — check if the quality tool is on PATH directly
   (works on any system; this is the primary probe)
2. Config/project file check — look for ecosystem-equivalent config
   (`.pylintrc`, `.flake8`, `.ruff.toml`, `.prettierrc`, etc.) and run
   the tool directly if found
3. `skill_view(name)` — Hermes-specific optimization: verify a matching
   skill exists and loads. Skip this step on non-Hermes agents.
4. Degraded mode — if none resolve, skip the check and log which checks
   were skipped and why

If a step resolves, use it. Do not chain further: `command -v` succeeding
means the tool is used directly; only fall through to config-file probe
when the binary is absent, and to `skill_view()` only when both prior
probes fail and the agent is Hermes.

Per-check availability table:

| Check | Depends on | Fallback chain |
| :---- | :--------- | :------------- |
| B2 Shellcheck | `shellcheck` binary | `command -v shellcheck` → skip, log reason |
| B3 Lint | language lint tool | `command -v <tool>` → project config file → `skill_view(name)` → skip, log reason |
| B6 Format | `prettier` / `black` / `rustfmt` etc. | `command -v <tool>` → project config file → `skill_view(name)` → skip, log reason |

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

If missing, emit INFO. Consider adding a simple check for tree cleanliness
and version alignment (see B4).

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

If no tags are found, skip this step.

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
| B7b      | Runtime files changed but CHANGELOG didn't | Depends on commit quality (see below) |
| B7c      | No `## Unreleased` section despite commits since last tag | Depends on commit quality (see below) |
| B7d      | Source files changed but version unchanged | INFO (advisory) |
| B7e      | Commit body missing required fields (what:/why:) | WARNING |

#### B7a: Commit message audit

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
`commit_body_format.required_fields` (default: none, so this check is
a no-op unless explicitly configured).

**How:** Run `scripts/check-commit-body.py --range origin/main..HEAD`
(or the configured baseline). The checker reads `.repo-health.json` for
`required_fields` and `pattern`. Violations are WARNING by default
(configurable via `.repo-health.json`).

**Remediation:** Add the required fields to commit bodies. Bypass with
`ALLOW_ATTRIBUTION_TRAILERS=1` if needed.

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

The 8 detection patterns (`which`, `grep -P`, `sed -i` without backup,
`echo` with escapes, hardcoded `/bin/bash`, octal `\012`, `find -exit`,
`flock`) and their portable replacements are defined in:

See [references/heuristic-discovery.md](references/heuristic-discovery.md)
§ B8 for the full detection table, remediation, and `.repo-health.json`
skip configuration.

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
| **Trigger path completeness** | Path list covers README.md, SECURITY.md, and other docs that CI validates | Path list omits doc files — documentation-only changes silently skip CI checks. Proved real in production: agents-markdown-formatter had a doc fix committed with CI green, but the fix was never validated because README.md was missing from trigger paths. |

The trigger-path-completeness signal is the dual of `paths-ignore`: instead
of docs triggering too much CI, missing doc paths in the trigger list cause
docs to trigger NO CI at all. Check that every CI-validated file type has a
corresponding trigger path entry. If a workflow validates docs (preflight
wording, frontmatter, URL freshness), its trigger paths must include
`README.md`, `SECURITY.md`, and any doc directory. A stale trigger path
list can produce green CI on broken docs.

If no `.github/workflows/` directory is found, skip this step.

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

See also [references/format-consistency-audit.md](references/format-consistency-audit.md)
for a complementary check on file-internal structure (frontmatter,
code-fence labels, forbidden paths, required sections) that extends B10's
surface-level metadata audit into document-internal conventions.

---

### B11: Co-author guard

**Why:** Commit trailers encode attribution and responsibility. The primary
failure mode is `Co-authored-by:` — agents may auto-insert this trailer,
creating permanent history artifacts. Other `*-by:` trailers (`Signed-off-by:`,
`Reviewed-by:`, `Tested-by:`) are legitimate open-source practices (Linux
kernel DCO, CNCF, code review workflows).

| Trailer | Default treatment | Rationale |
| :------ | :---------------- | :-------- |
| `Co-authored-by:` | **BLOCKING** | Primary failure case — agents auto-insert this |
| `Signed-off-by:` | **Allow** | DCO requirement, Linux kernel, CNCF standard |
| `Reviewed-by:` | **Allow** | Code review practice, common in OSS |
| `Tested-by:` | **Allow** | Legitimate CI/test attribution |
| `Suggested-by:` | **Allow** | Common in OSS |
| `Helped-by:` | **INFO** (advisory) | Rarely legitimate in agent commits, but not malicious |
| Other `*-by:` | **BLOCKING** | Catch-all for unknown patterns |

The `ALLOW_ATTRIBUTION_TRAILERS=1` bypass exists for projects that want
to allow all trailers regardless.

**Severity for B11:**

| Sub-step | What it does | Severity |
| :------- | :----------- | :------- |
| B11a     | Agent MUST NOT rule for `Co-authored-by:` | N/A (instruction) |
| B11b     | CONTRIBUTING.md policy documentation | N/A (documentation) |
| B11c     | Shared Python checker + commit-msg hook | BLOCKING (for Co-authored-by:) |
| B11d     | CI enforcement over commit range | BLOCKING (for Co-authored-by:) |

**How:** The enforcement is four-layer, from policy to automated blocking.
See [references/co-author-guard.md](references/co-author-guard.md) for the
full implementation, hook template, CI config, and counter-indications.

#### B11a: Agent instruction layer

Add a MUST NOT rule to the project's agent instruction file (AGENTS.md,
CLAUDE.md, or equivalent): agents must not include `Co-authored-by:`
or other unauthorized `*-by:` attribution trailers in commit messages.
The exact wording is in the reference file.

#### B11b: Policy layer

Add a "Commit trailers" section to CONTRIBUTING.md documenting the policy,
which trailers are allowed by default, and the `ALLOW_ATTRIBUTION_TRAILERS=1`
bypass mechanism.

#### B11c: Technical layer (shared checker + hook)

A single Python script (`scripts/check-commit-trailers.py`) serves both
local commit hooks and CI. It uses a generic `*-by:` regex to catch all
attribution trailer variants, then applies an allow-list for legitimate
trailers (`Signed-off-by:`, `Reviewed-by:`, `Tested-by:`, `Suggested-by:`).

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

### B12: Cross-agent portability

**Why:** Agent skill files that reference platform-specific tools
(`skill_view`, `hermes skills`, `Claude()`, `.cursor/rules/`) break
silently on other runtimes. No runtime validates this — a Hermes agent
never complains about Hermes-specific refs, but a Codex agent silently
misreads the skill. Unlike B8 (shell portability), this checks the
skill instructions themselves, not helper scripts.

**Severity:** BLOCKING. A single agent-specific reference makes the skill
unusable on other runtimes, and the failure is invisible to the authoring
agent.

**Decision guidance — when to skip B12:** Platform-specific skills that
intentionally target one runtime do not need a portability gate. The check
should be skipped when the project frontmatter explicitly declares a single
target (e.g. `compatibility: hermes`) AND the body references are
intentional (documenting a platform-specific CLI, config path, or hook
mechanism). The agents-markdown-formatter is a validated example:
`compatibility: hermes` frontmatter, `~/.hermes/skills/` path references
in body, Hermes post-write hook config — all intentional. Adding a
portability gate to such a skill creates exemptions-driven noise with no
benefit.

When in doubt, apply the two-question test from B0: (1) "What evidence
says this check is necessary?" and (2) "Will a runtime catch this faster
than our CI?" If the skill is intentionally platform-specific, the answer
to (1) is "no evidence — this is a design choice, not drift."

**How:** Walk `skills/` for all `*.md` files and scan for forbidden
patterns. See [references/cross-agent-portability.md](references/cross-agent-portability.md)
for the full pattern table, severity rationale, and implementation
reference (generalized from skill-discovery's `ci-check.py`).

**What to check:**
- Hermes tool names (`skill_view`, `skill_manage`)
- Hermes config paths (`~/.hermes/`)
- Hermes CLI commands (`hermes skills`, `hermes config`)
- Claude Code tools (`Claude()`)
- Codex CLI commands (`codex run`, `$skill-installer`)
- Gemini CLI commands (`gemini skills`)
- Platform adapter directory paths (`.claude/`, `.cursor/`, `.codex/`, `.gemini/`)

Each match is BLOCKING. Report the file, line, and matched pattern.
If no skill files are found, skip this step.

**Content companion:** B12 checks portability. For skill *content quality* review
— rule schema compliance, example correctness, validation infrastructure
coverage, and router-table alignment — see `references/skill-content-review.md`.

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

## Real-world heuristic example

The heuristic detection was verified against `agents-markdown-formatter`: its
detection patterns resolved correctly without any hardcoded project metadata.

| Signal                | agents-markdown-formatter                        |
| :-------------------- | :----------------------------------------------- |
| B1: Branch            | main                                             |
| B1: Remotes           | 1                                                |
| B2: Shell scripts     | `scripts/release.sh`, `staged-install-verify.sh` |
| B3: Consistency check | `check-consistency.js`                           |
| B4: Version sources   | `package.json`, `SKILL.md`, README badge         |
| B5: Tag/Release       | 10 tags, 10 releases                             |
| C1: Sync target       | Hermes skill                                     |

---

## Common pitfalls

1. **GitHub Releases are not created from git tags automatically.** An
   annotated tag is a git object. `gh release create` is a separate step.

2. **Tags are not pushed with `git push` by default.** Use `git push --follow-tags`
   (preferred — only pushes annotated tags on the current commit) or push each tag
   individually with `git push origin <tag>`. Avoid bare `git push --tags` which
   pushes every local tag, including stale ones.

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

7. **Investigate CI/workflows/pre-commit/hooks before suggesting a version release tag.**
   Before proposing a release, the agent MUST verify:
   - All CI workflows pass (check `.github/workflows/*.yml`, `.gitlab-ci.yml`, etc.)
   - Pre-commit hooks run cleanly (`pre-commit run --all-files` or equivalent)
   - Commit-msg hooks pass (including co-author guard, commit body format checks)
   - Any project-specific consistency check (`scripts/check-consistency.js`, `make test`, etc.) exits 0
   - No uncommitted changes remain (`git status --porcelain` empty)
   - Version alignment check passes (B4)
   - Tag/release integrity passes (B5)
   
   Skipping this investigation leads to releasing broken builds — the most
   common observed failure mode. The agent should run Phase B checks explicitly
   and confirm all BLOCKING/WARNING items are resolved before suggesting
   `git tag -a` or `gh release create`.

8. **Verify installed skill paths match `.hermes/config.yaml` external_dirs.**
   Hermes loads skills from multiple locations. Before syncing (Phase C) or
   recommending installs, confirm:
   - `.hermes/config.yaml` → `skills.external_dirs` includes the project's
     skill directory (e.g., `/home/sand/projects/repo-health-and-sync-skill`)
   - `hermes skills list` shows the skill as "local" or "external" (not missing)
   - The synced target (`~/.hermes/skills/<name>/`) matches the repo source
     (`diff -rq` clean)
   - No stale symlinks or duplicate installations exist
   
   Mismatched paths cause agents to load stale skill versions while the
   repo has updates. This is a frequent source of "the fix didn't take" reports.

7. **CI trigger paths can silently exclude doc files.** A workflow with
   path-restricted triggers that omits `README.md`, `SECURITY.md`, or doc
   directories produces green CI on documentation-only changes — even when
   those changes break CI-validated invariants (preflight wording,
   frontmatter schema, URL freshness). Cross-reference the file types each
   CI job validates against the trigger path list. If a job validates docs,
   the trigger paths must include the doc files. See B9 trigger-path-completeness
   signal.

8. **`.repo-health.json` is optional.** If absent, the heuristic fallback
   is used. If present with partial data, missing fields fall back to
   heuristics. A project should only add it when heuristics give wrong
   results or when explicit control is needed.

9. **The Hermes `patch` tool can corrupt GFM table pipes.** When `|`
   appears in `patch`'s find/replace anchors, the matching layer can
   misalign and produce `||` (adjacent pipes). This is not a formatter
   bug — the markdown formatter handles `||` correctly. If you see
   unexplained double-pipe corruption in table rows after a `patch` call,
   check `references/patch-tool-table-corruption.md` for diagnosis and
   defense layers.

---

## References

- [Agent Instruction Ecosystem](references/agent-instruction-ecosystem.md) — Portability tiers and adaptation paths for multi-forge projects
- [Anti-Drift Proportionality](references/anti-drift-proportionality.md) — When to add a check vs when to wait
- [Co-Author Guard](references/co-author-guard.md) — Four-layer enforcement for attribution trailers
- [Cross-Agent Portability](references/cross-agent-portability.md) — Detection patterns and CI enforcement for B12; companion script at `scripts/check-portability.py`
- [Cross-Agent Refactoring](references/cross-agent-refactoring.md) — Converting a platform-specific skill to cross-agent consumption (companion to B12)
- [Drift Pairs](references/drift-pairs.md) — Reusable cross-commit detection patterns
- [Format Consistency Audit](references/format-consistency-audit.md) — Document-internal structure checks (extends B10)
- [Heuristic Discovery](references/heuristic-discovery.md) — B1-B12 detection tables, severity, remediation
- [Skill Content Review](references/skill-content-review.md) — Rule schema compliance, example correctness, validation infrastructure for skill repos (companion to B12)
- [Skill Repo Publication Checklist](references/skill-repo-publication-checklist.md) — P1-P8 checks for making a skill repo public (extends B1-B12)
- [.gitignore Templates](references/gitignore-templates.md) — Official templates, agent-artifact patterns, per-language recommendations
- [Repo Health JSON Schema](references/repo-health-json-schema.md) — Full schema specification and field documentation
- [Sync Targets](references/sync-targets.md) — C1-C4 procedures and target types
- Conventional Commits: https://www.conventionalcommits.org/
- Keep a Changelog: https://keepachangelog.com/
- Semantic Versioning: https://semver.org/
- Shellcheck: https://www.shellcheck.net/
- GitHub CLI release docs: `gh help release`
