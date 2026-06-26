---
title: PROPOSALS — Research Basis for the Implementation Plan
date: 2026-06-25 (updated from 2025-06-25 — plan supersedes decisions)
status: historical reference document — decisions superseded by PLAN.md
relation-to-plan: "PLAN.md is the authoritative implementation plan.
  This document preserves the research that informed it. Decision content
  (recommendations, options, phase proposals) is preserved for provenance
  but marked where superseded."
---

# PROPOSALS — Repo Health and Sync Skill: Updated Proposals

This document captures the research that informed PLAN.md. It is a
historical reference — PLAN.md (1171 lines, 11 sections) is the
authoritative implementation plan. This file should be read alongside
it, not standalone.

Original date: 2025-06-25. Updated 2026-06-25 to note superseded content.

Based on research across:
- agent-concepts-study (4 study notes)
- hermes-skill-hq (durable-patterns.md)
- repo-consistency-enforcement skill (30 reference files)
- github/gitignore (official .gitignore templates, 175k ★)
- Anthropic Claude Code API docs
- OpenAI Codex / Agents SDK docs
- github-issues skill
- 16 user suggestions from USER-SUGGESTIONS.md

---

## Research Summary — Still Current

The research findings below are still current and complement the plan's
17-project survey (§1). The plan's survey covers breadth (9 ecosystems,
17 projects); this summary covers depth (study notes, proven patterns).

### Agent Instruction Ecosystem (from agent-concepts-study)

Four major agent frameworks converge on the same pattern:

| Tool | Canonical file | Scoped extension |
| :--- | :------------- | :--------------- |
| Anthropic Claude Code | `CLAUDE.md` | `.claude/rules/`, `@path` imports |
| OpenAI Codex | `AGENTS.md` | `AGENTS.override.md` (subdirectory) |
| GitHub Copilot | `.github/copilot-instructions.md` | `.github/instructions/*.instructions.md` |
| Cursor | `.cursorrules` | `.cursor/` community rules |

Key finding from `agent-instruction-boundaries-and-drift.md`:
> Do not multiply authoritative instruction surfaces unless there is a clear maintenance or scope reason.

Antidrift principle: every additional instruction file creates another
place where guidance can become duplicated, stale, contradictory, or
partially updated. The plan's single-file approach (SKILL.md → references)
is aligned with the ecosystem norm.

### Proportionate Anti-Drift (from agent-concepts-study)

From `proportionate-anti-drift-from-observed-failure.md`:

Anti-drift machinery is proportionate when:
- each check was added after a specific observed failure,
- each check has a single clear failure mode,
- the cost of a false pass is bounded,
- the maintenance cost of the check is low relative to the cost of the
  drift it prevents.

Anti-drift machinery is disproportionate when:
- checks are added speculatively ("this could break someday"),
- checks have overlapping or unclear scope,
- the verification is more complex than the thing being verified,
- checks accumulate without a pruning mechanism.

This maps to the plan's AP3 (Speculative Checks), §3 (File Swamp
Avoidance), and §4.1 (Evidence Quality Labels).

### Duplicate Guidance as Drift Surface (from agent-concepts-study)

From `duplicate-guidance-as-drift-surface.md`:

- Duplicate guidance is a drift surface whether it lives in two files
  or two sections of the same file.
- Tightening passes reveal progressively deeper issues (surface →
  structural → guidance).
- The 3-authority-surface pattern emerged: keep canonical guidance in
  one place, point to it from others.

Maps to AP1 (Duplicate Guidance) in the plan.

### Co-Author Guard (from hermes-skill-hq durable-patterns.md)

A three-layer enforcement pattern:

| Layer | Controls | Failure mode if missing |
| :---- | :------- | :---------------------- |
| Agent instructions (AGENTS.md) | AI agents reading the repo | Agent adds attribution without user knowledge |
| Human policy (CONTRIBUTING.md) | Human contributors | Human adds unauthorized co-author lines |
| Git hook (`.githooks/commit-msg`) | Everyone, at transport layer | Tool/CLI/IDE that bypasses social norms |
| CI enforcement | Pushed/pull-request commit ranges | Commits that bypassed the local hook |

Extended to 4 layers in the plan (B11a-d). Maps to B11 spec and
co-author-guard.md (Phase 3).

### Official .gitignore Templates (github/gitignore, 175k ★)

The official gitignore repository has a `Global/Agents.gitignore`
template covering:

| Tool | Suggested ignore pattern |
| :--- | :----------------------- |
| OpenAI Codex | `AGENTS.md` (comment — intentionally committed) |
| Claude Code | `.claude/*.local.json`, `.claude/**/*.log`, `CLAUDE.local.md` |
| Aider | `.aider.input.history`, `.aider.chat.history.md`, `.aider.llm.history`, `.aider.tags.cache.v*` |
| Gemini CLI | `gemini-debug.log`, `.gemini-clipboard/` |
| General agent artifacts | `.open-mem/`, `.omo/`, agent-local config files |

Key insight: most agent instruction files (`AGENTS.md`, `CLAUDE.md`,
`.cursorrules`) are **intentionally committed** — only local/personal
variants go in `.gitignore`. Maps to B10 in the plan.

### Cross-Platform Portability Patterns

From repo-consistency-enforcement and shell scripting best practices:

| Issue | Portable pattern | Non-portable |
| :---- | :--------------- | :----------- |
| Tool detection | `command -v` | `which` (different exit codes on BSD) |
| Grep portability | `grep -E` (ERE) | `grep -P` (PCRE, GNU-only) |
| sed -i | `sed -i.bak` (BSD) vs `sed -i` (GNU) | Blind `sed -i` without backup |
| printf | `printf '%s\n' "$var"` | `echo "$var"` (escape differences) |
| Shebang | `#!/usr/bin/env bash` | `#!/bin/bash` (not on BSD) |
| Line endings | `\n` not `\012` | Octal escapes differ |
| find predicates | POSIX `find ... -exec` | `find -exit` (GNU-only, known CI failure) |

Maps to B8 in the plan. The plan also adds detection patterns for
`flock`, `which`, `grep -P`, `sed -i` (no backup), `#!/bin/bash`,
`\012`, `find -exit`.

### Script Naming Conventions (from open-source conventions)

Across major projects (Linux kernel, Homebrew, Kubernetes, various),
scripts follow consistent naming:

| Prefix | Purpose |
| :----- | :------ |
| `check-*` / `verify-*` | Validation and consistency checks |
| `build-*` | Compilation and packaging |
| `install-*` | Installation and setup |
| `deploy-*` / `sync-*` | Deployment and synchronization |
| `run-*` / `start-*` | Execution and service management |
| `test-*` | Testing |
| `lint-*` / `format-*` | Code quality |
| `release-*` / `publish-*` | Release management |
| `clean-*` | Cleanup |
| `setup-*` / `init-*` | First-time setup |

Standard location: `scripts/` directory, lowercase-dash-separated names.
Tab-completion friendly: consistent prefixes for category grouping.

Maps to B2 naming convention check in the plan's §10.1 gap closure.

---

## User Suggestion Mapping — Historical (superseded by PLAN.md)

**This section is historical.** The current coverage mapping lives in
USER-SUGGESTIONS.md (raw source) and PLAN.md §1 (survey), with status
per suggestion listed below. This earlier mapping is retained for
provenance.

| # | Suggestion | Where covered in plan | Status |
| :- | :--------- | :-------------------- | :----- |
| 1 | Mature projects survey | §1 17-project survey + mature-project-patterns.md (P7) | Research |
| 2 | Anthropic/OpenAI research | PROPOSALS (here) + agent-instruction-ecosystem.md (P7) | Research |
| 3 | Commit messages over CHANGELOG | B7a-B7d + AP11 | Designed (Phase 2) |
| 4 | Cross-platform portability | B8 | Designed (Phase 4) |
| 5 | Canonical script naming | §10.1 closure → absorbed into B2 | Implemented (Phase 0) |
| 6 | Anti-stale/anti-drift | B0, B7b-d, AP3, §3 | Designed |
| 7 | CI efficiency + trigger scoping | B9 | Designed (Phase 5) |
| 8 | Separate maintainer from user | AP10, Phase C | Designed |
| 9 | Quality skills before implementation | §10.2 closure → B0 tri-layer pattern | Implemented (Phase 0) |
| 10 | Version tag anti-drift | B5, AP5 | Implemented (Phase 0) |
| 11 | .gitignore + repo metadata | B10, gitignore-templates.md (P7) | Designed (Phase 6) |
| 12 | Co-author guard | B11, co-author-guard.md (P1) | Designed (Phase 3) |
| 13 | Agent concepts consultation | §0 cites 6 notes + anti-drift-proportionality.md (P7) | Research |
| 14 | Cross-agent portability | §10.3 closure → B0 forge-awareness | Designed (Phase 7) |
| 15 | Templates with caution | AP8 | Design principle |
| 16 | Don't re-invent wheel | §3 File Swamp Avoidance, AP7, AP9 | Design principle |

---

## Historical Content — Superseded by PLAN.md

### Proposed New Phase Structure (original)

The original proposal extended B1-B6 to B7-B11, plus Phase C refinements.
PLAN.md §5 refines this into 8 concrete phases with dependency ordering,
evidence labels, and verification criteria. The original structure is
preserved here for provenance.

**Phase B — Project Health Baseline (as originally proposed):**

| Phase | Current | Proposed | Source |
| :---- | :------ | :------- | :----- |
| B1 | Git hygiene | Same + stale branch depth | — |
| B2 | Shellcheck | Same | — |
| B3 | Consistency check | Same + graceful skip | repo-consistency-enforcement |
| B4 | Version alignment | Strengthen: single source | config-doc-drift-prevention |
| B5 | Tag vs Release | Same + path-filter | github-actions-workflows |
| B6 | Format and lint | Same | — |
| B7 | — | Commit-message audit + cross-commit drift | agent-concepts-study, user #3, #6 |
| B8 | — | Cross-platform shell audit | user #4 |
| B9 | — | CI efficiency / trigger audit | user #7 |
| B10 | — | Repository metadata / .gitignore audit | user #11 |
| B11 | — | Co-author guard | user #12 |

### Implementation Options (original — superseded)

The plan chose **Option 3 (Two-phase)** and refined it into 8 phases.
Options 1 and 2 are recorded here for completeness.

| Option | Scope | Effort | Risk |
| :----- | :---- | :----- | :--- |
| 1. Minimal viable | Add B7 + B11 only | Low-Med | Fast path; leaves gaps |
| 2. Full restructure | 10 reference files, reduce SKILL.md, add B7-B11 | High | Cleanest; significant effort |
| 3. Two-phase | Phase 1: B7 + B11. Phase 2: restructure. | Medium | Pragmatic |

**Plan's refinement:** 8 phases instead of 2, with dependency graph,
evidence labels, and verification criteria. See PLAN.md §4-§5.

### Recommendation (original — superseded)

> Option 3 — Two-phase. Cross-commit drift detection (B7) and co-author
> guard (B11) address the most concrete user concerns. The restructure
> should happen once, not incrementally, but shouldn't block those
> improvements.

The plan adopted this direction and extended it. The recommendation is
now historical — the plan is the current decision record.

### Reference File Architecture (original)

The originally proposed file structure included a `templates/` directory
and `USER-SUGGESTIONS.md`. The plan rejected `templates/` (AP8 —
Templates Before Need) and plans to remove `USER-SUGGESTIONS.md` after
Phase 0. The plan's §2 evaluates 12 candidate reference files by priority
(5 P0, 5 P1, 1 P2, 1 skip). The original architecture is preserved here
for provenance.

```
# Original proposed structure (some items superseded by plan)
repo-health-and-sync-skill/
├── SKILL.md                           # ~200 lines
├── references/
│   ├── heuristic-discovery.md         # B1-B6 detection patterns
│   ├── drift-pairs.md                 # cross-commit drift
│   ├── release-checklist.md           # release steps
│   ├── sync-targets.md                # Phase C targets
│   ├── repo-health-json-schema.md     # .repo-health.json schema
│   ├── ci-wiring.md                   # CI integration
│   ├── agent-instruction-ecosystem.md # cross-agent patterns
│   ├── mature-project-patterns.md     # per-language conventions
│   ├── co-author-guard.md             # 3-layer enforcement
│   ├── gitignore-templates.md         # github/gitignore ref
│   └── anti-drift-proportionality.md  # heuristic
├── templates/
│   └── .repo-health.json.example      # ⚠ plan rejected (AP8)
└── USER-SUGGESTIONS.md                # ⚠ planned for removal
```

**Key differences from plan:**
- templates/ directory → rejected (AP8 — Templates Before Need)
- USER-SUGGESTIONS.md → planned removal after Phase 0
- Plan evaluates 12 files (5 P0 essential, 5 P1 valuable, 1 P2 deferred,
  1 skip) vs the 11 proposed here

---

## References

1. agent-concepts-study: `2026-06-10-agent-instruction-boundaries-and-drift.md`
2. agent-concepts-study: `2026-06-11-proportionate-anti-drift-from-observed-failure.md`
3. agent-concepts-study: `2026-06-12-duplicate-guidance-as-drift-surface.md`
4. agent-concepts-study: `2026-06-11-research-practice-loop-across-agent-repos.md`
5. hermes-skill-hq: `dev/hq-review/references/durable-patterns.md` §co-author guard
6. repo-consistency-enforcement skill (installed skill, 30 reference files)
7. github/gitignore repository: `Global/Agents.gitignore` (official template)
8. Anthropic Claude Code API docs (platform.claude.com/docs)
9. OpenAI API docs: Agents SDK, Codex tools (developers.openai.com)
10. config-doc-drift-prevention skill (installed skill)
11. github-actions-workflows skill (installed skill)
12. USER-SUGGESTIONS.md (extracted from SKILL.md)
