---
status: maintainer-reference
purpose: Developer workflow guide for maintainers of this skill.
audience: maintainers only — not shipped to skill users.
related: AGENTS.md routes agents to this maintainer reference.
---

# Maintaining the Repo Health Scan Skill

## Commit convention

Every commit must answer what and why. Use this body format:

```text
what: <one-line description of the change>
why:  <reason — design rationale, observed failure, user request, or finding>
```

Subject line: `type: scope — description`.

| Type | When to use |
| :--- | :---------- |
| `feat:` | New methodology addition |
| `docs:` | Documentation (README, docs/) |
| `refactor:` | Restructuring, no behaviour change |
| `fix:` | Bug fix in SKILL.md |
| `chore:` | Housekeeping (.gitignore, CI) |

## Verification checklist

Before marking work done, run through in order:

1. **Tree clean** — `git status --porcelain` shows nothing
2. **Doc audit passes** — `python3 scripts/doc-audit.py --self-test`
3. **No stale refs** — `grep -rn --include='*.md' 'PLAN\\.md\\|PROPOSALS\\.md\\|REPORT\\.md\\|USER-SUGGESTIONS\\.md' . | grep -v '.git/'` returns nothing
4. **Shellcheck clean** — on any modified `.sh` files
5. **Eval contract valid** — `python3 scripts/validate-evals.py`
6. **Trust contract valid** — `python3 scripts/check-trust.py`
7. **Versions aligned** — `python3 scripts/check-version-consistency.py`

The model regression is deliberately outside this required fast checklist.
After a material `SKILL.md` workflow or trigger change, run
`python3 scripts/run-codex-regression.py` locally or dispatch the dedicated
`Codex regression` workflow. Do not make ordinary changes depend on model
availability.

## How the skill works

The skill is a single SKILL.md with no shipped scripts, no reference files,
and no build process. The agent discovers repo characteristics at runtime
using tools already on PATH (`git`, `shellcheck`, `python3`, `gh`).

Changes to the methodology go directly into `skills/repo-health-and-sync-skill/SKILL.md`.
There is no sync step, no payload regeneration, and no duplicate reference
copies to maintain.

Root `AGENTS.md` is a routing adapter, not a second maintainer guide. It points
repository-health work to `SKILL.md` and repository changes to this file.

## Project structure

```text
├── .github/workflows/ci.yml
├── .gitignore
├── .gitattributes
├── AGENTS.md                      # Repository-level agent routing
├── CITATION.cff
├── LICENSE
├── README.md
├── SECURITY.md
├── docs/                          # Maintainer docs (not shipped)
│   ├── README.md
│   ├── codex-setup.md
│   ├── maintaining.md
│   ├── decisions.md
│   ├── research.md
│   └── doc-standards.json
├── evals/
│   └── cases/
│       └── repo-health-scan.json  # Local behavioral contract
├── scripts/                       # CI-only tooling (not shipped)
│   ├── check-expiry.py
│   ├── check-portability.py
│   ├── check-trust.py
│   ├── doc-audit.py
│   ├── extract-tests.py
│   ├── grade-codex-transcript.py
│   ├── run-codex-regression.py
│   ├── validate-evals.py
│   ├── validate-scripts.py
│   ├── verify-urls.py
│   └── verify.sh
└── skills/
    └── repo-health-and-sync-skill/
        └── SKILL.md               # The entire skill
```

## Common pitfalls

1. **Speculative checks.** A methodology addition needs an observed failure
   or a documented ecosystem pattern, not "seems useful."
2. **Over-instruction.** The methodology should be compact enough that the agent
   can read and apply it in one pass. If the SKILL.md grows significantly,
   trim the methodology back rather than adding reference files. Trust the
   agent's judgment for details; the methodology teaches *how to decide*,
   not *what to check*.
3. **Ecosystem drift.** The tools on PATH change over time. Verify that
   detection commands in SKILL.md still work against current tool versions.
4. **Platform-specific commands in a portable methodology.** Do not add
   Hermes-specific commands (`skill_view`, `hermes skills`) or agent-specific
   config paths to the skill payload. Track platform packaging and behavior in
   compatibility reports instead.
