# `repo-health-scan` Growth Roadmap

**Status:** Codex-first development

**Last reconciled:** 2026-07-13

This roadmap is based on the current repository, recorded compatibility tests,
official platform documentation, and the research sources listed below. It
separates completed foundation work, ordered Codex follow-ups, and deferred
cross-agent expansion so completed tasks do not remain disguised as open work.

---

## 1. Product Direction

`repo-health-scan` is a read-only methodology for terminal-capable coding
agents. It discovers repository shape, infers relevant invariants, and reports
concrete harm and remediation without applying a universal checklist.

The three-step contract is now observable in Codex:

1. Discover and emit a structured repository profile.
2. Select dimensions using explicit evidence from that profile.
3. Report only relevant findings with concrete harm and remediation.

Codex is the only active compatibility target. Other agents remain potential
targets, not verified support claims.

---

## 2. Evidence Baseline

| Evidence | Decision Supported |
|---|---|
| OpenAI plugin documentation requires `.codex-plugin/plugin.json` and supports a plugin-root-relative `skills` path. | Keep Codex packaging separate from the portable `SKILL.md` payload. |
| OpenAI skill documentation describes metadata-first discovery and progressive disclosure. | Keep trigger language precise and the loaded skill concise. |
| The 2026-07-13 isolated Codex transcript selected the unnamed skill prompt and loaded the installed payload. | Treat implicit Codex discovery as verified for CLI 0.133.0. |
| The 2026-07-13 conformance retest emitted the profile and evidence-linked dimension plan before health checks. | Treat the core Codex workflow as verified and preserve it with deterministic evals. |
| Current Codex skill validation rejects the blanket `compatibility` frontmatter field. | Record compatibility per agent instead of declaring `compatibility: all`. |
| GitHub documents `GH_TOKEN` for GitHub CLI API access in Actions and SSH/GPG/S/MIME for commit or tag signing. | Keep CI API authorization separate from git provenance policy. |
| Repository-context research warns that excess context can increase cost or reduce task performance. | Add profile fields through evidence-activated modules with strict budgets. |
| Addy Osmani's `agent-skills` keeps shared `SKILL.md` workflows alongside focused per-agent setup guides, verification, and limitations. | Keep README concise, maintain a dedicated Codex guide, and add other agent guides only with direct evidence. |
| Official Codex non-interactive guidance documents `codex exec --json`, ephemeral sessions, explicit sandboxes, and machine-readable output schemas. | Use raw JSONL locally and a schema-constrained final result for deterministic grading. |
| Official Codex GitHub Action guidance keeps the API key behind a proxy and supports read-only execution on trusted triggers. | Use the official action for manual and scheduled hosted runs; never expose the key to repository shell steps. |

Primary sources and research, accessed 2026-07-12 or 2026-07-13:

- https://learn.chatgpt.com/docs/build-plugins
- https://learn.chatgpt.com/docs/build-skills
- https://developers.openai.com/codex/noninteractive
- https://developers.openai.com/codex/github-action
- https://docs.github.com/en/actions/tutorials/authenticate-with-github_token
- https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits
- https://github.com/addyosmani/agent-skills
- https://arxiv.org/abs/2607.01456
- https://arxiv.org/abs/2605.11418
- https://arxiv.org/abs/2607.00911
- https://arxiv.org/abs/2606.17819
- https://arxiv.org/abs/2602.11988
- https://arxiv.org/abs/2606.14066

---

## 3. Current State

### Verified

| Area | Evidence |
|---|---|
| Skill schema | Current Codex skill validator passes. Frontmatter contains supported fields only. |
| Codex packaging | Plugin validator passes; local marketplace installation is verified. |
| Codex discovery | An unnamed release-audit prompt selected `repo-health-scan` and loaded the installed skill. |
| Codex workflow | The isolated retest emitted the profile and complete dimension plan before probes; all active checks cited profile evidence. |
| Codex setup | The focused guide was reproduced from a clean isolated `CODEX_HOME`; plugin installation and implicit discovery passed. |
| Final reporting | The full audit produced a structured final profile, concrete harm, remediation, and correct payload/tooling classification. |
| Probe correctness | Dirty-tree, TOML/JSON version parsing, attribution range, and command-block examples were corrected and smoke-tested. |
| Runtime boundary | The shipped payload is one `SKILL.md`; Python and shell scripts are maintainer-only. |
| Eval contract | `evals/cases/repo-health-scan.json` covers positive/negative triggers, this skill pack, and a Python library using `uv`. |
| Eval validation | `scripts/validate-evals.py` enforces profile-first ordering, activation evidence, skip reasons, and fixture diversity. |
| Security and trust | `scripts/check-trust.py` enforces bounded triggers, read-only instructions, opt-in network/output behavior, credential hygiene, versioned compatibility evidence, and payload separation. |
| Release consistency | The checker validates `SKILL.md`, plugin metadata, `CITATION.cff`, tags, and GitHub releases. Strict CI queries use a read-only job token. |
| Repository verification | Script self-tests, Ruff, ShellCheck, documentation audit, plugin validation, skill validation, and diff checks pass independently. |
| Local model regression | The first Codex CLI 0.133.0 run passed positive selection, profile/plan ordering, evidence-backed dimension accounting, seeded finding quality, and negative non-selection. |

### Remaining Gaps

| Gap | Consequence | Priority |
|---|---|---|
| The hosted Codex Action workflow has not completed its first run. | Local auth and execution do not prove the GitHub secret, action, and artifact path work together. | High |
| The model harness has one passing run and no reliability baseline. | A single pass cannot justify making the workflow blocking or estimate stable runtime and usage. | Medium |

---

## 4. Completed Milestone: Codex Workflow Conformance

**Result:** `workflow_verified` on Codex CLI 0.133.0.

`SKILL.md` now gives Step 1 and Step 2 an observable handoff:

- Require the agent to emit the structured `observed`/`inferred` profile before
  running any dimension-specific command.
- Require every active dimension to name at least one profile signal that
  activated it.
- Require an explicit skip reason for every candidate dimension that lacks
  activation evidence.
- Keep cross-platform checks inactive unless the profile contains a platform or
  user requirement.
- Keep attribution checks inactive when there are no commits outside the base
  branch or no attribution policy is present.
- Preserve read-only behavior and the distinction between shipped payload and
  maintainer-only tooling.

The isolated implicit Codex audit and its environment, prompt, selected skill,
profile event, dimension plan, findings, and deviations are recorded in
`docs/compatibility-reports/codex.md`.

Acceptance evidence:

- Implicit discovery still selects `repo-health-scan`.
- A structured profile appears in the transcript before the first dimension
  probe.
- Every active dimension cites profile evidence.
- Dimensions without evidence are skipped before probing.
- Findings retain concrete harm and remediation.
- No repository files are modified by the audit.
- The compatibility report status is `workflow_verified`.

---

## 5. Release Milestone and Ordered Follow-up

### 5.1 Completed: Release Current Codex Work

**Result:** `v0.3.0` published on 2026-07-13.

- Updated `SKILL.md`, `.codex-plugin/plugin.json`, and `CITATION.cff` together.
- Confirmed README describes the released behavior, Codex compatibility status,
  opt-in interfaces, and repository shape.
- Created a signed release commit and a new signed `v0.3.0` tag without moving
  `v0.2.0`.
- Published the matching GitHub release.
- Reran strict consistency and the full repository verifier successfully.

Acceptance met: local metadata, tag, GitHub release, and released plugin payload
all identify version `0.3.0`.

### 5.2 Implemented: Model-Driven Regression Harness

**Local result:** `verified_once` on Codex CLI 0.133.0 on 2026-07-13.

The harness now includes:

- An isolated Python/`uv` fixture with positive and negative prompts.
- A local `codex exec --json` runner that captures raw event streams and final
  responses while enforcing read-only, ephemeral execution.
- A deterministic grader for selection, raw profile/plan ordering,
  `activated_by` evidence, complete dimension accounting, skip behavior,
  seeded finding quality, severity ordering, and negative non-selection.
- A separate manual/weekly GitHub workflow using the official Codex Action and
  read-only safety strategy.
- Artifact and reliability documentation in `docs/codex-regression.md`.

First-run assertions:

- Positive skill selection and negative non-selection passed.
- The populated profile preceded the populated dimension plan.
- Every active dimension cited a valid profile path.
- All ten candidate dimensions were active or explicitly skipped.
- The seeded dirty-tree finding named the defect, harm, and remediation.

The hosted workflow remains `pending_first_run`. Keep the deterministic JSON
eval as the fast CI layer and do not make ordinary pull requests depend on the
model run until repeated executions demonstrate reliability, runtime, and
acceptable usage.

---

## 6. Deferred Work

These items are intentionally outside the current Codex-first milestone:

| Item | Resume When |
|---|---|
| Gemini, Claude Code, OpenCode, Cursor, or Hermes verification | Codex workflow conformance and setup are stable. |
| Root `plugin.json` and `npx skills add` claim | The current CLI contract is verified against this repository. |
| Additional per-agent setup guides and compatibility reports | The relevant agent is selected as an active target and tested directly. |
| `repo-sync` companion skill | Scan findings and the human approval boundary are stable. |
| Organization-wide scanner and dashboard | Single-repository JSONL behavior is executable and evaluated, not only instructional. |
| Generic CI integration guide | A real agent runtime and failure policy are selected. |
| `AGENTS.md` | A durable repository instruction need appears that is not already owned by `docs/maintaining.md`. |
| `CHANGELOG.md` | Release cadence makes a changelog more useful than GitHub release notes alone. |

No deferred item should appear in README as verified support before its own
fixture or compatibility report exists.

---

## 7. Future Profile Scaling

Keep the mandatory profile small:

```yaml
observed:
  languages:
  ci:
  package_managers:
  script_surface:
  shipped_payload:

inferred:
  repo_type:
  release_model:
  risk_context:
```

Activate optional modules only from Step 1 evidence:

| Module | Activation Evidence | Maximum Fields |
|---|---|---:|
| `release` | Tag, changelog, registry, container, or release workflow. | 6 |
| `agent` | Skill, plugin manifest, or agent instruction file. | 6 |
| `monorepo` | Workspace manifest or multiple packages/services. | 6 |
| `security` | Security policy, scanning, permissions, secrets, or signing policy. | 6 |
| `docs` | Documentation is the product or handoff risk is active. | 6 |

Profile rules:

- Core profile target: 8-10 fields; hard cap: 12.
- Optional module target: 4 fields; hard cap: 6.
- Every optional field carries one evidence path or command result.
- Confidence is `observed`, `inferred-high`, `inferred-low`, or `unknown`.
- Unknown is valid; never invent a value to activate a check.
- Modules add questions, not mandatory PASS/FAIL dimensions.

Implement profile modules only after repeated model-regression runs establish a
reliability and usage baseline; otherwise they expand the behavior surface
before the evaluation path is proven stable.

---

## 8. Priority Queue

| Order | Action | Effort | Impact |
|---:|---|---:|---|
| 1 | Configure the API-key secret, pass one manual hosted run, then enable the schedule and collect at least five runs with pass rate, duration, and token usage. | 1-2 hr plus observation | High |
| 2 | Tune the harness only for observed reliability or usage problems. | 0.5-1 day | Medium |
| 3 | Add evidence-activated profile modules with field budgets. | 1 day | Medium |

Completed foundation:

- Corrected methodology probes and structured profile.
- Added trigger-aware skill anatomy and valid Codex plugin packaging.
- Verified local plugin installation and implicit Codex discovery.
- Captured the first full workflow transcript and deviations.
- Verified profile-first Codex workflow conformance in an isolated read-only run.
- Added and executed the security/trust checklist as a local and CI gate.
- Reconciled README with Codex-only evidence and documented opt-in behavior.
- Added the focused Codex setup guide and reproduced it from an isolated home.
- Added deterministic eval fixtures and validation.
- Fixed dirty-tree verification.
- Enforced local/tag/release version consistency with strict CI API behavior.
- Removed unsupported blanket compatibility metadata.
- Published signed release `v0.3.0` with aligned skill, plugin, citation, tag,
  and GitHub Release versions.
- Added and locally verified the non-blocking Codex model regression runner,
  deterministic grader, isolated fixture, and trusted-trigger hosted workflow.

---

## 9. Constraints

1. The scan remains read-only and never becomes the fixer.
2. Repository evidence selects checks; there is no universal checklist.
3. Maintainer scripts never become required runtime payload implicitly.
4. Instruction-level JSONL and `.repo-health.json` remain labelled as contracts,
   not executable features.
5. Compatibility and installability claims require per-agent fixtures or
   reports.
6. External-facing decisions use current primary sources and record access
   dates; purely local command fixes use local tests.
7. API authorization and git provenance remain separate controls.
8. Profile growth follows progressive disclosure and strict field budgets.
9. Human approval separates scan findings from any future synchronization or
   repair workflow.

---

## 10. Near-Term Repository Shape

```text
repo-health-and-sync-skill/
├── .codex-plugin/
│   └── plugin.json
├── .github/workflows/ci.yml
├── README.md
├── SECURITY.md
├── repo-health-skill-roadmap.md
├── skills/
│   └── repo-health-and-sync-skill/
│       └── SKILL.md
├── evals/
│   └── cases/
│       └── repo-health-scan.json
├── docs/
│   ├── codex-setup.md                  # verified Codex setup
│   ├── maintaining.md
│   ├── decisions.md
│   └── compatibility-reports/
│       └── codex.md
└── scripts/                            # maintainer-only validation
    └── check-trust.py                  # security and trust contract
```
