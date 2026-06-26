---
title: .repo-health.json Schema
description: Schema specification and usage for the per-project override file.
status: reference
supersedes: inline schema in SKILL.md
---

# `.repo-health.json` — Schema Reference

Projects that want explicit configuration (rather than heuristic detection)
can add a `.repo-health.json` at their root. The skill checks for this file
at the start of each phase and uses its values when present.

The schema is versioned to allow evolution. When a `.repo-health.json`
exists, its values take precedence over heuristics. Partial overrides are
supported — missing fields fall back to heuristic detection.

---

## Schema

```json
{
  "version": 1,
  "remotes": ["origin", "ssh-origin"],
  "expected_branch": "main",
  "skip_shellcheck_paths": ["output/**"],
  "skip_version_alignment": false,
  "skip_releases": false,
  "version_files": [
    {
      "path": "package.json",
      "extract": "node -p \"require('./package.json').version\""
    }
  ],
  "consistency_check": "node scripts/check-consistency.js",
  "format_check": "npm run format:check",
  "format_fix": "npm run format",
  "sync_target": {
    "type": "hermes-skill",
    "name": "markdown-formatter",
    "install_cmd": "hermes skills install --force --yes CodeSigils/agents-markdown-formatter/markdown-formatter",
    "post_verify": "node ~/.hermes/skills/markdown-formatter/src/index.js --help"
  }
}
```

---

## Fields

| Field                    | Type             | Required | Description                                                     |
| :----------------------- | :--------------- | :------- | :-------------------------------------------------------------- |
| `version`                | integer          | yes      | Schema version (currently 1).                                   |
| `remotes`                | string[]         | no       | Explicit list of remote names to push to.                       |
| `expected_branch`        | string           | no       | Override the branch check (e.g. `"master"`).                    |
| `skip_shellcheck_paths`  | string[]         | no       | Glob patterns for shellcheck exclusion.                         |
| `skip_version_alignment` | boolean          | no       | Skip B4 version alignment.                                      |
| `skip_releases`          | boolean          | no       | Skip B5 tag/release check.                                      |
| `version_files`          | object[]         | no       | Custom version sources. Each entry has `path` and `extract`.    |
| `consistency_check`      | string           | no       | Override the B3 consistency check command.                      |
| `format_check`           | string           | no       | Override the B6 format check command.                           |
| `format_fix`             | string           | no       | Override the B6 format fix command.                             |
| `sync_target`            | object           | no       | Declare a sync target explicitly. See below.                    |

### `sync_target` fields

| Field         | Type   | Required | Description                                                              |
| :------------ | :----- | :------- | :----------------------------------------------------------------------- |
| `type`        | string | yes      | One of: `hermes-skill`, `directory-mirror`, `hq-directory`, `build-package` |
| `name`        | string | yes      | Target name (skill name, directory name, etc.).                          |
| `install_cmd` | string | no       | Explicit install/sync command.                                           |
| `post_verify` | string | no       | Command to run for post-sync verification.                               |

---

## Behaviour

- If `.repo-health.json` is absent → all heuristics used.
- If present with partial data → missing fields fall back to heuristics.
- A project should only add this file when heuristics give wrong results or when explicit control is needed.

## Design principle

`.repo-health.json` is optional by design. The skill's value is in
working without it. Adding it should be driven by observed heuristic
failures, not by speculative configuration. See AP3 (Speculative Checks)
and AP8 (Templates Before Need) in SKILL.md.
