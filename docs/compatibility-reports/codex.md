# Codex Compatibility Report

Status: `workflow_partially_verified`

Date: 2026-07-13

## Scope

This report verifies Codex plugin packaging, local marketplace installation,
implicit skill discovery, and a model-driven repository audit for
`repo-health-and-sync-skill`. Skill selection and final reporting passed. The
full workflow remains partial because the transcript did not emit the structured
profile as a distinct artifact before dimension commands and selected more
dimensions than the observed profile clearly justified.

## Sources

Accessed 2026-07-13:

- https://learn.chatgpt.com/docs/build-plugins
- https://learn.chatgpt.com/docs/build-skills

Evidence used:

- OpenAI plugin docs require `.codex-plugin/plugin.json`.
- OpenAI plugin docs show `skills` as a plugin-root-relative path such as
  `"./skills/"`.
- OpenAI skills docs describe progressive disclosure: Codex starts from skill
  `name`, `description`, and path before loading full `SKILL.md`.

## Environment

```text
codex-cli 0.133.0
repo: CodeSigils/repo-health-and-sync-skill
plugin: repo-health-and-sync-skill
plugin version: 0.2.0
isolated CODEX_HOME: .codex-test-home
temporary marketplace root: /tmp/repo-health-marketplace
activation CODEX_HOME: /tmp/repo-health-codex-eval-20260713
execution mode: ephemeral, read-only sandbox
```

The install test used an isolated `CODEX_HOME` under the workspace so the user's
real Codex configuration was not modified.

## Commands

Validate plugin manifest against the local Codex plugin validator:

```bash
python3 /home/sand/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py \
  /home/sand/projects/repo-health-and-sync-skill
```

Result:

```text
Plugin validation passed: /home/sand/projects/repo-health-and-sync-skill
```

Register the temporary local marketplace:

```bash
env CODEX_HOME=/home/sand/projects/repo-health-and-sync-skill/.codex-test-home \
  codex plugin marketplace add /tmp/repo-health-marketplace
```

Result:

```text
Added marketplace `repo-health-local` from /tmp/repo-health-marketplace.
Installed marketplace root: /tmp/repo-health-marketplace
```

Install the plugin from that marketplace:

```bash
env CODEX_HOME=/home/sand/projects/repo-health-and-sync-skill/.codex-test-home \
  codex plugin add repo-health-and-sync-skill --marketplace repo-health-local
```

Result:

```text
Added plugin `repo-health-and-sync-skill` from marketplace `repo-health-local`.
Installed plugin root: /home/sand/projects/repo-health-and-sync-skill/.codex-test-home/plugins/cache/repo-health-local/repo-health-and-sync-skill/0.2.0
```

Confirm installed status:

```bash
env CODEX_HOME=/home/sand/projects/repo-health-and-sync-skill/.codex-test-home \
  codex plugin list --marketplace repo-health-local
```

Result:

```text
repo-health-and-sync-skill@repo-health-local  installed, enabled  0.2.0
```

Confirm installed payload:

```text
.codex-plugin/plugin.json
skills/repo-health-and-sync-skill/SKILL.md
```

## Activation Tests

### Implicit Discovery

The first prompt omitted the skill name so that selection depended on the
installed skill metadata:

```text
Audit this repository before release. Before running repository probes,
identify and read any installed skill relevant to this request. State the
selected skill and summarize its three-step workflow, then stop without
performing the audit or modifying files.
```

Transcript excerpt:

```text
I'll use the repo health scan skill because this is a release-readiness
repository audit request.

Selected skill: repo-health-and-sync-skill:repo-health-scan.
```

Codex then read `SKILL.md` from the installed plugin cache and summarized the
Discover -> Infer -> Report workflow without running repository probes. This
verifies description-driven discovery for this prompt on Codex CLI 0.133.0.

### Full Workflow

The second prompt explicitly named the skill to isolate workflow conformance
from discovery:

```text
Audit this repository before release using repo-health-scan. Do not modify
files. Produce the structured observed/inferred repository profile before
selecting health dimensions, then report findings with concrete harm and
remediation.
```

## Workflow Result

| Requirement | Result | Evidence |
|---|---|---|
| Select and load the installed skill | Pass | Codex announced `repo-health-scan` and read `SKILL.md` from the plugin cache before repository inspection. |
| Produce an observed/inferred profile | Pass in final output | The final response began with structured `observed` and `inferred` YAML. |
| Write the profile before dimension checks | Partial | Codex stated that a profile was required and summarized the repo shape, but did not emit the structured YAML profile as a distinct transcript event before running dimension commands. |
| Check only profile-relevant dimensions | Partial | Codex skipped opt-in external reference health, but selected nine dimensions, including cross-platform and attribution checks without strong activation evidence. |
| Explain concrete harm and remediation | Pass | Four findings included impact and a specific remediation. |
| Distinguish payload from maintainer tooling | Pass | The profile identified `SKILL.md` as shipped payload and `scripts/` as maintainer-only. |
| Preserve read-only behavior | Pass | No repository files changed; the run used Codex's read-only sandbox. |

The final profile correctly identified the repository as a Codex plugin and
skill pack with a single shipped `SKILL.md`, maintainer-only Python and shell
scripts, GitHub Actions, no package manager, and a pre-release risk context.

The audit reported four evidence-backed findings:

1. `v0.2.0` points seven commits behind `HEAD`, so it does not identify the
   current artifact.
2. `scripts/check-version-consistency.py` does not enforce the versions in
   `.codex-plugin/plugin.json` or `CITATION.cff`.
3. GitHub release query failures degrade to "No GitHub releases found" and an
   exit-zero consistency result.
4. Recent commit messages do not follow the convention in
   `docs/maintaining.md`.

The first three findings described concrete release or CI harm and actionable
remediation. The fourth was proportionately reported as low impact.

Findings 2 and 3 were subsequently addressed: the checker now validates
`SKILL.md`, `.codex-plugin/plugin.json`, `CITATION.cff`, tags, and available
GitHub releases. CI supplies its read-only job token and treats API query
failure as an error; local runs report an explicit skip when the API is
unavailable.

## Deviations and Follow-up

Codex activation is verified. Full workflow conformance is now represented by
the local contract at `evals/cases/repo-health-scan.json`, which asserts:

- A structured observed/inferred profile appears before any dimension probe.
- Every selected dimension cites the profile signal that activated it.
- Dimensions without activation evidence are explicitly skipped, not probed.

`python3 scripts/validate-evals.py` checks the contract structure, ordering
requirements, profile evidence references, active/skipped separation, and both
skill-pack and non-skill fixtures. It does not run Codex or grade free-form model
output; repeat the transcript test when `SKILL.md` behavior changes materially.

One shellcheck probe initially attempted to write under `/tmp` despite the
read-only run. Codex recognized the sandbox failure and reran the probe without
writing. This did not modify the repository, but the eval should prefer probes
that are read-only on their first attempt.

## Notes

Directly adding this repository as a marketplace failed because a plugin root is
not a marketplace root. The working local marketplace layout was:

```text
/tmp/repo-health-marketplace/
├── .agents/plugins/marketplace.json
└── plugins/repo-health-and-sync-skill/
    ├── .codex-plugin/plugin.json
    └── skills/repo-health-and-sync-skill/SKILL.md
```

Using a symlink from the temporary marketplace plugin path back to this checkout
caused recursive copying because the isolated `CODEX_HOME` lived under the
workspace. The successful test used a minimal non-recursive temp copy containing
only `.codex-plugin/` and `skills/`.
