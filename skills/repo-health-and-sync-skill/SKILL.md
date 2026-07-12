---
name: repo-health-scan
description: >-
  Methodology for evaluating any git repository's health at runtime.
  The agent discovers the repo's shape, infers what invariants matter,
  and checks them using general-purpose tools already on PATH.
  No hardcoded checklists, no reference files, no shipped scripts.
  The methodology is the only artifact.
license: MIT
compatibility: all
metadata:
  author: CodeSigils
  version: "0.2.0"
  purpose: project-governance
  tags:
    - git-hygiene
    - methodology
    - runtime-discovery
    - health-audit
    - cross-project
---

# Repo Health Scan

A three-step methodology for evaluating any git repository's health.
The agent discovers, prioritises, and verifies — in that order.

Unlike a checklist, this methodology does not prescribe what to check.
It teaches the agent how to decide. Every repo is different. The right
checks for a 200K-line monorepo with 5 package managers are not the
right checks for a 12-line shell script. The agent decides.

---

## Step 1: Discover the repo's shape

Run these probes before forming any judgment about health. Do not guess
or infer from the repo name. Inspect the filesystem.

```bash
# What languages and tools does this project actually use?
ls *.json *.toml *.yaml *.yml *.cfg 2>/dev/null
ls *file 2>/dev/null
ls Dockerfile Containerfile 2>/dev/null

# What's the commit culture like?
git log --oneline -20
git log --format="%B" -5 | head -30

# What automation exists?
find .github/workflows -name '*.yml' 2>/dev/null | head -5
find . -maxdepth 1 -name '*.sh' 2>/dev/null
find scripts/ -name '*.py' -o -name '*.sh' 2>/dev/null | head -10

# What's the dependency surface?
find . -maxdepth 2 -name 'requirements*.txt' -o -name 'Cargo.toml' \
  -o -name 'go.mod' -o -name 'package.json' 2>/dev/null | head -10

# Is there a pre-existing health convention?
cat .repo-health.json 2>/dev/null || echo "no .repo-health.json"
```

From this output, form a concise repo profile — three lines max:

```
lang: Python + shell   deps: pip   CI: GitHub Actions
commits: conventional  tags: 12   maturity: active
```

This profile is the only thing between Step 1 and Step 2. If you cannot
write it, you did not run enough probes.

---

## Step 2: Infer what invariants matter

Given the repo profile, ask: what invariants would break if they drifted?

For each dimension below, check whether the repo profile makes the
invariant relevant. Skip dimensions that don't apply — do not produce
a PASS/FAIL for things the repo does not need.

| Dimension | Ask | Relevant when |
|-----------|-----|---------------|
| **History hygiene** | Is the working tree clean? Are there unpushed commits? | Always — cheap, universal |
| **Shell correctness** | Do .sh files pass shellcheck with no SC-level issues? | Any .sh files exist |
| **Version alignment** | Do version fields across manifests agree? | 2+ version sources |
| **Tag/release integrity** | Do git tags and GitHub releases overlap? | Any tags exist |
| **Commit quality** | Are messages structured? Are bodies informative? | Commits on this branch |
| **CI efficiency** | Is CI scoped to what changed? | CI config exists |
| **Cross-platform** | Do scripts use portable constructs? | .sh files + any macOS/BSD users |
| **Attribution drift** | Are unauthorized `Co-authored-by:` trailers present? | Commits since last release tag (or all commits if no tags) |
| **File coverage** | Does .gitignore cover agent/OS/build artifacts? | .gitignore exists |
| **External reference health** | Do all `https://` refs in docs/config resolve? | `REPO_HEALTH_VERIFY_REFS=1` env var (opt-in) |

For each relevant dimension, run exactly ONE command to check it:

```bash
# History hygiene
git status --porcelain && echo "clean" || echo "dirty"
git log origin/main..HEAD --oneline | wc -l

# Shell correctness
find . -name '*.sh' -not -path '*/node_modules/*' -not -path '*/.git/*' \
  -exec shellcheck {} \; 2>&1 | grep -c 'SC[0-9]*:' || true

# Version alignment
python3 -c "
import json, sys
versions = {}
for path in ['package.json', 'pyproject.toml', 'Cargo.toml']:
    try:
        with open(path) as f:
            data = json.load(f) if path.endswith('.json') else {}
        v = data.get('version', data.get('package', {}).get('version'))
        if v: versions[path] = v
    except: pass
if len(set(versions.values())) <= 1:
    print('PASS: versions aligned')
else:
    print(f'DRIFT: {versions}')
"

# Tag/release integrity
git tag --list 'v*' --sort=-version:refname | head -5
gh release list --limit 5 2>/dev/null || echo "gh not available"

# Commit quality (same as Step 1 — already observed)
# Just reach a judgment from what you already read

# CI efficiency
grep -c 'paths:' .github/workflows/*.yml 2>/dev/null && echo "scoped" \
  || echo "unscoped"

# Cross-platform shell
grep -n 'which\|grep -P\|sed -i[^.]' scripts/*.sh 2>/dev/null \
  | head -10 || echo "no patterns found"

# Attribution drift
last_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")
if [ -n "$last_tag" ]; then
  range="$last_tag..HEAD"
else
  range="HEAD"
fi
git log --format="%B" "$range" 2>/dev/null \
  | grep -c 'Co-authored-by:' || echo "0"

# .gitignore coverage
for pat in '.DS_Store' 'node_modules/' '__pycache__/' '.vscode/'; do
  grep -q "$pat" .gitignore 2>/dev/null || echo "MISSING: $pat"
done
```

Run only the commands for dimensions you deemed relevant. Skip the rest.
Do not emit PASS/WARNING/BLOCKING for skipped dimensions — they do not
apply to this repo.

---

## Step 3: Report findings with judgment, not labels

For each active dimension, report what you found. Do not use a
pre-defined severity scale. Use language that reflects actual harm:

```text
SHELL CORRECTNESS — 3 scripts, 6 SC warnings
  shellcheck reports SC2086 (unquoted var) in scripts/deploy.sh:17
  This causes silent failure when a path contains spaces.
  Remediation: wrap "$var" consistently. 5-minute fix.

COMMIT QUALITY — 10 conventional, 3 unstructured
  The unstructured commits are on a WIP branch (fix/parser-edge-case).
  The main branch is clean. No action needed.

VERSION ALIGNMENT — DRIFT
  package.json says 1.3.0, pyproject.toml says 1.2.0
  One of them is wrong. Cross-reference the latest tag.
```

If all active dimensions are healthy, report that in one line:

```text
PASS — 4 dimensions checked, all healthy.
```

If there is a blocking issue (dirty tree, shell script that literally
cannot run, version drift that would break a publish), say so explicitly
and stop. Do not continue checking other dimensions — fix the block first.

| **Structured output** | Emit JSONL for automation | `REPO_HEALTH_OUTPUT=jsonl` env var (opt-in) |

Example JSONL output:
```jsonl
{"dimension":"version_alignment","finding":"pyproject=1.2.0 Cargo=1.1.0","harm":"stale release","remediation":"sync to 1.2.0","confidence":0.95}
{"dimension":"external_reference_health","finding":"https://example.com/docs 404","harm":"dead link in README","remediation":"update URL","confidence":1.0}
```

---

## Optional: Pre-flight contract

Some repos carry a `.repo-health.json` at the root. When present, it
overrides the heuristic discovery in Step 2:

```json
{
  "skip": ["shell-correctness"],
  "require": ["custom-consistency-check"],
  "version_sources": ["pyproject.toml"],
  "commit_format": {"type": "conventional", "required_fields": ["what", "why"]}
}
```

Read it if it exists. Merge its settings into your dimension list.
If it declares a custom consistency check (`"require": [...]`), that
check replaces the default probe for that dimension.

---

## What this skill does not do

- It does not contain a checklist. Every repo is different.
- It does not ship scripts. The agent uses `git`, `shellcheck`,
  `python3`, `gh`, and whatever else is on PATH.
- It does not maintain reference files. Runtime discovery replaces
  lookup tables.
- It does not prescribe severity. The agent judges actual harm.
- It does not gate Phase C. Reverse sync is a separate concern from
  health scanning. If the repo needs a sync step, the agent designs
  it from the repo's sync targets, not from a pre-written procedure.

---

## Design principles (read before Step 1)

**The repo tells you what it needs.** Do not bring expectations. A
10-year-old project with 10K commits and no tags is valid if that's
how they work. Judge drift from local invariants, not from a universal
standard.

**Every invariant traces to a concrete failure.** If you cannot think
of a specific problem that would occur when this invariant breaks, the
check is speculative. Skip it.

**Run once, observe broadly.** One `ls`, one `find`, one `git log`
should give you the repo's shape. Do not chain five commands to
confirm what the first two already showed.

**Write the profile before the checks.** If you don't know the repo's
languages, tools, commit culture, and CI system, you cannot meaningfully
assess its health. Step 1 is not optional.

**The right number of checks is the one the repo needs, not the
one the skill defines.**

---

## Attribution drift dimension clarification

The **Attribution drift** check scans `origin/main..HEAD` — this covers
commits on the current branch that are not yet in `origin/main`. On a
fresh clone with no local commits, this range is empty and the check
correctly reports 0 trailers found. 

If you need to scan all commits in the repo (including history), adjust
the range to `HEAD` or use `git log --all`. The default range is
designed for pre-push/pre-merge validation where only new commits
matter.