# Eval Fixtures Reference

Deterministic fixtures for behavioral contract validation. Located at `evals/cases/repo-health-scan.json`.

## Fixture Overview

| Fixture | Repo Type | Key Profile Signals | Active Dimensions |
|---------|-----------|---------------------|-------------------|
| `codex-skill-pack` | Skill pack | One independent plugin-manifest version, GH Actions, shell files | 5 (all except version_alignment, cross_platform, attribution_drift, external_reference_health, reliability_test_gaps) |
| `python-library-without-shell` | Python lib (uv) | 2 version sources, GH Actions, no shell files | 5 (all except shell_correctness, cross_platform, attribution_drift, external_reference_health, reliability_test_gaps) |
| `monorepo-workspace` | Monorepo (TS + Python) | 3 version sources declared as one version-aligned release group (npm + uv), GH Actions, no shell files | 5 (all except shell_correctness, cross_platform, attribution_drift, external_reference_health, reliability_test_gaps) |
| `docs-only-product` | Documentation | No package managers, no version sources, no shell files | 4 (all except shell_correctness, version_alignment, cross_platform, attribution_drift, external_reference_health, reliability_test_gaps) |
| `single-plugin-version` | Skill pack | One independent plugin-manifest version | 4 (version_alignment skipped; all other non-applicable dimensions skipped) |
| `missing-tools-no-origin-main` | Skill pack | No CI, no upstream/remote-default base, shell files, one package version source | 4 (all except version_alignment, ci_efficiency, cross_platform, attribution_drift, external_reference_health, reliability_test_gaps) |
| `dirty-development-tree` | Library (uv) | Dirty working tree, GH Actions, shell files, 2 version sources | 7 (all except cross_platform, attribution_drift, external_reference_health) — the only fixture that activates `reliability_test_gaps` |

## Fixture Structure

Each fixture has:
```json
{
  "name": "fixture-name",
  "profile": {
    "observed": { ... },
    "inferred": { ... }
  },
  "expected": {
    "active_dimensions": [
      { "name": "...", "activated_by": ["observed.xxx"] }
    ],
    "skipped_dimensions": [
      { "name": "...", "skip_reason": "..." }
    ]
  }
}
```

## Validation Contract

The eval contract enforces:
- Profile before dimension checks (ordered_events: profile → dimension_checks → report)
- Every active dimension cites `activated_by` profile paths
- Every skipped dimension has `skip_reason`
- All 10 candidate dimensions accounted for (active + skipped = 10)
- Each active dimension's activation predicate is satisfied by the profile
- Fixture diversity: skill-pack + non-skill repository

## Running Validation

```bash
# Validate eval contract structure
python3 scripts/validate-evals.py

# Self-test
python3 scripts/validate-evals.py --self-test
```

## Adding New Fixtures

1. Add fixture to `evals/cases/repo-health-scan.json` under `fixtures[]`
2. Must include both `profile` (observed/inferred) and `expected` (active/skipped)
3. Must activate at least one dimension not in existing fixtures
4. Run `python3 scripts/validate-evals.py` to validate
5. Update this reference file

## Current Coverage Gaps (per roadmap)

| Gap | Fixture Needed |
|-----|----------------|
| Missing tools | `missing-tools-no-origin-main` ✅ |
| Monorepo | `monorepo-workspace` ✅ |
| Docs product | `docs-only-product` ✅ |
| No origin/main | `missing-tools-no-origin-main` ✅ |
| Dirty tree | `dirty-development-tree` ✅ |

All roadmap §2 fixture diversity gaps addressed in v0.3.0 consolidation.
