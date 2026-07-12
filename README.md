# Repo Health Scan

[![Release](https://img.shields.io/github/v/release/CodeSigils/repo-health-and-sync-skill?label=release)](https://github.com/CodeSigils/repo-health-and-sync-skill/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A methodology skill that teaches agents how to evaluate any git repository's
health at runtime. The agent discovers the repo's shape, infers what
invariants matter, and checks them using tools already on PATH.

No hardcoded checklists. No reference files. No shipped scripts. The
methodology is the only artifact.

---

## How it works

1. **Load the skill** via your agent's skill system.
2. **Point the agent at a repo** (any git repo, any language, any ecosystem).
3. The agent runs three steps — discover → infer → verify — and reports
   what it finds with judgment proportional to actual harm.

See [SKILL.md](SKILL.md) for the full three-step procedure.

---

## Install

Clone this repo and make the skill discoverable:

```bash
git clone --filter=blob:none https://github.com/CodeSigils/repo-health-and-sync-skill
```

Then choose your platform:

<details>
<summary><b>Hermes Agent</b></summary>

**Recommended for development — clone the repo and add to `external_dirs`:**
```yaml
skills:
  external_dirs:
    - /path/to/repo-health-and-sync-skill/skills
```
This loads the skill directly from the repo — every commit is immediately
reflected without reinstalling. The skill appears as a `local` skill.

**For end users — install from hub:**
```bash
hermes skills install CodeSigils/repo-health-and-sync-skill
```

*Other agents: see sections below for their native setup commands.*
</details>

<details>
<summary><b>Claude Code (Anthropic)</b></summary>

```bash
cp -r repo-health-and-sync-skill/skills/repo-health-and-sync-skill .claude/skills/
```

Claude Code discovers skills by scanning `.claude/skills/` for SKILL.md files.
</details>

<details>
<summary><b>Codex CLI (OpenAI)</b></summary>

```bash
cp -r repo-health-and-sync-skill/skills/repo-health-and-sync-skill .codex/skills/
```

Codex CLI discovers skills in `.codex/skills/` via filesystem walk.
</details>

<details>
<summary><b>OpenCode CLI</b></summary>

```bash
cp -r repo-health-and-sync-skill/skills/repo-health-and-sync-skill .opencode/skills/
```

Or create a symlink (zero-maintenance pointer):

```bash
ln -s /path/to/repo-health-and-sync-skill/skills/repo-health-and-sync-skill .opencode/skills/
```
</details>

<details>
<summary><b>Gemini CLI (Google)</b></summary>

```bash
cp -r repo-health-and-sync-skill/skills/repo-health-and-sync-skill .agents/skills/
```

Gemini CLI explicitly supports `.agents/skills/` as a cross-tool path.
</details>

<details>
<summary><b>Cursor</b></summary>

```bash
cp -r repo-health-and-sync-skill/skills/repo-health-and-sync-skill .cursor/rules/
```

Note: Cursor applies rules as chat context, not via invocation-based
discovery like CLI-focused agents.
</details>

<details>
<summary><b>Generic agentskills.io client</b></summary>

Copy the skill to your agent's configured skills directory. Most clients
that support the agentskills.io standard scan a `skills/` or
`.agents/skills/` directory.

```bash
cp -r repo-health-and-sync-skill/skills/repo-health-and-sync-skill <your-skills-dir>/
```
</details>

---

## What this repo does NOT include

| Excluded | Reason |
|----------|--------|
| Hardcoded checklists | The agent discovers what to check from the repo itself, not from a pre-written table. |
| Reference files | Every fact the skill needs is discovered at runtime (tools on PATH, repo state, filesystem). |
| Shipped scripts | The agent uses `git`, `shellcheck`, `python3`, `gh`, and whatever else is on PATH. |
| Install scripts | Every platform provides native skill consumption paths. A script would compete and drift. |
| Platform adapter files | User-side setup only. The repo ships only `skills/repo-health-and-sync-skill/SKILL.md`. |
| Plugin manifest | Filesystem discovery is sufficient at 1 skill. |
| Hermes-specific logic | The methodology is agent-agnostic. No `skill_view()`, no Hermes config paths. |

---

## Dependencies

None shipped. The skill expects the agent to have access to general-purpose
tools: `git`, `shellcheck`, `python3`. If a tool is absent, the agent
skips that dimension and reports the gap.

---

## Per-project configuration

Add a `.repo-health.json` at the repo root to override the agent's
heuristic discovery — declare which checks to skip, which version sources
to use, or a custom consistency check.

---

## Project structure

```text
├── .github/
│   └── workflows/
│       └── ci.yml        # CI pipeline
├── .gitignore
├── .repo-health.json
├── CITATION.cff
├── LICENSE
├── README.md
├── SECURITY.md
├── docs/                 # Maintainer documentation
│   ├── README.md
│   ├── maintaining.md
│   ├── decisions.md
│   ├── research.md
│   └── doc-standards.json
├── scripts/              # CI-only tooling (not shipped)
│   ├── check-expiry.py
│   ├── check-portability.py
│   ├── doc-audit.py
│   ├── extract-tests.py
│   ├── validate-scripts.py
│   ├── verify-urls.py
│   └── verify.sh
├── test-fixtures.json
└── skills/
    └── repo-health-and-sync-skill/
        └── SKILL.md      # The entire skill — one file, nothing else
```

---

## Design principles

**The repo tells you what it needs.** Do not bring expectations. Every
repo is different — the methodology discovers the shape before forming
judgments.

**Every invariant traces to a concrete failure.** If you cannot describe
the harm a broken invariant would cause, the check is speculative. Skip it.

**Run once, observe broadly.** One `git log`, one `find`, one `ls` should
give the repo's shape. Do not chain five commands to confirm what the
first two already show.

**Ship the methodology, not the collection.** The agent already has the
tools to check repo health. What it needs is a framework for deciding
what to check. That framework fits in one SKILL.md.

---

## See also

- [Hermes Agent docs](https://hermes-agent.nousresearch.com/docs) — skills,
  install, configuration
- [CodeSigils/agents-markdown-formatter](https://github.com/CodeSigils/agents-markdown-formatter) — GFM/MDX formatter with structural guards

---

## License

MIT — see [LICENSE](LICENSE).
