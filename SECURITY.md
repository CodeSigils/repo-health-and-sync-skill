# Security Policy

## Supported Versions

This repo is a single-SKILL.md methodology skill with supporting scripts.
There are no versioned releases — always use the latest commit from `main`.

## Reporting a Vulnerability

This project contains no runtime dependencies, no secrets, and no network-facing
service. It ships a single governance skill (`SKILL.md`) with supporting CI
tooling (`verify.sh`, `doc-audit.py`, and `check-commit-trailers.py`). If you
find an issue with the content or CI configuration, please open a public issue
on GitHub.

Do **not** open a public issue if the vulnerability involves the GitHub
Actions workflow (e.g., leaked secrets in CI logs). Report privately to the
repository owner via GitHub's security advisory tool.
