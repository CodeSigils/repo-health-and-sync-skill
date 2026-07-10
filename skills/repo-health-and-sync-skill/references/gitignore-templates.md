---
title: .gitignore Templates Reference
description: Official .gitignore templates per language, agent-artifact patterns from Agents.gitignore, and per-language recommendations.
status: reference
---

# .gitignore Templates Reference

This file collects .gitignore resources used by B10's audit. It is not a
template generator — it points to canonical sources so the agent can
recommend additions without carrying a template library.

---

## Official template repos

| Source | URL | Coverage |
| :----- | :--- | :------- |
| github/gitignore | <https://github.com/github/gitignore> | 500+ language/IDE templates, community maintained, 175k ★ |
| Official Python .gitignore | <https://github.com/github/gitignore/blob/main/Python.gitignore> | Python + tox + venv + pytest |
| Official Node .gitignore | <https://github.com/github/gitignore/blob/main/Node.gitignore> | Node + npm + yarn + pnpm |
| Official Rust .gitignore | <https://github.com/github/gitignore/blob/main/Rust.gitignore> | Cargo + Rust Analyzer |
| Official Go .gitignore | <https://github.com/github/gitignore/blob/main/Go.gitignore> | Go binaries + vendor |

---

## Agent-artifact patterns (from Agents.gitignore)

These patterns prevent agent and editor state files from being committed.
They should be present in every repo, regardless of language.

```gitignore
# Agent state files
.open-mem/
.omo/
.aider*
.aider*
CLAUDE.local.md
.claude/*.local.*
.claude/**/*.log
AGENT.md
GEMINI.md
gemini-debug.log
.agents/
.codex/
.opencode/
.cursor/
```

**Source:** <https://github.com/NousResearch/Agents.gitignore>

---

## Per-language recommendations

| Language(s) | Key patterns to ignore |
| :---------- | :--------------------- |
| Python | `__pycache__/`, `*.pyc`, `.venv/`, `venv/`, `.pytest_cache/`, `*.egg-info/`, `dist/`, `build/` |
| Node.js | `node_modules/`, `npm-debug.log*`, `.next/`, `dist/` |
| Rust | `target/`, `**/*.rs.bk` |
| Go | `vendor/`, `*.exe` (for compiled binaries) |
| Shell scripts | (usually patterns from OS junk + agent artifacts suffice) |
| Generic | `.DS_Store`, `Thumbs.db`, `*.swp`, `*.swo`, `*~`, `.vscode/`, `.idea/` |

---

## Using with B10

B10 checks each category against the project's `.gitignore`. When a pattern
is missing, the agent should recommend adding it and reference this file
for the exact syntax:

> The project's `.gitignore` is missing agent-artifact patterns.
> See [references/gitignore-templates.md](references/gitignore-templates.md)
> for the recommended additions from Agents.gitignore.

Do NOT copy-paste the full template into the output — point to the
reference and the specific missing patterns. This keeps the skill's output
concise and the canonical source in one place.
