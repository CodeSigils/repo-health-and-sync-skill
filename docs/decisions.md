# Decisions — Repo Health Scan (v0.2.0)

**Purpose:** Records the design decisions that shaped the current methodology.
The skill itself is `skills/repo-health-and-sync-skill/SKILL.md`. Research
evidence that informed these decisions is in `docs/research.md`.

---

## Methodology over checklist

**Decision:** Ship a three-step methodology (discover repo shape → infer what
invariants matter → verify at runtime). Do not ship a hardcoded B-phase
checklist.

**Why:** Every repo is different. A 200K-line monorepo with 5 package managers
needs different checks than a 12-line shell script. The agent decides what to
check based on what the repo profile reveals, not from a lookup table. This
matches every major ecosystem repo (addyosmani/agent-skills, openai/skills,
wondelai/skills) — none ship checklists.

**Evidence:** Ecosystem survey of 6 top-starred skill collections; study note
on 6 cross-project patterns (§ Methodology over Collection).

---

## Runtime discovery over reference tables

**Decision:** Do not ship reference files. The agent discovers everything it
needs at runtime using tools on PATH.

**Why:** The v0.1.0 design shipped 14 reference files as lookup tables for
detection heuristics, portability patterns, and co-author guard procedures.
These went stale as tools, paths, and conventions evolved. Runtime discovery
uses the repo's actual filesystem state and the tools on PATH — it stays
current between maintainer edits. Self-proving drift: the agentskills.io
Showcase page cycled 404→200→404 within 4 hours. A reference file claiming
it was 404 would have been wrong within hours.

**Evidence:** Hub marketplace research (skill-discovery docs); skill-discovery
durable findings § drift self-proof.

---

## No shipped scripts

**Decision:** The agent uses general-purpose tools directly (`git`, `shellcheck`,
`python3`, `gh`). Do not ship wrapper scripts.

**Why:** The v0.1.0 design shipped a Python checker for commit trailers and
commit body format, plus a shared verification script. These duplicated
functionality already available via `git log`, `shellcheck`, and `python3 -c`.
Every ecosystem repo (addyosmani, openai/skills) ships zero scripts in their
skill payloads. The methodology's detection commands call tools on PATH
directly — no wrapper needed.

**Evidence:** Ecosystem structural survey (2026-07-12 study note). All 6
surveyed repos ship zero runtime scripts.

---

## Portability Is Verified Per Agent

**Decision:** Keep the skill methodology free of agent-specific commands and
config paths, but do not declare blanket compatibility in `SKILL.md`
frontmatter. Record installation and workflow evidence in per-agent
compatibility reports.

**Why:** The methodology uses only `ls`, `git`, `shellcheck`, `python3`, `gh`,
and standard shell commands, so terminal-capable coding agents are plausible
targets. Discovery, packaging, tool availability, and
instruction-following behavior vary by agent. Portability of the text does not
prove end-to-end support.

**Evidence:** The current Codex skill validator rejects `compatibility` as an
unsupported frontmatter key. Codex installation, implicit discovery, and
workflow behavior are tracked in `docs/compatibility-reports/codex.md`; other
agents remain unverified.

---

## CI API Authentication Is Separate From Commit Signing

**Decision:** Pass the job-scoped `${{ github.token }}` to GitHub CLI as
`GH_TOKEN` for release queries. Keep SSH commit and tag signing as a separate
provenance policy.

**Why:** `gh release list` calls the GitHub API and needs API authorization.
An SSH signature proves who signed a git object; it does not authorize API
requests. The workflow grants only `contents: read`, which is sufficient for
the read-only release query and keeps the token scoped to the job.

**Evidence:** GitHub's `GITHUB_TOKEN` authentication guide explicitly configures
GitHub CLI through `GH_TOKEN`. GitHub's signing documentation describes SSH as
a mechanism for cryptographically signing commits and tags. Sources accessed
2026-07-13:

- https://docs.github.com/en/actions/tutorials/authenticate-with-github_token
- https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits

---

## Single-file payload

**Decision:** `skills/repo-health-and-sync-skill/SKILL.md` is the only shipped
file. No references, no scripts, no config.

**Why:** A methodology that fits in one file is consumed immediately — the
agent reads it once and applies it. Multi-file payloads require the agent to
load references on demand, which adds context overhead and risks skipped steps.
The v0.1.0 payload had 15+ files; the current payload has 1. This matches
openai/skills (payload: SKILL.md + per-skill refs), addyosmani (zero refs),
and wondelai (flat SKILL.md per skill).

**Evidence:** Structural survey of 6 CodeSigils repos vs 6 ecosystem repos
(2026-07-12 study note). The ecosystem consistently ships minimal payloads.

---

## Proportionate checking

**Decision:** The agent checks only dimensions that the repo profile reveals
as relevant. No universal checklist, no mandatory PASS/FAIL for every step.

**Why:** Running a version-alignment check on a repo with no version sources
wastes agent context and produces false negatives. Running a CI-efficiency
check on a repo with no CI config is noise. The methodology's Step 1
(discover shape) gates Step 2 (infer invariants) — only dimensions that
the repo profile shows as active are checked.

**Evidence:** v0.1.0 B0 principle "detect, don't enforce." Observed during
dogfooding: the old B-phase would emit WARNINGs for dimensions that didn't
apply, consuming the agent's attention on noise.

---

## Judgment over labels

**Decision:** The agent reports findings with context and harm assessment,
not pre-defined PASS/WARNING/BLOCKING labels.

**Why:** The old architecture used a fixed severity scale (PASS / WARNING /
BLOCKING) that couldn't account for project context. A loose `.gitignore`
in a solo personal project is less harmful than the same issue in a
multi-contributor open-source repo. The methodology's Step 3 instructs
the agent to use language that reflects actual harm ("This causes silent
failure when...") rather than a severity class that repeats on every report.

**Evidence:** Observed during dogfooding: B-phase reports would flag the
same items as WARNING regardless of the repo's stage or audience, wasting
the maintainer's attention on items that didn't need action.

---

## What this file does NOT document

This file documents v0.2.0 decisions. The v0.1.0 design (B-phases, 14
reference files, 10 shipped scripts, payload sync process) is archived in
git history (commits 2691398, 78b31c7). See also the agent-concepts-study
note `2026-07-12-skill-repo-structural-diversity-and-optimal-patterns.md`
for the structural analysis that motivated the v0.2.0 design.
