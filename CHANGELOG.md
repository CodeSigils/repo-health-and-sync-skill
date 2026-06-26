# Changelog

## Unreleased

- Initial skill framework: Phase B (B1-B6 project health baseline) and Phase C (C1-C4 reverse sync).
- B7 commit audit: message format consistency (B7a), cross-commit drift (B7b), CHANGELOG completeness (B7c), version-bump awareness (B7d).
- references/drift-pairs.md: reusable cross-commit detection patterns with `.repo-health.json` configuration.
- B11 co-author guard: 4-layer enforcement (agent instruction, policy, shared Python checker, CI) for attribution trailers.
- references/co-author-guard.md: full implementation, hook template, CI config, bypass, counter-indications.
- scripts/check-commit-trailers.py: shared Python checker with `*-by:` regex, `--self-test`, `--range`, and `ALLOW_ATTRIBUTION_TRAILERS=1` bypass.
- B8 cross-platform shell audit: 8 non-portable pattern detections against `.sh` files with portable replacements.
