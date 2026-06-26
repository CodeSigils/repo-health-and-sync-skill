# Changelog

## Unreleased

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
