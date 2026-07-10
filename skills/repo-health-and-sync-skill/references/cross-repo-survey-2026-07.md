# Cross-Repo Survey (July 2026)

Survey of 9 non-evidentia repos under CodeSigils to validate and improve the
repo-health-and-sync-skill's heuristic detection and coverage.

## Methodology

For each repo, checked: git state, CI, .gitignore, agent artifact dirs,
shell scripts, .githooks/, CHANGELOG, CONTRIBUTING, instruction-file conflicts,
build artifacts, branch name, remote count, and .repo-health.json adoption.

## Findings

### Zero CHANGELOG adoption (unexpected)
None of the 9 repos use CHANGELOG.md. The B7b/B7c commit-quality gate (B0
principle) would skip CHANGELOG enforcement for all of them. The skill's
CHANGELOG weight is disproportionate to real-world usage — the commit-quality
gate does the heavy lifting.

### Zero .repo-health.json adoption (expected, validates heuristics)
None of the 9 repos need per-project overrides. The heuristic detection
works well enough without explicit config. The file remains useful for edge
cases but is not a barrier to adoption.

### .githooks/ is a growing pattern
3 of 9 repos use `.githooks/` with `git config core.hooksPath`:
`hermes-skill-hq`, `neovim-latest-ubuntu`, `zero-md-formatter`.
The skill previously didn't detect, lint, or audit this directory.
Adding `.githooks/` to B2 (shellcheck), B8 (portability), and B10 (tracked
dir) closes this gap.

### Agent artifact dirs are proliferating
`.agents/`, `.codex/`, `.opencode/`, `.cursor/` appear across multiple repos.
B10's agent-artifact category was expanded to cover these. Common pattern:
gitignore the agent runtime dirs but track AGENTS.md/CLAUDE.md as committed
instruction files.

### Instruction-file conflicts are rare but real
`markdown-oxc-spike` and `hermes-skill-hq` both have AGENTS.md + agent runtime
dirs (.open-mem/, .omo/). No repo had WARP.md or CLAUDE.md alongside AGENTS.md
as a simultaneous conflict, but the check guard-rails against future drift.

### Container build artifacts need patterns
`neovim-latest-ubuntu` uses an `output/` directory for .deb artifacts.
`build/`, `output/`, and `.pytest_cache/` were missing from the build-artifact
category and were added.

## Repos surveyed

| Repo | Type | CI | Shell scripts | .githooks | .repo-health.json |
|------|------|----|---------------|-----------|-------------------|
| awesome-agent-trust | awesome-list | path-scoped | 0 | no | absent |
| emerging-pattern-proposals | research/notes | none | 0 | no | absent |
| hermes-skill-hq | knowledge-base | sophisticated | 14 | yes | absent |
| markdown-oxc-spike | spike | basic | 1 | no | absent |
| neovim-latest-ubuntu | devops/tooling | well-separated | 4 | yes | absent |
| py-review-skill | skill | basic | 0 | no | absent |
| python-project-workflow | skill | basic | 0 | no | absent |
| skill-discovery | skill | path-scoped | 0 | no | absent |
| zero-md-formatter | tool | test+publish split | 2 | yes | absent |

## Gaps identified and closed

1. **Agent artifact dirs**: added `.agents/`, `.codex/`, `.opencode/`, `.cursor/`
2. **Build artifacts**: added `.pytest_cache/`, `build/`, `output/`
3. **Sync-drift guard**: added B0 stale-mirror principle + Overview step 2
4. **.githooks/** detection: added to B2 shellcheck, B8 portability, B10 tracking
5. **.repo-health.json drift**: synced file from installed mirror to project source
