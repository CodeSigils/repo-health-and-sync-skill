# Codex Compatibility Report

Status: `install_verified`

Date: 2026-07-13

## Scope

This report verifies Codex plugin packaging and local marketplace installation
for `repo-health-and-sync-skill`. It does not yet verify model-driven workflow
activation or Step 1 -> Step 2 -> Step 3 behavior.

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

## Trigger Prompt

Planned prompt for workflow verification:

```text
Audit this repository before release using repo-health-scan.
```

## Workflow Result

Not yet run.

Expected behavior for the next compatibility step:

- Codex selects `repo-health-scan` from the trigger prompt.
- Codex writes a structured repo profile before dimension checks.
- Codex checks only dimensions relevant to the profile.
- Codex reports findings with concrete harm and remediation.
- Codex does not describe maintainer-only scripts as shipped runtime payload.

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
