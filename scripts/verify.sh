#!/usr/bin/env bash
# verify.sh — Consistency check for the repo-health-and-sync-skill repo
#
# Exercises the verification checklist from AGENTS.md. Exit 0 if everything
# passes, non-zero with details on first failure. Portable: no GNU-only flags.
set -euo pipefail

PASS=0
FAIL=0

check() {
    local label="$1"
    shift
    if "$@" >/dev/null 2>&1; then
        echo "  PASS  $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  $label"
        FAIL=$((FAIL + 1))
    fi
}

echo "=== verify.sh: self-consistency check ==="
echo ""

check "Tree is clean" git status --porcelain

check "Self-test: co-author checker" \
    python3 scripts/check-commit-trailers.py --self-test

# Cross-refs: every references/*.md linked from SKILL.md must exist
cross_miss=0
while IFS= read -r ref; do
    [ -z "$ref" ] && continue
    if [ ! -f "$ref" ]; then
        echo "  REF_MISS  $ref"
        cross_miss=$((cross_miss + 1))
    fi
done < <(grep -oE 'references/[A-Za-z0-9_.-]+\.md' SKILL.md | sort -u)
if [ "$cross_miss" -eq 0 ]; then
    echo "  PASS  SKILL.md cross-refs resolve"
    PASS=$((PASS + 1))
else
    echo "  FAIL  $cross_miss reference(s) missing"
    FAIL=$((FAIL + cross_miss))
fi

# No stale refs to deleted doc files
stale=0
for old in PLAN PROPOSALS REPORT USER-SUGGESTIONS; do
    if grep -rn --include='*.md' "${old}\.md" . 2>/dev/null \
        | grep -v '.git/' \
        | grep -v 'docs/decisions.md' \
        | grep -v 'docs/research.md' \
        | grep -q .; then
        echo "  STALE  reference to ${old}.md found"
        stale=$((stale + 1))
    fi
done
if [ "$stale" -eq 0 ]; then
    echo "  PASS  No stale refs to deleted docs"
    PASS=$((PASS + 1))
else
    echo "  FAIL  $stale stale reference(s)"
    FAIL=$((FAIL + stale))
fi

# SKILL.md under 600 lines
skill_len=$(wc -l < SKILL.md)
if [ "$skill_len" -le 600 ]; then
    echo "  PASS  SKILL.md $skill_len lines (≤600)"
    PASS=$((PASS + 1))
else
    echo "  FAIL  SKILL.md $skill_len lines exceeds 600"
    FAIL=$((FAIL + 1))
fi

# CHANGELOG has an Unreleased section
if grep -q '## Unreleased' CHANGELOG.md; then
    echo "  PASS  CHANGELOG.md has ## Unreleased"
    PASS=$((PASS + 1))
else
    echo "  FAIL  CHANGELOG.md missing ## Unreleased"
    FAIL=$((FAIL + 1))
fi

# Shellcheck: run on any .sh files found (excluding .git)
sh_count=$(find . -name '*.sh' -not -path './.git/*' | wc -l)
if [ "$sh_count" -gt 0 ]; then
    err=0
    while IFS= read -r -d '' f; do
        if ! shellcheck "$f" >/dev/null 2>&1; then
            echo "  SC_FAIL $f"
            err=$((err + 1))
        fi
    done < <(find . -name '*.sh' -not -path './.git/*' -print0)
    if [ "$err" -eq 0 ]; then
        echo "  PASS  shellcheck: $sh_count file(s) clean"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  shellcheck: $err file(s) with issues"
        FAIL=$((FAIL + 1))
    fi
else
    echo "  PASS  shellcheck: no .sh files to check"
    PASS=$((PASS + 1))
fi

# Version alignment (this repo): SKILL.md frontmatter is the single source
skill_ver=$(grep -E '^\s+version:' SKILL.md | sed 's/.*"\(.*\)".*/\1/' | tr -d '"')
if [ -n "$skill_ver" ]; then
    echo "  INFO  SKILL.md version: $skill_ver"
    # If a tag exists, ensure it matches
    latest_tag=$(git tag -l 'v*' --sort=-version:refname 2>/dev/null | head -1 || true)
    if [ -n "$latest_tag" ]; then
        tag_ver="${latest_tag#v}"
        if [ "$skill_ver" = "$tag_ver" ]; then
            echo "  PASS  Version matches latest tag ($latest_tag)"
            PASS=$((PASS + 1))
        else
            echo "  FAIL  SKILL.md version $skill_ver != tag $latest_tag"
            FAIL=$((FAIL + 1))
        fi
    else
        echo "  PASS  No tags yet — version $skill_ver is plausible"
        PASS=$((PASS + 1))
    fi
else
    echo "  INFO  No version found in SKILL.md frontmatter"
fi

echo ""
echo "--- Summary: $PASS pass, $FAIL fail ---"
exit "$FAIL"
