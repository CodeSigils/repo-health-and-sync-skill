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

# --- README documentation audit ---
echo ""
echo "=== Documentation audit === "
echo ""

# Doc A1: audience line
check "Doc: audience declared" grep -qE 'For Hermes|For skill maintainers' README.md

# Doc A2: self-guiding claim
check "Doc: self-guiding claim" grep -q 'self-guiding' README.md

# Doc A3: quickstart shell block
check "Doc: quickstart bash block" grep -q '```bash' README.md

# Doc A4: example output with B-check
check "Doc: example B-check output" grep -qE 'WARNING.*B[0-9]' README.md

# Doc A5: phase table covers all B1-B11 + C1-C4
phase_miss=0
for phase in B1 B2 B3 B4 B5 B6 B7 B8 B9 B10 B11 C1 C2 C3 C4; do
    if ! grep -q "\\*\\*${phase}\\*\\*" README.md; then
        echo "  PHASE_MISS  ${phase} not in README table"
        phase_miss=$((phase_miss + 1))
    fi
done
if [ "$phase_miss" -eq 0 ]; then
    echo "  PASS  Doc: phase table covers all B1-B11 + C1-C4"
    PASS=$((PASS + 1))
else
    echo "  FAIL  Doc: $phase_miss phase(s) missing from table"
    FAIL=$((FAIL + phase_miss))
fi

# Doc A6: cross-links
check "Doc: links to SKILL.md" grep -q 'SKILL.md' README.md
check "Doc: links to AGENTS.md" grep -q 'AGENTS.md' README.md
check "Doc: references/ link" grep -q 'references/' README.md

# Doc A7: See also section with ecosystem links
check "Doc: See also section" grep -q '## See also' README.md
check "Doc: ecosystem links" grep -qE 'hermes-agent\\.nousresearch\\.com|CodeSigils/hermes-skill-hq' README.md

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
