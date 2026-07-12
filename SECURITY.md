# Security Policy

## Supported Versions

This repo is a single-SKILL.md methodology skill with CI-only tooling in
`scripts/`. There are no versioned releases — always use the latest commit
from `main`.

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
