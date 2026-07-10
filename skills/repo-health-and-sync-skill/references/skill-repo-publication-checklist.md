# Skill Repo Publication Readiness

Beyond the generic B1-B12 health checks, agent skill repos need
additional verification before being made public. These checks
ensure the repo is discoverable, usable across runtimes, and
clearly communicates its purpose.

## Publication checklist

Run these in order after B1-B12 pass.

### P1: Agent-facing orientation

**Why:** A cold-landing agent needs to understand the repo's skill
structure without reading every SKILL.md file. Without orientation,
the agent wastes a session start discovering the routing pattern.

**Check:** Does the repo have an `AGENTS.md` or equivalent instruction
file that tells a cold agent how to use the skills?

**Severity:** RECOMMENDED. Without it, the agent will discover skills
through description matching alone — which works, but is slower and
may load the wrong sub-skill first.

**Remediation:** Add a short AGENTS.md (10-20 lines) that:
- States what the repo ships (e.g. "router + 5 focused sub-skills")
- Tells the agent which skill to load first
- Lists the sub-skills and when each applies
- Notes any cross-agent compatibility guarantees

See `py-review-skill/AGENTS.md` for a minimal example: 16 lines,
no governance, just cold-landing utility.

---

### P2: Per-platform install guidance

**Why:** Different agent runtimes have different skill discovery paths
(Hermes hub install, Claude Code `.claude/skills/`, Gemini CLI
`.agents/skills/`, Codex `.codex/skills/`, Cursor `.cursor/rules/`).
A README that only documents Hermes install excludes most of the
agentskills.io ecosystem.

**Check:** Does the README document install paths for at least the
most common agent runtimes (Hermes, Claude Code, Codex, OpenCode)?

**Severity:** RECOMMENDED. Users on undocumented platforms must
reverse-engineer the skill structure.

**Remediation:** Add collapsed `<details>` sections per platform
with the exact copy/symlink command. Example in
`py-review-skill/README.md` (6 platforms).

---

### P2a: README structure pattern

**Why:** A consistent README structure across skill repos makes them
easier to scan and reduces cognitive load for users who work with
multiple skills. The pattern that emerged from standardising
py-review-skill and python-project-workflow is:

```text
1. Badges row (license, CI, language, agentskills.io)
2. Description paragraph + per-feature bullets
3. Quick Start (collapsed per-platform install details)
4. How to Use (numbered steps)
5. Portability section (CI gate commitment)
6. Verify (local check commands)
7. Layout (file tree with shipping boundary annotation)
8. References table
9. License
```

**Check:** Does the README follow the structure above? In particular,
does it have a Portability section (P4's commitment to the user) and
a Layout section with the shipping boundary called out?

**Severity:** INFO. A working repo with a non-standard README is still
a working repo. But the structure is a form of machine-truth — a reader
who knows the pattern can find any section without reading the whole
file.

**Remediation:** Reorder sections to match. Add the Portability section
even if brief — it communicates cross-agent commitment to the reader.

---

### P3: Freshness markers

**Why:** Skill rules that reference external documentation (Python
docs, PEPs, library APIs) decay when the referenced source changes.
Without freshness markers, neither the author nor the agent knows
whether a rule is still current.

**Check:** Do rules with external references carry `Checked:` and
`Expires:` markers?

**Severity:** WARNING for rules with external references; INFO for
purely internal conventions (stable Python idioms). Rules without
external references should carry an explicit "stable, no external
refs" marker so readers don't wonder if it was forgotten.

**Remediation:** Add a `**Freshness:**` line per skill file or per
rule. Common values:
- `stable (no external references)` for core conventions
- `Checked: YYYY-MM-DD` + `Expires: YYYY-MM-DD` for volatile references

---

### P4: Portability gate in CI

**Why:** A skill repo may be cross-agent compatible at creation but
silently drift toward platform-specific references with any commit.
No runtime validates this — a Hermes agent never flags Hermes-only
refs as a problem, but a Codex agent silently misreads them.

**Check:** Does the CI workflow include a portability scan that
rejects agent-specific references (`skill_view`, `hermes skills`,
`Claude()`, platform adapter paths)?

**Severity:** BLOCKING for any repo that targets multiple runtimes.
The cost is ~75 lines of Python + 1 CI step. The failure mode
(silent cross-agent breakage) has been proven real (see
`2026-07-01-skill-discovery-durable-findings.md` §2).

**Remediation:** Add a portability checker script modeled on
`skill-discovery/.github/scripts/ci-check.py` or
`py-review-skill/.github/scripts/check-portability.py`. Run it
as the first CI step.

---

### P5: Rule schema enforcement

**Why:** Skill repos with structured review rules benefit from
programmatic schema validation. Without it, rules can drift in
format, missing required fields, or break naming conventions.

**Check:** If the repo defines structured rules (impact levels,
incorrect/correct examples, field labels), is the schema enforced
by CI or only by convention?

**Severity:** WARNING. Without enforcement, rule consistency depends
on manual review, which is the weakest validator.

**Remediation:** Add a validate.py that checks required fields,
impact values, naming prefix conventions, and code block presence.
See `py-review-skill/scripts/validate.py` for a reference
implementation with 175 lines of Python.

---

### P6: GitHub metadata

**Why:** A public repo with empty description and no topics is
invisible to GitHub search and ecosystem directories (Hermes Atlas,
agentskills.io, awesome lists).

**Check:** Does the GitHub repo have a non-empty description and at
least 3-5 relevant topics?

**Severity:** RECOMMENDED. Low effort, high discoverability impact.

**Remediation:**
```bash
gh repo edit <owner>/<repo> \
  --description "One-line description of what the skills do" \
  --add-topic "agentskills" \
  --add-topic "<domain>" \
  --add-topic "agent-skills"
```
Good default topics: `agentskills`, `agent-skills`, the domain
(e.g. `python`, `code-review`), and target platforms
(`hermes-agent`, `claude-code`, `codex`).

---

### P7: CI badge in README

**Why:** A CI badge is the first signal a visitor sees about repo
health. Absence suggests the project has no automated validation.

**Check:** Does the README have a CI badge pointing at the workflow?

**Severity:** INFO. Cosmetic but high-signal.

**Remediation:**
```markdown
[![CI](https://github.com/<owner>/<repo>/actions/workflows/ci.yml/badge.svg)](https://github.com/<owner>/<repo>/actions)
```

---

### P8: Set repo visibility

**Why:** A skill repo that remains private is invisible to the
ecosystem regardless of its quality.

**Check:** Is the repo public?

**Severity:** BLOCKING for any repo that should be discoverable.

**Remediation:**
```bash
gh repo edit <owner>/<repo> --visibility public
```

Note: This cannot be undone for repos that contain sensitive
history. Verify no secrets or credentials in git history before
running.

---

## Sequence for a publication readiness review

`\`\`text
1. Run B1-B12 (generic health baselines)
2. Check P1 (AGENTS.md presence)
3. Check P2 (per-platform README install docs)
4. Check P2a (README structure pattern)
5. Check P3 (freshness markers on volatile rules)
6. Check P4 (portability CI gate)
7. Check P5 (rule schema enforcement)
8. Check P6 (GitHub description + topics)
9. Check P7 (CI badge)
10. Check P8 (repo visibility)
11. Fix all BLOCKING items, then WARNINGs, then RECOMMENDEDs
`\`\`

BLOCKING items prevent publication. WARNINGs degrade user experience.
RECOMMENDEDs are quality-of-life improvements.

## References

- py-review-skill publication: `CodeSigils/py-review-skill` — reference
  implementation of all P1-P8 checks (commit 7cc717a, 313bd68)
- cross-agent portability gate: `references/cross-agent-portability.md`
  (this skill) — detailed pattern table and CI enforcement
- skill-discovery publication: `CodeSigils/skill-discovery` — portability
  gate, scoped CI, exclusion-table pattern
