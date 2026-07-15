# Security Policy

Report security issues privately through the
[GitHub Security Advisory](https://github.com/CodeSigils/repo-health-and-sync-skill/security/advisories/new)
rather than opening a public issue.

Security concerns in this repository include unsafe instructions in the skill
methodology, supply-chain risks in CI tooling, or references to compromised
external resources. Do not include exploit details in public reports.

Issues that do not involve the GitHub Actions workflow (leaked secrets in CI
logs, workflow injection) can be opened as public GitHub issues. Report
CI-related vulnerabilities through the advisory link above.

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
