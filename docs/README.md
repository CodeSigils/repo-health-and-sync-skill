# Maintainer docs — not shipped to skill users

This directory documents the project's architecture decisions and research
evidence. It is not part of the skill runtime — users who install this
skill do not receive these files.

The skill ships as a single SKILL.md with no reference files or scripts.
Everything the agent needs is discovered at runtime using general-purpose
tools on PATH.

**Start here:**

- [decisions.md](decisions.md) — what was built, why, phase rationale, anti-patterns avoided
- [codex-setup.md](codex-setup.md) — verified repository-local and plugin setup
- [maintaining.md](maintaining.md) — developer workflow and verification
- [research.md](research.md) — survey data, ecosystem tables, evidence that informed decisions
