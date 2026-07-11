# portability: allow-platform-ref
---
title: Sync Targets — Phase C Target Types and Verification
description: Runtime sync target detection, execution, and post-sync verification for Phase C.
status: reference
supersedes: inline sections in SKILL.md C1-C4
---

# Sync Targets — Phase C Target Types and Verification

This file contains the detailed sync target detection tables, execution
steps, and verification procedures. SKILL.md points here instead of
inlining the content.

---

## C1: Detect sync targets

**Discovery (runtime) — look for clues in the repo:**

- **Hermes skill**: any `SKILL.md` with `compatibility: hermes` in frontmatter. The skill name is in the `name:` frontmatter field.
- **HQ directory**: presence of `scripts/hq-sync.sh` or an `INDEX.md` at root.
- **Directory mirror**: presence of `scripts/sync-*.sh` or `scripts/*-sync-*.sh`.
- **Build package**: presence of `Containerfile`, `Dockerfile`, `build.sh`, or `release.sh`.

Priority order: `.repo-health.json` overrides all heuristics. If it declares
a `sync_target`, use that directly.

**Sync target types:**

| Type               | Meaning                                  | Heuristic clue                            |
| :----------------- | :--------------------------------------- | :---------------------------------------- |
| `hermes-skill`     | Installable Hermes Agent skill           | `SKILL.md` with `compatibility: hermes`   |
| `directory-mirror` | Config/tool directory with a sync script | `scripts/sync-*.sh`                       |
| `hq-directory`     | Hermes skill HQ clone                    | `INDEX.md` or `hq-sync.sh`                |
| `build-package`    | CI-built artifact (deb, binary, etc.)    | `build.sh`, `Containerfile`, `release.sh` |
| `none`             | No runtime target                        | None of the above                         |

---

## C2: Verify pre-sync state

Confirm Phase B completed without any BLOCKING items. If any BLOCKING issue
remains, report it and stop. Syncing a broken repo to a runtime target makes
the broken state durable.

---

## C3: Execute sync

Heuristic action per target type:

| Type               | Default action                                      | Preferred if sync script exists                  |
| :----------------- | :-------------------------------------------------- | :----------------------------------------------- |
| `hermes-skill`     | Prefer `skills.external_dirs`; otherwise install by hub id or HTTP(S) `SKILL.md` URL | Use the install/sync script in the repo if one exists |
| `directory-mirror` | Find and run `scripts/sync-*` or `scripts/*-sync-*` | Same default                                     |
| `hq-directory`     | `bash scripts/hq-sync.sh`                           | Uses it                                          |
| `build-package`    | Push a version tag and let CI handle the build      | Notify the user                                  |

For Hermes skills: current Hermes CLI installs by hub identifier or direct
HTTP(S) `SKILL.md` URL; do not assume a local filesystem path is accepted.
For local development, prefer adding the repo's `skills/` directory to
`skills.external_dirs` in `~/.hermes/config.yaml`. If a repo intentionally
uses a copied local install, locate the installed skill with `hermes skills
list` and verify source-vs-installed drift with `diff -rq` before and after
copying files.

---

## C4: Verify post-sync

**Runtime check** — confirm the installed CLI or tool actually works:

| Type             | Runtime verification                                           |
| :--------------- | :------------------------------------------------------------- |
| hermes-skill     | Run `node <installed-path>/src/index.js --help` or `--version` |
| directory-mirror | Re-run the project's precheck script (should now pass)         |
| hq-directory     | Confirm key files exist under `~/.hermes/hq/`                  |
| build-package    | Confirm CI pipeline triggered from tag push                    |

**Drift check** — compare the installed files against the repo source.
This verifies that what was synced actually matches what's in the repo.
Drift here means the sync was incomplete, stale, or corrupted.

The strategy depends on sync target type:

- **Hermes skill**: Determine the skill directory in the repo (the directory containing `SKILL.md`). Read the skill name from the `name:` frontmatter field, then locate the installed path with `hermes skills list`, configured `skills.external_dirs`, or a targeted search under `~/.hermes/skills/`. Do not assume `~/.hermes/skills/<name>/` is the active path. Walk all files under the repo's skill directory (excluding `node_modules/`) and check that each exists at the same relative path under the installed directory. Any file present in repo but missing from the installed copy is a drift warning.

- **Directory mirror**: If `.repo-health.json` declares a `sync_target.path`, run `diff -rq` between the repo root and that path, excluding `.git` and `node_modules`. Report any differing or missing files up to the first 20 lines of diff output.

- **HQ directory**: Check that key files (`INDEX.md`, `SKILL.md`) exist in both the repo and `~/.hermes/hq/` and have identical content. Any difference is a drift warning.

**Severity:**

- Runtime check fails (CLI exits non-zero, precheck fails, key file missing) → BLOCKING. Fix the sync immediately.
- Drift findings (files differ between repo and installed target) → WARNING. Some differences are expected — file permissions, `.gitignore`d artifacts, platform-specific paths. If every key file matches and the runtime check passes, the sync is clean.
