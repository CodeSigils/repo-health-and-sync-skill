# portability: allow-platform-ref
# Cross-Agent Refactoring Pattern

How to convert a Tier 3 (platform-specific) skill to be cross-agent
compatible. Companion to B12 — B12 detects portability issues; this
reference fixes them.

## When to refactor

Refactoring a skill for cross-agent consumption is worth the effort when:

- The CLI or tooling is already portable (e.g. pure Node.js with no
  runtime dependencies), but documentation/skill packaging is framed
  as platform-specific.
- The skill has no deep dependencies on agent-specific APIs (MCP servers,
  gateway integrations, platform-exclusive CLI workflows).
- You want the skill discoverable by users of other agents without
  duplicating or forking the repo.

Do NOT refactor when the skill genuinely depends on platform-exclusive
features (e.g. Hermes `hooks.post_tool_call`, gateway-specific events).

## Refactoring sequence

### Step 1: Strip Hermes-only frontmatter

Reduce SKILL.md frontmatter to the agentskills.io baseline — only `name`
and `description`. Remove `version`, `author`, `license`, `compatibility`,
and `metadata.hermes.tags`.

```yaml
# Before (Hermes-specific)
---
name: markdown-formatter
description: "..."
version: "1.2.0"
author: "CodeSigils"
license: "MIT"
compatibility: "hermes"
metadata.hermes.tags:
  - markdown
  - hermes-skill
  - ...
---

# After (portable baseline)
---
name: markdown-formatter
description: "..."
---
```

Hermes ignores unknown frontmatter fields — dropping these is
non-breaking for existing Hermes consumers.

### Step 2: Replace Hermes-specific path references

Where the skill body references `~/.hermes/skills/<name>/`, replace with
a generic `<skill-dir>` placeholder and a platform resolution table:

| Platform | Skill directory |
|----------|----------------|
| Hermes Agent | `~/.hermes/skills/<name>/` |
| Claude Code | `.claude/skills/<name>/` |
| Codex CLI | `~/.codex/skills/<name>/` |
| Gemini CLI / .agents/ | `.agents/skills/<name>/` |
| OpenCode | `.opencode/skills/<name>/` |
| Source checkout | `skills/<name>/` (in repo) |

Add a note that the CLI does not require any agent platform to function.

### Step 3: Restructure README

Replace a monolithic platform-specific install section with collapsed
`<details>` blocks per platform (same pattern as py-review-skill):

```markdown
<details>
<summary><b>Hermes Agent</b></summary>

```bash
hermes skills install owner/repo/skill-name
```
</details>
```

Include a "Direct (no agent)" option for plain CLI consumption.

### Step 4: Add a portability table

Document which components are portable and which are platform-specific:

| Component | Portable? |
|-----------|-----------|
| CLI binary | ✅ Pure Node.js/Python, no agent runtime required |
| SKILL.md | ✅ agentskills.io base frontmatter |
| Guard scripts | ✅ No agent tools referenced |
| Post-write hook | Platform-specific (agent feature) |

### Step 5: Update GitHub metadata

Run `gh repo edit` to update:
- Description: remove "Hermes skill" framing, use cross-agent language
- Topics: add `agentskills`, `claude-code`, `codex`, `opencode`, `gemini-cli`

### Step 6: Verify no breakage

- The `compatibility` field removal is safe — Hermes ignores it
- The path reference changes are documentation-only — no runtime impact
- Run existing tests/CI to confirm unchanged behavior
- Run `hermes skills list` to confirm the skill still loads

### Step 7: Version bump

Bump the minor version to reflect new cross-agent capability. Use a
separate commit from the refactoring changes for clean release history.

```
1.2.0 → 1.3.0
```

This signals to consumers that new capability was added without breaking
existing behavior.

## Common pitfalls

1. **Don't change runtime CLI behavior during the refactor.** The CLI
   should be identical before and after — only documentation and
   frontmatter change. Keep refactoring and functional changes in
   separate commits.

2. **Don't remove platform-specific content that has no portable
   equivalent.** Some features (Hermes post-write hooks, gateway config)
   are inherently platform-specific and should remain as subsections
   labeled with the platform name.

3. **Don't forget SECURITY.md.** If it references "this Hermes skill",
   update it to "this agentskills.io-compatible skill" or equivalent.

## References

- `CodeSigils/agents-markdown-formatter` — real refactoring from v1.2.0 to v1.3.0
- `references/cross-agent-portability.md` — detection patterns (B12)
