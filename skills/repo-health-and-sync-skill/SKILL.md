---
name: repo-health-scan
description: >-
  Methodology for evaluating any git repository's health at runtime.
  Guides the agent through discover, infer, and report: inspect the
  filesystem and git history, decide which invariants matter for this
  repository, then report findings with concrete harm and remediation.
  Use when asked to audit, review, assess, or check the health of a repo.
  Use before a release, archive, handoff, or onboarding session.
  Use when CI is failing and the cause is unclear.
  Not for single-file edits, narrow bug fixes, or feature implementation.
license: MIT
metadata:
  author: CodeSigils
  version: "0.3.0"
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

## When to Use

- Before cutting a release tag or publishing a GitHub Release
- When onboarding onto an unfamiliar repository
- When CI is failing and the cause is not obvious
- Before handing a project to a new maintainer
- When reviving a dormant repository
- After a large batch of AI-assisted commits

## When Not to Use

- For a task scoped to one file, one bug, or one feature
- For ordinary implementation work where the repository's overall health is not
  in question
- For repositories without git history, unless the user only wants a filesystem
  shape summary
- As an automatic fixer; this skill reports health findings and remediations,
  but does not mutate the repository

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
git status --short --branch
git tag --list 'v*' --sort=-version:refname | head -5
if git rev-parse --verify origin/main >/dev/null 2>&1; then
  git log origin/main..HEAD --oneline | head -20
fi

# What automation exists?
find .github/workflows -name '*.yml' 2>/dev/null | head -5
find . -maxdepth 1 -name '*.sh' 2>/dev/null
find scripts/ -name '*.py' -o -name '*.sh' 2>/dev/null | head -10

# What's the dependency surface?
find . -maxdepth 2 -name 'requirements*.txt' -o -name 'Cargo.toml' \
  -o -name 'go.mod' -o -name 'package.json' 2>/dev/null | head -10

# Is there a pre-existing health convention?
cat .repo-health.json 2>/dev/null || echo "no .repo-health.json"

# What does the project's .gitignore cover? (respect it when exploring)
cat .gitignore 2>/dev/null || echo "no .gitignore"

# Did the user or environment opt into a conditional check?
printf 'verify_refs=%s\n' "${REPO_HEALTH_VERIFY_REFS:-0}"
printf 'verify_releases=%s\n' "${REPO_HEALTH_VERIFY_RELEASES:-0}"
```

From this output, form and **emit** a concise structured repo profile before
checking any dimension. Separate observed facts from inferred labels. The
profile must be visible in the transcript as a `REPO PROFILE` block; do not keep
it only in internal reasoning or defer it to the final report:

```yaml
# REPO PROFILE
observed:
  vcs: git
  languages: Python + shell
  package_managers: pip
  ci: GitHub Actions
  script_surface: maintainer-only Python + shell
  version_sources: [SKILL.md, plugin.json, CITATION.cff, git tags]
  tags: present
  branch_commits_outside_base: none
  platform_requirements: none found
  verify_refs: false
  verify_releases: false
  shipped_payload: single SKILL.md

inferred:
  repo_type: skill-pack
  release_model: git tags
  risk_context: pre-release
```

Do not run a dimension-specific command before emitting this block. If you
cannot write it, run more discovery probes.

---

## Step 2: Infer what invariants matter

Given the emitted repo profile, ask: what invariants would break if they
drifted?

For each dimension below, check whether the repo profile makes the invariant
relevant. Before running any dimension command, emit a `DIMENSION PLAN` that:

- lists each active dimension with one or more exact profile paths in
  `activated_by`;
- lists each inactive dimension with a concrete `skip_reason`; and
- accounts for every candidate dimension in the table as active or skipped.

Use paths such as `observed.ci` or `inferred.release_model`. A request or
environment flag may also activate a dimension when recorded in the observed
profile. Do not activate a dimension from an assumption that is absent from the
profile.

```yaml
# DIMENSION PLAN
active:
  - name: shell_correctness
    activated_by: [observed.script_surface]
skipped:
  - name: cross_platform
    skip_reason: no platform or user requirement appears in the profile
```

Skip dimensions that do not apply; do not probe them or produce a PASS/FAIL for
them.

| Dimension | Ask | Relevant when |
|-----------|-----|---------------|
| **History hygiene** | Is the working tree clean? Are there unpushed commits? | Always — cheap, universal |
| **Shell correctness** | Do .sh files pass shellcheck with no SC-level issues? | Any .sh files exist |
| **Version alignment** | Do version fields across manifests agree? | 2+ version sources |
| **Tag/release integrity** | Do local version tags align, and, when opted in, do GitHub releases overlap? | Any tags exist |
| **Commit quality** | Are messages structured? Are bodies informative? | Commits on this branch |
| **CI efficiency** | Is CI scoped to what changed? | CI config exists |
| **Cross-platform** | Do scripts use portable constructs? | .sh files + any macOS/BSD users |
| **Attribution drift** | Are unauthorized `Co-authored-by:` trailers present? | Commits on the current branch that are not yet in `origin/main` |
| **File coverage** | Does .gitignore cover agent/OS/build artifacts? | .gitignore exists |
| **External reference health** | Do all `https://` refs in docs/config resolve? | `REPO_HEALTH_VERIFY_REFS=1` env var (opt-in) |

Only after emitting the dimension plan, run the smallest command or command
block that answers each active dimension. Do not run probes for skipped
dimensions:

```bash
# History hygiene
if [ -n "$(git status --porcelain)" ]; then
  echo "DIRTY: working tree has uncommitted changes"
else
  echo "CLEAN: working tree has no uncommitted changes"
fi
if git rev-parse --verify origin/main >/dev/null 2>&1; then
  git log origin/main..HEAD --oneline | wc -l
else
  echo "origin/main unavailable"
fi

# Shell correctness
find . -name '*.sh' -not -path '*/node_modules/*' -not -path '*/.git/*' \
  -exec shellcheck {} \; 2>&1 | grep -c 'SC[0-9]*:' || true

# Version alignment
python3 - <<'PY'
import json
import pathlib
import re

versions = {}

package_json = pathlib.Path("package.json")
if package_json.exists():
    try:
        data = json.loads(package_json.read_text())
        if isinstance(data.get("version"), str):
            versions["package.json"] = data["version"]
    except Exception as exc:
        versions["package.json"] = f"unreadable:{exc.__class__.__name__}"

def load_toml(path):
    try:
        import tomllib
    except ModuleNotFoundError:
        return None
    try:
        return tomllib.loads(path.read_text())
    except Exception:
        return None

pyproject = pathlib.Path("pyproject.toml")
if pyproject.exists():
    data = load_toml(pyproject)
    version = None
    if data:
        version = data.get("project", {}).get("version")
        version = version or data.get("tool", {}).get("poetry", {}).get("version")
    if not version:
        match = re.search(r'(?m)^version\s*=\s*["\']([^"\']+)["\']', pyproject.read_text())
        version = match.group(1) if match else None
    if version:
        versions["pyproject.toml"] = version

cargo = pathlib.Path("Cargo.toml")
if cargo.exists():
    data = load_toml(cargo)
    version = data.get("package", {}).get("version") if data else None
    if not version:
        text = cargo.read_text()
        package_block = re.search(r'(?ms)^\[package\](.*?)(?:^\[|\Z)', text)
        if package_block:
            match = re.search(r'(?m)^version\s*=\s*["\']([^"\']+)["\']', package_block.group(1))
            version = match.group(1) if match else None
    if version:
        versions["Cargo.toml"] = version

if len(versions) < 2:
    print(f"SKIP: fewer than two version sources found: {versions}")
elif len(set(versions.values())) == 1:
    print(f"PASS: versions aligned: {versions}")
else:
    print(f"DRIFT: {versions}")
PY

# Tag/release integrity
git tag --list 'v*' --sort=-version:refname | head -5
if [ "${REPO_HEALTH_VERIFY_RELEASES:-0}" = "1" ]; then
  gh release list --limit 5 2>/dev/null || echo "GitHub release query failed"
else
  echo "SKIP: GitHub release query requires REPO_HEALTH_VERIFY_RELEASES=1"
fi

# Commit quality (same as Step 1 — already observed)
# Just reach a judgment from what you already read

# CI efficiency
grep -c 'paths:' .github/workflows/*.yml 2>/dev/null && echo "scoped" \
  || echo "unscoped"

# Cross-platform shell
grep -n 'which\|grep -P\|sed -i[^.]' scripts/*.sh 2>/dev/null \
  | head -10 || echo "no patterns found"

# Attribution drift + secret scan
if git rev-parse --verify origin/main >/dev/null 2>&1; then
  range="origin/main..HEAD"
else
  range="HEAD"
fi
git log --format="%B" "$range" 2>/dev/null | tee /tmp/commit-bodies.txt | grep -c 'Co-authored-by:' || echo "0"
# Scan commit bodies for secret-like patterns
grep -E '(api[_-]?key|secret|token|password|passwd|credential)\s*[:=]\s*[A-Za-z0-9_\-]{20,}' /tmp/commit-bodies.txt >/dev/null && echo "SECRET PATTERN in commit message body" || echo "No secret patterns in commit messages"
rm -f /tmp/commit-bodies.txt

# .gitignore coverage
for pat in '.DS_Store' 'node_modules/' '__pycache__/' '.vscode/'; do
  grep -q "$pat" .gitignore 2>/dev/null || echo "MISSING: $pat"
done
# Secret-bearing patterns — use git check-ignore to handle negations correctly
for f in .env .env.local .env.production; do
  git check-ignore --no-index "$f" >/dev/null 2>&1 || echo "MISSING: $f (not ignored)"
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

If any finding contains sensitive values (API keys, tokens, passwords,
connection strings, private URLs), **redact the value before including it in
the report**. Flag the presence of a potential secret without exposing the
secret itself — e.g. "a hard-coded credential was found in config.py" not
"API_KEY = sk-1234...".

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

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "I know this repo well enough to skip Step 1." | Repository shape changes. Run the probes and write the profile before judging. |
| "CI is green, so the repo is healthy." | CI only checks what it is configured to check. Version drift, stale docs, and attribution drift can be invisible. |
| "This checklist does not mention it, so I should skip it." | There is no universal checklist. Step 2 asks what would break in this repo if it drifted. |
| "I should run every probe to be thorough." | Irrelevant probes create noise. Only check dimensions activated by the repo profile. |
| "This finding is minor, so I will omit it." | Report concrete harm and let the human decide whether to act. |

## Red Flags

- Reporting PASS for a dimension that was skipped
- Running a dimension probe before emitting the structured repo profile and
  dimension plan
- Activating a dimension without naming its profile evidence
- Treating missing tags, missing CI, or missing package manifests as defects
  without explaining concrete harm
- Applying a universal severity scale instead of judging local impact
- Producing findings for tooling that is maintainer-only, not shipped runtime
  payload
- Emitting JSONL when `REPO_HEALTH_OUTPUT=jsonl` was not requested
- Including credential material, tokens, or secrets in findings without
  redaction — flag existence, not values

## Verification

After completing the scan:

- [ ] A concise structured repo profile was written before dimension checks
- [ ] The profile separates observed facts from inferred labels
- [ ] A dimension plan accounts for every candidate before probes run
- [ ] Every active dimension cites profile evidence
- [ ] Only dimensions relevant to that profile were checked
- [ ] No skipped dimension was reported as PASS
- [ ] Every finding describes concrete harm, not abstract nonconformance
- [ ] Blocking findings are named explicitly and placed first
- [ ] Maintainer-only scripts are not described as shipped runtime payload
- [ ] JSONL output is emitted only when `REPO_HEALTH_OUTPUT=jsonl` is set
- [ ] Credentials, tokens, or secrets are redacted or reported by existence
  only, not included as raw values in findings

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
observed languages, tools, CI system, shipped payload, script surface, and
inferred repo type, you cannot meaningfully assess its health. Step 1 is
not optional.

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
