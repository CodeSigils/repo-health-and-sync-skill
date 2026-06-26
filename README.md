# Repo Health and Sync Skill

A Hermes agent skill that audits any git repository for health issues and
syncs its content to runtime targets.

## Install

```
hermes skills install repo-health-and-sync-skill
```

## Quick start

1. `cd` into any git repository
2. Load the skill: `hermes skills load repo-health-and-sync-skill`
3. Run Phase B checks in order (B1 through B6)
4. If no blocking issues, run Phase C (reverse sync)

See [SKILL.md](SKILL.md) for the full phase descriptions, severity mapping,
and per-check instructions.

## Project structure

```
├── SKILL.md              # Canonical skill definition (agent-optimized)
├── references/           # Per-check detail and configuration
├── scripts/              # Enforcement scripts (e.g. co-author guard)
├── docs/                 # Maintainer docs — decisions and research
└── README.md             # You are here
```

## Requirements

- `git` — all checks operate on a git repository
- `shellcheck` — required for B2 (skip if absent)
- `gh` CLI — required for B5 tag vs release check (skip if absent)
- Compatible with any Hermes agent runtime

## License

MIT
