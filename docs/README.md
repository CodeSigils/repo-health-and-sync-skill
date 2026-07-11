# Maintainer docs — not shipped to skill users

This directory documents the project's architecture decisions and research
evidence. It is not part of the skill runtime — users who `hermes skills install`
this skill do not receive these files.

## Scripts boundary

The repo has two script locations, each with a different purpose:

| Location | Shipped? | Purpose |
| :------- | :------- | :------ |
| `scripts/` | No — dev-only | Maintainer tooling: `verify.sh` (CI gate), `doc-audit.py`, `sync-payload.sh`, `payload-manifest.json` |
| `skills/repo-health-and-sync-skill/scripts/` | Yes — runtime | Shipped scripts the skill instructions reference: `check-commit-trailers.py` (B11), `check-commit-body.py` (B7e), `check-portability.py` (B12) |

When `scripts/` and `skills/*/scripts/` share a filename (e.g. `check-commit-trailers.py`),
they are byte-identical — the shipped version is a copy of the dev version at
release time. The CI gate (`bash scripts/verify.sh`) verifies this is current.

**Start here:**

- [decisions.md](decisions.md) — what was built, why, phase rationale, anti-patterns avoided
- [research.md](research.md) — survey data, ecosystem tables, evidence that informed decisions

These two files consolidated information from earlier draft documents. They
are self-contained — each can be read independently — and reference each
other and SKILL.md as needed.
