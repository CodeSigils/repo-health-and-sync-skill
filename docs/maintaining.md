---
status: maintainer-reference
purpose: Developer workflow guide for maintainers of this skill.
audience: maintainers only — not shipped to skill users.
supersedes: AGENTS.md
---

# Maintaining the Repo Health Skill

## Commit convention

Every commit must answer what and why. Use this body format:

```
what: <one-line description of the change>
why:  <reason — design rationale, observed failure, user request, or finding>
```

Subject line: `type: scope — description`.

| Type | When to use |
| :--- | :---------- |
| `feat:` | New check, reference file, or B-phase addition |
| `docs:` | Documentation (README, docs/) |
| `refactor:` | Restructuring, no behaviour change |
| `fix:` | Bug fix in skill code or reference files |
| `chore:` | Housekeeping (.gitignore, CI) |

Cite evidence sources (survey finding, user request, observed failure).

## Verification checklist

Before marking work done, run through in order:

1. **Tree clean** — `git status --porcelain` shows nothing
2. **Self-tests pass** — `python3 scripts/check-commit-trailers.py --self-test`,
   `python3 scripts/doc-audit.py --self-test`, and
   `bash scripts/verify.sh --self-test`
3. **Cross-refs resolve** — `bash scripts/verify.sh` checks every `references/*.md`
   linked from SKILL.md and validates `docs/doc-standards.json` schema
4. **No stale refs** — `grep -rn --include='*.md' 'PLAN\.md\|PROPOSALS\.md\|REPORT\.md\|USER-SUGGESTIONS\.md' . | grep -v '.git/'` returns nothing
5. **SKILL.md under 740 lines** — `wc -l < SKILL.md` must be ≤ 740
6. **Tagged releases** — every user-facing change gets an annotated tag (`git tag -a`)
7. **Shellcheck clean** — on any modified `.sh` files

## How to add or modify a B-check

1. **Decide scope** — new B-check (B12), extend existing one, or add reference?
2. **Ground it** — needs observed failure or user request, false-positive assessment, severity, and skip condition.
3. **Update SKILL.md** — follow `### B<N>: Title` → Why → How → Severity → Remediation → Reference link.
4. **Update or add reference file** — detail in `references/`, not inline. Every file needs YAML frontmatter.
5. **Update docs/research.md** — add evidence with quality label (research-backed / observed / pragmatic).
6. **Update docs/decisions.md** — record architectural shifts.
7. **Verify** — see [Verification checklist](#verification-checklist) above.
8. **Commit** — structured what:/why: body, evidence cited.

## Project structure

Top-level layout (canonical source: `git ls-files`):

```
├── SKILL.md              Canonical skill definition
├── README.md             User-facing install/quickstart
├── LICENSE               MIT
├── .gitattributes        Git/Linguist configuration
├── .gitignore            Agent state + OS/IDE junk
├── .repo-health.json     Self-configuration for the skill's own repo
├── docs/
│   ├── README.md         Maintainer docs index
│   ├── maintaining.md    THIS FILE — developer workflow
│   ├── decisions.md      Architecture decisions
│   ├── research.md       Evidence sources
│   └── doc-standards.json Doc audit manifest
├── references/           One concern per file
└── scripts/
    ├── check-commit-trailers.py
    ├── doc-audit.py
    └── verify.sh
```

Key constraint: maintainer-only paths (`scripts/`, `.github/` if present, `docs/`) are
never included in Phase C sync targets. See [SKILL.md §C](SKILL.md#c1-detect-targets).

## Common pitfalls

1. **Duplicating content between SKILL.md and references/.** Detail goes in
   references/; SKILL.md holds the index and per-check Why/How/Severity.
2. **Speculative checks.** "Seems useful" without an observed failure or
   user request will accumulate maintenance debt before value.
3. **Forgetting to update cross-refs on rename/delete.** A single stale
   `references/` link breaks the skill. Verify with the checklist above.
4. **Letting SKILL.md grow past 740 lines.** When it approaches this ceiling,
   extract to a new reference file or consolidate existing ones.
