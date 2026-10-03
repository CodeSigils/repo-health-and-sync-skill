# Codex Model Regression

Status: non-blocking maintainer evaluation implemented. The last certified
baseline is Codex CLI 0.153.2 (runs 13–16). The `reliability_test_gaps` payload
is **not certified**: it is unobserved, not failing. Dropping the
`tag_release_integrity` dimension is a material payload change, so runs 13-16
describe an earlier contract and the baseline for the current contract is
**unresolved**. Earlier versions remain historical evidence, and later versions
require their own recorded run before becoming a claim.

Local status: `twenty_two_runs_recorded_current_payload_uncertified_pending_run`.
Hosted workflow status: `pending_first_run`.

Local runs through an authenticated Codex CLI are the primary reliability path.
The hosted workflow is optional infrastructure for maintainers with API-key
billing; its status does not block local evaluation or profile scaling.

This harness complements `evals/cases/repo-health-scan.json`. The existing JSON
contract remains the fast deterministic CI gate; the model regression checks
whether an actual Codex run follows that contract on an isolated repository.

## Scenarios

The runner creates a temporary Python library with `uv` metadata, GitHub
Actions, a repository-local copy of the skill, a narrow parser defect, and one
untracked scratch file.

It executes two read-only scenarios:

1. A repository-health audit that should select `repo-health-scan`, emit the profile before
   dimension checks, account for every dimension, and report the seeded health
   defect with harm and remediation.
2. A narrow parser task that should not activate the repository-health skill.

The deterministic grader checks selection, event ordering, profile-backed
`activated_by` paths, complete active/skip accounting, skip status, finding
quality, severity ordering, and negative-trigger behavior.

## Local Run

Requirements:

- Authenticated `codex` CLI on `PATH`.
- Git and Python 3.11 or later.
- Network access for the Codex model request; the evaluated agent itself runs
  with a read-only sandbox and no network opt-in variables.

Run:

```bash
python3 scripts/run-codex-regression.py
```

The command prints the artifact directory. Each run writes:

- `positive-transcript.jsonl` and `negative-transcript.jsonl`: raw `codex exec
  --json` event streams.
- `positive-result.json`: schema-constrained profile, dimension plan, and report.
- `negative-result.txt`: final response to the narrow implementation prompt.
- `positive-stderr.log` and `negative-stderr.log`: CLI diagnostics.
- `grade.json`: deterministic pass/fail details.
- `run-summary.json`: run timing, CLI/model identity when available,
  per-scenario status and failure phase, last-event metadata, aggregate usage,
  grade status, and artifact paths. It is written for both passing and failed
  runs.

The summary is runner-only observability. It does not change the prompts,
fixture, Codex command, read-only sandbox, timeout, output schema, or grader.
Scenario failure phases distinguish startup, tool execution, model inference,
and output capture; the run-level summary separately identifies fixture setup
and grading failures. Incomplete runs therefore do not require manual transcript
reconstruction.

Generated fixtures and artifacts are ignored by git. Use `--fixture-dir` or
`--output-dir` when a stable diagnostic location is needed.

## First Recorded Run

The first complete local run passed on 2026-07-13 with Codex CLI 0.133.0:

- Positive transcript: 43 JSONL events. The skill was selected, the populated
  profile preceded the populated dimension plan, all ten dimensions were
  active or skipped, and the dirty-tree finding named `scratch.txt` with harm
  and remediation.
- Negative transcript: 21 JSONL events. The response stayed on the parser bug
  and did not read or name the repository-health skill.
- Combined reported usage: 153,545 input tokens, including 112,384 cached input
  tokens; 5,141 output tokens; and 774 reasoning output tokens.
- The deterministic grade passed with no errors.

The negative run could not execute pytest because the read-only sandbox had no
usable temporary directory. That limitation did not affect the trigger test or
the model's identification of the narrow parser fix. The local CLI also logged
a non-fatal stale model-cache warning; both turns still completed normally.

One pass is not a reliability baseline. Record at least five runs before
expanding the profile contract. Local runs are sufficient; hosted runs may
contribute when API-key billing is available.

## Reliability Run Log

Record each completed run here. Preserve failed runs and notable deviations so
the baseline reflects model reliability rather than only successful attempts.
Use `not recorded` for historical data that cannot be recovered.

|  Run | Date       | Execution | CLI     | Model        | Grade                | Duration     | Token usage                                                   | Notes                                                                                                                                                                    |
| ---: | ---------- | --------- | ------- | ------------ | -------------------- | ------------ | ------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
|    1 | 2026-07-13 | Local     | 0.133.0 | not recorded | Pass                 | not recorded | 153,545 input (112,384 cached); 5,141 output; 774 reasoning   | Negative-run pytest could not use a temporary directory; non-fatal stale model-cache warning.                                                                            |
|    2 | 2026-07-14 | Local     | 0.133.0 | not emitted  | Pass                 | 2m 05s       | 136,050 input (106,880 cached); 5,535 output; 1,233 reasoning | Positive and negative scenarios passed; non-fatal stale model-cache warning.                                                                                             |
|    3 | 2026-07-14 | Local     | 0.133.0 | not emitted  | Timeout              | 15m 00s      | unavailable; no `turn.completed` event                        | Positive scenario selected the skill and began discovery, then stopped emitting events; negative scenario did not run. Same-session evidence.                            |
|    4 | 2026-07-16 | Local     | 0.133.0 | not emitted  | Fail                 | 3m 28s       | 147,894 input (118,144 cached); 6,279 output; 1,512 reasoning | Positive and negative scenarios completed; deterministic grading exposed that the standalone JSONL row could be mistaken for a health dimension.                         |
|    5 | 2026-07-16 | Local     | 0.133.0 | not emitted  | Pass                 | 2m 30s       | 142,893 input (101,248 cached); 5,577 output; 1,330 reasoning | Same-session rerun after clarifying that structured output is an output mode, not a dimension; positive and negative scenarios passed.                                   |
|    6 | 2026-07-16 | Local     | 0.133.0 | not emitted  | Pass                 | 2m 08s       | 141,350 input (120,704 cached); 5,410 output; 813 reasoning   | Final recommendation pass: bounded upstream/default-base resolution, heuristic scanner guidance, and positive/negative scenarios passed.                                 |
|    7 | 2026-07-16 | Local     | 0.133.0 | not emitted  | Pass                 | 2m 11s       | 139,874 input (101,760 cached); 4,973 output; 446 reasoning   | Exact final payload after adding quiet/redacted native-scanner output handling; positive and negative scenarios passed.                                                  |
|    8 | 2026-07-16 | Local     | 0.133.0 | not emitted  | Fail                 | 2m 34s       | 160,054 input (117,376 cached); 6,249 output; 748 reasoning   | Consolidated payload completed both scenarios; deterministic grading found that the profile and dimension plan were emitted in the same message.                         |
|    9 | 2026-07-16 | Local     | 0.133.0 | not emitted  | Pass                 | 2m 32s       | 117,709 input (79,360 cached); 6,936 output; 1,155 reasoning  | Exact consolidated payload passed after requiring the profile to be emitted in its own message before dimension planning.                                                |
|   10 | 2026-08-24 | Local     | 0.149.0 | not recorded | Pass                 | 2m 08s       | 206,184 input (146,176 cached); 5,537 output; 783 reasoning   | Revised profile/evidence contract passed positive and negative scenarios after making extended profile fields conditional and canonical activation paths explicit.       |
|   11 | 2026-09-06 | Local     | 0.153.2 | not recorded | Fail → regraded Pass | 2m 16s       | 232,095 input (197,632 cached); 3,092 output; 85 reasoning    | Initial run after payload trim exposed an invented custom dimension and bundled profile/plan; transcript grader was then corrected for separate human-readable messages. |
|   12 | 2026-09-06 | Local     | 0.153.2 | not recorded | Fail → regraded Pass | 2m 23s       | 232,265 input (201,472 cached); 2,975 output; 55 reasoning    | Same behavior under the pre-fix grader; no model or tool failure. Regraded successfully after the transcript compatibility fix.                                          |
|   13 | 2026-09-06 | Local     | 0.153.2 | not recorded | Pass                 | 2m 06s       | 231,904 input (201,728 cached); 2,850 output; 11 reasoning    | First clean run under the corrected transcript grader; profile and plan messages were separately observed.                                                               |
|   14 | 2026-09-06 | Local     | 0.153.2 | not recorded | Pass                 | 2m 18s       | 231,042 input (197,376 cached); 2,969 output; 86 reasoning    | Second clean time-separated run under the corrected grader; positive and negative scenarios passed.                                                                      |
|   15 | 2026-09-06 | Local     | 0.153.2 | not recorded | Pass                 | 2m 30s       | 255,211 input (221,440 cached); 2,955 output; 68 reasoning    | Third clean time-separated run under the corrected grader; positive and negative scenarios passed.                                                                      |
|   16 | 2026-09-06 | Local     | 0.153.2 | not recorded | Pass                 | 2m 06s       | 207,118 input (173,824 cached); 2,677 output; 23 reasoning    | Focused semantic trigger review: positive repository-health audit activated the skill; negative narrow task did not; transcript grader passed.                              |
| 17   | 2026-09-27 | Local     | 0.157.1 | not emitted  | Fail                 | 2m 14s       | 165,694 input (113,536 cached); 2,755 output; 38 reasoning    | Both scenarios completed; grading rejected the unknown dimension `reliability_test_gaps` because the grader's dimension set predated it.                                 |
| 18   | 2026-09-27 | Local     | 0.157.1 | not emitted  | Fail                 | 2m 15s       | 188,594 input (159,488 cached); 2,681 output; 30 reasoning    | Same unknown-dimension grading failure; the model emitted the new dimension in both attempts.                                                                            |
| 19   | 2026-09-27 | Local     | 0.157.1 | not emitted  | Fail                 | 2m 15s       | 190,773 input (162,304 cached); 2,586 output; 52 reasoning    | Both scenarios completed; grading found `profile.observed` missing `reliability_audit_requested` because the result schema stripped the field from model output.         |
| 20   | 2026-09-27 | Local     | 0.157.1 | not emitted  | Fail                 | 1m 56s       | 213,489 input (184,320 cached); 2,819 output; 86 reasoning    | Positive completed with the correct flag; the negative scenario was rejected at model inference by an external account usage limit.                                      |
| 21   | 2026-09-28 | Local     | 0.157.1 | not emitted  | Pass                 | 2m 11s       | 162,979 input (134,912 cached); 2,749 output; 43 reasoning    | Clean pass of the reliability payload at commit `2c7deef`; the model activated `reliability_test_gaps` and found the planted `split("=")` defect.                        |
| 22   | 2026-09-28 | Local     | 0.157.1 | not emitted  | Fail                 | 0m 04s       | not recorded                                                  | Positive scenario rejected at model inference by an external account usage limit; the negative scenario did not start. No model output.                                  |

Runs 1-3 predate the `run-summary.json` observability added in `f21214c`.
Their committed log entries remain the authoritative historical evidence; do
not manufacture or backfill generated summaries. Structured summaries begin
with the first subsequent run, including when that run fails or times out.

The initial evidence checkpoint requires five recorded runs with CLI version,
pass or failure, duration, and token usage. Record the model when the CLI emits
it or the run selects one explicitly; do not infer a default model from the CLI
version. A stable reliability baseline additionally requires repeated runs of
the same payload. Review the pass rate and deviations before changing the
harness or expanding `SKILL.md`.

Current evidence: twenty-two runs recorded, with twelve plain passes, two
failures regraded to passes, five deterministic grading failures, one timeout,
and two model-inference failures. Runs 4 and 8 found real instruction
ambiguities; runs 5, 9, and 10 passed after targeted corrections. Runs 13–16 are
four clean passes of the unchanged hardened payload on Codex CLI 0.153.2; run 16
additionally served as the focused semantic trigger review. The historical
payload changes mean the complete log remains diagnostic, while runs 13–16
provide the last repeated-baseline evidence.

**No run covers the current payload.** Runs 17–22 exercise the
`reliability_test_gaps` work, and only run 21 was a clean model observation. The
five failures are not model-reliability signal: runs 17–19 were deterministic
grading failures caused by harness and schema defects that were found and fixed
during development, and runs 20 and 22 were rejected at model inference by an
external account usage limit. Run 21 passed, but it executed against the payload
at commit `2c7deef`; the two commits after it changed `SKILL.md` — removing a
conflicting activation predicate, adding the discovery probe, and amending the
frontmatter trigger. The current payload therefore has **zero** recorded runs.
Treat it as unobserved rather than unreliable: it has neither passing nor failing
evidence, and one recorded run of a materially changed payload would not satisfy
the repeated-run requirement above in any case. The certification can be
re-established once the account quota allows a run against the current payload.

Excluded infrastructure attempt: on 2026-07-14, a run inside the restricted
network sandbox timed out after 900 seconds immediately after `turn.started`,
without receiving model content. It is not counted as a model-reliability run;
the successful run above used the authenticated CLI with network access.

Excluded interrupted attempt: `20260927T171259Z` produced both scenario
transcripts and a positive result but no `run-summary.json` and no `grade.json`,
so it has no recorded CLI version, grade, duration, or token usage. It is not
counted; the surrounding runs 17–22 record what was observed. Seven artifacts
therefore exist under `artifacts/codex-regression/` for runs 17–22.

## Optional GitHub Actions

`.github/workflows/codex-regression.yml` runs only by trusted manual dispatch or
the weekly schedule. It is intentionally absent from push and pull-request
triggers, so model availability, cost, and nondeterminism cannot block ordinary
changes.

This path requires API-key billing; a ChatGPT subscription used to authenticate
the local Codex CLI does not provide the workflow secret. Configure an
`OPENAI_API_KEY` repository secret before dispatching the workflow.
The workflow uses the official `openai/codex-action` with its read-only safety
strategy instead of exposing the key to repository-controlled shell steps. It
uploads the two final responses and deterministic grade for 14 days. Detailed
progress remains in the Action log; local runs are the source for raw JSONL
transcripts.

The hosted workflow is implemented but has not yet been dispatched; the
repository currently has no configured secrets. Do not mark it verified until
the secret is configured and its uploaded grade artifact passes. After that
manual baseline, set the repository variable `CODEX_REGRESSION_ENABLED=true` to
enable weekly runs. Scheduled events skip the job while the variable is absent
or false, avoiding predictable failures before credentials are provisioned.

## Reliability Boundary

A single pass is evidence for that model, CLI, prompt, and fixture execution;
it is not proof that every future run will pass. Keep this workflow non-blocking
until at least five recorded local or hosted runs establish an acceptable pass
rate, runtime, and usage. Investigate failures from the captured artifacts
before changing the skill or grader.

Official Codex references, accessed 2026-07-13:

- https://developers.openai.com/codex/noninteractive
- https://developers.openai.com/codex/github-action
