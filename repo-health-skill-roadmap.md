# `repo-health-scan` — Evidence-Backed Growth Roadmap

**Cross-agent compatibility, repository governance, and skill quality strategy**

Generated July 2026 from local inspection of this repository plus public evidence
from the `addyosmani/agent-skills` repository, OpenAI Codex plugin docs, and
recent agent-skill research. External sources were accessed on 2026-07-12.

---

## 1. Executive Summary

The core `repo-health-scan` idea is strong: it is a read-only methodology that
asks the agent to discover repository shape, infer relevant invariants, and
report concrete harm instead of applying a universal checklist.

The roadmap should shift from "add more checks" to "make the skill easier to
discover, safer to trust, and easier to verify across agents." Public evidence
supports five near-term moves:

1. Fix factual probe issues in `SKILL.md` so the methodology's example
   commands do what they claim.
2. Align `SKILL.md` with common skill anatomy: Overview, When to Use, Process,
   Common Rationalizations, Red Flags, and Verification.
3. Add precise trigger language to frontmatter because skill descriptions are
   used for auto-discovery.
4. Separate generic skills packaging from Codex plugin packaging. Codex uses
   `.codex-plugin/plugin.json`; a root `plugin.json` alone is not sufficient.
5. Add lightweight eval and compatibility fixtures, but describe them as local
   evidence unless a specific registry contract is verified.

---

## 2. Evidence Snapshot

| Evidence | What It Supports | Roadmap Impact |
|---|---|---|
| `addyosmani/agent-skills` README advertises `npx skills add addyosmani/agent-skills` and lists many supported agents. | A skills pack can be distributed broadly through a CLI and agent-specific setup paths. | Keep the distribution goal, but test this repo's exact manifest requirements before promising installability. |
| `addyosmani/agent-skills` includes root `plugin.json`, `AGENTS.md`, `docs/*-setup.md`, `evals/`, `.codex-plugin/`, `.gemini/`, and `.opencode/`. | Mature packs carry both generic skill metadata and platform-specific integration files. | Add the same categories incrementally, starting with metadata and one setup guide per verified agent. |
| OpenAI Codex plugin docs state every Codex plugin has a manifest at `.codex-plugin/plugin.json` and may include a `skills/` directory. | Codex support requires a Codex-specific manifest path. | Replace the root-only `plugin.json` recommendation with `.codex-plugin/plugin.json` plus optional root metadata if the skills CLI needs it. |
| `agent-skills` Codex setup says Codex consumes the root `skills/` directory and skills are invoked with `@skill-name`. | The current `skills/repo-health-and-sync-skill/SKILL.md` layout can work for Codex once packaged. | Add a Codex setup guide and a local install smoke test. |
| `agent-skills` Gemini setup says Gemini auto-discovers `SKILL.md` files and descriptions matter for activation. | Trigger wording in `description` is operational, not cosmetic. | Make `Use when` phrasing part of Phase 1. |
| Recent research on SKILL.md quality reports widespread skill smells and stresses metadata, behavioral contracts, evaluation, and security risks. | Skill files should be treated as maintained software artifacts. | Add explicit verification, anti-rationalization, eval, and supply-chain review tasks. |
| OpenAI's skills docs describe progressive disclosure and a bounded initial skill list. | Context is scarce; profile growth should be modular and activated only when relevant. | Scale the repo profile through optional modules, not a larger mandatory profile. |
| Repository-context studies report that unnecessary context can raise cost or hurt task performance. | More profile fields are not automatically better. | Add field budgets, evidence requirements, and module activation rules. |
| Repository-exploration research favors focused evidence summaries over broad context dumps. | Profile fields should cite the file or command that justified them. | Add evidence and confidence to future profile modules. |

Sources:

- https://github.com/addyosmani/agent-skills
- https://raw.githubusercontent.com/addyosmani/agent-skills/main/docs/codex-setup.md
- https://raw.githubusercontent.com/addyosmani/agent-skills/main/docs/gemini-cli-setup.md
- https://raw.githubusercontent.com/addyosmani/agent-skills/main/docs/opencode-setup.md
- https://learn.chatgpt.com/docs/build-plugins
- https://learn.chatgpt.com/docs/build-skills
- https://arxiv.org/abs/2607.01456
- https://arxiv.org/abs/2605.11418
- https://arxiv.org/abs/2607.00911
- https://arxiv.org/abs/2606.17819
- https://arxiv.org/abs/2602.11988
- https://arxiv.org/abs/2606.14066

---

## 3. Current-State Review

### What Already Works

| Area | Status |
|---|---|
| Skill path | `skills/repo-health-and-sync-skill/SKILL.md` exists. |
| Frontmatter | Has `name`, `description`, `license`, `compatibility`, and metadata. `compatibility: all` is a claim in metadata; verification should be tracked per agent. |
| Core workflow | Clear discover → infer → report loop. |
| Project philosophy | Avoids a fixed universal checklist. |
| Automation surface | Repo has maintenance scripts and CI, but the skill itself is still methodology-first. |
| Runtime implementation | No executable scanner is shipped. JSONL output and `.repo-health.json` are instruction-level contracts, not enforced code paths. |
| Codex plugin manifest | `.codex-plugin/plugin.json` exists, passes local plugin validation, and installs from a temporary local Codex marketplace. |
| Local verification | Maintainer self-tests cover syntax, documentation audit, portability, and version consistency. |

### Gaps to Fix

| Gap | Risk | Priority |
|---|---|---|
| Some probe examples are factually wrong or ambiguous. | Agents may report false health signals while following the skill exactly. | High |
| The repo profile is too compressed for repo-type-specific suggestions. | Agents must infer too much from three lines and can miss distinctions such as shipped payload vs maintainer tooling. | High |
| README platform-install claims are stale relative to current Codex plugin docs. | Users may install into paths that are not the documented current path. | High |
| Codex workflow activation has not been transcript-tested. | Install works, but skill selection and Step 1 -> Step 2 -> Step 3 behavior are not yet verified in Codex. | High |
| No non-Codex compatibility smoke tests. | `compatibility: all` is a metadata claim, not verified evidence. | High |
| No eval case file. | Hard to regression-test whether agents follow the method. | Medium |
| No security/trust review of skill instructions. | Skill metadata and instructions can influence selection and behavior. | Medium |
| Setup docs are absent. | Users of Codex, Gemini, Cursor, and OpenCode have no clear install path. | Medium |

---

## 4. Phase 0 — Correct the Methodology Examples

**Goal:** make the current single-file skill factually reliable before expanding
distribution.

Fix these concrete issues in `SKILL.md`:

- Replace the history hygiene dirty-tree example. `git status --porcelain`
  exits 0 even when files are dirty, so `git status --porcelain && echo "clean"`
  can print both dirty output and `clean`.
- Replace the version alignment example with real parsers for `package.json`,
  `pyproject.toml`, and `Cargo.toml`, or narrow the example to JSON only. The
  current snippet silently ignores TOML manifests.
- Resolve the attribution drift range conflict. Step 2 describes scanning from
  the latest tag, while the later clarification describes `origin/main..HEAD`.
- Reconcile "run exactly ONE command" with dimensions that currently show
  multiple commands or multi-command snippets.
- Move JSONL and `.repo-health.json` wording into "agent output contract" and
  "optional configuration contract" language so users do not infer executable
  support.
- Fix CI's non-gating smoke test path. It currently references
  `skills/repo-health-and-sync-skill/scripts/check-portability.py`, but this
  repo does not ship scripts inside the skill directory.
- Classify all existing Python scripts as maintainer-only tooling. They may
  validate this repository, but README, `SKILL.md`, install docs, compatibility
  reports, and plugin packaging must not imply they ship as runtime skill
  payload.

Expand the Step 1 profile from a three-line sketch into a short structured
inventory. Keep it concise, but make the dimensions explicit enough to drive
repo-type-specific suggestions:

```text
observed:
  languages: Markdown, Python, shell
  ci: GitHub Actions
  script_surface: maintainer-only Python + shell
  shipped_payload: single SKILL.md

inferred:
  repo_type: skill-pack
  release_model: git tags, GitHub Releases intended
  agent_surface: SKILL.md only; packaging manifests absent
  risk_context: cross-agent distribution
```

Suggested profile fields:

| Field | Why it matters |
|---|---|
| `repo_type` | Separates library, app, CLI, docs, infra, monorepo, and skill-pack expectations. |
| `release_model` | Drives tag/release/package/version checks only when they can cause real harm. |
| `agent_surface` | Makes skill-pack and agent-config checks explicit without applying them to normal repos. |
| `script_surface` | Distinguishes shipped runtime scripts from maintainer-only validation scripts. |
| `shipped_payload` | Prevents maintainer docs/scripts from being mistaken for user-facing functionality. |
| `risk_context` | Tunes the scan for pre-release, handoff, onboarding, failing CI, or routine review. |

Use the expanded profile to suggest checks by repo type without hardcoding a
universal checklist:

| Profile signal | Suggested checks |
|---|---|
| `repo_type=skill-pack` | `SKILL.md` anatomy, trigger description, packaging manifests, compatibility fixtures, instruction/runtime claim consistency. |
| `repo_type=cli` + `script_surface=shell` | Shell correctness, portability, install docs, release tags. |
| `release_model=package registry` | Version alignment, changelog, tag/package consistency. |
| `repo_type=monorepo` + `ci=GitHub Actions` | Path filters, workflow duplication, package boundary drift. |
| `maturity=dormant` or `risk_context=handoff` | Docs freshness, dead links, stale CI, maintainer instructions. |

Exit criteria:

- The examples are copy-pasteable in a normal git repository.
- Every example command's success/failure semantics match the surrounding text.
- The roadmap, README, and `SKILL.md` agree on what is runtime functionality
  versus maintainer-only tooling.
- The profile separates observed facts from inferred labels before any
  repo-type-specific checks are selected.

Phase 0 is the implementation gate for the rest of the roadmap. Do not start
packaging, compatibility reports, or companion skills until these conditions are
met:

- `SKILL.md` probe examples are copy-pasteable and status-correct.
- The structured profile contract is documented in `SKILL.md`.
- README capability and install claims match the skill's actual runtime model.
- CI no longer references nonexistent staged-install paths.
- Python scripts under `scripts/` remain maintainer-only, and no file under
  `skills/repo-health-and-sync-skill/` depends on them.
- A manual transcript or local fixture demonstrates the corrected Step 1 → Step 2
  → Step 3 flow.
- External-facing implementation decisions are grounded in current evidence.
  Web research is not required for purely local command corrections, but is
  required before changing install guidance, plugin manifests, compatibility
  claims, registry claims, or agent-platform behavior. Record the source URL and
  access date in the relevant doc, fixture, or compatibility report.

---

## 5. Phase 1 — Make Activation and Packaging Correct

**Goal:** make the skill discoverable and installable in at least one verified
agent path before broadening distribution language.

### 5.1 Update `SKILL.md` Frontmatter

Status: implemented. The description now uses trigger-aware language:

```yaml
description: >-
  Methodology for evaluating any git repository's health at runtime.
  Guides the agent through discover → infer → report: inspect the
  filesystem and git history, decide which invariants matter for this
  repository, then report findings with concrete harm and remediation.
  Use when asked to audit, review, assess, or check the health of a repo.
  Use before a release, archive, handoff, or onboarding session.
  Use when CI is failing and the cause is unclear.
  Not for single-file edits, narrow bug fixes, or feature implementation.
```

### 5.2 Add Skill Anatomy Sections

Status: implemented. `SKILL.md` now includes:

- `When to Use`
- `When Not to Use`
- `Common Rationalizations`
- `Red Flags`
- `Verification`

The highest-value verification checks:

- A concise structured repo profile was written before dimension checks.
- The profile distinguishes observed facts from inferred repo type and risk
  context.
- Only dimensions relevant to that profile were checked.
- No skipped dimension was reported as PASS.
- Every finding describes concrete harm.
- Blocking findings are listed first.
- JSONL output is only emitted when `REPO_HEALTH_OUTPUT=jsonl` is set.

### 5.3 Update README Install Claims

Status: partially implemented. README now distinguishes repository-local skill
copying from plugin packaging and documents `.agents/skills/` for Codex. Still
verify Hermes-specific instructions before treating them as current.

- Document `.agents/skills/` as the generic repository-skill path when using
  OpenAI's current skills docs.
- Document Codex plugin installation separately from filesystem skill copying.
- Remove or qualify the claim that "filesystem discovery is sufficient" for
  Codex distribution.
- Keep Hermes-specific instructions only if they are still verified against the
  Hermes skill installer.

### 5.4 Validate Codex Plugin Manifest

Status: manifest added and install-verified. OpenAI's Codex plugin docs require:

```text
.codex-plugin/plugin.json
```

The required location and `skills` path shape are evidence-backed from OpenAI
docs. The local manifest also passes the Codex plugin validator and installs
from a temporary local marketplace; see `docs/compatibility-reports/codex.md`.
The remaining Codex work is workflow activation: run a trigger prompt and record
whether Codex follows Step 1 -> Step 2 -> Step 3.

### 5.5 Treat Root `plugin.json` as Generic Skills Metadata

The `addyosmani/agent-skills` repo has a root `plugin.json`, and its README uses
`npx skills add`. Add a root `plugin.json` only after verifying the current
`skills` CLI accepts this repo's structure.

Proposed minimal root metadata:

```json
{
  "name": "repo-health-and-sync-skill",
  "version": "0.2.0",
  "description": "Methodology for evaluating any git repository's health at runtime."
}
```

Do not claim `npx skills add CodeSigils/repo-health-and-sync-skill` works until
it has been tested.

---

## 6. Phase 2 — Prove Compatibility With Small Fixtures

**Goal:** replace `compatibility: all` with repeatable evidence.

Create:

```text
docs/
  codex-setup.md
  gemini-cli-setup.md
  cursor-setup.md
  opencode-setup.md
  compatibility-reports/
    codex.md
    gemini-cli.md
    cursor.md
    opencode.md
```

Each compatibility report should include:

1. Agent/version.
2. Install command or file placement.
3. Trigger prompt.
4. Whether the agent produced Step 1, Step 2, and Step 3 in order.
5. Any deviations, especially skipped repo profile or irrelevant PASS results.

Prefer text transcripts over screenshots. They diff cleanly, survive in git, and
can be reviewed in pull requests.

Treat `compatibility: all` as unverified until these reports exist. Report status
as `claimed`, `verified:<agent>`, or `blocked:<agent>` rather than as a blanket
project property.

---

## 7. Phase 3 — Add Local Evals

**Goal:** detect regressions in the skill's behavioral contract.

Create:

```text
evals/cases/repo-health-scan.json
```

Initial case:

```json
{
  "skill_name": "repo-health-scan",
  "trigger": {
    "positive": [
      { "prompt": "Audit the health of this repo before I cut a release", "top_k": 1 },
      { "prompt": "Check if this repository is in good shape", "top_k": 3 },
      { "prompt": "CI is failing for no obvious reason. Check the repo.", "top_k": 3 }
    ],
    "negative": [
      { "prompt": "Review the changes in this PR", "owner": "code-review-and-quality" },
      { "prompt": "Fix the parser bug in src/parser.ts", "owner": "implementation" }
    ]
  },
  "expectations": [
    "A repo profile is written before any dimension is checked",
    "The profile separates observed facts from inferred repo type and risk context",
    "Repo-type-specific checks are selected from the profile rather than a fixed preset",
    "Only relevant dimensions are checked",
    "Probe command semantics match their reported status",
    "Every finding describes concrete harm",
    "Blocking issues are named first",
    "Skipped dimensions are not reported as PASS"
  ]
}
```

Keep registry claims out of the roadmap until a public registry contract is
confirmed. The eval is still valuable as a local regression fixture.

Acceptance criteria:

- Positive trigger prompts select `repo-health-scan` before general code review
  or implementation workflows.
- Negative prompts do not select `repo-health-scan`.
- At least one fixture covers this repository as a `skill-pack`.
- At least one fixture covers a non-skill repository so profile-specific behavior
  is not overfit to this project.

---

## 8. Phase 4 — Add Security and Trust Review

**Goal:** make the skill safe to distribute.

Recent research treats `SKILL.md` as operational text that can affect discovery,
selection, and agent behavior. Add a small review checklist:

- Frontmatter description is accurate and not over-broad.
- The skill does not ask agents to hide actions, bypass approvals, or execute
  destructive commands.
- External links in docs are verified.
- Runtime commands are read-only unless explicitly documented.
- JSONL automation is opt-in.
- Compatibility reports identify the exact agent version tested.
- Maintainer-only scripts are not represented as runtime skill capabilities.

Add this to either `SECURITY.md` or `docs/maintaining.md`.

---

## 9. Phase 5 — Companion Skills and Automation

**Goal:** extend the ecosystem without weakening the read-only scan contract.

### `repo-sync`

Separate fixer skill. Trigger only after a human reviews `repo-health-scan`
findings.

Scope:

- Manifest version alignment.
- Release/tag consistency repair.
- Commit trailer cleanup.
- Documentation link fixes.

Constraint: no automatic writes from `repo-health-scan`.

### `repo-health-org-scan`

Batch scanner for platform teams.

Inputs:

- GitHub org/repo list.
- Local `repos.txt`.
- Workspace directory.

Output:

- JSONL findings per repo.
- Optional summary dashboard.

### CI Integration

Document CI usage as an example, not as the default execution path. Most CI
systems cannot invoke an interactive coding agent reliably without additional
infrastructure.

Start with:

```text
docs/ci-integration.md
```

Include:

- How to request JSONL output.
- How to fail on blocking findings.
- What is not supported without an agent runtime.

---

## 10. Phase 6 — Scale the Profile With Modules

**Goal:** make the profile useful for larger and more specialized repositories
without bloating every scan.

Keep the core profile mandatory and small:

```text
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

Add optional profile modules only when Step 1 evidence justifies them:

| Module | Activate when | Example fields |
|---|---|---|
| `release` | Tags, changelog, package registry, container, or release workflow exists. | `tags`, `changelog`, `registry`, `release_notes`, `release_owner` |
| `agent` | `SKILL.md`, `.agents/skills`, `.codex-plugin`, `AGENTS.md`, `CLAUDE.md`, or agent rules exist. | `skills`, `plugin_manifests`, `instruction_files`, `compatibility_claims` |
| `monorepo` | Workspace manifests or multiple packages/services exist. | `packages`, `workspace_tool`, `ci_path_filters`, `release_boundaries` |
| `security` | Security policy, dependency scanning, permissions, secrets, or signed-commit policy exists. | `secrets_policy`, `dependency_scanning`, `workflow_permissions`, `signed_commits` |
| `docs` | Docs are the product or handoff/onboarding is the risk context. | `docs_root`, `link_policy`, `maintainer_docs`, `freshness_signal` |

Every optional field should carry compact evidence:

```yaml
release_model:
  value: git tags
  confidence: high
  evidence: "git tag --list 'v*' returned v0.2.0"
```

Budget rules:

- Core profile: target 8-10 fields, hard cap 12.
- Optional module: target 4 fields, hard cap 6.
- Evidence: one path or command result per field.
- Confidence: `observed`, `inferred-high`, `inferred-low`, or `unknown`.
- Unknown is acceptable; do not fill fields by guessing.

Future scans can compare profiles:

```text
profile_changed:
  agent_surface: SKILL.md only -> SKILL.md + .codex-plugin
  release_model: git tags -> git tags + GitHub Releases
```

This lets the skill detect repository evolution without reintroducing a fixed
checklist. The module decides what extra questions to ask; the repo evidence
still decides whether the checks matter.

---

## 11. Revised Priority Matrix

| Action | Effort | Impact | Confidence |
|---|---:|---|---|
| Fix factual probe examples in `SKILL.md` | 1-2 hr | High | High |
| Expand repo profile contract with observed/inferred fields | 1 hr | High | High |
| Add optional profile modules with field budgets | 1 day | Medium | High |
| Classify Python tooling as maintainer-only in docs and checks | 30 min | High | High |
| Verify Codex workflow activation transcript | 30-60 min | High | High |
| Add root `plugin.json` after `npx skills` validation | 30 min | Medium | Medium |
| Add `AGENTS.md` intent mapping | 20 min | Medium | High |
| Add Codex and Gemini setup docs | 1-2 hr | Medium | High |
| Add OpenCode and Cursor setup docs | 1-2 hr | Medium | Medium |
| Add local eval case | 1 hr | Medium | High |
| Add compatibility reports for two agents | 2-4 hr | High | High |
| Add security/trust checklist | 45 min | Medium | High |
| Build `repo-sync` companion skill | 2-3 days | High | Medium |
| Build org scan variant | 3-5 days | High | Medium |
| CI integration doc | 1 day | Medium | Medium |

---

## 12. Design Constraints to Preserve

1. **The scan skill remains read-only.** It can recommend fixes, but it does not
   mutate the repository.
2. **No universal checklist.** The skill teaches the agent how to infer relevant
   checks from the current repository.
3. **No required runtime helper scripts.** Repository maintenance scripts are
   fine, but running `repo-health-scan` should not depend on bundled code.
4. **Python is maintainer tooling unless explicitly repackaged.** Existing
   Python scripts support this repository's CI and documentation checks; they
   are not part of the `repo-health-scan` skill payload.
5. **Human approval between scan and sync.** The companion fixer skill starts
   only after findings are reviewed.
6. **Claims need fixtures.** Any compatibility or installability claim should
   point to a setup doc, report, or reproducible command.
7. **Instruction-level features are labelled as contracts.** Do not imply JSONL,
   `.repo-health.json`, or compatibility behavior is enforced by bundled code.
8. **Profile growth follows progressive disclosure.** Keep the core profile
   small; load optional modules only when repo evidence activates them.
9. **Profile fields need evidence and confidence.** Unknown is better than a
   guessed field that steers the scan toward irrelevant checks.
10. **External-facing changes need current evidence.** Verify platform behavior,
   install paths, manifest schemas, registry rules, security guidance, and
   compatibility claims against primary sources before editing. Local command
   fixes can be grounded in local tests instead.

---

## 13. Target Repository Structure

```text
repo-health-and-sync-skill/
├── .codex-plugin/
│   └── plugin.json
├── AGENTS.md
├── CHANGELOG.md
├── README.md
├── plugin.json                         # only after npx skills validation
├── skills/
│   ├── repo-health-and-sync-skill/
│   │   └── SKILL.md
│   └── repo-sync/
│       └── SKILL.md
├── evals/
│   └── cases/
│       └── repo-health-scan.json
├── docs/
│   ├── codex-setup.md
│   ├── gemini-cli-setup.md
│   ├── cursor-setup.md
│   ├── opencode-setup.md
│   ├── ci-integration.md
│   └── compatibility-reports/
│       ├── codex.md
│       ├── gemini-cli.md
│       ├── cursor.md
│       └── opencode.md
└── scripts/                            # repo maintenance only, not skill runtime
```
