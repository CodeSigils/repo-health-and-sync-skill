---
title: Co-Author Guard — B11 Reference
description: Four-layer enforcement pattern for preventing unauthorized attribution trailers in commits.
status: reference
---

# Co-Author Guard — B11 Reference

This file documents the four-layer enforcement model for preventing
unauthorized attribution trailers (`Co-authored-by:`, `Signed-off-by:`,
`Helped-by:`, `Reviewed-by:`) in commit messages. Agents should apply
B11a-c during project setup and B11d for CI enforcement.

---

## The problem

Agents or humans may inadvertently include attribution trailers in commit
messages. Once pushed, these become part of the permanent git history.
Trailers can imply credit, responsibility, or review that was not actually
given. Prevention is better than history rewrite.

---

## Four-layer model

| Layer | What | Where | When applied |
| :---- | :--- | :---- | :----------- |
| B11a  | Agent instruction (MUST NOT rule) | AGENTS.md / CLAUDE.md / .cursorrules | At project inception or agent session start |
| B11b  | Policy documentation | CONTRIBUTING.md | Onboarding / PR submission |
| B11c  | Technical checker (commit-msg hook) | `.git/hooks/commit-msg` + `scripts/check-commit-trailers.py` | Every local commit |
| B11d  | CI enforcement | GitHub Actions / GitLab CI / pre-PUSH hook | Every push / PR |

---

## B11a: Agent instruction layer

Add to the project's agent instruction file (AGENTS.md / CLAUDE.md):

> **MUST NOT include attribution trailers in commit messages.**
> Do not add `Co-authored-by:`, `Signed-off-by:`, `Helped-by:`,
> `Reviewed-by:`, or any `*-by:` trailers. Use `ALLOW_ATTRIBUTION_TRAILERS=1`
> environment variable to bypass the checker when a genuine cross-user commit
> is required.

---

## B11b: Policy layer

Add a section to CONTRIBUTING.md (or create one if it doesn't exist):

> ### Commit trailers
>
> This project blocks unauthorized attribution trailers (`Co-authored-by:`,
> `Signed-off-by:`, `*-by:`) in commit messages. These trailers imply credit
> or review that may not have been given. If you have a genuine need for
> cross-user attribution (pair programming, mailing-list patch), set
> `ALLOW_ATTRIBUTION_TRAILERS=1` in your environment and document why in the
> commit body.

---

## B11c: Technical layer (commit-msg hook)

**Shared checker:** `scripts/check-commit-trailers.py` — single source of
truth used by both local hooks and CI. See that file for the full
implementation.

Install the hook:

```bash
cat > .git/hooks/commit-msg << 'HOOK'
#!/usr/bin/env bash
set -euo pipefail
exec python3 "$(git rev-parse --show-toplevel)/scripts/check-commit-trailers.py" "$1"
HOOK
chmod +x .git/hooks/commit-msg
```

The hook reads the commit message file, runs the checker, and blocks the
commit if unauthorized trailers are found. Bypass via:
`ALLOW_ATTRIBUTION_TRAILERS=1 git commit -m "..."`.

---

## B11d: CI enforcement

For GitHub Actions — add to `.github/workflows/ci.yml`:

```yaml
- name: Check commit trailers
  run: python3 scripts/check-commit-trailers.py --range origin/main..HEAD
```

For GitLab CI — add to `.gitlab-ci.yml`:

```yaml
check-trailers:
  script:
    - python3 scripts/check-commit-trailers.py --range origin/main..HEAD
```

The `--range` mode inspects every commit in the range for trailers.
It reuses the same `find_violations()` logic as the local hook.

---

## Bypass mechanism

Set `ALLOW_ATTRIBUTION_TRAILERS=1` in the environment to disable all
trailer checking. This applies to both the local hook and CI:

```bash
# Local commit
ALLOW_ATTRIBUTION_TRAILERS=1 git commit -m "..."

# CI (via repository secret or CI variable)
# Set ALLOW_ATTRIBUTION_TRAILERS=1 in CI environment
```

---

## Self-test mode

The checker includes a `--self-test` mode that verifies the detection logic
is working correctly. Add this to CI as a regression guard:

```bash
python3 scripts/check-commit-trailers.py --self-test
```

Expected output on success:

```
--- Self-test: all 10 pass ---
```

---

## Counter-indications

1. **Pair-programming teams.** If every commit genuinely involves co-authors,
   the guard creates friction. In that case, set `ALLOW_ATTRIBUTION_TRAILERS=1`
   for the repo's CI and skip the hook installation. Document the decision in
   `.repo-health.json`.

2. **Mailing-list workflows.** Projects accepting patches via email
   (`Signed-off-by:`) or Gerrit (`Reviewed-by:`) need trailers. Skip B11
   entirely for those projects.

3. **Single-contributor repos.** One person working alone is unlikely to
   accidentally credit someone else. B11 is low-value here — install only
   if you observe the problem.

---

## `.repo-health.json` configuration

```json
{
  "skip_trailer_check": false,
  "allow_trailers": false,
  "trailer_check_mode": "hook-and-ci",
  "ci_baseline": "origin/main"
}
```

If `skip_trailer_check` is true (or if no `scripts/` directory exists), B11
is skipped entirely. If `allow_trailers` is true, the project has opted out
of trailer enforcement — documented in the config rather than silently
disabled.
