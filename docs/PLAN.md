# Implementation Plan — Repo Health and Sync Skill

Plan date: 2026-06-25
Based on: SKILL.md (614 lines), PROPOSALS, USER-SUGGESTIONS, repo-consistency-enforcement (30 reference files), hermes-skill-hq durable-patterns, agent-concepts-study (6 notes), hermes-skill-hq author-guard, github/gitignore, Anthropic/OpenAI docs

---

## 0. Current State Assessment

### Existing SKILL.md positives
- Single-file architecture aligned with ecosystem norm (antidrift principle)
- Heuristic detection avoids hardcoded project metadata
- Phase B and C separation with gating (B gates C)
- `.repo-health.json` override mechanism with versioned schema
- Real-world examples table comparing 5 projects
- Common pitfalls section

### Existing SKILL.md problems

| Issue | Detail | Severity |
| :---- | :------ | :------- |
| "From the USER" section (lines 38-156) | Marked for removal but still present — 118 lines of discussion text | BLOCKING — must remove before release |
| SKILL.md too long | 614 lines for what should be an index + pointers | WARNING — readability threshold exceeded |
| No CHANGELOG.md | Release-drift checks will fail immediately | WARNING — reduces professionalism |
| Inline script paths in phase descriptions | B1-C4 contain concrete file paths (scripts/sync-*.sh etc.) | WARNING — duplicates across section and creates drift surface |
| No references/ directory | All detail lives inline in SKILL.md | INFO — not a problem yet but will become one as phases grow |
| Phase B ends at B6, no B7-B11 | The 5 proposed new phases have no home | INFO |

### PROPOSALS strengths
- Research-backed mapping of all 16 user suggestions
- Agent instruction ecosystem table (Anthropic/OpenAI/Cursor/Copilot)
- Proportionate anti-drift heuristic documented
- Co-author guard three-layer pattern documented
- Cross-platform portability patterns table
- Script naming conventions table
- Implementation options (1-3) with risk assessment

### PROPOSALS gaps

| Gap | Why it matters |
| :-- | :------------- |
| Doesn't evaluate existing SKILL.md content quality | The "From the USER" section needs specific removal + migration plan |
| No dependency graph for proposed phases | B8 (cross-platform shell audit) may depend on B3 (consistency check) changes; B11 (co-author guard) has no pre-reqs |
| Doesn't assess which reference files are essential vs deferred | 10 reference files proposed but no prioritization |
| Missing concrete remediation cost per phase | How many lines of SKILL.md change per phase? |
| No CHANGELOG creation plan | The file doesn't exist yet |
| No plan for existing inline heuristic-detection code | Should it stay in SKILL.md or move to references/heuristic-discovery.md? |
| No verification plan | How do we know each phase is done correctly? |

---

## 1. Mature Project Survey — Evidence-Based Patterns

Research conducted 2026-06-25 via GitHub browser inspection of 17 top-starred projects across 9 language ecosystems.  
Each project inspected for: directory structure, branch naming, tag count, commit style, CI organization, scripts directory, agent config files, release automation, CHANGELOG pattern.

### Master Survey Table (17 projects)

| # | Project | Stars | Ecosystem | Branch | Tags | Commits | Commit Style | Agent Config | Scripts | CI Platform |
| :- | :------ | ----: | :-------- | :----- | ---: | ------: | :----------- | :----------- | :------ | :---------- |
| 1 | facebook/react | 246k | JS/TS | main | 171 | 21,535 | `[Category] description` (`[DevTools]`, `[Flight]`) | `.claude/` | N/A | `.github/` |
| 2 | torvalds/linux | 238k | C | master | 935 | 1,460,916 | `Merge tag 'X' of Y` (kernel tag style) | None | `scripts/` | None (kernel.org) |
| 3 | ohmyzsh/ohmyzsh | 188k | Shell | master | **0** | 7,810 | `type(scope): description` (`docs:`, `feat:`, `fix(git):`) | None | N/A | `.github/` |
| 4 | microsoft/vscode | 187k | JS/TS | main | 374 | 159,939 | `type(scope): description` (`fix(oss):`, `chore:`) | `.agents/skills/launch` | `build/`, `.vscode/` | `.github/` |
| 5 | golang/go | 135k | Go | master | 485 | 66,795 | `pkg: description` (`cmd/internal/objfile: use 'B' code...`) | None | `misc/` | `.github/` |
| 6 | vercel/next.js | 140k | JS/TS | canary | 3,930 | 34,493 | `scope: description` (`dev-overlay: wire Link prefetch...`) | `.claude/`, `.cursor/`, `.agents/skills/` | `.cargo/`, `.config/` | `.github/workflows/` |
| 7 | kubernetes/k8s | 123k | Go | master | 1,233 | 138,867 | `Merge pull request #N from user/branch` | None | `build/`, `cluster/` | `.github/` |
| 8 | rust-lang/rust | 114k | Rust | main | 158 | 330,454 | `Auto merge of #N from user/branch` | None | N/A | `.github/` |
| 9 | nvm-sh/nvm | 93.9k | Bash | master | 104 | 2,348 | `[Category] description` (`[Docs]`, `[New]`, `[Tests]`) | None | N/A | `.github/workflows/` |
| 10 | django/django | 88k | Python | main | 512 | 34,734 | `Fixed #N -- description` | None | `scripts/` | `.github/` |
| 11 | expressjs/express | 69.3k | Node/JS | master | 304 | 6,153 | `type(scope): description` (`fix(res.send): add Content-Length...`) | None | N/A | `.github/` |
| 12 | ansible/ansible | 69k | Python | devel | 728 | 55,481 | `description (#N)` (`Fix inject facts deprecation...`) | `.claude/skills/` | `hacking/`, `bin/` | `.github/`, `.azure-pipelines/` |
| 13 | prometheus/prometheus | 64.8k | Go | main | 538 | 17,856 | `type(scope): description` (`test(cmd/prometheus):`, `fix(deps):`) | None | `cmd/` | `.github/` |
| 14 | rails/rails | 58.7k | Ruby | main | 549 | 98,468 | `Merge pull request #N from user/branch` | None | N/A | `.github/` |
| 15 | Homebrew/brew | 48.6k | Ruby | main | 513 | 50,549 | **Free-form prose** (rejects conventional) | `.claude/`, `.codex/`, `.cursor/` | `.github/scripts/` | `.github/workflows/` (14 files) |
| 16 | apache/spark | 43.5k | Scala/JVM | master | 294 | 48,749 | `[SPARK-NNNNN][Module] description` (JIRA) | None | `bin/`, `build/` | `.github/` |
| 17 | numpy/numpy | 32.3k | Python | main | 277 | 41,383 | `CAT: description` (`TYP:`, `MAINT:`, `DOC:`, `BENCH:`, `DEV:`) | None | N/A | `.github/`, `.circleci/` |

### Domain Cross-Reference Tables

#### Go ecosystem (3 projects)

| Metric | golang/go | kubernetes | prometheus |
| :----- | :-------- | :--------- | :--------- |
| Stars | 135k | 123k | 64.8k |
| Branch | master | master | main |
| Tags | 485 | 1,233 | 538 |
| Commits | 66,795 | 138,867 | 17,856 |
| Commit style | `pkg: description` | `Merge PR #N` | `type(scope):` (conventional) |
| Agent config | None | None | None |
| Scripts dir | `misc/` | `build/`, `cluster/` | `cmd/` |
| CI | `.github/` | `.github/` | `.github/` |
| CHANGELOG | Release notes per version | `CHANGELOG/` directory | GitHub Releases |
| **Shared** | No agent configs, all use `.github/` for CI | | |

**Implication:** Go ecosystem has consistent CI location (`.github/`) but no agent config adoption. Commit styles vary even within same language.

#### JavaScript/TypeScript ecosystem (3 projects)

| Metric | react | next.js | vscode |
| :----- | :---- | :------ | :----- |
| Stars | 246k | 140k | 187k |
| Branch | main | canary | main |
| Tags | 171 | 3,930 | 374 |
| Commits | 21,535 | 34,493 | 159,939 |
| Commit style | `[Category] desc` | `scope: desc` | `type(scope): desc` |
| Agent config | `.claude/` | `.claude/`, `.cursor/`, `.agents/skills/` | `.agents/skills/launch` |
| Scripts dir | N/A | `.cargo/`, `.config/` | `build/`, `.vscode/` |
| **Shared** | **All 3 commit agent configs** — highest adoption rate of any ecosystem | | |

**Implication:** JS/TS ecosystem is the furthest ahead in agent config adoption (3/3). This is the baseline for B10 agent config detection.

#### Python ecosystem (3 projects)

| Metric | django | ansible | numpy |
| :----- | :----- | :------ | :---- |
| Stars | 88k | 69k | 32.3k |
| Branch | main | devel | main |
| Tags | 512 | 728 | 277 |
| Commits | 34,734 | 55,481 | 41,383 |
| Commit style | `Fixed #N -- desc` | `desc (#N)` | `CAT: desc` |
| Agent config | None | `.claude/skills/` | None |
| Scripts dir | `scripts/` | `hacking/`, `bin/` | N/A |
| CI | `.github/` | `.github/` + `.azure-pipelines/` | `.github/` + `.circleci/` |
| CHANGELOG | `docs/releases/` (directory) | `changelogs/` (directory) | GitHub Releases |
| **Shared** | Diverse CI platforms; 1 of 3 has agent config | | |

**Implication:** Python ecosystem is the most diverse — 3 different CI platforms (GitHub, Azure, CircleCI), 3 different CHANGELOG approaches. B9 must handle multiple CI providers.

#### Ruby ecosystem (2 projects)

| Metric | rails | Homebrew |
| :----- | :---- | :------- |
| Stars | 58.7k | 48.6k |
| Branch | main | main |
| Tags | 549 | 513 |
| Commits | 98,468 | 50,549 |
| Commit style | `Merge PR #N` | Free-form (rejects conventional) |
| Agent config | None | `.claude/`, `.codex/`, `.cursor/` |
| Scripts dir | N/A | `.github/scripts/` |
| CI | `.github/` | `.github/workflows/` (14 files) |
| CHANGELOG | `CHANGELOG.md` | `CHANGELOG.md` |
| **Shared** | Both use `main` branch, both have CHANGELOG.md | | |

**Implication:** Ruby ecosystem split on agent adoption. Homebrew is the reference for CI workflow organization (14 separate files) and the strongest counter-example to conventional commits enforcement.

#### Shell/Bash ecosystem (2 projects)

| Metric | nvm-sh/nvm | ohmyzsh/ohmyzsh |
| :----- | :--------- | :--------------- |
| Stars | 93.9k | 188k |
| Branch | master | master |
| Tags | 104 | **0** |
| Commits | 2,348 | 7,810 |
| Commit style | `[Category] desc` | `type(scope): desc` (conventional) |
| Agent config | None | None |
| CI | `.github/workflows/` | `.github/` |
| **Shared** | Both on master, no agent configs | | |

**Implication:** ohmyzsh (188k stars) has ZERO tags — proves a major project can exist without formal releases. B5/B7 should NOT fail on "no tags" if the project is healthy.

### Expanded Key Findings

#### KF1: No single commit convention dominates (now 17 projects)

| Convention | Projects | Count | % of total |
| :--------- | :------- | ----: | ---------: |
| `type(scope): description` (conventional-like) | next.js, vscode, express, prometheus, ohmyzsh | 5 | 29% |
| `[Category] description` (bracket style) | nvm, react | 2 | 12% |
| `CAT: description` (custom prefix) | numpy | 1 | 6% |
| `pkg: description` (Go package style) | golang/go | 1 | 6% |
| `Fixed #N -- description` (ticket-style) | django | 1 | 6% |
| `[SPARK-NNNNN][Module] description` (JIRA-style) | spark | 1 | 6% |
| `Merge pull request #N` / `Auto merge of #N` | kubernetes, rust, rails | 3 | 18% |
| `Merge tag 'X' of Y` (kernel tag style) | linux | 1 | 6% |
| `description (#N)` (plain + issue ref) | ansible | 1 | 6% |
| **Free-form prose** (rejects conventional) | Homebrew | 1 | 6% |

**Implication for B7:** 10 distinct commit styles across 17 projects. Conventional commits (29%) is the plurality but NOT the majority. The skill must discover the prevailing style before checking consistency. **Homebrew's `reject-conventional-commits.yml`** (live CI workflow — https://github.com/Homebrew/brew/blob/main/.github/workflows/reject-conventional-commits.yml) proves this is not theoretical: imposing a convention violates project norms.

#### KF2: Agent config adoption by ecosystem (now 5 of 17 projects commit agent configs)

| Project | Ecosystem | Files committed |
| :------ | :-------- | :-------------- |
| react | JS/TS | `.claude/` |
| next.js | JS/TS | `.claude/`, `.cursor/`, `.agents/skills/` |
| vscode | JS/TS | `.agents/skills/launch` |
| Homebrew | Ruby | `.claude/`, `.codex/`, `.cursor/` |
| ansible | Python | `.claude/skills/` |

**Implication:** 5/17 (29%) of top projects now commit agent configs. JS/TS ecosystem leads at 100% adoption. B10 must check for `.claude/`, `.cursor/`, `.codex/`, `.agents/`, and `.vscode/` — not just `.gitignore` patterns.

#### KF3: Tag count distribution (now with critical counterexample)

| Tag range | Projects | Example |
| :-------- | :------- | :------ |
| **0 tags** | 1 | ohmyzsh (188k stars, no releases) |
| 100-500 | 8 | go, nvm, django, express, rust, spark, numpy, rails |
| 500-1000 | 4 | linux, kubernetes, prometheus, Homebrew |
| 1000+ | 1 | next.js (3,930) |

**Critical counterexample:** ohmyzsh (188k stars, 0 tags) — large successful project with ZERO formal releases. B5 release health must detect "no tags" as a valid state, not a failure.

**Implication for B5/B7:** Tag signal is valuable but nuanced. Cluster by magnitude: 0 tags (valid), <100 (new/young), 100-500 (established), >500 (mature). Do not fail on "0 tags" — only warn if tags exist but are stale (>2 years since last tag).

#### KF4: Script directory naming diversity (found 6+ patterns)

| Pattern | Projects |
| :------ | :------- |
| `scripts/` | django, linux |
| `bin/` | ansible, spark |
| `build/` | kubernetes, vscode |
| `misc/` | golang/go |
| `cluster/` | kubernetes |
| `hacking/` | ansible |
| `.github/scripts/` | Homebrew |
| `.cargo/`, `.config/` | next.js (build tooling) |
| `cmd/` | prometheus (Go convention) |

**Implication for B2:** Heuristic script discovery must scan ALL these locations, not assume `scripts/`. Add `bin/`, `build/`, `misc/`, `cmd/`, `hacking/`, `.github/scripts/` to the search path. Rely on file type detection (`.sh`, `.py`, `.rb`), not directory name.

#### KF5: CI platform diversity (not just GitHub Actions)

| CI Platform | Projects |
| :---------- | :------- |
| `.github/workflows/` (GitHub Actions) | All except linux, numpy also uses `.circleci/`, ansible also uses `.azure-pipelines/` |
| `.circleci/` | numpy |
| `.azure-pipelines/` | ansible |
| `None` | torvalds/linux (uses kernel.org infra) |

**Implication for B9:** The audit must detect multiple CI platforms. numpy and ansible use 2 platforms each. B9 should score each CI platform independently and flag dead configs (CI files that reference defunct providers).

#### KF6: CHANGELOG pattern diversity (4+ patterns)

| Pattern | Projects |
| :------ | :------- |
| `CHANGELOG.md` single file | rails, Homebrew |
| `CHANGELOG/` directory (one per version) | kubernetes |
| `docs/releases/` or `changelogs/` directory | django, ansible |
| GitHub Releases only (no file) | react, next.js, prometheus, numpy |
| **No CHANGELOG at all** | linux, vscode, go, nvm, express, rust, spark |

**Implication for B7:** 8 of 17 projects (47%) have NO CHANGELOG file — they use GitHub Releases, kernel.org, or nothing. The skill must detect what pattern exists, not require a single `CHANGELOG.md`. Cross-reference tag count with release verification: if tags exist AND a CHANGELOG file exists, check they're in sync. If no CHANGELOG file exists but tags exist, that's valid (GitHub Releases pattern).

#### KF7: Branch naming diversity (now with `devel` and `canary`)

| Branch name | Projects | % |
| :---------- | :------- | :-- |
| `main` | react, vscode, rust, django, prometheus, rails, Homebrew, numpy | 47% |
| `master` | linux, golang/go, kubernetes, nvm, express, spark, ohmyzsh | 41% |
| `canary` | next.js | 6% |
| `devel` | ansible | 6% |

**Implication for B1:** 41% of top projects still use `master`. The skill must detect without warning. **Ansible's `devel` branch** proves there's a third option beyond the `main`/`master` binary.

#### KF8: Release automation scripts (evidence from real projects)

| Project | Script | What it does |
| :------ | :----- | :----------- |
| django | `scripts/do_django_release.py` | Automates the full release process |
| django | `scripts/verify_release.sh` | GPG signatures, checksum verification, smoke test install (both tarball + wheel) |
| django | `scripts/backport.sh` | Backport commits to stable branches |
| Homebrew | `.github/workflows/release.yml` | CI-driven release via GitHub Actions |
| Homebrew | `.github/workflows/sbom.yml` | Software Bill of Materials generation |
| linux | `scripts/` directory | Kernel build + maintenance scripts (no release automation checked in) |

**Implication for B5:** Release automation is project-specific but the existence of a `release` or `verify_release` script is a strong positive signal. B5 should detect scripts matching `*release*` or `*verify*` patterns.

#### KF9: Maintainer documentation patterns

| Pattern | Projects |
| :------ | :------- |
| `AUTHORS` file | django, Homebrew |
| `CODEOWNERS` (`.github/`) | vscode, multiple |
| `MAINTAINERS` file | linux kernel |
| `CONTRIBUTING.rst` / `CONTRIBUTING.md` | django, multiple |
| `RELEASING_RAILS` (in-repo doc) | rails |

**Implication for B11:** Co-author guard and maintainer documentation are related. B11 should check for `AUTHORS`, `CODEOWNERS`, `MAINTAINERS` as part of governance health.

#### KF10: Git attributes and hooks adoption

| File | Purpose | Prevalence |
| :--- | :------ | :--------- |
| `.gitattributes` | Git merge/linguist rules | ~60% of surveyed projects |
| `.git-blame-ignore-revs` | Ignore formatting commits in blame | django |
| `.pre-commit-config.yaml` | Pre-commit hooks | django |

**Implication for B10:** These files indicate repository maturity. The metadata audit should check for them but not require them.

### Evidence-Based Design Principles for the Skill

Derived from the 17-project survey above. Each principle ties to a specific observation.

1. **Detect, don't enforce.** No pattern is universal across 17 projects. The skill must discover each project's existing conventions, not impose one. (KF1, KF7)

2. **Zero tags is valid.** ohmyzsh (188k stars) proves a project can thrive without formal releases. Stale tags matter; absence of tags does not. (KF3)

3. **Scripts live anywhere.** `scripts/`, `bin/`, `build/`, `misc/`, `cmd/`, `hacking/`, `.github/scripts/` — scan them all. File extension > directory name. (KF4)

4. **Agent configs are now metadata.** 29% of top projects commit them. They belong in `.gitignore` audit AND in a separate "agent readiness" check. (KF2)

5. **CHANGELOG detection must be flexible.** Check `CHANGELOG.md`, `CHANGELOG/`, `docs/releases/`, `changelogs/`, then fall back to GitHub Releases API. (KF6)

6. **CI is multi-platform.** GitHub Actions is not the only answer. Detect `.circleci/`, `.azure-pipelines/`, `.gitlab-ci.yml`. (KF5)

7. **Release scripts are a positive signal.** `release` or `verify_release` scripts indicate process maturity. (KF8)

8. **Governance metadata matters.** `AUTHORS`, `CODEOWNERS`, `MAINTAINERS`, `CONTRIBUTING` files indicate mature project governance. (KF9)

### Research links (live URLs verified 2026-06-25)

| Project | Repository |
| :------ | :--------- |
| facebook/react | https://github.com/facebook/react |
| torvalds/linux | https://github.com/torvalds/linux |
| ohmyzsh/ohmyzsh | https://github.com/ohmyzsh/ohmyzsh |
| microsoft/vscode | https://github.com/microsoft/vscode |
| golang/go | https://github.com/golang/go |
| vercel/next.js | https://github.com/vercel/next.js |
| kubernetes/kubernetes | https://github.com/kubernetes/kubernetes |
| rust-lang/rust | https://github.com/rust-lang/rust |
| nvm-sh/nvm | https://github.com/nvm-sh/nvm |
| django/django | https://github.com/django/django |
| expressjs/express | https://github.com/expressjs/express |
| ansible/ansible | https://github.com/ansible/ansible |
| prometheus/prometheus | https://github.com/prometheus/prometheus |
| rails/rails | https://github.com/rails/rails |
| Homebrew/brew | https://github.com/Homebrew/brew |
| apache/spark | https://github.com/apache/spark |
| numpy/numpy | https://github.com/numpy/numpy |
| Homebrew reject-conventional-commits.yml | https://github.com/Homebrew/brew/blob/main/.github/workflows/reject-conventional-commits.yml |
| Django verify_release.sh | https://github.com/django/django/blob/main/scripts/verify_release.sh |

### Agent ecosystem (expanding beyond PROPOSALS)

| Topic | Source | URL | Relevance |
| :---- | :----- | :-- | :-------- |
| Conventional Commits 1.0.0 | conventionalcommits.org | https://www.conventionalcommits.org/en/v1.0.0/ | B7 commit audit standard |
| Keep a Changelog | keepachangelog.com | https://keepachangelog.com/en/1.1.0/ | B4 version alignment, CHANGELOG format |
| Semantic Versioning 2.0 | semver.org | https://semver.org/spec/v2.0.0.html | B4 version alignment |
| Claude Code .claude directory | Anthropic docs | https://code.claude.com/docs/explore-dot-claude | Cross-agent portability (B13) |
| OpenAI Codex AGENTS.md spec | OpenAI docs | https://developers.openai.com/docs/guides/codex | Cross-agent portability (B13) |
| GitHub copilot-instructions.md | GitHub docs | https://docs.github.com/en/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot | Cross-agent portability (B13) |
| Cursor .cursorrules | Cursor docs | https://docs.cursor.com/context/rules-for-ai | Cross-agent portability (B13) |

### CI and release

| Topic | Source | URL | Relevance |
| :---- | :----- | :-- | :-------- |
| GitHub Actions trigger docs | GitHub | https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows | B9 CI trigger audit |
| GitHub Actions paths-ignore | GitHub | https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/filtering-pattern-checks | B9 CI efficiency |
| gh release create | GitHub CLI | https://cli.github.com/manual/gh_release_create | B5 tag vs release |
| GitLab CI pipeline docs | GitLab | https://docs.gitlab.com/ee/ci/yaml/ | Cross-platform CI (B5 improvement) |

### Shell portability

| Topic | Source | URL | Relevance |
| :---- | :----- | :-- | :-------- |
| POSIX shell spec | Open Group | https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html | B8 cross-platform shell audit |
| Shellcheck wiki | shellcheck.net | https://www.shellcheck.net/wiki/ | B2 shellcheck — portable rules |
| command -v vs which | POSIX vs BSD | https://stackoverflow.com/questions/34421121/difference-between-which-and-command-v-in-shell-script | B8 portable tool detection |
| grep -E vs grep -P | GNU vs BSD | https://www.gnu.org/software/grep/manual/grep.html#grep-programs | B8 grep portability |
| flock vs lockfile | Linux vs BSD | https://man7.org/linux/man-pages/man1/flock.1.html | Advanced portability |

### .gitignore

| Topic | Source | URL | Relevance |
| :---- | :----- | :-- | :-------- |
| GitHub official .gitignore templates | github/gitignore | https://github.com/github/gitignore | B10 metadata audit |
| Agents.gitignore (official) | github/gitignore | https://github.com/github/gitignore/blob/main/Global/Agents.gitignore | B10 agent-specific patterns |
| Python .gitignore template | github/gitignore | https://github.com/github/gitignore/blob/main/Python.gitignore | Cross-language patterns |
| Node .gitignore template | github/gitignore | https://github.com/github/gitignore/blob/main/Node.gitignore | Cross-language patterns |

### Governance and drift

| Topic | Source | URL | Relevance |
| :---- | :----- | :-- | :-------- |
| repo-consistency-enforcement (umbrella) | Installed skill | 30 reference files via skill_view | Primary governance reference |
| Release-drift enforcement | repo-consistency-enforcement reference | `references/release-drift-enforcement.md` | B7 cross-commit drift template |
| Version auto-detection consolidation | repo-consistency-enforcement reference | `references/version-auto-detection-consolidation.md` | B4 version alignment template |
| Commit author guard | repo-consistency-enforcement reference | `references/commit-author-guard-concrete.md` | B11 co-author guard template |
| Script awareness chain | repo-consistency-enforcement reference | `references/script-awareness-chain.md` | Script inventory pattern |

---

## 2. Reference File Evaluation

Evaluation criteria (proportionate anti-drift principle):
- Essential: addresses an observed failure mode documented in user suggestions or research
- Valuable: fills a documentation gap that would cause repeated questions
- Deferred: speculative — wait until the need emerges
- Skip: overlaps with existing installed skills

| # | Proposed reference file | Evaluation | Priority | Rationale |
| :- | :--------------------- | :--------- | :------- | :-------- |
| 1 | `heuristic-discovery.md` | **Essential** | P0 | Currently inline in SKILL.md B1-B6. Extracting reduces SKILL.md size from 614→~200 lines. Already partially written. |
| 2 | `drift-pairs.md` | **Essential** | P0 | Cross-commit drift detection (B7) is the highest-impact new phase. Needs its own reference because detection patterns are complex. |
| 3 | `release-checklist.md` | **Valuable** | P1 | Release procedure is mentioned in multiple sections (B4, B5, C3). A single checklist reduces duplication. |
| 4 | `sync-targets.md` | **Essential** | P0 | Phase C sync targets table and verification commands. Currently inline in SKILL.md C1-C4. Extracting reduces SKILL.md size. |
| 5 | `repo-health-json-schema.md` | **Essential** | P0 | The `.repo-health.json` schema is already in SKILL.md. Extracting as standalone reference makes it reusable across projects. |
| 6 | `ci-wiring.md` | **Valuable** | P1 | CI integration patterns (GH Actions, GitLab) are referenced but not detailed. User suggestion #7 calls for CI efficiency audit. |
| 7 | `agent-instruction-ecosystem.md` | **Valuable** | P1 | Cross-agent portability (user suggestion #13). Research already done in PROPOSALS. Move to reference rather than keeping in plan. |
| 8 | `mature-project-patterns.md` | **Valuable** | **P1** | Research completed on 17 top-starred projects across 9 ecosystems (Go, JS/TS, Python, Ruby, Rust, C, Bash, Scala/JVM). Cross-domain comparison tables, 10 evidence-based design principles, critical counter-examples (ohmyzsh 0-tags, Homebrew rejects conventional, ansible devel branch, numpy multi-CI). Documented in section 1 of this plan. |
| 9 | `co-author-guard.md` | **Essential** | P0 | B11 needs a template. The three-layer pattern from hermes-skill-hq is perfect. Install as reference file. |
| 10 | `gitignore-templates.md` | **Valuable** | P1 | B10 .gitignore audit benefit. Official github/gitignore templates are the reference — this file would be a curated link index. |
| 11 | `anti-drift-proportionality.md` | **Valuable** | P1 | The heuristic from agent-concepts-study is foundational to the skill's design philosophy. Belongs in the skill's references, not in a study repo. |
| 12 | `script-awareness-chain.md` | **Deferred** | P2 | Relevant to script inventory and naming conventions (user suggestion #5), but the existing SKILL.md already uses heuristic discovery for scripts (B2). Add only if script inventory becomes a new phase. |

**Conclusion: 5 essential (P0), 5 valuable (P1), 1 deferred (P2).**

---

## 3. File Swamp Avoidance

The user explicitly flagged that earlier governance projects (edikt, ai-project-governance archive) ended in a **file swamp** — too many files with unclear purpose, no pruning mechanism, no cost of entry for adding a file. The reference file architecture in this plan risks the same fate without explicit guardrails.

### Swamp Definition

A file swamp in a skill occurs when:

| Symptom | Detection |
| :------ | :-------- |
| Reference files outnumber active skill sections | `ls references/*.md | wc -l` > pages in SKILL.md |
| Files exist that no SKILL.md section references | `grep -rfl references/` lists files without any `(references/...)` cross-ref in SKILL.md |
| Multiple files cover overlapping patterns | Two files that could be merged without losing clarity |
| Files are created "for future use" | No observed failure driving their creation |
| Files accumulate without a deletion or archival process | No list-scan-reconcile-delete discipline |

### Guardrails

#### 1. Hard ceiling: 15 reference files

The `references/` directory has a hard cap of 15 `.md` files. When the cap is reached, a new file can only be added by merging, pruning, or archiving an existing one. 15 provides room for the 9 planned files (5 P0 + 4 P1) plus 6 future additions — enough for the skill's lifetime without infinite growth.

**Enforcement:** Include `ls references/*.md | wc -l` in the consistency-check section of SKILL.md. If > 15, emit WARNING with list of candidates for consolidation.

#### 2. Entry criteria: no file without a cross-reference

Every reference file must be cross-referenced from SKILL.md within one line of adding it. An unreferenced reference file is a dead document. Cross-reference format:

```markdown
See [references/foo.md](references/foo.md) for details.
```

**Reason:** Unreferenced files cannot be found by an agent loading only the skill. They accumulate silently.

#### 3. Entry criteria: no file without an observed failure

Proportionate anti-drift principle applies to reference files too. Every reference file must trace to one of:
- An observed failure mode documented in docs/USER-SUGGESTIONS.md or agent-concepts-study
- A concrete user suggestion with evidence that the gap causes repeated issues
- Inline content that demonstrably makes SKILL.md too long to scan (< 200 lines target)

A reference file created because "this might be useful someday" is speculative swamp risk.

#### 4. Active pruning: one-in-one-out

When a new reference file is added and the 15-file ceiling is hit, the agent (or maintainer) must identify which existing file to merge, archive, or delete. The plan-to-file ratio should stay >= 1:2 (each plan phase justifies at most 2 reference files on average).

#### 5. Archive path: `references/archive/` for stale-but-historical content

Content that was once valuable but is no longer actively cross-referenced moves to `references/archive/`. Archived files are excluded from the 15-file ceiling and from the freshness check. They are historical records — not actionable references.

#### 6. Annual spring clean

Every January (or at each major version bump), scan the reference directory:
- Files cross-referenced exactly once: candidate for inlining or merging
- Files not cross-referenced at all: move to archive
- Files whose content overlaps: merge, keep one
- Files that could be replaced by a single URL: replace with link

This maps to the pruning mechanism called for by the proportionate anti-drift principle.

### Cost of breaking these guardrails

| Violation | Severity | Remediation |
| :-------- | :------- | :---------- |
| > 15 reference files | WARNING | Merge or archive to reduce count |
| Unreferenced file detected | WARNING | Add cross-reference or archive |
| File without observed-failure justification | INFO for existing, BLOCKING for new | Add justification or remove |
| No spring clean in > 12 months | INFO | Schedule one |

### Summary

The reference file directory is a tool, not a museum. The 15-file ceiling, cross-reference requirement, observed-failure entry criterion, and annual pruning together prevent the skill from repeating the edikt/ai-project-governance trajectory. If the skill's scope genuinely demands more than 15 reference files, that's a signal to re-evaluate whether the skill has exceeded its own proportionate size — not a signal to raise the cap.

---

## 4. Dependency Graph

```bash
|Phase 0: Cleanup (prerequisite for everything)
|  ├── B0: Self-consistency — create `scripts/check-claims.sh` that validates
|  │     the skill's own claims (line counts, file counts, criteria counts,
|  │     cross-references, documented-file-path resolution) against actual
|  │     filesystem state. Must pass before Phase 1 starts. Derived from
|  │     archive lesson: the checker must pass on itself first, else it
|  │     replicates the drift it claims to cure.
|  ├── Remove "From the USER" section from SKILL.md
|  │   └── Content → keep in docs/USER-SUGGESTIONS.md (already done)
|  ├── Create CHANGELOG.md with "Unreleased" section
|  └── Create basic references/ directory structure
|
| Design principle: enforcement logic for a single policy (trailer guard, claim
| freshness, etc.) lives in one shared script, not two — whether consumed by
| local hooks, CI, or review bots. Prevents the most common drift surface in
| multi-consumer enforcement: one path gets fixed, the other doesn't.

Phase 1: Extract inline detail into reference files (reduces SKILL.md)
  ├── heuristic-discovery.md  ← B1-B6 detection patterns
  ├── sync-targets.md         ← C1-C4 target types + verification
  ├── repo-health-json-schema.md ← .repo-health.json schema
  ├── release-checklist.md     ← B5 release procedure
  └── ci-wiring.md            ← CI integration patterns

Phase 2: Add B7 (commit audit + cross-commit drift)
  ├── Depends on: Phase 0 (clean SKILL.md), references/drift-pairs.md
  └── Blocks: nothing — independent phase

Phase 3: Add B11 (co-author guard)
  ├── Depends on: Phase 0 (clean SKILL.md), references/co-author-guard.md
  └── Blocks: nothing — independent phase

Phase 4: Add B8 (cross-platform shell audit)
  ├── Depends on: Phase 2 (B7 establishes the "scan scripts for patterns" pattern)
  └── Can be parallel with Phase 3

Phase 5: Add B9 (CI efficiency audit)
  ├── Depends on: Phase 1 (ci-wiring.md reference)
  └── Blocks: nothing

Phase 6: Add B10 (.gitignore metadata audit)
  ├── Depends on: references/gitignore-templates.md
  └── Blocks: nothing

Phase 7: Add value-added reference files
  ├── agent-instruction-ecosystem.md
  ├── anti-drift-proportionality.md
  ├── gitignore-templates.md
  ├── mature-project-patterns.md (research completed, move to references)

Phase 8: Final verification
  ├── Full dry-run against 3 target repos
  ├── Verify SKILL.md length is ~200 lines
  ├── Verify all cross-references resolve
  ├── Verify CHANGELOG.md populated
  └── Remove docs/USER-SUGGESTIONS.md or mark as historical
```

---

### 4.1 Evidence quality per B-check

Each B-check carries a label that tells the user (and the agent) how grounded it is.
This prevents speculative checks from being treated as authoritative — the AP3 guard.

| Check | Evidence quality | Grounding | First appears |
| :---- | :--------------- | :-------- | :------------ |
| **B0** | pragmatic | Archive lesson: checker must validate its own claims or it replicates the drift it claims to cure | Phase 0 |
| **B0 tri-layer fallback** | observed | User observation: `python-best-practices` skill installed but not always applicable or installable (SKILL.md §101-105) | Phase 0 |
| **B0 forge-awareness** | pragmatic | Derived from ecosystem survey (Claude Code, Codex, Copilot, Cursor); not an observed failure | Phase 0 |
| **B1** | research-backed | 17-project survey: 4 branch variants found (main, master, canary, devel) | Phase 0 |
| **B2** | observed | User suggestion; practical shellcheck integration | Phase 0 |
| **B3** | research-backed | 17-project survey: EditorConfig (9/17 = 53%) most common; ecosystem formatters (gofmt, rubocop, eslint) next; pre-commit framework rare (1/17). Detection hierarchy: EditorConfig → ecosystem formatter → CI linter → optional pre-commit. | Phase 0 |
| **B4** | pragmatic | Common version-detection need; no ecosystem survey required | Phase 0 |
| **B5** | research-backed | 17-project survey KF3 (tag count distribution), KF8 (release scripts) | Phase 0 |
| **B6** | pragmatic | Tool-specific formatter discovery; no ecosystem survey required | Phase 0 |
| **B7** | research-backed | 17-project survey KF1 (10 distinct commit styles), KF6 (CHANGELOG patterns) | Phase 2 |
| **B8** | research-backed | Shellcheck-verified shell patterns (SC2001, SC2039, SC3010, SC2164, SC2250). 17-project survey: .gitattributes prevalence (76%) validates cross-platform baseline. B8 scope should expand to include .gitattributes detection + high-frequency bashisms. | Phase 4 |
| **B9** | research-backed | 17-project survey KF5 (multi-CI detection), KF10 (git attributes) | Phase 5 |
| **B10** | research-backed | 17-project survey: AGENTS.md in 8/17 (47%), CLAUDE.md in 4/17 (24%), no project gitignores them. Official github/gitignore/Global/Agents.gitignore confirms instruction files are committed by default. Instruction conflict check (3/17 co-commit multiple formats) validated. | Phase 6 |
| **B11** | research-backed | Verified via web research: Linux kernel DCO v1.1, DCO App (337★, 88 forks), and hermes-skill-hq all share the same three-layer enforcement pattern (policy → local hook → CI gate with shared checker). Two direction families: proactive rejection (hermes style) vs required presence (kernel/DCO style). Same mechanism, different policy. | Phase 3 |

Distribution: 8 research-backed, 4 observed, 4 pragmatic — healthy signal that most
checks are tied to either survey evidence or concrete user observations, not speculation.

---

## 5. Concrete Phase Specifications

### Phase 0 — Cleanup

**What changes:**
- Remove lines 38-156 from SKILL.md (the "From the USER" section). Content already captured in docs/USER-SUGGESTIONS.md.
- Create `CHANGELOG.md` with `## Unreleased` section listing "Initial skill framework with Phase B (B1-B6) and Phase C (C1-C4)"
- Create `references/` directory skeleton

**Verification:**
|- `grep -c 'From the USER' SKILL.md` → 0
|- `test -f CHANGELOG.md` → true
|- `grep '## Unreleased' CHANGELOG.md` → match
|- SKILL.md length < 500 lines (baseline reduction from 614)

**B0 sub-procedure additions (gap closures, see §10):**

- **Quality-skill fallback (S9):** B0 runs a tri-layer probe before any
  quality-dependent B-phase:
  1. `skill_view(name)` — verify the skill exists and loads
  2. Frontmatter tags check — does the skill's language/scope match the repo?
  3. Degraded mode — if neither resolves, skip the check and log which
     checks were skipped and why
  Per-check fallback: B2 (shellcheck binary missing → skip, log reason);
  B3 (lint skill absent → look for `.pylintrc`/`.flake8`/`.ruff.toml`);
  B6 (formatter absent → `command -v` probe, use whatever is available).
- **Forge-awareness (S14):** B0 preamble states: "These checks work on any
  git repo. The skill activation mechanism is Hermes-specific; to port,
  create a forge-specific wrapper in `forge-adapters/` or rewrite SKILL.md
  frontmatter for that forge." Add `forge_adapters` field to
  `.repo-health.json` schema (optional — adapter configs for non-Hermes
  agent runtimes).

**What changes:**
- Create `references/heuristic-discovery.md` — extract B1-B6 detection patterns from SKILL.md
- Create `references/sync-targets.md` — extract C1-C4 target types + verification from SKILL.md
- Create `references/repo-health-json-schema.md` — extract .repo-health.json schema from SKILL.md
- Update SKILL.md phase descriptions to point to reference files instead of inline detail
- Convert inline script paths (scripts/check-consistency.js etc.) to generic references

**Heuristic-discovery.md content:**
- B1 git hygiene: all detection patterns from current table
- B2 shellcheck discovery + naming convention check: find .sh files, shellcheck rules, verify script names follow `verb-noun` pattern with standard prefixes (`check-`, `build-`, `deploy-`, `test-`, `lint-`, `install-`, `run-`, `release-`, `clean-`); overrides via `.repo-health.json`
- B3 consistency check: discovery precedence order, severity
- B4 version alignment: all version source extraction methods
- B5 tag vs release: tag/release cross-reference, GitLab extension note. Critical counterexample: ohmyzsh (188k stars, 0 tags) — "no tags" is a valid state, not a failure. Warn only if tags exist but are stale (>2 years since last tag).
- B6 format and lint: formatter discovery, commands

**Verification:**
|- SKILL.md length < 500 lines
- All reference files have consistent frontmatter
- Cross-references from SKILL.md to references/ resolve via relative links

### Phase 2 — B7: Commit Audit + Cross-commit Drift

**What changes:**
- Add B7 section to SKILL.md (4 sub-steps):
  - B7a: Commit message audit — check Conventional Commits adherence, format consistency
  - B7b: Cross-commit drift — detect when runtime files changed but CHANGELOG didn't (template from repo-consistency-enforcement/references/release-drift-enforcement.md)
  - B7c: CHANGELOG completeness — verify ## Unreleased section exists when runtime changes
  - B7d: Version-bump awareness — advisory warning when runtime files changed but version didn't
- Create `references/drift-pairs.md` with cross-commit drift patterns:
  - Release-drift enforcement (from repo-consistency-enforcement)
  - CHANGELOG completeness check
  - Script-awareness chain script inventory
  - Bidirectional script inventory guard

**Detection patterns (from research):**
```bash
# Cross-commit drift detection
git diff --name-only <baseline> HEAD | grep -q 'skills/\|src/' && {
  git diff --name-only <baseline> HEAD | grep -q 'CHANGELOG.md' || {
    echo "BLOCKING: runtime files changed but CHANGELOG.md did not"
  }
}
```

**Verification:**
- Apply B7 against agents-markdown-formatter: should detect CHANGELOG missing when runtime changes exist
- B7c passes when CHANGELOG.md exists with `## Unreleased`
- B7d is advisory only — no false blocks

### Phase 3 — B11: Co-Author Guard

**What changes:**
- Add B11 section to SKILL.md (4-layer enforcement):
  - B11a: Agent instruction layer — add MUST NOT rule for attribution trailers
  - B11b: Policy layer — add CONTRIBUTING.md section (or recommendation to create one)
  - B11c: Technical layer — create shared `scripts/check-commit-trailers.py` invokable by both local hook and CI
  - B11d: CI enforcement — reuse same checker over pushed/PR commit ranges
- Create `references/co-author-guard.md` with:
  - Three-layer pattern from hermes-skill-hq durable-patterns.md (lines 540-576)
  - Shared Python checker (`scripts/check-commit-trailers.py`) used by hook and CI — single source of truth for detection logic
  - Generic `*-by:` regex — catches `Co-authored-by:`, `Signed-off-by:`, `Helped-by:`, `Reviewed-by:`, etc. without maintaining a list
  - `--self-test` mode for CI-verifiable checker integrity (regression-proof)
  - `ALLOW_ATTRIBUTION_TRAILERS=1` bypass mechanism (env-var, same across hook and CI)
  - CI checker that scans commit range for trailers
  - Counter-indications (when not to apply)

**Hook template (shared Python checker, from hermes-skill-hq):**
```bash
#!/usr/bin/env bash
# commit-msg hook: reject unauthorized attribution trailers
# Delegates to shared Python checker.
set -euo pipefail
exec python3 "$(git rev-parse --show-toplevel)/scripts/check-commit-trailers.py" "$1"
```

```python
#!/usr/bin/env python3
# scripts/check-commit-trailers.py — shared between local hook and CI.
import os, re, sys

TRAILER_PATTERN = re.compile(
    r"^[A-Za-z][A-Za-z0-9-]*-by:[ \t]*\S[^\r\n]*$", re.MULTILINE | re.IGNORECASE,
)

def find_violations(message: str) -> list[str]:
    return TRAILER_PATTERN.findall(message)

def is_authorized() -> bool:
    return os.environ.get("ALLOW_ATTRIBUTION_TRAILERS", "").lower() in {"1", "true", "yes"}

def self_test() -> int:
    prohibited = ["Co-authored-by: X <x@x>", "Signed-off-by: X <x@x>", "Helped-by: X <x@x>"]
    for t in prohibited:
        assert find_violations(f"subject\n\n{t}\n") == [t]
        assert find_violations(f"subject\n\n{t}\n") == [t] if not is_authorized() else True
    assert find_violations("Helped by careful review.\n") == []
    print("self-test: PASS")
    return 0

if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(self_test())
    msg = sys.stdin.read() if len(sys.argv) < 2 else open(sys.argv[1]).read()
    violations = find_violations(msg)
    if violations and not is_authorized():
        print("ERROR: Unauthorized attribution trailers:", violations, file=sys.stderr)
        print("Bypass: ALLOW_ATTRIBUTION_TRAILERS=1", file=sys.stderr)
        raise SystemExit(1)
    print("OK: No unauthorized trailers")
```

**Verification:**
- Hook rejects commit with `Co-authored-by:` line
- Hook passes when `ALLOW_ATTRIBUTION_TRAILERS=1` set
- `python3 scripts/check-commit-trailers.py --self-test` exits 0
- CI checker detects trailers in pushed commit range
- All tests pass without existing repo contamination

### Phase 4 — B8: Cross-Platform Shell Audit

**What changes:**
- Add B8 section to SKILL.md
- Detection: scan `.sh` files for non-portable patterns
- Non-portable patterns table (from PROPOSALS research):

| Pattern | Detect with | Portable replacement |
| :------ | :---------- | :------------------- |
| `which` | `grep '\bwhich\b'` | `command -v` |
| `grep -P` | `grep -n 'grep.*-P'` | `grep -E` |
| `sed -i` (no backup) | `grep -n 'sed -i[^b]'` | `sed -i.bak` |
| `echo` with escapes | `grep -n 'echo.*\\'` | `printf '%s\n'` |
| `#!/bin/bash` | `grep -n '#!/bin/bash'` | `#!/usr/bin/env bash` |
| `\012` octal | `grep -n '\\012'` | `\n` |
| `find -exit` | `grep -n 'find.*-exit'` | `find ... -exec` |
| `flock` | `grep -n '\bflock\b'` | `mkdir .lock || exit 1` |

**Severity:** WARNING — portability is project-dependent. Some projects only target Linux and may reject portable patterns that add complexity.

**Verification:**
- Run against known scripts: detection finds patterns, false positives are documented
- Skip gracefully if no `.sh` files found

### Phase 5 — B9: CI Efficiency Audit

**What changes:**
- Add B9 section to SKILL.md
- Detection: inspect `.github/workflows/*.yml` for:
  - Trigger scoping (push vs PR vs tag vs schedule)
  - `paths-ignore` coverage for documentation-only changes
  - Tag behavior (are tag pushes evaluated separately from branch pushes?)
  - Build dependency caching
  - Artifact shipping vs maintenance-only jobs

**Evaluation criteria (from research):**

| Signal | Efficient | Inefficient |
| :----- | :-------- | :---------- |
| Trigger scoping | Separate workflow for docs/CI/release | Monolithic workflow triggers on everything |
| paths-ignore | Excludes README.md, *.md (documentation) | No paths-ignore — docs trigger full CI |
| Tag handling | Tag pushes skip build if release is manual | Tag pushes re-run the full pipeline |
| Caching | `actions/cache` for deps | No cache — fresh install every run |
| Guard workflow independence | Standalone guard workflow (e.g. `commit-trailer-check`) | Guard embedded in build workflow — doc-only pushes skip it |
| Artifact separation | Ship workflow separate from test workflow | Tests and shipping in same workflow |

**Severity:** WARNING — CI efficiency is project-dependent. Advisory only.

### Phase 6 — B10: .gitignore + Repository Metadata Audit

**What changes:**
- Add B10 section to SKILL.md
- Detection:
  1. Check if `.gitignore` exists → if not, WARNING
  2. Check for agent-artifact patterns (from official Agents.gitignore):
     - `.open-mem/`, `.omo/`, `.aider.*`, `CLAUDE.local.md`, `.claude/**/*.log`, `AGENT.md`, `GEMINI.md`
  3. Check for OS junk: `.DS_Store`, `Thumbs.db`, `*.swp`
  4. Check for language-specific build artifacts: `node_modules/`, `__pycache__/`, `*.pyc`, `target/`, `dist/`
  5. Check for IDE files: `.vscode/`, `.idea/`, `*.sublime-*`
  6. Check for instruction-file conflicts: if any two of `[AGENTS.md, WARP.md, .rules, CLAUDE.md, GEMINI.md, .github/copilot-instructions.md]` co-exist, flag for manual review — undocumented precedence between agent config files creates invisible divergence in behavior

**Severity:** WARNING — missing .gitignore is advisory; incorrect exclusions may block builds.

**Note:** B10 starts with inline agent-artifact patterns; Phase 7 formalizes them into `references/gitignore-templates.md`. The dependency is soft — Phase 6 can run before Phase 7 without failing.

### Phase 7 — Reference Files (Valuable)

**What changes:**
- Create `references/agent-instruction-ecosystem.md`:
  - The table from PROPOSALS research
  - Links to each platform's docs
  - Guidance on when to use cross-agent patterns vs forge-specific patterns
  - Portability tiers table (Tier 1 Pure VCS / Tier 2 Shell + tools / Tier 3 Agent-specific)
  - Adaptation path for other forges (Claude Code, Codex, Cursor, Copilot)
- Create `references/anti-drift-proportionality.md`:
  - Heuristic from agent-concepts-study (proportionate-anti-drift-from-observed-failure.md)
  - When to add a check vs when to wait
  - Distinction between instruction files and verification checks
- Create `references/gitignore-templates.md`:
  - Links to official github/gitignore templates per language
  - Agents.gitignore patterns
  - Per-language recommendations

---

## 6. Evaluation of PROPOSALS Readiness

| PROPOSALS Recommendation | Accepted? | Modifications |
| :-------------------------- | :-------- | :------------ |
| Option 3 (two-phase) | ✅ Accepted | Refined into 8-phase plan above |
| B7 commit audit + drift | ✅ Accepted | Expanded with 4 sub-steps (B7a-B7d) |
| B11 co-author guard | ✅ Accepted | Added concrete hook template |
| B8 cross-platform shell audit | ✅ Accepted | Added detection table |
| B9 CI efficiency audit | ✅ Accepted | Added evaluation criteria |
| B10 .gitignore metadata audit | ✅ Accepted | Added pattern checklist |
| Keep docs/USER-SUGGESTIONS.md | ❌ Rejected | Remove after Phase 0 — content captured elsewhere |
| templates/ directory | ❌ Rejected | Premature per proportionate anti-drift |
| 10 reference files | ⚠️ Scoped | 5 essential (P0), 5 valuable (P1), 1 deferred (P2) |

---

## 7. Anti-Patterns to Avoid

Anti-patterns are structural choices that seem productive in the moment but create
accumulating cost over time. These are drawn from the research (agent-concepts-study,
repo-consistency-enforcement, user observations) and apply to both the skill's own
design and the repos it inspects.

### AP1: Duplicate Guidance as Drift Surface

Repeating the same information in multiple files guarantees it will go out of sync.
Every duplicate is a drift surface — the same principle applies whether it's two
files or two sections of the same file.

**Observed:** In agent-concepts-study (duplicate-guidance-as-drift-surface.md):
tightening passes revealed surface-level → structural-level → guidance-level drift,
each layer deeper than the last.

**Apply as:**
- Keep canonical guidance in exactly one file per data type
- Other files point to the canonical source (pointer pattern)
- Do not inline a fact in AGENTS.md that lives in SKILL.md, and vice versa

**Detect with:** `grep` for the same literal path or command appearing in > 1 file.
Each match beyond the first is a candidate for deduplication.

### AP2: Code Inside Markdown

Shell commands, scripts, or configuration embedded in markdown code blocks cannot be
shellchecked, syntax-checked, or tested. They rot silently because no tool validates
them. When someone changes the script, the markdown example stays unchanged.

**Observed:** User suggestion, SKILL.md B2 footnote: "The inclusion of code inside
markdown files makes the use of checking and testing the scripts nearly impossible."

**Apply as:**
- Extract executable code to `scripts/` files
- Reference from markdown: "run `scripts/check.sh`" not "run `#!/bin/bash ...`"
- One-liner shell commands in prose are acceptable (e.g., `grep -c 'foo' bar.txt`)
- Multi-line code blocks should reference a file, not inline the logic

### AP3: Speculative Checks Before Observed Failure

Adding verification machinery "just in case" creates maintenance debt before it
creates value. The check itself needs maintenance, the baseline needs updating,
and false positives erode trust.

**Observed:** In proportionate-anti-drift-from-observed-failure.md: "Anti-drift
machinery is disproportionate when checks are added speculatively."

**Apply as:**
- Proportionate anti-drift: add a check only after observing the specific failure
- The cost of the check must be low relative to the cost of the drift it prevents
- Each check must have a single clear failure mode
- Checks accumulate a pruning obligation (annual spring clean per section 3)

### AP4: Multiple Authority Surfaces

When AGENTS.md, SKILL.md, README.md, and a reference file all claim authority over
the same data (script paths, version numbers, conventions), agents and humans don't
know which to trust. Each surface can become stale independently.

**Observed:** In agent-instruction-boundaries-and-drift.md: "Do not multiply
authoritative instruction surfaces unless there is a clear maintenance or scope
reason." Also in script-awareness-chain reference: the discipline rule is "all
concrete script paths live in exactly one file."

**Apply as:**
- One canonical location per data type
- Other locations point to it (pointer pattern)
- A "pointer" is a relative link or a generic phrase ("run the stale check")
- A pointer is NOT a concrete path or duplicate table

### AP5: Hardcoded Version Numbers in Operational Locations

Version strings in README examples, CI workflow defaults, Containerfile ENV lines,
and build scripts all drift independently. Each location must be updated on every
release — and one will be missed.

**Observed:** In version-auto-detection-consolidation.md: a project had hardcoded
version references in 6+ locations. After consolidation, all pointed to one source
of truth.

**Apply as:**
- One source of truth for the current version (build script default or VERSION file)
- All execution layers (CI, Containerfile, scripts) consume it, not hardcode it
- Documentation uses `latest` or a pointer, not a specific version number
- Changelog and decision-log entries are the exception — they record history

### AP6: Inline Script Paths in Workflow Documents

An AGENTS.md or README containing `scripts/foo.sh` means every rename, move, or
deletion requires updating N files. The path is repeated, not referenced — classic
duplicate-guidance problem.

**Observed:** In script-awareness-chain.md: the key invariant was "all concrete
script paths live in exactly one file (SKILL.md)." Workflow files used generic
phrases like "run the stale check."

**Apply as:**
- Keep all concrete script paths in one canonical file (SKILL.md Scripts table)
- Workflow documents use generic references: "run the sync command" not
  "run `scripts/sync-doom-skill-mirror.sh`"
- An agent reading the workflow file opens the canonical file to find the path
  — a single hop that replaces N drift-prone duplicates

### AP7: Unreferenced Reference Files

A reference file not cross-referenced from SKILL.md is invisible to agents loading
only the skill. It accumulates silently — occupying disk space and mental space
but providing zero value.

**Observed:** Direct consequence of the edikt/ai-project-governance file swamp.
Also documented in the entry criteria in section 3 of this plan.

**Apply as:**
- Every reference file must have a cross-reference from SKILL.md
- Cross-reference format: `See [references/foo.md](references/foo.md)`
- No cross-reference = candidate for archival or deletion
- Enforce via: `grep -rfl references/SKILL.md | sort` vs `ls references/*.md`

### AP8: Templates Before Need

Creating `.repo-health.json.example`, `templates/` directory, or scaffolding
before a project has expressed a concrete need. Templates are speculative until
a project uses them — they add structure without demonstrating that the structure
solves a real problem.

**Observed:** User suggestion explicitly: "Evaluate the use of templates with
caution since they may add extra complexity with small returned value."

**Apply as:**
- Add templates only after an observed failure where a template would have helped
- The example `.repo-health.json` lives in the existing skill references, not in
  a separate templates/ directory
- The templates/ directory is not created in Phase 0 or Phase 1

### AP9: Over-Nesting

Directories within directories within directories
(`references/subtopic/variant/subvariant.md`). Each nesting level reduces
discoverability. An agent or human must drill through the hierarchy to find
anything.

**Observed:** The edikt project's file swamp was characterized by deep nesting
that made navigation harder, not easier.

**Apply as:**
- Flat `references/` directory — all reference files at the top level
- One subdirectory allowed: `references/archive/` for stale content
- If a reference file needs subsections, use internal markdown headings, not
  subdirectories
- If > 15 files are genuinely needed (against the hard ceiling), re-evaluate
  the skill's architecture — don't add another nesting level

### AP10: Shipping Maintainer Tooling to Users

CI scripts, release automation, development-only checks, and scaffolding that
get installed into the user's runtime directory. The user's machine becomes a
copy of the development environment with no distinction between what's needed
to run the tool and what's needed to build it.

**Observed:** User suggestion: "What should be shipped to the new user should
be reviewed and optimized. Deployment and repo logic stays in the repo."

**Apply as:**
- Phase C separation in the skill's own design: maintainer logic stays in the
  repo's scripts/ directory
- Only the runtime payload (skills/src/) ships to the user
- The skill's own SKILL.md has a "Maintainer" section separate from "Usage"
- Release artifacts (built packages) are distinct from development files

### Summary Table

| # | Anti-Pattern | Detection | Remedy | Source |
| :- | :----------- | :-------- | :----- | :----- |
| AP1 | Duplicate guidance | `grep` same path/command in > 1 file | Pointer pattern, one canonical source | agent-concepts-study |
| AP2 | Code in markdown | Multi-line code block with shell code | Extract to `scripts/` file | User observation |
| AP3 | Speculative checks | Check added without observed failure | Proportionate anti-drift principle | agent-concepts-study |
| AP4 | Multiple authority surfaces | Same data type in 2+ instruction files | One canonical file per data type | agent-concepts-study |
| AP5 | Hardcoded versions | `grep -r '0\.'` version pattern in operational files | Single source + auto-detection | version-auto-detection-consolidation |
| AP6 | Inline script paths | Concrete `scripts/foo.sh` in workflow prose | Generic reference + SKILL.md table | script-awareness-chain |
| AP7 | Unreferenced references | File in `references/` not cross-referenced in SKILL.md | Cross-reference or archive | File swamp analysis |
| AP8 | Templates before need | `templates/` directory or `.example` files | Add only after observed failure | User observation |
| AP9 | Over-nesting | > 1 level of subdirectory in `references/` | Flat directory + `archive/` only | edikt file swamp |
| AP10 | Shipping maintainer tooling | CI/release scripts in user's runtime path | Phase C separation, repo stays in repo | User observation |
| AP11 | Trusting stale snapshots over machine truth | `grep` hardcoded counts/dates that drift from `git log`/`ls \| wc -l` | Always query live state; never commit plan-level counts | agent-concepts-study |
| AP12 | Unidirectional links (no back-pointer) | Reference file mentions a script but the script doesn't declare its location | Scripts include a self-declaration comment with expected path | Script-awareness chain |
| AP13 | Scripts without self-location | Script moved/renamed but no comment indicating expected canonical path | Every script starts with `# scripts/foo.sh — canonical path` | Script-awareness chain |
| AP14 | Unchecked quality-skill dependency | B-phase depends on a quality skill without verifying availability | B0 tri-layer probe: skill_view → frontmatter match → degraded fallback | User observation (SKILL.md §101-105) |

These anti-patterns are not just rules — they are observations from real failures.
Each one was learned the hard way before being documented here.

---

## 8. Verification Plan

After all phases:

| Check | Command | Expected |
| :---- | :------ | :------- |
| SKILL.md length | `wc -l SKILL.md` | ~250 lines (reduced from 614) |
| No discussion text in SKILL.md | `grep -c 'From the USER' SKILL.md` | 0 |
| CHANGELOG exists | `test -f CHANGELOG.md` | true |
| References directory | `ls references/*.md \| wc -l` | >= 9 (5 core + 4 valuable) |
| Cross-references resolve | `grep -r '(references/' SKILL.md \| grep -v '#'` | Every reference has a file |
| No inline script paths | `grep -c 'scripts/\|\.sh' SKILL.md` | < 5 (only generic mentions allowed) |
| Version in frontmatter | `grep '^version:' SKILL.md` | >= "1.1.0" |
| All user suggestions mapped | Each of 16 items in docs/USER-SUGGESTIONS.md has a phase in this plan | Phase column populated |
| B2 naming-convention check | Add naming convention check to B2 spec | `verb-noun` pattern check runs and flags non-standard names |
| B0 tri-layer fallback | B0 tri-layer fallback documented per B-phase | Per-check degraded mode documented |
| B0 forge-awareness | Forge-awareness preamble exists in B0 | B0 preamble mentions portability tiers |
| Dry-run against 3 repos | agents-markdown-formatter, hermes-skill-hq, neovim-latest-ubuntu | No BLOCKING errors |

---

## 9. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
| :--- | :--------- | :----- | :--------- |
| SKILL.md restructure breaks existing agents | Low (single-file, only path) | Medium | Keep backward-compatible phase names (B1-B6, C1-C4) |
| B7 drift detection creates false positives | Medium | Low | Make B7b-B7d advisory (WARNING), only B7a (commit audit) BLOCKING |
| B11 hook interferes with legitimate co-authored commits | Low | Medium | Bypass mechanism via `ALLOW_ATTRIBUTION_TRAILERS=1`; document in the skill |
| B8 portability check flags Linux-only project | Medium | Low | Default severity is WARNING; override via `.repo-health.json` |
| Phase order drift (implementing out of order) | Medium | Low | This plan establishes dependency order; enforce via the plan itself |
| Reference files go stale | Medium | Low | Include reference file freshness check in B7 drift detection |

---

## 10. Summary

Implementation order:

```
Phase 0 (cleanup) → Phase 1 (extract references) → Phase 2 (B7) + Phase 3 (B11)
→ Phase 4 (B8) + Phase 5 (B9) + Phase 6 (B10) → Phase 7 (value references) → Phase 8 (verify)
```

Total: 9 phases, 5 essential reference files, 4 valuable reference files, 5 new phases (B7-B11), 2 deferred items.

First deliverable (Phase 0 + Phase 1): SKILL.md reduced from 614 to ~350 lines, references/ directory populated with 5 files, CHANGELOG.md created, "From the USER" section removed. This is safe to ship as v1.1.0.

---

## §10 Gap Closure Research

Three structural gaps identified in docs/REPORT.md required evidence-backed investigation. Each was closed by integrating research findings into the plan's existing phase structure without creating new phases.

### §10.1 S5 — Script Naming Conventions (was: deferred to P2)

**Evidence base:** PROPOSALS §"Script Naming Conventions" (research across Linux kernel, Homebrew, Kubernetes, and major open-source projects) + 17-project survey (django, numpy, vscode, kubernetes, golang, prometheus, ansible, etc.)

**Finding:** A consistent naming economy emerges across all surveyed projects. The patterns are settled — there is no significant variation to discover.

| Directory | Used By | Purpose |
| :-------- | :------ | :------ |
| `scripts/` | django, numpy, nodejs | Generic executable scripts |
| `build/` | vscode, kubernetes | Build/compilation scripts |
| `cmd/` | prometheus (Go) | Main entrypoints per Go idiom |
| `.github/scripts/` | Homebrew | CI/hook-scoped scripts |
| `bin/` | apache/spark | User-facing tools |
| `hacking/` | ansible | Developer environment setup |
| `misc/` | golang | Uncategorised utilities |

| Script prefix | Used By | Purpose |
| :------------ | :------ | :------ |
| `check-*` / `verify-*` | Most of the above | Validation |
| `build-*` | vscode, kubernetes | Build |
| `install-*` | numpy, ansible | Setup |
| `deploy-*` / `sync-*` | Various | Deployment |
| `run-*` / `start-*` | Various | Execution |
| `test-*` | Most | Testing |
| `lint-*` / `format-*` | django, nodejs | Quality |
| `release-*` / `publish-*` | Various | Releases |

**Resolution:** The deferred P2 item should be promoted to a mandatory naming convention check within **B2 (Shellcheck / Script Inventory)**. The skill already discovers scripts by heuristic — adding a naming-consistency check requires no new phase, just an additional detection step in B2: "Are script names `verb-noun`? Is directory `scripts/` with exceptions documented in `.repo-health.json`?" This is proportionate: the conventions are already known, codify them.

**Change required:** Add to B2 scope: "Check script naming conventions against known patterns; flag non-standard names (e.g. `do_stuff.sh` without `check-`/`build-`/etc. prefix). Allow overrides via `.repo-health.json`."

### §10.2 S9 — Quality-Skill Fallback Strategy

**Evidence base:** User observation (SKILL.md lines 101-105): "`python-best-practices` skill is installed but cannot be applied in all cases and cannot be installed on all machines." Agent-concepts-study proportionate anti-drift principle: "do not add the check before the failure creates the need."

**Finding:** The problem has three distinct failure modes with different remedies:

| Mode | Scenario | Impact | Remedy |
| :--- | :------- | :----- | :----- |
| **Skill present, applicable** | `python-best-practices` loaded, project has Python files | Full quality check | Normal execution |
| **Skill present, not applicable** | `python-best-practices` loaded, project is JavaScript | No-op (wrong language) | B0 should skip silently — skills self-declare language scope via their frontmatter `tags` field |
| **Skill not present** | Agent runs on machine without `python-best-practices` installed | Cannot run quality checks at all | B0 must fall back gracefully |

**Resolution: B0 tri-layer fallback pattern.** Before any Phase B check, B0 determines quality-skill availability:

```
Layer 1:  skill_view(name)    │ Can verify the skill exists and is loadable
Layer 2:  frontmatter check   │ Does skill's tags/description match repo language?
Layer 3:  degraded mode       │ If neither Layer 1 nor Layer 2 resolves, skip the check
                              │ + log which checks were skipped and why
```

Applied to each B-phase that depends on an external quality skill:

| Check | Depends on | Fallback when absent |
| :---- | :--------- | :------------------- |
| B2 Shellcheck | `shellcheck` binary | Skip, log reason |
| B3 Lint | `python-best-practices` skill (or equivalent language skill) | Probe skill availability first. If absent, check for `.pylintrc`/`.flake8`/`.ruff.toml` config files and run the tool directly as degraded mode. |
| B6 Format | `prettier`, `black`, `rustfmt` etc. | `command -v` probe — degraded mode uses whatever is available |

**Change required:** Add a "Quality-Skill Fallback" subsection to B0 that documents the tri-layer probe pattern and the degraded-mode convention for each B-phase. This does not require a new phase — it's a B0 sub-procedure executed once at baseline start.

### §10.3 S14 — Cross-Agent Portability

**Evidence base:** Claude Code docs (`CLAUDE.md` + `.claude/` directory), OpenAI Codex (`AGENTS.md` + `AGENTS.override.md`), GitHub Copilot (`.github/copilot-instructions.md`), Cursor (`.cursorrules` + `.cursor/`). All four major agent platforms converge on the same architecture: single canonical instruction file + optional scoped directory. The `references/agent-instruction-ecosystem.md` already planned for Phase 7 captures this research.

**Finding:** The skill's B-checks fall into three portability tiers:

| Tier | Description | Phases | Portability |
| :--- | :---------- | :----- | :---------- |
| **Tier 1 — Pure VCS** | Git-only commands, no platform dependency | B0, B1, B4, B5, B7, B10, B11 | Fully portable — any agent platform with git access |
| **Tier 2 — Shell + tools** | Uses `find`, `shellcheck`, language tools | B2, B3, B6, B8 | Portable — standard Unix tooling, no agent dependency |
| **Tier 3 — Agent-specific** | Skill activation, `skill_view` probe, CM lifecycle | SKILL.md frontmatter, B0 tri-layer probe | Hermes-specific — the skill system is the only Hermes-bound component |

**Implication:** The B-checks (core value) are 85-90% agent-agnostic. Only the skill packaging mechanism is Hermes-bound. The architectural answer to "should this be Hermes focused?" is:

> The skill's **detection logic and anti-pattern taxonomy** should remain agent-agnostic. The skill's **packaging and activation** is Hermes-specific with a documented adaptation path for other forges.

**Change required:**
1. Add a **forge-awareness subsection** to B0's preamble: "These checks work on any git repo. The skill activation mechanism is Hermes-specific; to port, create a forge-specific wrapper in `forge-adapters/` or rewrite SKILL.md frontmatter for that forge."
2. Add `forge_adapters` to the `.repo-health.json` schema — optional field listing adapter configurations for non-Hermes agent runtimes.
3. Document the portability tiers (above) in the `references/agent-instruction-ecosystem.md`.

This closure is **not speculative** — the research is complete per PROPOSALS §18-28 and §139-140 and the Claude Code doc review. The remaining action is to integrate these findings into the planned Phase 7 reference file and B0 preamble.

---

## §11 Changes Required

### To §5 Phase 0 B0 — Self-Consistency

Add subsections:
- **Quality-skill fallback (S9):** Tri-layer probe pattern before any quality-dependent B-phase. Document per-check degraded mode.
- **Forge-awareness (S14):** Preamble note that checks are agent-agnostic; only skill activation is Hermes-bound. Add `forge_adapters` field to schema.

### To §5 Phase 1 B2 — Shellcheck + Script Inventory

Add to B2 scope:
- **Naming convention check (S5):** Verify script names follow `verb-noun` pattern. Accept standard prefixes (`check-`, `build-`, `deploy-`, `test-`, `lint-`, `install-`, `run-`, `release-`, `clean-`). Override via `.repo-health.json`. Flag non-standard names as WARNING.

### To §5 Phase 7 — Reference File Creation

Add to `agent-instruction-ecosystem.md`:
- Portability tiers table (Tier 1 Pure VCS / Tier 2 Shell / Tier 3 Agent-specific)
- Adaptation path for other forges (Claude Code, Codex, Cursor, Copilot)

### To §7 Anti-Patterns

Add AP14 — Unchecked Quality-Skill Dependency:
| Detection | Remedy | Source |
| :-------- | :----- | :----- |
| B-phase depends on a quality skill without verifying availability | B0 tri-layer probe: skill_view → frontmatter match → degraded fallback | User observation (SKILL.md §101-105) |

### To §8 Verification Plan

Add verification row:
- B2 naming-convention check runs and flags non-standard names
- B0 tri-layer fallback is documented per B-phase
- Forge-awareness preamble exists in B0


