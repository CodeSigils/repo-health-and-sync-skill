# AGENTS.md — Repo Health and Sync Skill

This file governs how this repository is developed. Read it first before
modifying the skill. Canonical skill behaviour is in [SKILL.md §B0](SKILL.md#b0-design-principles-read-before-phase-b).

---

## Commit convention

Every commit must answer what and why. Use this body format:

```
what: <one-line description of the change>
why:  <reason — design rationale, observed failure, user request, or finding>
```

Subject line: `type: scope — description`. Types match this repo's commit convention:

- `feat:` — new check, reference file, or B-phase addition
- `docs:` — documentation (AGENTS.md, README, docs/)
- `refactor:` — restructuring, no behaviour change
- `fix:` — bug fix in skill code or reference files
- `chore:` — housekeeping (gitignore, CI)

An agent reading `git log` cold should understand *what* was built, *why*,
and *what evidence* supported it — without reading SKILL.md. Cite evidence
sources (survey finding, user suggestion number, observed failure).

---

## Maintainer principles (adapted from SKILL.md §B0)

These apply to *how we develop this skill*, not what the skill checks.

| Principle | Why | Canonical source |
| :-------- | :-- | :--------------- |
| **Proportionate anti-drift** | Every addition traces to observed failure or user request. Speculative checks accumulate debt. | [SKILL.md §B0](SKILL.md#b0-design-principles-read-before-phase-b) |
| **Repo as source** | `scripts/`, `.github/`, `docs/` are never sync targets. | [SKILL.md §C](SKILL.md#c1-detect-targets) |
| **Portable grep** | `-P` is GNU-only; use `-E` or awk/sed instead. | [SKILL.md §B8](SKILL.md#b8-cross-platform-shell) |
| **Cross-reference integrity** | Every `references/*.md` link resolves. Verify after rename/delete. | [SKILL.md](SKILL.md) § verification |
| **File-swamp ceiling** | `references/` hard ceiling: 15 files. | [docs/decisions.md](docs/decisions.md) §15-file ceiling |
| **Quality-skill fallback** | Probe tool availability before depending on it. Degrade gracefully. | [SKILL.md §B6](SKILL.md#b6-format--lint) |
| **Script decomposition** | `scripts/` uses delegation: `verify.sh` orchestrates, focused scripts own one concern each. Soft ceiling of 5 files before splitting into subdirectories. | [verify.sh](scripts/verify.sh) → [doc-audit.py](scripts/doc-audit.py) + [check-commit-trailers.py](scripts/check-commit-trailers.py) |

---

## Documentation standards

Documentation completeness is enforced by `scripts/doc-audit.py` reading
`docs/doc-standards.json` — the manifest IS the spec. Adding a new requirement
means adding one entry to the JSON file; no shell greps to maintain.

Currently the manifest covers `README.md` and `AGENTS.md` (project
structure). The architecture supports multi-file manifests — add new file
keys to the JSON to extend. Contributions are welcome for SKILL.md,
`docs/README.md`, and reference file standards.

**Guard structural content against drift.** Lists, trees, and lookup tables
that enumerate tracked files, directories, or phases must be verified against
`git ls-files` (or equivalent) via `doc-standards.json`. An omission in a
listing is a documentation defect — the manifest should catch it.
`contains-all` checks are the simplest mechanism: a flat list of expected
entries in one check, matching any occurrence in the target file. Use this
whenever documentation enumerates a bounded set of real artifacts.

Run `bash scripts/verify.sh` before every commit; it includes the doc audit
and validates the manifest schema via `--self-test`.

---

## How to add or modify a B-check

1. **Decide scope** — new B-check (B12), extend existing one, or add reference?
2. **Ground it** — needs observed failure or user request, false-positive assessment, severity, and skip condition.
3. **Update SKILL.md** — follow `### B<N>: Title` → Why → How → Severity → Remediation → Reference link.
4. **Update or add reference file** — detail in `references/`, not inline. Every file needs YAML frontmatter.
5. **Update docs/research.md** — add evidence with quality label (research-backed / observed / pragmatic).
6. **Update docs/decisions.md** — record architectural shifts.
7. **Verify** — see [Verification checklist](#verification-checklist) below.
8. **Commit** — structured what:/why: body, evidence cited.

---

## Verification checklist

Before marking work done, run through this checklist in order:

1. **Tree clean** — `git status --porcelain` shows nothing
2. **Self-tests pass** — `python3 scripts/check-commit-trailers.py --self-test`,
   `python3 scripts/doc-audit.py --self-test`, and
   `bash scripts/verify.sh --self-test`
3. **Cross-refs resolve** — `bash scripts/verify.sh` checks every `references/*.md`
   linked from SKILL.md and validates `docs/doc-standards.json` schema.
   (No inline command — this file is the pointer, that file is the check.)
4. **No stale refs** — `grep -rn --include='*.md' 'PLAN\.md\|PROPOSALS\.md\|REPORT\.md\|USER-SUGGESTIONS\.md' . | grep -v '.git/'` returns nothing
5. **SKILL.md under 650 lines** — `wc -l < SKILL.md` must be ≤ 650
6. **Tagged releases** — every user-facing change gets an annotated tag (`git tag -a`)
7. **Shellcheck clean** — on any modified `.sh` files

For complex changes, write a temporary verification script under
`/tmp/hermes-verify-*.sh` and clean it up after.

---

## Project structure (canonical source: `git ls-files`)

Only file that is not a tracked file and lives at repo root: none —
the repo has only tracked files, no uncommitted infrastructure.
Top-level layout:

- **AGENTS.md** — maintainer instructions (this file)
- **SKILL.md** — canonical skill definition
- **README.md** — user-facing install/quickstart
- **LICENSE** — MIT
- **.gitattributes** — Git/Linguist configuration
- **.gitignore** — agent state + OS/IDE junk
- **.repo-health.json** — self-configuration for the skill's own repo
- **docs/** — 3 files + doc-standards.json: README.md (audience), decisions.md (architecture), research.md (evidence)
- **references/** — one concern per file
- **scripts/** — `check-commit-trailers.py` (Python checker, 12/12 self-test), `doc-audit.py` (manifest-driven doc checker)

Key constraint: maintainer-only paths (`scripts/`, `.github/` if present, `docs/`) are
never included in Phase C sync targets. See [SKILL.md §C](SKILL.md#c1-detect-targets).

---

## Common pitfalls

These are the patterns most likely to cause rework or drift:

1. **Duplicating content between SKILL.md and references/.** Detail goes in
   references/; SKILL.md holds the index and per-check Why/How/Severity.
2. **Speculative checks.** "Seems useful" without an observed failure or
   user request will accumulate maintenance debt before value.
3. **Forgetting to update cross-refs on rename/delete.** A single stale
   `references/` link breaks the skill. Verify with the checklist above.
4. **Letting SKILL.md grow past 650 lines.** When it approaches this ceiling,
   extract to a new reference file or consolidate existing ones.
