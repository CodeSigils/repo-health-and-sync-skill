# Cross-Agent Portability Check

Detect agent-specific references in shipped SKILL.md files.
Part of repo-health Phase B — run after B10 (metadata audit) and
before C-phase sync.

## Why

Agent skill files that reference platform-specific tools (`skill_view`,
`hermes skills`, `Claude()`, `.cursor/rules/`) break silently on other
runtimes. No runtime validates cross-agent portability — a Hermes agent
never complains about Hermes-specific refs, but a Codex agent silently
misreads the skill.

## Detection patterns

Scan all shipped `skills/*/SKILL.md` (or `*.md` in the skill directory)
for these patterns:

| Pattern | Example | Breaks on |
|---------|---------|-----------|
| Hermes tool name | `skill_view(name)`, `skill_manage(action='create')` | Claude Code, Codex, OpenCode, Gemini CLI, Cursor |
| Hermes Python import | `from hermes_tools import ...` | All non-Hermes agents (import fails at runtime) |
| Hermes config path | `~/.hermes/` or `HERMES_CONFIG_DIR` | All non-Hermes agents |
| Hermes CLI command | `hermes skills install`, `hermes config set` | All non-Hermes agents |
| Claude Code tool | `Claude()` or `claude.md` | Hermes, Codex, OpenCode |
| Codex CLI command | `codex run` or `$skill-installer` | Hermes, Claude Code |
| Gemini CLI command | `gemini skills` | Hermes, Claude Code, Codex |
| Platform adapter path | `.claude/`, `.cursor/`, `.codex/`, `.opencode/`, `.gemini/` | All agents not on that platform |

## Severity

BLOCKING — a single agent-specific reference makes the skill unusable on
other runtimes, and the failure is invisible to the authoring agent.

## Exemptions for documentation-only references

Reference files may list platform paths for documentation purposes — e.g.
"check `.cursor/rules/` for agent instruction files" in a project-orientation
guide. Mark exempt lines with an inline comment:

```text
# portability: allow-platform-ref
```

The scanning script skips lines containing this marker. Use sparingly —
only for lines that genuinely document platform conventions rather than
instructing the agent to use them.

**Good — documentation listing:**
```
- `AGENTS.md`, `CLAUDE.md`, `.cursor/rules/*` # portability: allow-platform-ref
```

**Bad — would mask a real violation:**
```
Run `skill_view(name)` to inspect the skill  # portability: allow-platform-ref  ← WRONG
```

## Ready-to-use script

This skill ships a complete, copyable portability gate at
`scripts/check-portability.py`. Copy it to `.github/scripts/check-portability.py`
in any skill repo, add a CI step, and it works immediately — no configuration
needed. It implements all patterns below, the inline exemption mechanism,
and scans `skills/**/*.md`.

## CI integration

Add the portability check as a CI step. Place it first in the workflow
so it fails fast before other checks run:

```yaml
- name: Check cross-agent portability
  run: python3 .github/scripts/check-portability.py
```

## Pitfalls

1. **CI triggers must include `.github/scripts/`.** If the workflow uses
   path-restricted triggers (`on.push.paths`), add `.github/scripts/**`
   to both push and pull_request trigger lists. Without it, editing the
   portability script silently skips CI — the gate becomes self-broken.

2. **Scope to the shipped surface only.** Scan `skills/**/*.md`, not the
   whole repo. README and repo-root docs are expected to reference specific
   platforms — those are documentation, not instruction drift.

## When to skip (and when not to)

A portability gate is **not** the right choice for every project. The
decision depends on the skill's portability tier:

| Tier | Characteristic | Gate needed? |
|------|---------------|--------------|
| **Fully portable** (Tier 1) | Only `name`/`description` frontmatter. Body references no CLI tools, no agent-specific commands. | Yes — enforcement ensures no accidental drift |
| **Tools-portable** (Tier 2) | References generic CLI tools (`git`, `python3`, `curl`). No agent-specific tool names. | Yes — easy to slip a platform reference into a shell command |
| **Platform-specific** (Tier 3) | Explicitly targets one agent (e.g. `compatibility: hermes`). Uses agent-specific tools and config paths by design. | **No** — intentional references are not drift |

Skip the portability gate when:
- The project declares a single target platform in SKILL.md frontmatter
  (e.g. `compatibility: hermes`) and accepts the portability restriction.
- The skill's core functionality depends on agent-specific APIs (MCP
  servers, gateway integrations, platform-exclusive CLI workflows).

Do NOT skip when:
- The project currently has no agent-specific references but has no CI
  gate — a single future commit can silently break portability.
- The project declares no platform restriction but happens to be
  Hermes-only by convention. Add the gate and the `compatibility` field
  together.

## References

- `CodeSigils/skill-discovery/.github/scripts/ci-check.py` — original implementation
- `CodeSigils/py-review-skill/.github/scripts/check-portability.py` — adapted implementation
