# portability: allow-platform-ref
# Skill Content Review

Use alongside B12 (Cross-Agent Portability) when reviewing an agent skill
repository. B12 checks whether skill files are *portable*; this checklist
checks whether they are *correct, complete, and well-structured.*

## What makes skill repos different from regular code

Skill files (.md with YAML frontmatter) are both documentation and code: an
agent reads them as runtime instructions, but their correctness is not
mechanically verifiable by tests in the normal sense. Review must focus on
structure, schema, and example quality rather than execution paths.

## Workflow

### 1. Discover the shipped surface

```bash
ls skills/*/SKILL.md            # enumerate skills
git ls-files 'skills/**/*.md'   # ensure all are tracked
```

Expected: every subdirectory under `skills/` has a `SKILL.md`. No orphan
directories, no `.md` files outside `skills/` that should be in it.

### 2. Read all skills in parallel

Batch-read every `skills/*/SKILL.md`. For each:

| Aspect | What to check |
|--------|---------------|
| **Frontmatter** | Only `name` + `description` (agentskills.io v1). Name must match folder. |
| **Description length** | >= 12 words in CI? (longer descriptions improve agent match reliability) |
| **Rule count** | 5-9 per focused skill. Fewer = gaps; more = agent context wasted. |
| **Rule structure** | Every rule has: Impact, Applies when, Skip when, Python, Tools, Review signal, Reason |
| **Incorrect/Correct** | Each rule has both. Verify the pair actually demonstrates the rule (not just adjacent example that happens to illustrate a different point). |
| **Impact consistency** | CRITICAL+HIGH for real correctness/security; LOW for style/opinions |
| **Rule ID prefix** | Each skill's rules start with a consistent prefix matching the domain (`type-*`, `error-*`, `anti-*`, `async-*`, `style-*`). |
| **Portability** | No `skill_view`, `skill_manage`, `hermes skills`, `Claude()`, platform directories |
| **Router table** | If a router skill dispatches to sub-skills, verify the routing table has correct file-to-skill mapping and clear skip-when conditions. |

### 3. Read all validation scripts

Every script in `scripts/` and `.github/scripts/`. For each:

- Does the README or CI describe what it does and is that accurate?
- **Schema enforcer** — what fields does it validate? Are they the right ones?
- **Expiry check** — are there freshness markers (`Checked`/`Expires`)? Is
  expiry checked in CI? Does it fail on expiry or just warn? (Warn = silent rot)
- **Test-case extraction** — script that extracts examples from skill files.
  Should have a `--check` mode that verifies the generated output is up to date.
- **URL verifier** — checks reachability of external references. Should handle
  HEAD-with-GET-fallback for servers that reject HEAD.
- **Portability gate** — scans for agent-specific patterns. What's in the
  forbidden list? Is the gate separate from the general CI or embedded?

### 4. Read the CI workflow

```yaml
- Are all validation scripts actually executed in CI?
- Is there a portability gate?
- Path triggers — do they match the files each validator operates on?
- Schedule — is there a weekly freshness cron?
- Does expiry checking cause a failure (exit 1) or just a warning (exit 0)?
- Python version matrix — does it match the project's `requires-python`?
```

### 5. Read supporting documentation

- **AGENTS.md / CLAUDE.md** — cold-landing agent orientation. Should describe
  what the skills do and how to load them.
- **docs/extraction-log.md** — provenance tracking: where skills were sourced
  from, transformation notes, license.
- **docs/methodology-alignment.md** — design principles and constraints that
  shaped the skill set.
- **README.md** — quick-start instructions for each agent runtime, CI badges,
  validation section, license.

### 6. Check git history

```bash
git log --oneline -20   # commit quality and evolution pattern
git remote -v           # verify origin
```

Look for: meaningful commit messages, evidence of CI fixes or script
iterations, and whether the skill set evolved organically or was a bulk
import.

### 7. Cross-reference for drift

Check that values repeated across files agree:

- Version numbers in `pyproject.toml` / `package.json` / `SKILL.md` frontmatter /
  README badge URLs
- Script descriptions in README match script docstrings
- CI step names match the validation steps listed in README
- Frontmatter `name` matches the parent directory name

### 8. Synthesize findings

Produce a structured report:

| Section | Key questions |
|---------|---------------|
| **Architecture** | Router + sub-skill separation? Single-concern skills? |
| **Content quality** | Rule schema compliance, example accuracy, scope coverage |
| **Portability** | Cross-agent compatibility, CI gate enforcement |
| **Validation infra** | What scripts exist, do they run in CI, are they correct? |
| **Documentation** | README, AGENTS.md, extraction-log, methodology docs |
| **Issues** | Findings with severity (BLOCKING / WARNING / INFO) |
| **Recommendations** | Actionable, prioritized items |

## Common pitfalls

- **Skipping scripts.** Validation scripts are part of the deliverable for a
  skill repo. A broken validator means broken quality assurance. Read every
  script, not just the skill files.
- **Trusting CI at face value.** CI workflows have their own bugs — missing
  path triggers, wrong exit-code handling, scripts that were added to the README
  but never wired into CI. Read the full YAML.
- **Assuming examples prove the rule.** Having an Incorrect/Correct pair is
  necessary but not sufficient. The Incorrect example must be genuinely wrong
  (not just non-idiomatic) and the Correct example must be production-quality,
  not library-prescriptive.
- **Missing the router.** If there's a router skill, routing tables are easy
  to mis-align. A change to one skill may not be reflected in the router's
  trigger table.
- **Ignoring freshness rot.** Skills with external references (`References:`)
  must have `Checked`/`Expires` dates. If the expiry checker returns 0 on
  expired markers (warn-only), those dates silently accumulate into rot.
- **Missing namespace checks.** Rule IDs must be unique across the entire skill
  set, not just within a single skill. Duplicate IDs confuse both agents and
  automated extraction.
- **Flagging fixable issues as inherent limitations.** When you identify a
  concrete problem with a known remediation — dead CI gate, missing
  validator, silent pass-through, stale noqa annotation — implement the fix
  in the same pass. Labeling it an "inherent limitation" or "fundamental
  constraint" wastes the finding. Reserve those labels for genuine tradeoffs
  where every option has a meaningful cost and you've enumerated them. A
  single-pass fix cycle is cheaper than a follow-up commit, and reviewing
  what you just changed is easier than re-context-switching later.
