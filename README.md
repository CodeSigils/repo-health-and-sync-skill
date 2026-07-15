# Repo Health Scan

[![Release](https://img.shields.io/github/v/release/CodeSigils/repo-health-and-sync-skill?label=release)](https://github.com/CodeSigils/repo-health-and-sync-skill/releases)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

**Repo Health Scan** — audits any git repository for release readiness,
maintenance drift, and handoff health. The agent discovers the repo's
shape, infers what invariants matter, and reports findings with concrete
harm and remediation.

This skill handles pre-release audits, unfamiliar-repo onboarding,
dormant-repo revival, CI failure triage, and AI-assisted commit review.
Works on any git repository — Python, Rust, shell, docs-only, or monorepo.

It does **not** ship hardcoded checklists, runtime scripts, or reference
files. Pair it with
[`py-review-skill`](https://github.com/CodeSigils/py-review-skill) for
dedicated Python code review.

The shipped payload is one `SKILL.md` — no agent-specific commands or
paths — so it works with any terminal-capable coding agent. It is
agentskills.io-compatible.

**Compatibility status:** Codex CLI 0.133.0 is the only verified agent target.
The `SKILL.md` payload is designed to be portable, but other agents are not
supported claims until they have their own recorded compatibility tests.

---

## How it works

1. **Load the skill** via your agent's skill system.
2. **Point the agent at a repo** (any git repo, any language, any ecosystem).
3. The agent runs three steps — discover → infer → report — and reports
   what it finds with judgment proportional to actual harm.

See [SKILL.md](skills/repo-health-and-sync-skill/SKILL.md) for the full three-step procedure.

---

## Install

Clone this repo and make the skill discoverable:

```bash
git clone --filter=blob:none https://github.com/CodeSigils/repo-health-and-sync-skill
```

For repository-local Codex use, place the skill under `.agents/skills/`:

```bash
mkdir -p .agents/skills
cp -r repo-health-and-sync-skill/skills/repo-health-and-sync-skill .agents/skills/
```

Codex discovers repository skills from `.agents/skills/`. For reusable
distribution, this repository includes `.codex-plugin/plugin.json`. The tested
repository-local and marketplace procedures are in the
[Codex setup guide](docs/codex-setup.md); exact test evidence is recorded in the
[Codex compatibility report](docs/compatibility-reports/codex.md).

Other agents may be able to consume the portable `SKILL.md`, but installation,
discovery, and workflow behavior remain unverified. Platform-specific setup
instructions will be added only with a matching compatibility report. The
[skill portability contract](docs/portability-contract.md) defines the claim
levels and evidence required before support is advertised.

---

## What this repo does NOT include

| Excluded | Reason |
|----------|--------|
| Hardcoded checklists | The agent discovers what to check from the repo itself, not from a pre-written table. |
| Reference files | Every fact the skill needs is discovered at runtime (tools on PATH, repo state, filesystem). |
| Shipped runtime scripts | The agent uses `git`, `shellcheck`, `python3`, `gh`, and whatever else is on PATH. |
| Install scripts | Every platform provides native skill consumption paths. A script would compete and drift. |
| Platform adapter files | User-side setup only. The repo ships only `skills/repo-health-and-sync-skill/SKILL.md`. |
| Runtime plugin code | The Codex plugin manifest points at the skill directory; it does not add runtime scripts, hooks, MCP servers, or connectors. |

---

## Dependencies

None shipped with the skill payload. The skill expects the agent to have
access to general-purpose tools already on PATH: `git`, `shellcheck`,
`python3`, and optionally `gh`. If a tool is absent, the agent skips that
dimension and reports the gap.

The Python and shell files under `scripts/` are maintainer-only checks for
this repository's CI and documentation. They are not installed as skill
runtime helpers and should not be copied into `skills/repo-health-and-sync-skill/`.

The optional [Codex model regression](docs/codex-regression.md) runs positive
and negative prompts against an isolated fixture. It is manual or scheduled,
uses a read-only sandbox, and does not block ordinary pull requests.

---

## Per-project configuration

Add a `.repo-health.json` at the repo root to override the agent's
heuristic discovery — declare which checks to skip, which version sources
to use, or a custom consistency check.

Optional behavior is explicit:

| Variable | Effect |
|---|---|
| `REPO_HEALTH_VERIFY_RELEASES=1` | Allow the GitHub release query for tag/release integrity. |
| `REPO_HEALTH_VERIFY_REFS=1` | Allow network checks for external references. |
| `REPO_HEALTH_OUTPUT=jsonl` | Emit automation-oriented JSONL instead of the normal report. |

---

## Project structure

```text
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Deterministic CI pipeline
│       └── codex-regression.yml      # Non-blocking model evaluation
├── .codex-plugin/
│   └── plugin.json       # Codex plugin manifest
├── .gitignore
├── AGENTS.md             # Repository-level agent routing
├── CITATION.cff
├── LICENSE
├── README.md
├── repo-health-skill-roadmap.md
├── SECURITY.md
├── docs/                 # Maintainer documentation
│   ├── README.md
│   ├── codex-setup.md
│   ├── codex-regression.md
│   ├── portability-contract.md
│   ├── compatibility-reports/
│   │   └── codex.md
│   ├── maintaining.md
│   ├── decisions.md
│   ├── evidence-urls.json
│   ├── research.md
│   └── doc-standards.json
├── evals/
│   ├── cases/
│   │   └── repo-health-scan.json  # Local behavioral contract
│   └── codex/                     # Model prompts and output schema
├── scripts/              # CI-only tooling (not shipped)
│   ├── check-expiry.py
│   ├── check-portability.py
│   ├── check-trust.py
│   ├── check-version-consistency.py
│   ├── doc-audit.py
│   ├── extract-tests.py
│   ├── grade-codex-transcript.py
│   ├── run-codex-regression.py
│   ├── validate-evals.py
│   ├── validate-scripts.py
│   ├── verify.sh
│   └── verify-urls.py
├── skills/
│   └── repo-health-and-sync-skill/
│       └── SKILL.md      # The entire skill — one file, nothing else
```

---

## Design principles

**The repo tells you what it needs.** Do not bring expectations. Every
repo is different — the methodology discovers the shape before forming
judgments.

**Every invariant traces to a concrete failure.** If you cannot describe
the harm a broken invariant would cause, the check is speculative. Skip it.

**Run once, observe broadly.** One `ls`, one `find`, one `git log`
should give you the repo's shape. Do not chain five commands to
confirm what the first two already showed.

**Write the profile before the checks.** If you don't know the repo's
languages, tools, commit culture, and CI system, you cannot meaningfully
assess its health. Step 1 is not optional.

**The right number of checks is the one the repo needs, not the
one the skill defines.**

---

## See also

- [Codex compatibility report](docs/compatibility-reports/codex.md) — tested
  version, installation evidence, and workflow results
- [Codex setup guide](docs/codex-setup.md) — repository-local and plugin setup
- [Codex model regression](docs/codex-regression.md) — isolated runner, grader,
  and non-blocking workflow
- [Skill portability contract](docs/portability-contract.md) — canonical
  payload, thin adapters, and per-runtime certification
- [Growth roadmap](repo-health-skill-roadmap.md) — verified scope and ordered
  follow-ups
- [Maintainer guide](docs/maintaining.md) — repository verification and release
  workflow
- [CodeSigils/agents-markdown-formatter](https://github.com/CodeSigils/agents-markdown-formatter) — GFM/MDX formatter with structural guards

---

## License

MIT — see [LICENSE](LICENSE).
