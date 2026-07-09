# Repo Health and Sync Skill

[![Release](https://img.shields.io/github/v/release/CodeSigils/repo-health-and-sync-skill?label=release)](https://github.com/CodeSigils/repo-health-and-sync-skill/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

*For Hermes agents and skill maintainers.* A two-phase procedure the agent
runs inside any git repository: health baseline checks (B1-B11) and reverse
sync (C1-C4). Discovers everything at runtime — no hardcoded metadata.

---

## Install

```bash
hermes skills install CodeSigils/repo-health-and-sync-skill
```

<details>
<summary><b>Hermes Agent — live-edit setup (recommended for development)</b></summary>

Clone the repo, then add the `skills/` directory to `skills.external_dirs`
in `~/.hermes/config.yaml`:

```yaml
skills:
  external_dirs:
    - /path/to/repo-health-and-sync-skill/skills
```

This loads the skill directly from the repo — every commit is immediately
reflected without reinstalling. The skill appears as a `local` skill in
`hermes skills list`.

**Alternative — copy the skill:**

```bash
cp -r skills/repo-health-and-sync-skill ~/.hermes/skills/
```
</details>

## Quick start

```bash
cd /path/to/some/repo
hermes skills load repo-health-and-sync-skill
# The agent then runs: Phase B (B1→B11), fix blocking items, continue.
```

The skill is self-guiding. The agent reads [SKILL.md](SKILL.md) and walks
through each check, reporting PASS / WARNING / BLOCKING for every phase.
Example output when B2 finds a shell script issue:

```
WARNING  B2: Shellcheck — scripts/deploy.sh (SC2086: double quote to
prevent globbing)
```

---

## Phase overview

| Phase | Scope | Details | Can skip when |
| :---- | :---- | :------ | :------------ |
| **B1** | Git hygiene | Dirty trees, orphan tags, un-pushed commits | — |
| **B2** | Shellcheck | Every `.sh` file, `command -v` guard | No `.sh` files |
| **B3** | Consistency check | Project's own check or `.repo-health.json` | No check found (INFO/WARNING) |
| **B4** | Version alignment | Cross-manifest version consistency | No version sources |
| **B5** | Tag vs Release | Tags vs GitHub Releases cross-ref | No tags |
| **B6** | Format + lint | Project's own formatter config | No config found |
| **B7** | Commit audit | 4 sub-steps: format, drift, CHANGELOG, version | Sub-steps degrade gracefully per missing baseline |
| **B8** | Cross-platform shell | Non-portable patterns (`which`, `grep -P`, `sed -i` without backup) | No `.sh` files |
| **B9** | CI efficiency | Trigger scoping, caching, artifact separation | No `.github/workflows/` |
| **B10** | .gitignore + meta | 6-category coverage + instruction-file conflicts | — |
| **B11** | Co-author guard | 4-layer `*-by:` trailer enforcement | Single-contributor repos |
| **C1** | Detect targets | Heuristic scan or `.repo-health.json` | No sync target clues found |
| **C2** | Pre-sync verify | Phase B must have no BLOCKING items | — |
| **C3** | Execute sync | Default copy or declared `install_cmd` | — |
| **C4** | Post-sync verify | File walk or `diff -rq` | — |

Phase B gates Phase C: never sync a broken repo. Full detail in
[SKILL.md](SKILL.md).

---

## Dependencies

- **git** — all checks operate on a git repository
- **shellcheck** — required for B2 (skipped gracefully if absent)
- **gh** CLI — required for B5 (tag vs release); skipped gracefully if absent
None are hard requirements — the skill degrades gracefully when a tool is
not on PATH, skipping the check and logging the reason.

---

## Per-project configuration

Add a `.repo-health.json` at your repo root to override heuristics, declare
sync targets, or add a custom consistency check. See
[`references/repo-health-json-schema.md`](references/repo-health-json-schema.md).

---

## Project structure

```text
├── SKILL.md              # Canonical skill definition
├── README.md             # User-facing install/quickstart
├── SECURITY.md           # Security policy and reporting
├── .gitattributes        # Git/Linguist configuration
├── .gitignore            # B10 target (agent-artifact + OS/IDE patterns)
├── LICENSE               # MIT
├── .repo-health.json     # Self-configuration for the skill's own repo
├── .github/
│   └── workflows/
│       └── ci.yml        # CI pipeline
├── docs/
│   ├── README.md         # Audience note
│   ├── maintaining.md    # Maintainer workflow
│   ├── decisions.md      # Architecture rationale
│   ├── research.md       # Evidence base
│   └── doc-standards.json# Doc completeness manifest
├── references/           # Per-check detail and configuration
├── scripts/              # Enforcement scripts
└── skills/               # Deployable skill package
    └── repo-health-and-sync-skill/
        ├── SKILL.md
        ├── references/    # Per-check detail (subset)
        └── scripts/
            └── check-commit-trailers.py
```

---

## Design principles

- **Portable grep** — the skill enforces POSIX-compatible grep (`-E`, never `-P`)
- **Proportionate anti-drift** — every check traces to an observed failure
- **Zero tags is valid** — some healthy projects never tag
- **Repo as source** — maintainer tooling stays out of user installs

Full principles in [SKILL.md §B0](SKILL.md#b0-design-principles-read-before-phase-b).

---

## See also

- [Hermes Agent docs](https://hermes-agent.nousresearch.com/docs) — skills,
  install, configuration
- [CodeSigils/agents-markdown-formatter](https://github.com/CodeSigils/agents-markdown-formatter) — GFM/MDX formatter with structural guards

---

## License

MIT — see [LICENSE](LICENSE).
