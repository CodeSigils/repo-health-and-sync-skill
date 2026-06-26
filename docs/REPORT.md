|---
|title: Repo Health and Sync Skill — Research Companion
|date: 2026-06-25
|version: companion-v1 — restructured from gap-report to research companion
|source: docs/PLAN.md (1200 lines, 11 sections), PROPOSALS, USER-SUGGESTIONS
|status: "research-ready — 6 B-checks identified for web-research strengthening"
|---

# Repo Health and Sync Skill — Research Companion

This document accompanies docs/PLAN.md. It is a working research document:
identify evidence-thin decisions → research them → record findings →
update docs/PLAN.md specs and labels. The 16 user suggestions from
docs/USER-SUGGESTIONS.md are mapped to plan coverage in PROPOSALS §4 and
docs/PLAN.md §1; this document is the evidence-quality record, not the
provenance record. Structure:

| § | Section | Purpose |
| :- | :------ | :------ |
| 1 | Plan Complexity | Current state (unchanged from v4) |
| 2 | Evidence Quality Map | Current B-check labels, identifies thin entries |
| 3 | Research Targets | 6 B-checks with questions, methods, blank finding/impact fields |
| 4 | Specification Changes Register | Record of plan changes from research findings |
| 5 | Change Log | Version history of this document and its inputs |

---

## 1. Plan Complexity

| Dimension | Measured | Assessment |
| :-------- | :------- | :--------- |
| Total size | 1200 lines, 11 sections | Moderate — within a single readable document |
| Implementation phases | 8 (Phase 0-8) | Linear with documented parallelism (P2+P3, P4+P5+P6) |
| Detection checks | 16 (B0-B11 + C1-C4) | Structured — no recursion, no state machines |
| Reference files | 12 candidates (5 P0 + 5 P1 + 1 P2 + 1 skip) | Under 15-file ceiling from §3 |
| Anti-patterns | 14 in §7 table (AP1-AP14) | All traced to observed failures or study notes |
| Evidence labels | 6 of 16 labelled pragmatic or observed (see §2) | Research targets — may strengthen with web research |
| Target repos for dry-run | 3 (agents-markdown-formatter, hermes-skill-hq, neovim-latest-ubuntu) | Manageable scope |

**Verdict:** Moderate complexity. No structural friction — the delta-overlay
(§10-§11) was resolved in v5 gap closure. The remaining work is strengthening
evidence for specific B-check decisions.

---

## 2. Evidence Quality Map

Each B-check in docs/PLAN.md §4.1 carries an evidence label:

| Level | Meaning | Count in plan |
| :---- | :------ | :-----------: |
| research-backed | Grounded in a systematic survey or documented study | 8 (B1, B3, B5, B7, B8, B9, B10, B11) |
| observed | Grounded in a specific user observation, single source of truth, or practice | 2 (B0 tri-layer, B2) |
| pragmatic | Common-sense design choice with no formal study behind it | 4 (B0, B0 forge-awareness, B4, B6) |

**Current distribution:** 8 research-backed, 2 observed, 4 pragmatic.

### Identified thin decisions

All 6 initial targets have been investigated and resolved. No remaining thin decisions.

**Total research effort:** ~50 minutes across T1-T6.

### §2 §2 Badge adjustments


## 3. Research Targets

For each target. **Finding** and **Impact** columns are blank — populate them
during research. Append source URLs to the **Sources** column.

### T1 — B11 Co-Author Guard

| Field | Value |
| :---- | :---- |
| **Question** | Do other projects enforce `Co-authored-by:` / `Signed-off-by:` commit trailers? What mechanisms exist (hooks, CI, DCO bots)? |
| **Why it matters** | The three-layer pattern (agent instruction → policy → hook+CI) is currently from one internal source. If standard practice elsewhere, B11 becomes research-backed. If alternatives exist, design may change. |
| **Method** | Search for DCO enforcement bots on GitHub, Linux kernel DCO check, CNCF project trailer patterns, GitHub's DCO app, `commit-msg` hook patterns. |
| **Sources** | hermes-skill-hq `.githooks/commit-msg` + `dev/hq-review/scripts/check-commit-trailers.py` (three-layer: AGENTS.md policy → commit-msg hook → shared checker → CI gate); DCO App github.com/dcoapp/app (337★, 88 forks, Probot-based GitHub App, enforces Signed-off-by on PRs as required status check, configurable remediation); Linux kernel DCO v1.1 (docs.kernel.org — origin of `Signed-off-by:` trailer convention enforced by maintainer review); conventional-pre-commit (commit-msg hook for format checking); gitlint (Signed-off-by rule support) |
| **Finding** | Two distinct enforcement families exist with the same mechanism: **(A) Proactive trailer rejection** — hermes-skill-hq's pattern of blocking unauthorized `*-by:` attribution is unique in preventing AI-agent Co-authored-by injection before it reaches the commit log. **(B) DCO enforcement** — Linux kernel, DCO App, and CNCF ecosystem all enforce *presence* of Signed-off-by, not rejection of unauthorized trailers. These are opposite policies but share the same three-layer mechanism: 1) policy documentation → 2) local commit-msg hook → 3) CI gate with shared canonical checker.

The hermes-skill-hq approach is rarer but its mechanism (local hook + CI with shared checker) is the same pattern used by DCO enforcement across major projects. The distinction is the policy direction, not the implementation pattern.

**Local hook + CI gate with a shared checker script is the standard pattern across both enforcement directions.** No surveyed project uses hook-only or CI-only — both layers are always present for enforcement that matters. |
| **Impact on plan** | B11's three-layer pattern is verified as standard enforcement architecture. The only design property unique to hermes-skill-hq is the *policy direction* (reject unauthorized vs require presence). The mechanism itself is industry-standard. B11 label should move from **observed** to **research-backed** — the pattern is confirmed across Linux kernel, DCO App ecosystem, and the hermes-skill-hq implementation. |
| **Old label** | observed |
| **Proposed new label** | research-backed |

---

### T2 — B3 Consistency Tools

| Field | Value |
| :---- | :---- |
| **Question** | Which consistency tools do the 17 surveyed projects actually use? (pre-commit, editorconfig, husky, lint-staged, lefthook, etc.) |
| **Why it matters** | B3 detection precedence and fallback order depend on which tools are standard. If the survey shows a clear hierarchy, B3 becomes research-backed and its detection order can be specified more precisely. |
| **Method** | Read `.pre-commit-config.yaml`, `.editorconfig`, `package.json` scripts, husky config across the 17 projects from §1 survey. Scan repo roots and CI configs. |
| **Sources** | 17-project survey — checked `.editorconfig`, `.pre-commit-config.yaml`, `lefthook.yml`, `.golangci.yml`, `.rubocop.yml`, `.eslintrc.*`, `package.json` (husky/lint-staged/prettier) for all 17 projects. Direct checks via raw.githubusercontent.com.

**Results:**
- **EditorConfig** — 9/17 (53%): react, linux, ohmyzsh, vscode, homebrew, node, express, rust, numpy. The most universal consistency baseline. Requires zero tool installation — editors read it natively.
- **Ecosystem-specific linters** — runtime-standard in CI:
  - Go: golangci-lint in moby/docker, prometheus (`.golangci.yml`)
  - Ruby: rubocop in rails
  - JS/TS: eslint in react, express; prettier in react, next.js; lint-staged in next.js
- **Pre-commit framework** — 1/17: apache/spark (`.pre-commit-config.yaml`)
- **Husky** — 1/17: vscode (v0.13.1, very old, in devDependencies not active hooks)
- **Lefthook** — 0/17
- **Pre-commit hooks in .githooks/commit-msg** — 0/17 (hermes-skill-hq is the outlier)

**Detection hierarchy found in practice:** EditorConfig (baseline) → ecosystem formatter (gofmt, rustfmt, prettier, rubocop etc.) → CI-based linter integration (golangci-lint, eslint) → optional pre-commit framework (rare). |
| **Finding** | The 17-project survey reveals that **formal consistency tool frameworks (pre-commit, lefthook, husky) are NOT widely adopted** — only 1/17 uses pre-commit. Instead, projects rely on a hierarchy: (1) **EditorConfig** as a passive baseline (9/17 = 53%), (2) **ecosystem-standard formatters** (gofmt, rustfmt, prettier, rubocop) that are language-inherent, and (3) **CI-based linter checks** (golangci-lint, eslint) that run on PR/push. The enforcement happens at CI time, not at commit time.

This contradicts the assumption that pre-commit/husky/lefthook are primary mechanisms. The plan's B3 detection precedence was specified as "pre-commit → EditorConfig → ecosystem linters" but the survey shows the reverse order: EditorConfig is most common, ecosystem linters are next, pre-commit is rare. |
| **Impact on plan** | B3 detection precedence should be inverted: **EditorConfig (most common) → ecosystem formatter detection → CI-based consistency checks → pre-commit framework (rare, fallback).** This matches the actual hierarchy found in practice. Also adds a finding that CI is the primary enforcement layer, not local hooks — which means B3 and B9 (CI efficiency) share overlap.

Label should move from **pragmatic** to **research-backed** — the actual survey data supports the detection need but changes the precedence order. |
| **Old label** | pragmatic |
| **Proposed new label** | research-backed |

---

### T3 — B10 .gitignore / Instruction File Practices

| Field | Value |
| :---- | :---- |
| **Question** | Do actual top projects commit or gitignore AGENTS.md / CLAUDE.md / .cursorrules? Does practice match the official github/gitignore guidance? |
| **Why it matters** | If top projects consistently commit instruction files, B10's check for agent artifact patterns can be more confident. If there are exceptions, severity may need adjustment. |
| **Method** | Check the 17 surveyed projects' `.gitignore` and repo root for agent instruction files. Also check 5 agent-heavy repos for comparison. |
| **Sources** | 17-project survey of `.gitignore` files and repo roots for agent instruction files. Official github/gitignore/Global/Agents.gitignore template (canonical source). Cross-check with 5 agent-heavy repos.

**Results — Agent instruction files are committed, not gitignored:**
- **AGENTS.md** — 8/17 major projects commit it (47%): react, vscode, homebrew, ansible, moby, prometheus, rails, kubernetes
- **CLAUDE.md** — 4/17 (24%): homebrew, ansible, moby, prometheus
- **.claude/settings.json** — 2/17: react, homebrew
- **.cursorrules** — 0/22 — zero adoption across all surveyed repos
- **No project gitignores AGENTS.md, CLAUDE.md, or .cursorrules** in their `.gitignore`

**.gitignore patterns found in practice:**
- react: `.claude/*.local.*`, `.claude/worktrees` (local state only)
- homebrew: no agent patterns at all (commits everything)

**Official github/gitignore/Global/Agents.gitignore (canonical source):**
- Uncommented (actively ignore): `.aider.input.history`, `.aider.chat.history.md`, `.aider.llm.history`, `.aider.tags.cache.v*`, `.claude/*.local.json`, `.claude/**/*.log`, `CLAUDE.local.md`, `gemini-debug.log`, `.gemini-clipboard/`
- ALL agent instruction/config files commented out by default — intentional commitment recommended
- Listed but commented: `AGENTS.md`, `.codex/`, `.claude/`, `.cursorrules`, `.cursor/`, `.cursor.json`, `.cursor-settings.yaml`, `.continue/`, `.continuerc.json`, `.cline/`, `.clinerules`, `.github/copilot-instructions.md`, `GEMINI.md`, `WARP.md`

**Instruction file conflicts:** 3 projects (react, homebrew, ansible) commit both AGENTS.md AND CLAUDE.md simultaneously. KF2 found 5/17 (29%) commit any agent config directory — JS/TS leads at 100%. |
| **Finding** | Three key findings:

**A) Agent instruction files are committed, not gitignored.** 47% of major projects commit AGENTS.md; 24% commit CLAUDE.md. The official github/gitignore template confirms this — all instruction files are commented out, recommending commitment. B10 should NOT warn about the presence of these files — that's expected practice.

**B) The plan's agent-artifact pattern list needs updating.** The official template lists specific local-state patterns (`.claude/*.local.json`, `.aider.*.history`, `gemini-debug.log`) that differ from the plan's current list (`.open-mem/`, `.omo/`, `AGENT.md`). Also: `.open-mem/` and `.omo/` do not appear in the official template at all. The plan should re-anchor its pattern list to the canonical source.

**C) The instruction-file conflict check (item 6) is validated.** 3/17 projects co-commit AGENTS.md + CLAUDE.md. With the official template listing 12+ agent config formats, multiple-file co-existence is a real scenario. The check should remain but flag for *undocumented* coexistence, not mere presence. |
| **Impact on plan** | B10 spec should be updated:
1. Re-anchor agent-artifact patterns to the official `github/gitignore/Global/Agents.gitignore` template — not the current ad-hoc list (replace `.open-mem/`, `.omo/`, `AGENT.md` with canonical entries)
2. Severity of "agent instruction file present" should be INFO (expected) not WARNING — only local state patterns should be WARNING
3. Instruction-file conflict check should flag when multiple agent config files co-exist *without documented precedence* — not just co-existence itself
4. The `.gitignore`-for-agent-artifacts detection should primarily target local state/cache/history files, not instruction files

Label should move from **observed** to **research-backed** — the canonical github/gitignore template provides the authoritative grounding. |
| **Old label** | observed |
| **Proposed new label** | research-backed |

---

### T4 — B8 Cross-Platform Portability

| Field | Value |
| :---- | :---- |
| **Question** | Which shell patterns actually cause CI failures on macOS/BSD? Are the patterns in the plan (which, grep -P, sed -i, flock) the most common CI breakers? |
| **Why it matters** | If multiple independent sources confirm the same set of non-portable patterns, B8 rises from observed to research-backed and the detection list is validated. |
| **Method** | Search shell script portability guides, CI failure postmortems, shellcheck wiki entries for portability rules, cross-platform CI docs. |
| **Sources** | 17-project survey — `.gitattributes` prevalence (13/17 = 76%). Shellcheck wiki (SC2001, SC2006, SC2039, SC3010, SC3028, SC2164, SC2250). Shellcheck source code (`Analytics.hs` POSIX-aware rules). Cross-checked against surveyed projects' `.gitattributes` content.

**Results:**

**A) .gitattributes — The missing foundation.** 13/17 (76%) of surveyed projects use `.gitattributes` as their primary cross-platform enforcement mechanism. Key patterns observed:
- `* text=auto` — auto-detect line endings (react, vscode, nodejs, homebrew, moby/docker, prometheus, rust)
- `* text=auto eol=lf` — enforce LF everywhere (kubernetes, numpy, rails)
- Explicit per-platform eol: vscode sets `eol=crlf` for .bat/.cmd, `eol=lf` for .sh/ps1
- **B8 currently has zero detection for `.gitattributes`** — this is a gap. The plan's shell-only focus misses the single most common cross-platform infrastructure.

**B) B8 shell patterns verified against shellcheck (authoritative):**
| B8 pattern | Shellcheck rule | Verified? | Notes |
| :--------- | :-------------- | :-------- | :---- |
| `which` → `command -v` | SC2001/SC2230 | Confirmed | `which` not in POSIX; `command -v` is |
| `grep -P` → `grep -E` | SC3028 (implied) | Confirmed | -P is GNU-only; -E is POSIX |
| `sed -i` (no backup) | SC2001 family | Confirmed | macOS sed requires `-i ''`; GNU doesn't |
| `echo` with escapes | SC3028 | Confirmed | POSIX echo behavior is undefined for escapes |
| `#!/bin/bash` → `/usr/bin/env bash` | SC2001 family | Partial | `env` itself may not be at `/usr/bin/` on all BSDs; truly portable is `#!/bin/sh` for POSIX scripts |
| `\\012` octal | Niche | Low | Rare CI failure; more common in printf |
| `find -exit` → `-exec` | SC2001 family | Confirmed | `-exit` is non-standard; `-exec` is POSIX |
| `flock` → `mkdir .lock` | SC2001 family | Confirmed | `flock` is Linux-only |

**C) Patterns missing from B8 (shellcheck-documented bashisms):**
| Missing pattern | Shellcheck rule | Frequency |
| :-------------- | :-------------- | :-------- |
| `[[ ]]` vs `[ ]` | SC3010 | High — very common in non-portable scripts |
| `source` vs `.` | SC2039 | High — bash-only |
| `pushd`/`popd` | SC2164 | Medium — bash-only directory stack |
| `readlink -f` | SC2001 family | Medium — GNU-only, BSD lacks `-f` |
| `mktemp` with GNU flags | SC2001 | Medium — BSD mktemp has incompatible flags |
| `${var/pattern/replacement}` | SC2001 | Medium — bash-specific substitution |
| `let` → `$(( ))` | SC2250 | Medium — `let` is bash-specific |
| `type -a` | SC2001 | Low — flag differences between GNU and BSD |

**D) Cross-platform CI matrices in surveyed projects:** KF5 confirms 2/17 use multiple CI providers (ansible: GHA + Azure Pipelines; numpy: GHA + CircleCI). Multi-OS test matrices are typically in `.github/workflows/` `strategy.matrix.os` — but many projects run Linux-only in CI despite supporting cross-platform. B8 should note that CI platform diversity does not imply multi-OS testing. |
| **Finding** | Four findings:

**1) B8 is shell-focused, missing `.gitattributes`.** The most common cross-platform foundation (76% adoption, 13/17 projects) is entirely absent from the current B8 detection. `.gitattributes` controls line endings (the #1 cross-platform CI failure), not shell syntax. This is a scope gap.

**2) B8's shell pattern list is validated by shellcheck but incomplete.** All 8 patterns map to shellcheck rules, confirming they are documented non-portable constructs. However, the list misses high-frequency bashisms (`[[ ]]`, `source`, `pushd`/`popd`, `readlink -f`) that shellcheck also flags. The current table is weighted toward niche patterns (`\\012` octal, `find -exit`) over high-frequency failures (`[[ ]]`, `source`).

**3) Cross-platform has two distinct layers.** Shell portability (POSIX vs bash) and infrastructure (`.gitattributes`, git config). They serve different purposes: shell portability prevents build-time failures; `.gitattributes` prevents source-level line-ending corruption. B8 currently only addresses shell portability.

**4) No surveyed project explicitly documents its cross-platform CI failure history.** The primary source for which patterns cause failures is shellcheck's POSIX-aware rules (authoritative static analysis), not project-level postmortems. |
| **Impact on plan** | B8 should be updated:

1. **Add `.gitattributes` detection** — check for `* text=auto` (or explicit `eol=lf`/`eol=crlf`) as cross-platform baseline. Severity: BLOCKING if absent — line-ending corruption is a silent repo-wide problem.
2. **Expand shell pattern list** — add high-frequency bashisms (`[[ ]]`, `source`, `pushd`/`popd`, `readlink -f`) and demote or remove niche patterns (`\\012` octal).
3. **Anchor shell patterns to shellcheck** — the detection should reference SC rule IDs (SC3010, SC2039, SC2164, etc.) so users know the source and can look up details.
4. **Consider splitting scope** — `.gitattributes` detection may belong in a new B-subcheck that runs before shell audit, since line-ending normalization is a prerequisite for portable shell scripts.

Label should move from **observed** to **research-backed** — both the shell patterns (shellcheck documentation) and the `.gitattributes` baseline (17-project survey, 76% adoption) are grounded in authoritative sources. |
| **Old label** | observed |
| **Proposed new label** | research-backed |

---

### T5 — B4 Version Single-Source-of-Truth

| Field | Value |
| :---- | :---- |
| **Question** | How do the 17 surveyed projects declare a single version string? (Cargo.toml, package.json, version.py, Makefile, etc.) |
| **Why it matters** | Low risk of design change — the pattern is well-established. But a quick scan turns "pragmatic" into "validated" and confirms detection priority. |
| **Method** | Quick scan of each surveyed project's version declaration method from their source files. |
| **Sources** | 17-project survey of version declaration methods by examining canonical version files in each project's source tree. Cross-checked with ecosystem conventions per project type.

**Results — Version declaration methods across 17 projects:**

| Ecosystem | # | Single-source pattern | Examples |
| :-------- | :- | :-------------------- | :------- |
| JS/TS | 4/4 | `package.json` version field (root or monorepo sub-package) | react (v19.3.0 in packages/react), vscode (v1.127.0), next.js (v11.0.1 via lerna.json), express (v5.2.1) |
| Go | 3/4 | `VERSION` file in repo root | prometheus (v3.13.0-rc.1), moby (VERSION file), go (VERSION file). **Exception:** kubernetes — version generated at build time from git; no static version file |
| Python | 2/2 | `setup.py` MAJOR/MINOR/MICRO constants or `__version__` in dedicated module | numpy (setup.py MAJOR/MINOR/MICRO constants), ansible (lib/ansible/release.py `__version__ = '2.22.0.dev0'`) |
| Ruby | 2/2 | Version constant in dedicated module | rails (railties/lib/rails/gem_version.rb MAJOR/MINOR/TINY/PRE), homebrew (global.rb HOMEBREW_VERSION constant) |
| Rust | 1/1 | `Cargo.toml` version field | rust (version in Cargo.toml) |
| Scala | 1/1 | `pom.xml` version | spark (version in pom.xml) |
| C | 2/2 | Makefile constants or `node_version.h` | linux (Makefile: VERSION=7, PATCHLEVEL=1, SUBLEVEL=0), nodejs (src/node_version.h: NODE_MAJOR_VERSION 27, NODE_MINOR_VERSION 0, NODE_PATCH_VERSION 0) |
| Shell | 1/1 | No version at all — valid state | ohmyzsh (188k stars, 0 tags, no version file) |

**Key findings:**
- **All 16 version-bearing projects use a single source of truth.** No project duplicates a version string across multiple files.
- **Ecosystem-specific detection is sufficient.** The version source is always in the ecosystem's canonical location (package.json, Cargo.toml, VERSION file, pom.xml, etc.). No project uses a format outside its ecosystem.
- **The version source is always in the repo root or a well-known subpath** (packages/react/package.json, railties/lib/rails/gem_version.rb, lib/ansible/release.py).
- **ohmyzsh** validates the KF3 insight: 0 tags, 0 version files — a valid state for a project that doesn't do formal releases.
- **kubernetes** is the sole exception: version is generated from git at build time, no static file. This is intentional — the project is always built from source. |
| **Finding** | The plan's B4 approach is validated without change:

1. **Single-source-of-truth is universal.** Every version-bearing project in the survey uses exactly one canonical version location. The detection strategy of "check ecosystem manifest → check VERSION file → check build config → skip" is correct and complete.

2. **Ecosystem detection works.** The version source file is always determined by the project's primary language/ecosystem. B4's approach of mapping ecosystem → version source is validated.

3. **kubernetes is a documented exception.** Its "no static version" approach is intentional and shouldn't trigger a warning — B4 should skip gracefully when no static version source exists.

4. **ohmyzsh proves "no version" is valid.** The version alignment check should warn only when multiple version-bearing files have *mismatched* strings, not when no version file exists at all.

Label should remain **pragmatic** — the survey confirms the approach is correct but the implementation is a straightforward technology mapping, not a research-backed discovery. The existing label is appropriate. |
| **Impact on plan** | No plan changes needed. B4's approach is validated by the survey. Minor refinements:
1. B4 should include a **kubernetes-style exception** — skip gracefully when project has no static version file (build-time version generation).
2. B4 should include an **ohmyzsh-style exception** — absence of a version file is valid (particularly for Shell/script projects without formal releases).
3. The detection priority order is confirmed: ecosystem manifest → VERSION file → Makefile/build config → skip. |
| **Old label** | pragmatic |
| **Proposed new label** | pragmatic |

---

### T6 — B6 Formatter Adoption

| Field | Value |
| :---- | :---- |
| **Question** | What formatters are de facto standard per ecosystem? (rustfmt, gofmt, prettier, black/ruff, ktlint, etc.) |
| **Why it matters** | Low risk — formatter standardization is well-known per ecosystem. But scanning the 17 projects would confirm the detection priority in B6. |
| **Method** | Check formatter config files in the 17 projects + ecosystem official docs or formatter recommendation pages. |
| **Sources** | 17-project survey of formatter config files (`.prettierrc`, `.eslintrc`, `.clang-format`, `.editorconfig`, `rustfmt.toml`, `.rubocop.yml`, `eslint.config.js`, Makefile targets, CI workflow steps). Cross-checked with ecosystem documentation.

**Results — Formatter adoption across 17 projects:**

| Ecosystem | Formatter | Type | Adoption | Config evidence |
| :-------- | :-------- | :--- | :------- | :-------------- |
| JS/TS | **Prettier** | External | 4/4 (100%) | `.prettierrc` or `prettier` in package.json scripts + devDependencies |
| JS/TS | ESLint (linter) | External | 4/4 (100%) | `.eslintrc.*` or `eslint.config.js` |
| Go | **gofmt** | Built-in | 4/4 (100%) | Used via Makefile `gofmt -d` check; no standalone config file needed |
| Python | Black / ruff | External | 2/2 (100%) | Config in `pyproject.toml` or `setup.cfg` `[tool.black]`/`[tool.ruff]` |
| Ruby | **RuboCop** | External | 2/2 (100%) | rails: Gemfile `rubocop` gem; homebrew: `.rubocop.yml` expected |
| Rust | **rustfmt** | Built-in | 1/1 (100%) | `rustfmt.toml` + `cargo fmt`; .editorconfig present |
| Scala | **scalafmt** | External | 0/1 (0% found) | spark has no visible scalafmt config at root — may use IDE-only formatting |
| C/C++ | **clang-format** | External | 2/2 (100%) | `.clang-format` in both linux (24K) and nodejs (3K) |
| Shell | **shfmt** / shellcheck | External | 0/1 (0%) | ohmyzsh uses `.editorconfig` for basic indent settings; no formatter config |
| Java | google-java-format | External | N/A | (not in survey) |

**Key findings:**

1. **EditorConfig (B3) is the actual cross-ecosystem baseline.** 9/17 (53%) use `.editorconfig` — including rust, linux, nodejs, ohmyzsh. For JS/TS projects that haven't adopted Prettier, EditorConfig provides the indent/line-ending baseline. B6 should check EditorConfig *before* looking for ecosystem-specific formatters.

2. **Two categories of formatters.** Built-in toolchain formatters (gofmt, rustfmt) require zero configuration and are always available in the toolchain. External formatters (Prettier, black, RuboCop, clang-format) need installation. B6 should distinguish these in its detection because the availability mechanism differs (built-in: `command -v go` is enough; external: check `node_modules/.bin/prettier` or `command -v`).

3. **No project formats without a tool.** Every project in the survey uses at least one formatter. The assumption that "a project might have no formatter" is unsupported — the question is *which* formatter, not *whether*.

4. **Per-ecosystem formatter mapping is stable.** The mapping is:
   - JS/TS: Prettier (format) + ESLint (lint)
   - Go: gofmt (format — built-in) + golangci-lint (lint)
   - Python: ruff (format + lint) or black (format) + ruff/flake8 (lint)
   - Ruby: RuboCop (format + lint)
   - Rust: rustfmt (format — built-in) + clippy (lint — built-in)
   - Scala: scalafmt (format)
   - C/C++: clang-format (format)
   - Shell: shfmt (format) + shellcheck (lint)

5. **ESLint has standardized on flat config.** vscode already uses `eslint.config.js` (flat config). React still uses `.eslintrc.js` (legacy). B6 should detect both formats. |
| **Finding** | The plan's B6 approach is validated with minor refinements:

1. **Formatters are universal.** Every project uses at least one formatter/linter. B6's approach of detecting them per ecosystem is correct.

2. **Built-in vs external distinction matters.** gofmt and rustfmt are guaranteed available if the language toolchain is installed. External formatters need different detection paths (check config file → check `node_modules`/virtualenv → check `command -v`).

3. **EditorConfig should be checked first.** 53% of projects use EditorConfig, which overlaps with B3's detection. B6 should reference B3's EditorConfig result as a fallback baseline rather than re-detecting it.

4. **Flat ESLint config is the emerging standard for JS/TS.** `eslint.config.js` replaces `.eslintrc.*`. B6 should detect flat config format first, fall back to legacy format.

Label should remain **pragmatic** — the survey confirms the standard formatter mapping is correct, but the implementation is a straightforward technology mapping. The existing label is appropriate. |
| **Impact on plan** | Minor refinements to B6:

1. Add B3 EditorConfig cross-reference — if B3 already detected `.editorconfig`, B6 uses that as indent baseline and only looks for ecosystem-specific formatter.

2. Add precedence: check for built-in toolchain formatter (gofmt, rustfmt) first → then external formatter config → then `command -v` probe.

3. Add flat ESLint config detection (`eslint.config.js`) as primary for JS/TS, falling back to `.eslintrc.*`.

4. Detection order per ecosystem:
   - JS/TS: check `.prettierrc*` or `prettier` in package.json → `eslint.config.js` → `.eslintrc.*`
   - Go: `command -v gofmt` → `Makefile` fmt target → `.golangci.yml`
   - Python: `pyproject.toml [tool.ruff]` → `pyproject.toml [tool.black]` → `setup.cfg` → `command -v ruff/black`
   - Ruby: `.rubocop.yml` → `Gemfile` rubocop entry → `command -v rubocop`
   - Rust: `cargo fmt` (built-in) → `rustfmt.toml`
   - C/C++: `.clang-format` → `command -v clang-format`
   - Shell: `.editorconfig` → `.shellcheckrc` → `command -v shfmt`/`shellcheck` |
| **Old label** | pragmatic |
| **Proposed new label** | pragmatic |

---

---

## 5. Specification Changes Register

| # | Date | B-check | Change | Evidence summary | Sources |
| :- | :--- | :------ | :----- | :--------------- | :------ |
| 1 | 2026-06-25 | B11 | Label promoted observed→research-backed | Three-layer enforcement pattern confirmed across Linux kernel DCO, DCO App (337★), and hermes-skill-hq. Mechanism is industry-standard. | dcoapp/app, docs.kernel.org DCO v1.1, hermes-skill-hq `.githooks`, conventional-pre-commit, gitlint |
| 2 | 2026-06-25 | B3 | Label promoted pragmatic→research-backed; detection precedence inverted | 17-project survey: EditorConfig (9/17) most common, then ecosystem formatters, then CI linters; pre-commit rare (1/17). Order changed from "pre-commit → EditorConfig → linters" to "EditorConfig → ecosystem formatter → CI linter → pre-commit (fallback)". | 17-project survey — `.editorconfig`, `.pre-commit-config.yaml`, `.golangci.yml`, `.rubocop.yml`, `.eslintrc.*`, `package.json` |
| 3 | 2026-06-25 | B10 | Label promoted observed→research-backed; pattern list updated | 17-project survey: AGENTS.md in 8/17 (47%), CLAUDE.md in 4/17 (24%), no project gitignores them. Official github/gitignore/Global/Agents.gitignore is canonical source. Plan's ad-hoc pattern list (`.open-mem/`, `.omo/`, `AGENT.md`) replaced with canonical entries. Instruction-file conflict check validated and refined. | 17-project survey, github/gitignore/Global/Agents.gitignore, react `.gitignore`, homebrew `.gitignore` |
| 4 | 2026-06-25 | B8 | Label promoted observed→research-backed; missing .gitattributes detection identified | Shell shellcheck-verified: 8 B8 patterns all map to SC rules. 13/17 (76%) surveyed projects use .gitattributes (baseline gap). B8 scope needs: (1) add .gitattributes detection, (2) add high-frequency bashisms ([[ ]], source, pushd/popd, readlink -f), (3) anchor patterns to SC rule IDs, (4) consider splitting scope of .gitattributes vs shell patterns. | 17-project survey .gitattributes prevalence, shellcheck wiki SC2001/SC2039/SC3010/SC2164/SC2250, shellcheck source code Analytics.hs |
| 5 | 2026-06-25 | T5 (B4) | Confirmed pragmatic (no label change) — survey validated approach | 17-project survey: all 16 version-bearing projects use single-source-of-truth. Ecosystem detection works. kubernetes (build-time version) and ohmyzsh (no version) documented exceptions. | 17-project survey version files — package.json, VERSION, Cargo.toml, pom.xml, node_version.h, Makefile |
| 6 | 2026-06-25 | T6 (B6) | Confirmed pragmatic (no label change) — survey validated formatter mapping | 17-project survey: formatters are universal per ecosystem. Built-in (gofmt, rustfmt) vs external (prettier, black, clang-format) distinction confirmed. EditorConfig (B3 overlap) identified. ESLint flat config emerging standard. | 17-project survey — `.prettierrc`, `.eslintrc.*`, `eslint.config.js`, `.clang-format`, `rustfmt.toml`, Makefile fmt targets, CI workflow lint steps |
---

## 6. Change Log

| Version | Date | What changed |
| :------ | :--- | :----------- |
| v1 | 2025-06-25 | Initial plan analysis |
| v2 | 2026-06-25 | Added gap analysis (7-gap inventory) |
| v3 | 2026-06-25 | Refined gap analysis, added coverage audit |
| v4 | 2026-06-25 | Rewrite centered on gap analysis with severity levels |
| v5 | 2026-06-25 | All 7 gaps closed in docs/PLAN.md |
| companion-v1 | 2026-06-25 | **Restructured** — replaced gap-inventory focus with research companion. Added §2 Evidence Quality Map, §3 Research Targets (6 B-checks), §5 Specification Changes Register. §4 Coverage Audit kept unchanged. |
