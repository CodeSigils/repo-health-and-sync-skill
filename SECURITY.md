# Security Policy

## Supported Versions

This repo is a single-SKILL.md methodology skill with CI-only tooling in
`scripts/`. Security fixes are supported on the latest release and `main`;
older tags do not receive backports.

## Skill Trust Checklist

Maintainers must review this checklist whenever the skill instructions,
fixtures, compatibility evidence, or packaging changes. The enforceable parts
run through `python3 scripts/check-trust.py` in local verification and CI.

- [x] Trigger metadata states both when the skill applies and when it does not.
- [x] Runtime probes are read-only; the skill contains no destructive commands,
  privilege escalation, approval bypasses, or automatic fixes.
- [x] Network access is explicit: release and external-reference queries require
  opt-in environment flags.
- [x] JSONL output is emitted only when `REPO_HEALTH_OUTPUT=jsonl` is set.
- [x] Eval fixtures and recorded compatibility evidence contain no credentials.
- [x] Compatibility claims name the tested agent and exact version.
- [x] The shipped `SKILL.md` payload remains separate from maintainer-only
  scripts, evals, CI, and documentation.

Last reviewed: 2026-07-13 against Codex CLI 0.133.0.

## Reporting a Vulnerability

This project contains no runtime dependencies, no secrets, and no network-facing
service. It ships a single governance skill
(`skills/repo-health-and-sync-skill/SKILL.md`) with no supporting scripts or
reference files — the agent discovers everything at runtime using tools already
on PATH. CI-only tooling lives in `scripts/` and `.github/` and is not shipped
to users.

If you find an issue with the content or CI configuration, please open a public
issue on GitHub.

Do **not** open a public issue if the vulnerability involves the GitHub
Actions workflow (e.g., leaked secrets in CI logs). Report privately to the
repository owner via GitHub's security advisory tool.
