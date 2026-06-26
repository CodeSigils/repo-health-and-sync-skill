---
title: Agent Instruction Ecosystem
description: Canonical instruction files across major agent platforms, guidance on portability tiers, and adaptation paths for multi-forge projects.
status: reference
---

# Agent Instruction Ecosystem

Every major agent platform uses an instruction file at repo root to guide
agent behavior. These files are conceptually equivalent but have different
filenames, scoping mechanisms, and precedence rules. This reference
documents the landscape so the skill can advise on instruction-file
strategies.

---

## Canonical instruction files by platform

| Platform | Canonical file | Scoped extension | Precedence |
| :------- | :------------- | :--------------- | :--------- |
| Anthropic Claude Code | `CLAUDE.md` | `.claude/rules/`, `@path` imports | Last loaded wins; root file first, then rules directory |
| OpenAI Codex | `AGENTS.md` | `AGENTS.override.md` (subdirectory) | Override files shadow root file per directory |
| GitHub Copilot | `.github/copilot-instructions.md` | `.github/instructions/*.instructions.md` | Instructions merged; later files can override |
| Cursor | `.cursorrules` | `.cursor/` community rules | `.cursorrules` is canonical; directory rules extend |
| Windsurf | `.windsurfrules` | — | Single file, no scoping |
| Claude (web/API inline) | System prompt | N/A | Per-session, not file-based |

---

## Portability tiers

Agent instruction patterns fall into three portability tiers. Choose the
highest tier that meets your project's needs.

| Tier | Name | Scope | Instruction file | Example repos |
| :--- | :--- | :--- | :--------------- | :------------ |
| **1** | Pure VCS (git only) | Any forge, any agent | None — relies on CONTRIBUTING.md + conventions | golang/go, rust-lang/rust |
| **2** | Shell + tools | Any forge, any agent — uses standard Unix tooling | One file at repo root: `CLAUDE.md` or `AGENTS.md` | torvalds/linux, python/cpython |
| **3** | Agent-specific | Uses platform-specific instruction scoping, rules directories, or forge-specific checks | Both root file and scoped rules directory | Personal agent projects, hermetic CI repos |

**Tier 1** is the most portable but gives agents no structured guidance.
**Tier 2** is the sweet spot for most projects — one file, standard tools.
**Tier 3** unlocks platform features (scoped rules, codebase indexing) but
creates forge lock-in.

---

## Adaptation path for other forges

If your project targets multiple agent platforms, follow this adaptation
path rather than maintaining separate instruction sets:

```bash
# Claude Code reads this on entry
CLAUDE.md → (primary)

# Cursor also reads this — or symlink to .cursorrules
.cursorrules → symlink to CLAUDE.md

# GitHub Copilot reads this
.github/copilot-instructions.md → (focus on GitHub-specific workflow)

# OpenAI Codex reads this
AGENTS.md → (focus on project-level context)
```

**Key principle:** One canonical source, platform-specific files point to
it via pointer pattern (see references/anti-drift-proportionality.md).

If two or more of the following files co-exist with no documented
precedence, the skill flags it as a WARNING:

- `AGENTS.md`
- `WARP.md`
- `.rules`
- `CLAUDE.md`
- `GEMINI.md`
- `.github/copilot-instructions.md`

**Worst case observed:** A repo with `CLAUDE.md`, `AGENTS.md`, `.cursorrules`,
and `.github/copilot-instructions.md` — all defining different rules, all
loaded by different agents, none referencing each other.

---

## Recommendations

1. **Start at Tier 2.** One `CLAUDE.md` at repo root covers Claude Code,
   Cursor (via symlink), and most agents.
2. **Only add platform-specific files when you need platform features.**
   Scoped rules directories are useful for large monorepos but add drift
   surface for small projects.
3. **Document precedence explicitly.** If you have multiple instruction
   files, add a comment at the top of each: "This file is primary for X;
   see Y for Z."
4. **Use `.repo-health.json` to skip instruction-file warnings** when
   multiple files are intentional.
