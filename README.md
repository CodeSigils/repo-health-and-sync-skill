# Repo Health and Sync Skill

[![Release](https://img.shields.io/github/v/release/CodeSigils/repo-health-and-sync-skill?label=release)](https://github.com/CodeSigils/repo-health-and-sync-skill/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Two-phase procedure for any git repository: project health baseline (B1-B11)
and reverse sync (C1-C4). Discovers everything at runtime — no hardcoded
project metadata. Works on any repo the agent is dropped into.

---

## Install

```bash
hermes skills install CodeSigils/repo-health-and-sync-skill
```

## Quick start

1. `cd` into any git repository
2. Load the skill: `hermes skills load repo-health-and-sync-skill`
3. Run Phase B checks (B1 through B6)
4. If no blocking issues, run Phase C (reverse sync)

---

## Phase overview

| Phase | Scope | Details |
| :---- | :---- | :------ |
| **B1** | Git hygiene | Dirty trees, orphan tags, un-pushed commits |
| **B2** | Shellcheck | Every `.sh` file, graceful skip if absent |
| **B3** | Consistency check | Project's own check script or `.repo-health.json` |
| **B4** | Version alignment | Cross-manifest version consistency |
| **B5** | Tag vs Release integrity | Tags vs GitHub Releases cross-reference |
| **B6** | Format + lint | Project's own formatter config |
| **B7** | Commit audit | 4 sub-steps: format, drift, changelog, version bump |
| **B8** | Cross-platform shell | GNU-only patterns in `.sh` files |
| **B9** | CI efficiency | Workflow trigger scoping, caching, artifact separation |
| **B10** | .gitignore + metadata | 6-category coverage audit |
| **B11** | Co-author guard | 4-layer attribution trailer enforcement |
| **C1-C4** | Reverse sync | Repo-to-target sync with post-sync verification |

Phase B gates Phase C: never sync a broken repo.

---

## Requirements

- **git** — all checks operate on a git repository
- **shellcheck** — required for B2 (skipped gracefully if absent)
- **gh** CLI — required for B5 (tag vs release); skipped gracefully if absent
- Compatible with any Hermes agent runtime

---

## Project structure

```
├── SKILL.md              # Canonical skill definition (~575 lines)
├── references/           # 8 files — per-check detail and configuration
├── scripts/              # Enforcement scripts
├── docs/                 # Maintainer documentation
│   ├── decisions.md      # Architecture rationale
│   └── research.md       # Evidence base
├── .repo-health.json     # Self-configuration for the skill's own repo
└── AGENTS.md             # How to develop this skill
```

---

## Conventions

- **Portable grep** — the skill enforces POSIX-compatible grep (`-E`, never `-P`)
- **Proportionate anti-drift** — every check traces to an observed failure
- **Zero tags is valid** — some healthy projects never tag
- **Repo as source** — maintainer tooling in `scripts/` and `docs/` is never synced to users

Full design principles in [SKILL.md §B0](SKILL.md#B0-Design-principles-read-before-Phase-B).

---

## License

MIT — see [LICENSE](LICENSE).
