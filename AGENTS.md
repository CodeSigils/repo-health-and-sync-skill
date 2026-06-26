# AGENTS.md — Repo Health and Sync Skill

This file governs how this repository is developed and maintained. It is the
first thing an agent should read when asked to modify this skill.

---

## Commit convention

Every commit must answer two questions for a human or agent reading the log
cold. Use this format for the commit message body:

```
what: <one-line description of the change>
why:  <reason this change was necessary — design rationale, observed
      failure, user request, or research finding>
```

The subject line should be `type: scope — short description` matching the
conventional-commits style this project uses in its own CHANGELOG:

- `feat:` — new check, reference file, or B-phase addition
- `docs:` — documentation (AGENTS.md, README, docs/, comment-only changes)
- `refactor:` — restructuring with no behaviour change
- `fix:` — bug fix in skill code or reference files
- `chore:` — housekeeping (gitignore, changelog, CI)

Write detailed bodies. An agent reading `git log` from a fresh clone should
understand *what* was built, *why* it was the right call, and *what evidence*
supported it — without reading SKILL.md. Include the evidence source when
relevant (survey finding, user suggestion number, observed failure).

**Examples of good vs poor commits from this project's history:**

| Good | Poor |
| :--- | :--- |
| `docs: B0 portable-grep principle, fix 2 GNU-only violations` | `changelog: flatten doc update` |
| Body explains the rule, where the violations were, and the fix. | Single line, no why, reader must chase the diff. |

---

## This project's own B0 principles

These apply to *how we develop the skill itself*, not what the skill checks.

### Proportionate anti-drift
Every new check or reference file must trace to a specific observed failure,
concrete user request, or systematic research finding. Speculative additions
accumulate maintenance debt. When unsure, add to `docs/research.md` as a
research target instead of implementing directly.

### Repo as source (applies to us)
`scripts/`, `.github/`, and `docs/` are maintainer-only. They are never sync
targets. The CHANGELOG and AGENTS.md stay in the repo; they are *not* part
of the skill runtime.

### Portable grep in skill code
Every `grep` command in SKILL.md, reference files, and scripts must use
POSIX-compatible flags. `-P` (PCRE) is GNU-only and fails on BSD/macOS.
Use `-E` for extended regex or POSIX basic regex by default. For extraction
logic that PCRE `\K` enables, use `awk` or `sed` instead.

### Cross-reference integrity
Every path in a reference link (`references/foo.md`) must resolve to a real
file. Verify after any rename, delete, or addition with `git ls-files`.

### Quality-skill fallback (also applies to us)
Before depending on an external tool (shellcheck, formatters, linters) in
a verification script or detection pattern, probe availability and degrade
gracefully. Never hardcode a path or assume installation.

### File-swamp ceiling
`references/` has a 15-file hard ceiling. Adding a 9th file means one of the
existing 8 must be merged, archived, or deleted. Same principle applies to
`scripts/` — one script, one concern.

---

## File structure

```
├── AGENTS.md              # THIS FILE — how to develop the skill
├── SKILL.md               # Canonical skill definition (~575 lines)
├── CHANGELOG.md           # Release line per unreleased feature
├── README.md              # User-facing install and quickstart
├── LICENSE                # MIT
├── .gitignore             # Agent local state + OS/IDE junk
├── docs/
│   ├── README.md          # Maintainer audience note
│   ├── decisions.md       # Architecture decisions and phase rationale
│   └── research.md        # Evidence base and survey data
├── references/            # 8 files — one concern each
│   ├── agent-instruction-ecosystem.md
│   ├── anti-drift-proportionality.md
│   ├── co-author-guard.md
│   ├── drift-pairs.md
│   ├── gitignore-templates.md
│   ├── heuristic-discovery.md
│   ├── repo-health-json-schema.md
│   └── sync-targets.md
└── scripts/
    └── check-commit-trailers.py  # Shared Python checker (10/10 self-test)
```

---

## How to add or modify a B-check

1. **Decide where it belongs.** Does it add a new B-check (B12), extend an
   existing one, or add a reference file for an existing check?

2. **Ground it.** Every new check needs:
   - **Observed failure** or **user request** (cite the source)
   - **False-positive assessment** — when would this fire incorrectly?
   - **Severity** (INFO / WARNING / BLOCKING) with the criterion
   - **Skip condition** — how does the agent know to skip gracefully?

3. **Update SKILL.md.** Add a section following the existing structure:
   `### B<N>: Title` → Why → How → Severity → Remediation → Reference link.

4. **Update or add reference file.** Detail goes in `references/`, not inline.
   Each reference file starts with YAML frontmatter (title, description, status).

5. **Update docs/research.md.** Add the evidence or research that supports
   the check. Label it by evidence quality (research-backed / observed /
   pragmatic).

6. **Update docs/decisions.md.** If the new check changes architecture or
   introduces a new principle, record it in the decisions file.

7. **Update CHANGELOG.md.** Every user-facing change gets a `-` line in
   `## Unreleased`.

8. **Verify.** Write a temporary verification script that exercises the
   change, run it, then clean it up. At minimum, run:
   - `git status --porcelain` — confirm clean tree
   - `python3 scripts/check-commit-trailers.py --self-test`
   - Cross-reference integrity (every `references/*.md` in SKILL.md resolves)
   - Shellcheck on any new `.sh` files

9. **Commit** with structured what:/why: body.

---

## Shellcheck compliance

Every `.sh` file in this repo must pass shellcheck with zero warnings.
This is enforced by the project's own B2 check. Run before committing:

```bash
shellcheck scripts/*.sh 2>/dev/null || shellcheck --shell=bash scripts/*.sh
```

If the repo contains no `.sh` files at a given point, that's fine — but any
`.sh` file added must pass shellcheck.

---

## Changelog discipline

Every change that affects SKILL.md, reference files, scripts, or docs gets
a line in `## Unreleased`. The line should be a concise summary that
a downstream reader (or a release notes generator) can understand.

When releasing, create an annotated tag, update `## Unreleased` to a version
heading, and push. The `gh release create` step is separate from tagging.

---

## Verification standard

Before marking work as done:

1. **Tree is clean** — `git status --porcelain` shows nothing
2. **Self-tests pass** — `python3 scripts/check-commit-trailers.py --self-test`
3. **Cross-refs resolve** — every `references/foo.md` linked from SKILL.md exists
4. **No stale references** — old deleted files are not referenced anywhere
5. **SKILL.md under 600 lines** — hard ceiling
6. **CHANGELOG updated** — if the change is user-facing
7. **Shellcheck clean** — on any modified `.sh` files

For complex changes, write an ad-hoc temporary verification script under
`/tmp/hermes-verify-*.sh` and clean it up after.

---

## Research and evidence standards

This project maintains two distinct doc types:

| File | Content | Audience |
| :--- | :------ | :------- |
| `docs/decisions.md` | What was built, why, architecture rationale | Maintainer reviewing the project |
| `docs/research.md` | Survey data, ecosystem tables, evidence findings | Maintainer evaluating evidence |

Evidence quality labels (used in research.md):

- **research-backed** — grounded in systematic survey or documented study
- **observed** — grounded in specific user observation or single source
- **pragmatic** — common-sense design choice with no formal study

Promote labels when new evidence supports them. Never leave a label at
"pragmatic" when research exists that could back it.

---

## Common pitfalls for maintainers

1. **Duplicating content between SKILL.md and references/.** If the same
   detail appears in both, it will drift. SKILL.md holds the index and
   per-check "Why / How / Severity / Remediation"; references hold the detail.

2. **Adding speculative checks.** "Seems useful" is not a sufficient reason.
   Every B-check traces to an observed failure or user request.

3. **Forgetting to update cross-refs on rename/delete.** `references/` and
   `SKILL.md` must stay in sync. Verify with a quick grep after structural
   changes.

4. **Letting SKILL.md grow past 600 lines.** The ceiling is firm. When it
   approaches, extract to a new reference file or consolidate existing ones.

5. **Committing without a structured body.** A one-line subject doesn't
   survive cold-start context. Every commit needs "what:" and "why:" sections.

6. **Shipping maintainer tooling.** `scripts/`, `.github/`, and `docs/` are
   never sync targets. Don't put user-facing content there.
