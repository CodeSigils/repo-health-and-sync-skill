# Codex Model Regression

Status: non-blocking maintainer evaluation implemented against Codex CLI
0.133.0. Later versions require their own recorded run before they become a
compatibility claim.

Local status: `verified_once`. Hosted workflow status: `pending_first_run`.

This harness complements `evals/cases/repo-health-scan.json`. The existing JSON
contract remains the fast deterministic CI gate; the model regression checks
whether an actual Codex run follows that contract on an isolated repository.

## Scenarios

The runner creates a temporary Python library with `uv` metadata, GitHub
Actions, a repository-local copy of the skill, a narrow parser defect, and one
untracked release scratch file.

It executes two read-only scenarios:

1. A release audit that should select `repo-health-scan`, emit the profile before
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

One pass is not a reliability baseline. Record repeated hosted and local runs
before using this workflow as a required check or expanding the profile
contract.

## GitHub Actions

`.github/workflows/codex-regression.yml` runs only by trusted manual dispatch or
the weekly schedule. It is intentionally absent from push and pull-request
triggers, so model availability, cost, and nondeterminism cannot block ordinary
changes.

Configure an `OPENAI_API_KEY` repository secret before dispatching the workflow.
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
until repeated scheduled runs establish an acceptable pass rate, runtime, and
cost. Investigate failures from the captured artifacts before changing the
skill or grader.

Official Codex references, accessed 2026-07-13:

- https://developers.openai.com/codex/noninteractive
- https://developers.openai.com/codex/github-action
