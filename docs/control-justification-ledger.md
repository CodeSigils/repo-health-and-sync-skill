# Control-justification ledger

> Maintainer-only record. Each recurring control must have a named failure
> mode, evidence, and an explicit cost/coverage decision.

Reviewed: `2026-10-03`
Repository scale: solo maintainer; protected `main`; no mandatory second review.

| Control | Trigger | Failure mode addressed | Evidence | Cost | Decision |
| --- | --- | --- | --- | --- | --- |
| `lint` job | PR, push, schedule, manual | Drift in docs/contracts, unsafe script changes, portability, or trust regressions | `scripts/verify.sh --self-test`, validators, ShellCheck/Ruff; required on `main` | ~10 min timeout, ~12 s actual (run `36846473400`) | **Retain** as the primary merge gate, pinned to the 3.13 floor. Not a matrix and not a reusable-workflow caller: both rename the reported check, and `main` requires the literal context `lint`. |
| `python-range` job | PR, push, schedule, manual | The payload breaks on a release `requires-python` admits but CI never tests | The Python-sensitive validation set runs against 3.14; the 2026-10-03 workflow run passed after removal of the former version-consistency control | ~12 s, in parallel with `lint` | **Retain.** Checking only the floor leaves `>=3.13` half-promised. Add to required contexts once its reported context name is confirmed. |
| `full-verify` job | PR, push, schedule, manual | Tree-level integration drift after the required `lint` gate | Runs `scripts/verify.sh --after-lint`, retaining the tree, stale-reference, and full documentation checks without repeating `lint` checks | ~5 min; serialized after lint | **Retain** because it verifies the remaining aggregate contract while `lint` stays the required status context. |
| `phase-b-gate` job | PR and push to `main` | Whitespace, dirty-tree, empty-range, or non-conventional authored commits | Caught generated merge-subject false failure; now excludes merge commits in `scripts/check-commit-convention.py` | ~3 min | **Retain**, with merge-commit handling documented and tested. |
| `check-expiry` job | Weekly schedule or manual dispatch | Maintainer references silently exceed their review date | Manual run `34025441454` passed on 2026-09-06; no later scheduled result was observed during the 2026-09-08 audit | ~5 min; external state | **Retain**, but keep out of PR merge gates. |
| `verify-urls` job | Weekly schedule or manual dispatch | Evidence URLs become unavailable or redirect unexpectedly | Local verifier run on 2026-09-08 passed 18/18 URLs; prior manual run `34025441454` passed on 2026-09-06 | ~10 min; transient network failures | **Retain**, retry transient failures, keep out of PR merge gates. |
| Local Codex regression | Manual maintainer evaluation | Model no longer follows profile-first, activation, skip, or finding contracts | Runs 13–15 passed on Codex CLI 0.153.2 | ~2–3 min plus model tokens | **Retain as non-blocking**; run after material payload changes. |

## Review rule

Revisit this ledger when a control fails, causes recurring maintenance friction,
or its protected failure mode no longer exists. Do not add a gate merely because
another repository has one; record the failure mode and evidence first.

## Removed controls

| Control | Removed | Reason |
| --- | --- | --- |
| Release `verify` job | 2026-10-01 | Ran three times for `v0.4.0` while the tag was force-moved between attempts; two of the three runs failed at the step whose purpose was idempotence. Its protected failure mode was a tag-integrity concern that protected `main` already covers more reliably. |
| Release `release` job | 2026-10-01 | Only ran after a release cadence that had already stalled, and the published `v0.4.0` predates the payload rename, so the smoke test it was meant to gate did not gate it. |

`main` is now the distribution channel. See [maintaining.md](maintaining.md) for
what replaced the release procedure.
