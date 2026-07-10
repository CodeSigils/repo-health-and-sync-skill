---
title: Commit Message Formats — Reference for B7a
description: Survey of structured commit message formats observed across projects. B7a samples and classifies but does not enforce any single format.
status: reference
---

# Commit Message Formats Reference

This file documents the structured commit message formats that B7a (Commit message audit) knows how to classify. It is a reference catalogue, not a prescription — B7a detects what the project already uses.

---

## Formats B7a Recognises

| Format | Example | Classification |
| :----- | :------ | :------------- |
| Conventional Commits (with scope) | `feat(auth): add OAuth2 refresh flow` | **Structured** |
| Conventional Commits (no scope) | `fix: handle null response in parser` | **Structured** |
| Topic-style (noun phrase + colon) | `parser: handle null response` | **Structured** |
| Unstructured (no colon prefix) | `Handle null response in parser` | **Unstructured** |

**Threshold:** B7a samples the last 10 commits. If **fewer than 7/10** are Structured, it emits a WARNING. This is a culture signal, not a block.

---

## What B7a Does NOT Recognise (by design)

| Format | Example | Why it's not in the classification |
| :----- | :------ | :--------------------------------- |
| `what:` / `why:` body | `feat: add OAuth2 refresh flow`<br>`what: add refresh token rotation`<br>`why: fixed token expiry race observed in prod` | This is a **commit body convention**, not a subject-line format. B7a only classifies the subject line (first line). Projects using this convention will show as "Structured" on the subject line, which is correct — the body convention is a separate layer. |
| Git trailer blocks | `Signed-off-by:`, `Co-authored-by:` | These are trailers, not subject formats. B11 handles trailer policy. |
| Emoji prefixes | `✨ feat: ...` | Treated as Conventional Commits with emoji — classified as Structured. |

---

## Maintainer Note (this repo only)

The **repo-health-and-sync-skill** maintainers use a `what:`/`why:` body convention documented in `docs/maintaining.md`:

```
what: <one-line description of the change>
why:  <reason — design rationale, observed failure, user request, or finding>
```

This is an **internal maintainer workflow** for this skill repo. It is not recommended, detected, or enforced by B7a for other projects. If you want this convention in your project, document it in your `AGENTS.md` / `CLAUDE.md` / `CONTRIBUTING.md` and optionally add a commit-msg hook.

---

## Extending B7a Classification

If a project uses a subject-line format not captured above (e.g., `CHORE: ...`, `[FEAT] ...`, `#123: ...`), the agent can:
1. Note the format in the B7a output
2. Recommend adding it to the project's `.repo-health.json` under `commit_formats` for future runs
3. The skill's heuristic table in `heuristic-discovery.md` can be extended with a new row

The goal is **detection**, not enforcement.