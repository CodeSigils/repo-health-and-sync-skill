# portability: allow-platform-ref
---
title: Proportionate Anti-Drift
description: Principles for keeping speculative checks from accumulating maintenance debt.
status: reference
---

# Proportionate Anti-Drift

## Principles

1. **Every check must trace to an observed failure mode.** If you haven't
   seen this failure in any of your projects, you don't need a check for it.
   Add checks reactively, not preemptively.

2. **If a check fires and you're surprised, consider disabling it.**
   A check that produces noise you ignore trains you to ignore all checks.
   Silence means delete or disable, not patch around.

3. **Speculative checks accumulate debt faster than real ones.**
   Each unused check is code to maintain, document, and troubleshoot.
   The cost is small per check but compound across 10+ checks.

4. **One-in, one-out for new checks.** Before adding a new check, review
   existing ones. Remove or demote any that haven't fired in 6 months.

## When to skip a check

| Signal                                     | Action                          |
| :----------------------------------------- | :------------------------------ |
| Check exists but hasn't fired in 6+ months | Downgrade to INFO or remove     |
| Check fires but you fix it by ignoring it  | Remove check, fix root cause    |
| Check requires manual inspection every run | Make it a DRY RUN / report-only |
| Check is aspirational (should fix one day) | Delete it until ready to act    |
