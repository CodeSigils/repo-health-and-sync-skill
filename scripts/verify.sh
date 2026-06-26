#!/usr/bin/env bash
# verify.sh — Consistency check for the repo-health-and-sync-skill repo
#
# Exercises the verification checklist from AGENTS.md. Exit 0 if everything
# passes, non-zero with details on first failure. Portable: no GNU-only flags.
set -euo pipefail

PASS=0
FAIL=0

check() {
    local label="$1"; shift
    local out rc
    out=$("$@" 2>&1) && rc=0 || rc=$?
    if [ "$rc" -eq 0 ]; then
        echo "  PASS  $label"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  $label"
        echo "    command: $*"
        if [ -n "$out" ]; then
            echo "    output (first 5 lines):"
            echo "$out" | head -5 | sed 's/^/      /'
        fi
        FAIL=$((FAIL + 1))
    fi
}

echo "=== verify.sh: self-consistency check ==="
echo ""

check "Tree is clean" git status --porcelain

check "Self-test: co-author checker" \
    python3 scripts/check-commit-trailers.py --self-test

check "Self-test: doc audit" \
    python3 scripts/doc-audit.py --self-test

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

# --- README documentation audit (manifest-driven) ---
echo ""
echo "=== Documentation audit === "
echo ""
python3 scripts/doc-audit.py
doc_exit=$?
if [ "$doc_exit" -eq 0 ]; then
    PASS=$((PASS + 1))
else
    # doc-audit.py already printed individual failures; count as one block failure
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
# Extract version from YAML frontmatter between --- markers.
# Uses Python (stdlib, no yaml dependency) to handle single/double quotes,
# optional leading whitespace, and nested metadata.version field.
skill_ver=$(python3 -c "
import re
with open('SKILL.md') as f:
    content = f.read()
parts = content.split('---', 2)
if len(parts) < 3:
    exit()
fm = parts[1]
# Try metadata.version first, then top-level version
for pat in [r'^\\s+version:\\s*[\"\\'](.+?)[\"\\']',
            r'^version:\\s*[\"\\'](.+?)[\"\\']']:
    m = re.search(pat, fm, re.MULTILINE)
    if m:
        print(m.group(1))
        break
" 2>/dev/null || true)
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
        echo "  FAIL  No tags found — SKILL.md has version $skill_ver but no v* tag"
        FAIL=$((FAIL + 1))
    fi
else
    echo "  INFO  No version found in SKILL.md frontmatter"
fi

echo ""
echo "--- Summary: $PASS pass, $FAIL fail ---"
exit "$FAIL"
