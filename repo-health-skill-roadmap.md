# `repo-health-scan` Growth Roadmap

**Status:** Codex-first development

**Last reconciled:** 2026-07-13

This roadmap is based on the current repository, recorded compatibility tests,
official platform documentation, and the research sources listed below. It
separates completed foundation work, the active Codex milestone, and deferred
cross-agent expansion so completed tasks do not remain disguised as open work.

---

## 1. Product Direction

`repo-health-scan` is a read-only methodology for terminal-capable coding
agents. It discovers repository shape, infers relevant invariants, and reports
concrete harm and remediation without applying a universal checklist.

The current priority is not adding more health dimensions. It is making the
existing three-step contract reliably observable in Codex:

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
| The full Codex audit emitted a correct final profile and actionable findings but probed weakly justified dimensions before emitting the profile. | Tighten profile ordering and dimension activation before declaring full workflow conformance. |
| Current Codex skill validation rejects the blanket `compatibility` frontmatter field. | Record compatibility per agent instead of declaring `compatibility: all`. |
| GitHub documents `GH_TOKEN` for GitHub CLI API access in Actions and SSH/GPG/S/MIME for commit or tag signing. | Keep CI API authorization separate from git provenance policy. |
| Repository-context research warns that excess context can increase cost or reduce task performance. | Add profile fields through evidence-activated modules with strict budgets. |
| Comparative skill repositories use platform-specific packaging alongside portable skill content. | Consider broader packaging only after each target is verified directly. |

Primary sources and research, accessed 2026-07-12 or 2026-07-13:

- https://learn.chatgpt.com/docs/build-plugins
- https://learn.chatgpt.com/docs/build-skills
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
| Final reporting | The full audit produced a structured final profile, concrete harm, remediation, and correct payload/tooling classification. |
| Probe correctness | Dirty-tree, TOML/JSON version parsing, attribution range, and command-block examples were corrected and smoke-tested. |
| Runtime boundary | The shipped payload is one `SKILL.md`; Python and shell scripts are maintainer-only. |
| Eval contract | `evals/cases/repo-health-scan.json` covers positive/negative triggers, this skill pack, and a Python library using `uv`. |
| Eval validation | `scripts/validate-evals.py` enforces profile-first ordering, activation evidence, skip reasons, and fixture diversity. |
| Release consistency | The checker validates `SKILL.md`, plugin metadata, `CITATION.cff`, tags, and GitHub releases. Strict CI queries use a read-only job token. |
| Repository verification | Script self-tests, Ruff, ShellCheck, documentation audit, plugin validation, skill validation, and diff checks pass independently. |

### Remaining Gaps

| Gap | Consequence | Priority |
|---|---|---|
| The full Codex transcript did not emit the structured profile before dimension probes. | The required Discover -> Infer boundary is not externally auditable. | High |
| Codex selected cross-platform and attribution checks without strong profile evidence. | The skill can drift back toward a broad checklist and waste context. | High |
| The eval is a deterministic contract validator, not a model grader. | CI cannot prove future Codex output conforms to the contract. | Medium |
| No focused security/trust review exists. | Operational skill text could acquire unsafe or over-broad instructions unnoticed. | Medium |
| Codex setup is embedded in README rather than a focused setup document. | Installation evidence is harder to reproduce and maintain. | Medium |
| `v0.2.0` predates the current Codex packaging, eval, and validation work. | The latest release does not contain the current implementation. | High before release |

---

## 4. Active Milestone: Codex Workflow Conformance

**Goal:** move the Codex report from `workflow_partially_verified` to
`workflow_verified` without expanding the methodology.

Update `SKILL.md` so Step 1 and Step 2 have an observable handoff:

- Require the agent to emit the structured `observed`/`inferred` profile before
  running any dimension-specific command.
- Require every active dimension to name at least one profile signal that
  activated it.
- Require an explicit skip reason when a nearby dimension lacks activation
  evidence.
- Keep cross-platform checks inactive unless the profile contains a platform or
  user requirement.
- Keep attribution checks inactive when there are no commits outside the base
  branch or no attribution policy is present.
- Preserve read-only behavior and the distinction between shipped payload and
  maintainer-only tooling.

Rerun the isolated implicit Codex audit after the instruction change. Record the
CLI version, prompt, selected skill, profile event, activated dimensions,
skipped dimensions, findings, and deviations in
`docs/compatibility-reports/codex.md`.

Acceptance criteria:

- Implicit discovery still selects `repo-health-scan`.
- A structured profile appears in the transcript before the first dimension
  probe.
- Every active dimension cites profile evidence.
- Dimensions without evidence are skipped before probing.
- Findings retain concrete harm and remediation.
- No repository files are modified by the audit.
- The compatibility report status becomes `workflow_verified`, or remains
  partial with the exact failed criterion recorded.

---

## 5. Ordered Follow-ups

### 5.1 Security and Trust Review

Add a concise checklist to `SECURITY.md` or `docs/maintaining.md` covering:

- Accurate, bounded trigger language.
- No hidden actions, approval bypasses, or destructive commands.
- Read-only runtime probes by default.
- Opt-in network and JSONL behavior.
- No secrets or personal credentials in fixtures and transcripts.
- Per-agent compatibility evidence with exact tested versions.
- Clear separation between skill payload and maintainer tooling.

Acceptance: the checklist is part of maintainer verification and the current
skill passes it.

### 5.2 Codex Setup Document

Create `docs/codex-setup.md` from the verified local marketplace procedure.
Document repository-local skill placement separately from plugin installation,
include the tested CLI version, and link to the compatibility report. Do not
copy the full transcript into the setup guide.

Acceptance: a clean isolated Codex home can install and discover the skill by
following only the setup document.

### 5.3 Release Current Codex Work

After workflow conformance and security review:

- Choose the next semantic version based on the accumulated behavior and
  packaging changes; `0.3.0` is the current recommendation.
- Update `SKILL.md`, `.codex-plugin/plugin.json`, and `CITATION.cff` together.
- Run strict release consistency with authenticated GitHub access.
- Commit using the documented what/why convention.
- Create a new signed tag; do not move `v0.2.0`.
- Publish the matching GitHub release and rerun strict consistency.

Acceptance: local metadata, tag, GitHub release, and released plugin payload all
identify the same artifact.

### 5.4 Model-Driven Regression Harness

Investigate a repeatable Codex transcript runner only after the instruction
contract is stable. Keep the deterministic JSON eval as the fast CI layer.

Minimum grader assertions:

- Skill selected for positive prompts and not selected for negative prompts.
- Profile event precedes dimension events.
- Every dimension event includes valid `activated_by` profile paths.
- Skipped dimensions are never reported as PASS.
- Findings include harm and remediation.

Do not make ordinary pull requests depend on a flaky or account-dependent model
run. Use scheduled, manual, or release-gate execution unless reliability and
cost are demonstrated.

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

Implement profile modules only after the active Codex conformance milestone;
otherwise they increase the behavior surface before the core ordering contract
is reliable.

---

## 8. Priority Queue

| Order | Action | Effort | Impact |
|---:|---|---:|---|
| 1 | Tighten profile emission and dimension activation; rerun Codex transcript. | 1-2 hr | High |
| 2 | Add and execute the security/trust checklist. | 45-60 min | High |
| 3 | Add the focused Codex setup document and reproduce it from a clean home. | 1 hr | Medium |
| 4 | Prepare and publish the next coherent release without moving `v0.2.0`. | 1-2 hr | High |
| 5 | Design a non-blocking model-driven regression harness. | 1 day | Medium |
| 6 | Add evidence-activated profile modules with field budgets. | 1 day | Medium |

Completed foundation:

- Corrected methodology probes and structured profile.
- Added trigger-aware skill anatomy and valid Codex plugin packaging.
- Verified local plugin installation and implicit Codex discovery.
- Captured the first full workflow transcript and deviations.
- Added deterministic eval fixtures and validation.
- Fixed dirty-tree verification.
- Enforced local/tag/release version consistency with strict CI API behavior.
- Removed unsupported blanket compatibility metadata.

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
│   ├── codex-setup.md                  # next focused setup artifact
│   ├── maintaining.md
│   ├── decisions.md
│   └── compatibility-reports/
│       └── codex.md
└── scripts/                            # maintainer-only validation
```
