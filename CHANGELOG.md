# Changelog

## Unreleased

- feat: add README documentation audit to verify.sh (§Doc A1–A7)
- refactor: replace inline doc greps with manifest-driven doc-audit.py + docs/doc-standards.json
- docs: update AGENTS.md for manifest-driven doc standards, update project structure

- Repo metadata: updated README.md (install command, badges, phase table), added .gitattributes, set 6 GitHub topics
- README.md: closed 10 gaps — how-it-works, output example, audience, C-row expansion, .repo-health.json link, contributors pointer, SKILL.md table link, "See also" — +31 lines, tightened
- scripts/verify.sh: fixed 2 GNU-only violations (grep -oP → -oE, sort -V → git --sort)

## [0.1.0] - 2026-06-26

- Initial skill framework: Phase B (B1-B6 project health baseline) and Phase C (C1-C4 reverse sync).
- B7 commit audit: message format consistency (B7a), cross-commit drift (B7b), CHANGELOG completeness (B7c), version-bump awareness (B7d).
- references/drift-pairs.md: reusable cross-commit detection patterns with `.repo-health.json` configuration.
- B11 co-author guard: 4-layer enforcement (agent instruction, policy, shared Python checker, CI) for attribution trailers.
- references/co-author-guard.md: full implementation, hook template, CI config, bypass, counter-indications.
- scripts/check-commit-trailers.py: shared Python checker with `*-by:` regex, `--self-test`, `--range`, and `ALLOW_ATTRIBUTION_TRAILERS=1` bypass.
- B8 cross-platform shell audit: 8 non-portable pattern detections against `.sh` files with portable replacements.
- B9 CI efficiency audit: 6 signal evaluation table for `.github/workflows/*.yml` (trigger scoping, paths-ignore, caching, etc.).
- B10 `.gitignore` + repository metadata audit: 6-category check (agent artifacts, OS junk, build artifacts, IDE files, instruction-file conflicts).
- references/agent-instruction-ecosystem.md: agent instruction files per platform, portability tiers, adaptation paths.
- references/gitignore-templates.md: official templates, agent-artifact patterns from Agents.gitignore, per-language recommendations.
- Phase 8: end-to-end verification (42/42 pass); historical research docs archived.
- 'Repo as source' B0 principle: separate maintainer tooling from user install, closes user suggestion #8.
- Flatten docs/ from 4 research documents (2000 lines) to 2 human-readable files: decisions.md (164 lines) + research.md (223 lines)
- root README.md: user-facing install/quickstart
- docs/README.md: maintainer audience note; B0 updated to include docs/ in never-sync list
- B2: shellcheck binary guard in "How" step (both SKILL.md and heuristic-discovery.md)
- AGENTS.md: structured skill-development guide with commit conventions, verification standards, maintainer best practices (tightened from 227 to 110 lines via pointer-over-inline)
- Dogfood: added scripts/verify.sh (self-consistency, 8/8), .repo-health.json, patched 3 missing .gitignore patterns (.claude/*.log, AGENT.md, GEMINI.md)
- B0: 'Portable grep in skill code' principle; fixed 2 GNU-only `grep -P` usages in reference files (heuristic-discovery.md, drift-pairs.md)
