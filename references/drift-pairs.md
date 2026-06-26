---
title: Drift Pairs — Cross-commit Detection Patterns
description: Reusable diff-based patterns for detecting drift between file change sets and expected side-effects (CHANGELOG updates, version bumps, script consistency).
status: reference
---

# Drift Pairs — Cross-commit Detection Patterns

These patterns detect when a change in one part of the repo **should have**
produced a corresponding change in another, but didn't. They're the core of
B7 (commit audit) and reusable by B11 (co-author guard).

---

## 1. Cross-commit drift (B7b)

Detect when runtime source files changed but CHANGELOG.md did not.

```bash
baseline="${1:-origin/main}"
if git diff --name-only "$baseline" HEAD | grep -qE '^(skills/|src/|lib/)'; then
  if ! git diff --name-only "$baseline" HEAD | grep -q 'CHANGELOG.md'; then
    echo "BLOCKING: runtime files changed but CHANGELOG.md did not"
    echo "  Changed runtime files:"
    git diff --name-only "$baseline" HEAD | grep -E '^(skills/|src/|lib/)'
  fi
fi
```

**Configurable runtime paths:** The regex patterns (`skills/|src/|lib/`)
should be overridable via `.repo-health.json` → `drift_paths`. Default
heuristic: look for a `src/`, `lib/`, `skills/`, or `app/` directory at
repo root.

---

## 2. CHANGELOG completeness (B7c)

Verify that `## Unreleased` exists when the repo has had commits since the
last release tag.

```bash
latest_tag=$(git tag -l 'v*' --sort=-version:refname | head -1)
if [ -n "$latest_tag" ]; then
  # Commits since last tag?
  count=$(git rev-list "$latest_tag..HEAD" --count 2>/dev/null || echo 0)
  if [ "$count" -gt 0 ] && [ -f CHANGELOG.md ]; then
    if ! grep -q '## Unreleased' CHANGELOG.md; then
      echo "WARNING: $count commits since $latest_tag but no ## Unreleased in CHANGELOG.md"
    fi
  fi
else
  # No tags at all — check if there's any CHANGELOG
  if [ -f CHANGELOG.md ]; then
    if ! grep -q '## Unreleased' CHANGELOG.md; then
      echo "INFO: no release tags found; CHANGELOG.md exists but has no ## Unreleased section"
    fi
  fi
fi
```

---

## 3. Version-bump awareness (B7d)

Advisory: detect when source files changed but version field didn't.

```bash
baseline="${1:-origin/main}"
src_changed=$(git diff --name-only "$baseline" HEAD | grep -cE '^(src/|lib/|skills/)' || true)
if [ "$src_changed" -gt 0 ]; then
  version_changed=$(git diff "$baseline" HEAD -- package.json 2>/dev/null | grep -c '"version"' || true)
  if [ "$version_changed" -eq 0 ]; then
    echo "ADVISORY: $src_changed source file(s) changed but version unchanged"
    echo "  This may be expected for non-release work. Review before releasing."
  fi
fi
```

---

## 4. Script-awareness chain (general purpose)

Detect when a script is added or modified but the project's script-inventory
file (`.scripts.yml`, `Makefile` script listing, `package.json` scripts)
wasn't updated.

```bash
baseline="${1:-origin/main}"
new_scripts=$(git diff --name-only --diff-filter=A "$baseline" HEAD -- 'scripts/*.sh' 'scripts/*.py' 2>/dev/null || true)
if [ -n "$new_scripts" ]; then
  echo "INFO: new scripts detected — consider updating script inventory:"
  echo "$new_scripts"
fi
```

---

## 5. Bidirectional script inventory guard

If the project has a `.scripts.yml` or equivalent inventory, verify the
inventory and actual scripts are in sync (no scripts missing from inventory,
no inventory entries without a matching script).

```bash
if [ -f .scripts.yml ]; then
  inventory_scripts=$(awk '/^[[:space:]]+-[[:space:]]+/ {print $2}' .scripts.yml | sort -u)
  actual_scripts=$(find scripts/ -name '*.sh' -o -name '*.py' | sed 's|^scripts/||' | sort -u)
  for script in $inventory_scripts; do
    if ! echo "$actual_scripts" | grep -qF "$script"; then
      echo "WARNING: .scripts.yml lists '$script' but no matching file found"
    fi
  done
  for script in $actual_scripts; do
    if ! echo "$inventory_scripts" | grep -qF "$script"; then
      echo "INFO: script '$script' exists but not listed in .scripts.yml"
    fi
  done
fi
```

---

## Usage in `.repo-health.json`

```json
{
  "drift_paths": ["src/", "lib/", "skills/"],
  "skip_drift_check": ["docs/**", "tests/**"],
  "changelog_path": "CHANGELOG.md",
  "version_source": "package.json",
  "script_inventory": ".scripts.yml"
}
```

All drift pairs skip gracefully when their dependencies don't exist (no git
history, no CHANGELOG.md, no tags, no scripts). They produce INFO-level
output rather than BLOCKING when the preconditions aren't met.
