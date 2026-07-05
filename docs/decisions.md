# Decisions — Repo Health and Sync Skill

**Purpose:** This file records the project's course — what was built, why, and
what decisions shaped it. A maintainer reviewing this project should understand
the architecture and rationale without reading the other docs files.

**References:** Research evidence that informed these decisions is in
`docs/research.md`. The skill itself is `SKILL.md`.

---

## Project scope

Two-phase procedure for any git repository:

- **Phase B** — Project health baseline (B1-B11). Inspects the repo at runtime
  for git hygiene, shell safety, version alignment, commit quality, CI
  efficiency, and metadata integrity.
- **Phase C** — Reverse sync (C1-C4). Deploys repo content to runtime targets
  (skill directories, config mirrors, etc.) with repo-as-source discipline.

Phase B gates Phase C: never sync a broken repo.

---

## Architecture decisions

### Single-file skill + reference files

**Decision:** SKILL.md is the canonical skill definition (~550 lines). Detail
lives in `references/` (8 files). No content duplicated between them.

**Why:** Single-file index + pointed references is the ecosystem norm across
Hermes, Claude Code, Codex, and Copilot. Inline detail in SKILL.md creates
a drift surface when the same pattern appears in multiple phase sections
(AP1 — duplicate guidance).

### No `templates/` directory

**Decision:** Rejected. SKILL.md contains example commands directly; reference
files contain config schemas when needed.

**Why:** Templates Before Need (AP8). A `.repo-health.json.example` would need
maintenance independent of the schema reference file. The running text in
SKILL.md and `references/repo-health-json-schema.md` serve the same purpose
without an extra file.

### 8 reference files, not 12

**Decision:** Started from 12 candidates, delivered 8. Prioritised by observed
failure modes.

**Why:** Proportionate anti-drift (B0) — every reference file should trace to
a specific observed failure or concrete user request. The 4 deferred files
(release-checklist.md, ci-wiring.md, mature-project-patterns.md,
script-awareness-chain.md) were not grounded in enough evidence to justify
their maintenance cost.

### 15-file ceiling on references/

**Decision:** Hard ceiling — when a new file would bring the count to 16, an
existing one must be merged, archived, or deleted.

**Why:** File-swamp avoidance (AP7). Each extra file increases scanning time
and cross-reference surface. 15 is the empirically chosen limit from the
ecosystem survey (no surveyed project exceeds this).

### Not a general governance skill

**Decision:** Scope is bounded to git-level health + reverse sync. Does not
cover code quality (linting/formatting beyond detection), CI pipeline design,
or project-specific governance policies.

**Why:** Don't re-invent the wheel (AP9). Existing tools (shellcheck, EditorConfig,
pre-commit, ecosystem formatters) already handle those concerns. The skill
detects whether they're present but does not replace them.

### Eliminated repo CHANGELOG.md

**Decision:** Removed this repo's `CHANGELOG.md` (30bd423). Git tags and
annotated release metadata are the release record.

**Why:** The CHANGELOG was a duplicate drift surface — every commit needed
a CHANGELOG entry AND a commit message, and the two could diverge. Git tags
are single-source: `git tag -a` records the version, `git log` is the
history. The verification checklist now says "every release gets an
annotated tag" instead of "every change gets a CHANGELOG line."

**Impact:**
- `verify.sh` no longer checks for `## Unreleased`
- AGENTS.md checklist item 6 replaced with "Tagged releases"
- SKILL.md references to CHANGELOG remain — they instruct agents about
  checking *other repos'* CHANGELOGs (conceptual, not self-referential)

---

## B0 design principles (read before any phase)

| Principle | Why it exists |
| :-------- | :------------ |
| **Commit log vs CHANGELOG** | `git log` is the authoritative record. CHANGELOG enforcement is proportionate to commit quality. |
| **Detect, don't enforce** | No convention is universal. Discover the project's patterns before imposing rules. |
| **Zero tags is valid** | ohmyzsh (188k stars) proves absence of tags is not a defect. Only stale tags matter. |
| **Proportionate anti-drift** | Every check traces to an observed failure. Speculative checks accumulate debt before value. |
| **Repo as source** | The repo is authoritative; deployed targets are derived. Never ship maintainer tooling to users. |
| **Forge-awareness** | Detection logic is agent-agnostic. Activation mechanism (SKILL.md) is Hermes-specific. Portability tiers documented. |
| **Quality-skill fallback** | Three-layer probe before depending on external tools: skill_view → frontmatter → degraded mode/skip. |

---

## Phase rationale

| Phase | What it checks | Why it matters | Severity if absent |
| :---- | :------------- | :------------- | :----------------- |
| B1 | Git hygiene | Dirty trees, orphan tags, un-pushed commits accumulate misleading context | INFO — actionable |
| B2 | Shellcheck | Shell scripts are the most common automation defect vector | WARNING — actionable |
| B3 | Consistency check | Project-specific invariants cannot be generic; discover and run the project's own check | BLOCKING on drift, WARNING on missing |
| B4 | Version alignment | Version skew between manifests is the leading cause of stale-release bugs | WARNING — multi-source skew |
| B5 | Tag vs Release integrity | Tags and GitHub Releases are separate artifacts; tags can be orphaned | WARNING — actionable |
| B6 | Format + lint | Consistent formatting reduces diff noise and prevents formatting-only commits | WARNING — advisory |
| B7 | Commit audit (4 sub-steps) | Unchecked commits accumulate silently until a release fails | WARNING to BLOCKING per sub-step |
| B8 | Cross-platform shell | Linux-only patterns break CI on macOS/BSD and block cross-platform contributors | WARNING — project-dependent |
| B9 | CI efficiency | Docs-only changes should not trigger full builds; tag pushes should not re-run branch CI | WARNING — advisory, project-dependent |
| B10 | .gitignore + metadata | Build artifacts, OS junk, and agent state leak into commits without .gitignore rules | WARNING — advisory |
| B11 | Co-author guard | Accidental attribution trailers create permanent history artifacts | BLOCKING |

Phase C (C1-C4) syncs repo content to runtime targets. Only runs when Phase B
has no BLOCKING items.

---

## Implementation order

1. **Phase 0:** Extract inline detail to reference files, establish B0 principles
2. **Phase 1:** B7 (commit audit) + drift-pairs reference file
3. **Phase 2:** B11 (co-author guard) + shared Python checker
4. **Phase 3:** B8 (cross-platform shell audit) — parallel with P2
5. **Phase 4:** B9 (CI efficiency audit) — parallel with P2/P3
6. **Phase 5:** B10 (.gitignore + metadata audit)
7. **Phase 6:** Value-added reference files (agent-ecosystem, gitignore-templates)
8. **Phase 7:** End-to-end verification against self
9. **Phase 8:** Move research docs to `docs/`, mark historical files

---

## File structure at completion

```
├── AGENTS.md                 # THIS FILE — how to develop the skill
├── SKILL.md                  # ~601 lines — canonical skill definition
├── README.md                 # User-facing install/quickstart
├── LICENSE                   # MIT
├── .gitignore                # Agent-artifact patterns + OS/IDE junk
├── .gitattributes            # Git/Linguist configuration
├── docs/
│   ├── README.md             # Maintainer audience note
│   ├── decisions.md          # What and why
│   ├── research.md           # Evidence base
│   └── doc-standards.json    # Doc completeness manifest
├── references/               # 8 files — one concern each
│   ├── agent-instruction-ecosystem.md
│   ├── anti-drift-proportionality.md
│   ├── co-author-guard.md
│   ├── drift-pairs.md
│   ├── gitignore-templates.md
│   ├── heuristic-discovery.md
│   ├── repo-health-json-schema.md
│   └── sync-targets.md
└── scripts/
    ├── verify.sh                 # Orchestration (self-consistency)
    ├── check-commit-trailers.py  # Shared Python checker (12/12 self-test)
    └── doc-audit.py              # Manifest-driven doc completeness audit
```

---

## Key anti-patterns avoided

| AP | Name | What we did instead |
| :- | :--- | :------------------ |
| AP1 | Duplicate guidance | Single-file SKILL.md + pointed references. No content duplicated. |
| AP3 | Speculative checks | Every B-check traces to an observed failure or concrete user request. |
| AP7 | File swamp | 15-file ceiling on references/. Maintainer must merge or delete to add. |
| AP8 | Templates before need | No `templates/` directory. Examples inline in SKILL.md. |
| AP9 | Re-inventing wheels | Shellcheck, EditorConfig, ecosystem formatters — detect, don't replace. |
| AP10 | Shipping maintainer tooling | CI scripts and release infra stay in repo, never sync to user runtime. |
| AP11 | Stale CHANGELOG enforcement | Commit-log-aware: defer to `git log` when commit quality is high. |
