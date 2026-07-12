# Research — Repo Health and Sync Skill

> **v0.2.0 note:** This file describes the evidence base that informed the
> v0.1.0 design (B-phases, reference files, shipped scripts). The current
> skill (v0.2.0) is a methodology-only single SKILL.md. The research evidence
> here — ecosystem surveys, portability patterns, co-author guard analysis —
> still informed the methodology's design principles. None of the reference
> files cited below exist in the current repo.

**Purpose:** Evidence base that informed the decisions in `docs/decisions.md`.
Contains survey data, ecosystem tables, and research findings. This file is
the reference for *what was found*, not *what was decided*.

---

## 1. 17-project survey (ecosystem patterns)

17 top-starred projects across 9 language ecosystems inspected for: directory
structure, branch naming, tags, commit style, CI organization, scripts
directory, agent config files, agent instruction files, CHANGELOG approach,
and .gitattributes usage.

### Survey snapshot

| Ecosystem | Projects | Shared traits |
| :-------- | :------- | :------------ |
| Go (3) | golang/go, kubernetes, prometheus | No agent configs; `.github/` for CI; commit styles vary within ecosystem |
| JS/TS (4) | react, vscode, next.js, express | **100% agent config adoption** — only ecosystem where all projects commit them |
| Python (3) | django, ansible, numpy | Most diverse CI platforms (GitHub, Azure, CircleCI); 1/3 has agent config |
| Ruby (2) | rails, Homebrew | Homebrew is reference for CI workflow organization (14 separate files) |
| Rust (1) | rust-lang/rust | Built-in toolchain formatting (rustfmt); no agent config |
| C/C++ (2) | torvalds/linux, nodejs | `.clang-format` universal; no agent configs |
| Shell (2) | ohmyzsh, nvm | **ohmyzsh has zero tags** — proves absence of tags is not a defect |

### Key findings

**KF1 — No single commit convention dominates.** 10 distinct commit styles
across 17 projects. Conventional Commits is the plurality (29%) but not the
majority. Homebrew explicitly rejects conventional commits via CI workflow.
B7 must discover the prevailing style before checking consistency.

**KF2 — 29% of top projects commit agent configs.** 5/17 commit `.claude/`,
`.cursor/`, `.codex/`, `.agents/`, or `.vscode/` configs. JS/TS leads at
100% adoption. These are instruction files — committed, not gitignored.

**KF3 — Zero tags is a valid project state.** ohmyzsh (188k stars) has no
tags and no releases. The only actionable tag problem is *stale* tags, not
*absent* tags.

**KF4 — .gitattributes is the most common cross-platform mechanism.** 13/17
(76%) use `.gitattributes` for line-ending control. This is more common
than any shell portability pattern. B8 initially missed this entirely.

**KF5 — Pre-commit/husky/lefthook are NOT widely adopted.** Only 1/17
(apache/spark) uses pre-commit. Projects rely on EditorConfig (53%) →
ecosystem formatters → CI-based linting. Enforcement happens at CI time,
not commit time.

**KF6 — Formatters are universal.** Every project in the survey uses at
least one formatter/linter. The question is *which* formatter, not *whether*.
Built-in toolchain formatters (gofmt, rustfmt) require no config; external
formatters (prettier, black, clang-format) need installation.

---

## 2. Agent instruction ecosystem

Canonical instruction file per platform:

| Tool | Canonical file | Scoped extension |
| :--- | :------------- | :--------------- |
| Anthropic Claude Code | `CLAUDE.md` | `.claude/rules/`, `@path` imports |
| OpenAI Codex | `AGENTS.md` | `AGENTS.override.md` |
| GitHub Copilot | `.github/copilot-instructions.md` | `.github/instructions/*.instructions.md` |
| Cursor | `.cursorrules` | `.cursor/` community rules |

**Key principle:** Do not multiply authoritative instruction surfaces without
a clear maintenance or scope reason. Every additional file creates another
place where guidance can become duplicated, stale, or contradictory.

---

## 3. Cross-platform portability — verified patterns

All 8 B8 shell patterns validated against shellcheck rules:

| B8 pattern | Shellcheck rule | Priority |
| :--------- | :-------------- | :------- |
| `which` → `command -v` | SC2230 | High |
| `grep -P` → `grep -E` | SC3028 | High |
| `sed -i` (no backup) | SC2001 | High |
| `echo` with escapes | SC3028 | High |
| `#!/bin/bash` → `#!/usr/bin/env bash` | SC2001 | Medium |
| `\012` octal | Niche | Low — rare CI failure |
| `find -exit` → `-exec` | SC2001 | Medium |
| `flock` → `mkdir .lock \|\| exit 1` | SC2001 | Medium |

**Patterns identified as missing** from the original B8: `[[ ]]` (SC3010),
`source` vs `.` (SC2039), `pushd`/`popd` (SC2164), `readlink -f`, GNU
`mktemp` flags, `${var/pattern/replacement}` (SC2001), `let` (SC2250).

---

## 4. Co-author guard research

Two distinct enforcement families, same mechanism:

- **Proactive trailer rejection** — hermes-skill-hq pattern: block unauthorized
  `*-by:` attribution before it reaches the commit log. This is the rarer
  direction.
- **DCO enforcement** — Linux kernel, DCO App (337★), CNCF ecosystem: enforce
  *presence* of `Signed-off-by`, not rejection of unauthorized trailers.

Both use the same architecture: policy documentation → local commit-msg hook →
shared checker script → CI gate. No surveyed project uses hook-only or CI-only
for enforcement that matters.

---

## 5. .gitignore patterns — official vs practice

**Official github/gitignore/Global/Agents.gitignore (canonical) directs:**

- **Ignore** (local state only): `.aider.*.history`, `.claude/*.local.json`,
  `.claude/**/*.log`, `CLAUDE.local.md`, `gemini-debug.log`, `.gemini-clipboard/`
- **Commit** (all commented out): `AGENTS.md`, `.codex/`, `.claude/`,
  `.cursorrules`, `.cursor/`, `GEMINI.md`, `WARP.md`,
  `.github/copilot-instructions.md`

**Practice from survey:** 47% of projects commit AGENTS.md, 24% commit
CLAUDE.md. No project gitignores agent instruction files. The official
template confirms this: instruction files are intentionally committed,
local variants go in .gitignore.

---

## 6. Script naming conventions (from open-source survey)

| Prefix | Purpose | Frequency |
| :----- | :------ | :-------- |
| `check-*` / `verify-*` | Validation and consistency | Ubiquitous |
| `build-*` | Compilation and packaging | Ubiquitous |
| `install-*` | Installation and setup | Common |
| `deploy-*` / `sync-*` | Deployment | Common |
| `run-*` / `start-*` | Execution and service | Very common |
| `test-*` | Testing | Ubiquitous |
| `lint-*` / `format-*` | Code quality | Very common |
| `release-*` / `publish-*` | Release management | Common |
| `clean-*` | Cleanup | Common |
| `setup-*` / `init-*` | First-time setup | Common |

Standard location: `scripts/` directory. Names lowercase-dash-separated.
Consistent prefixes enable tab-completion grouping.

---

## 7. Evidence quality distribution

| Label | Meaning | Count | B-checks |
| :---- | :------ | ----: | :------- |
| research-backed | Grounded in systematic survey or documented study | 8 | B1, B3, B5, B7, B8, B9, B10, B11 |
| observed | Grounded in specific user observation or single source | 2 | B0 tri-layer, B2 |
| pragmatic | Common-sense design, no formal study | 4 | B0 (forge-awareness), B4, B6 |

**Changes through research:** B3, B8, B10, B11 promoted from
observed/pragmatic to research-backed during T1-T6 investigation. B4 and B6
remained pragmatic — survey confirmed their approach but found no need for
revision.

---

## 8. User suggestions — disposition

All 16 user suggestions mapped to implementation or explicit design position:

| # | Suggestion | Status | Where landed |
| :- | :--------- | :----- | :----------- |
| 1 | Mature projects survey | Research | Survey table in this file; real-world table in SKILL.md |
| 2 | Anthropic/OpenAI practices | Reference | Agent ecosystem table in this file; `references/agent-instruction-ecosystem.md` |
| 3 | Commit messages over CHANGELOG | Implemented | B0 commit-log-first + B7a-B7c |
| 4 | Cross-platform portability | Implemented | B8 (8 patterns) + this file §3 |
| 5 | Canonical script naming | Implemented | B2 verb-noun check + this file §6 |
| 6 | Anti-stale/anti-drift | Implemented | B0 proportionate anti-drift + B7b-d |
| 7 | CI efficiency | Implemented | B9 (6-signal table) |
| 8 | Separate maintainer from user | Implemented | B0 repo-as-source + Phase C |
| 9 | Quality skills before impl | Implemented | B0 tri-layer fallback |
| 10 | Version tag anti-drift | Implemented | B5 tag vs release |
| 11 | .gitignore + repo metadata | Implemented | B10 (6 categories) + this file §5 |
| 12 | Co-author guard | Implemented | B11 (4-layer) + this file §4 |
| 13 | Agent concepts study | Reference | `references/anti-drift-proportionality.md` cites study notes |
| 14 | Cross-agent portability | Implemented | B0 forge-awareness + ecosystem reference |
| 15 | Templates with caution | Principle | AP8 — no `templates/` directory exists |
| 16 | Don't re-invent wheel | Principle | AP7/AP9 — 17-file discipline, scope bounded |

---

## 9. Specification changes register

Changes that propagated from research findings into SKILL.md:

| # | B-check | Change | Source |
| :- | :------ | :----- | :----- |
| 1 | B11 | Label promoted observed → research-backed | Three-layer enforcement pattern confirmed across Linux kernel DCO, DCO App |
| 2 | B3 | Label promoted pragmatic → research-backed; detection order inverted | Pre-commit adoption is rare (1/17); EditorConfig is baseline (53%) |
| 3 | B10 | Label promoted observed → research-backed; pattern list re-anchored | Official github/gitignore template is canonical; plan's ad-hoc list replaced |
| 4 | B8 | Label promoted observed → research-backed; .gitattributes gap identified | 76% adoption across surveyed projects; shellcheck verified all patterns |
| 5 | B4 | Confirmed pragmatic (no change) | 17-project survey validated single-source-of-truth approach |
| 6 | B6 | Confirmed pragmatic (no change) | Survey confirmed formatter mapping; built-in vs external distinction added |

---

## 10. Primary research sources

- **agent-concepts-study** (`~/labs/agent-concepts-study/`): 6 study notes on
  instruction boundaries, proportionate anti-drift, duplicate guidance, and
  research-practice loops
- **hermes-skill-hq**: `dev/hq-review/references/durable-patterns.md` —
  co-author guard pattern
- **repo-consistency-enforcement skill** (30 reference files): consistency
  tool detection patterns
- **github/gitignore** (175k★): `Global/Agents.gitignore` — official agent
  artifact template
- **Anthropic Claude Code docs**: platform.claude.com/docs
- **OpenAI Codex / Agents SDK**: developers.openai.com
- **shellcheck wiki**: SC2001, SC2230, SC2039, SC3010, SC3028, SC2164, SC2250
- **DCO App**: github.com/dcoapp/app (337★) — Signed-off-by enforcement bot
- **Linux kernel DCO v1.1**: docs.kernel.org — origin of Signed-off-by
  trailer convention
- **config-doc-drift-prevention skill** (installed): drift detection patterns
- **github-actions-workflows skill** (installed): CI workflow patterns
