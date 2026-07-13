#!/usr/bin/env python3
"""Validate the skill's security and trust contract."""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL = Path("skills/repo-health-and-sync-skill/SKILL.md")

FORBIDDEN_ACTIONS = {
    "destructive file removal": re.compile(r"\brm\s+(?:-[^\n]*r[^\n]*f|-[^\n]*f[^\n]*r)\b"),
    "destructive git reset": re.compile(r"\bgit\s+reset\s+--hard\b"),
    "forced git update": re.compile(r"\bgit\s+push\b[^\n]*(?:--force|-f\b)"),
    "approval bypass": re.compile(r"--(?:dangerously-)?bypass|--no-verify\b"),
    "privilege escalation": re.compile(r"\bsudo\b"),
}

SECRET_PATTERNS = {
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "GitHub token": re.compile(r"\b(?:gh[oprsu]_[A-Za-z0-9_]{20,})\b"),
    "OpenAI-style secret": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
}


def read(root: Path, relative: Path | str) -> str:
    return (root / relative).read_text(encoding="utf-8")


def frontmatter_description(text: str) -> str:
    """Return the folded description text from YAML frontmatter."""
    if not text.startswith("---\n"):
        return ""
    frontmatter = text.split("---", 2)[1]
    lines = frontmatter.splitlines()
    description: list[str] = []
    collecting = False
    for line in lines:
        if line.startswith("description:"):
            collecting = True
            continue
        if collecting and line.startswith("  "):
            description.append(line.strip())
        elif collecting:
            break
    return " ".join(description)


def guarded_command(text: str, variable: str, command: str) -> bool:
    """Return whether command appears inside a shell guard for variable."""
    pattern = re.compile(
        rf'if \[ "\$\{{{re.escape(variable)}:-0\}}" = "1" \]; then'
        rf"(?:(?!\nfi\n).)*{re.escape(command)}(?:(?!\nfi\n).)*\nfi\n",
        re.DOTALL,
    )
    return pattern.search(text) is not None


def scan_secrets(root: Path) -> list[str]:
    """Scan fixtures and compatibility reports for credential material."""
    errors: list[str] = []
    paths = sorted((root / "evals").rglob("*"))
    paths += sorted((root / "docs/compatibility-reports").rglob("*"))
    for path in paths:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"{path.relative_to(root)} contains a {label}")
    return errors


def validate_repo(root: Path = REPO_ROOT) -> list[str]:
    """Return violations of the documented trust contract."""
    errors: list[str] = []
    skill = read(root, SKILL)
    description = frontmatter_description(skill)
    security = read(root, "SECURITY.md")
    readme = read(root, "README.md")
    codex_report = read(root, "docs/compatibility-reports/codex.md")

    if "Use when" not in description or "Not for" not in description:
        errors.append("skill trigger description is not positively and negatively bounded")
    if "does not mutate the repository" not in skill:
        errors.append("skill does not declare its read-only runtime boundary")

    for label, pattern in FORBIDDEN_ACTIONS.items():
        if pattern.search(skill):
            errors.append(f"skill contains {label}")

    if not guarded_command(skill, "REPO_HEALTH_VERIFY_RELEASES", "gh release list"):
        errors.append("GitHub release query is not guarded by its network opt-in")
    if "REPO_HEALTH_VERIFY_REFS=1" not in skill:
        errors.append("external reference checks are not explicitly opt-in")
    if "REPO_HEALTH_OUTPUT=jsonl" not in skill:
        errors.append("JSONL output is not explicitly opt-in")

    if not re.search(r"Status: `workflow_verified`", codex_report):
        errors.append("Codex compatibility is not workflow_verified")
    if not re.search(r"codex-cli\s+\d+\.\d+\.\d+", codex_report):
        errors.append("Codex compatibility evidence lacks an exact CLI version")

    if "maintainer-only checks" not in readme or "repo ships only" not in readme:
        errors.append("README does not separate payload from maintainer tooling")
    if "## Skill Trust Checklist" not in security:
        errors.append("SECURITY.md lacks the maintainer trust checklist")

    errors.extend(scan_secrets(root))
    return errors


def run_self_tests() -> int:
    """Exercise frontmatter, guard, action, and secret detection helpers."""
    sample = "---\ndescription: >-\n  Use when auditing. Not for edits.\n---\n"
    assert frontmatter_description(sample) == "Use when auditing. Not for edits."
    guarded = (
        'if [ "${REPO_HEALTH_VERIFY_RELEASES:-0}" = "1" ]; then\n'
        "  gh release list --limit 5\n"
        "fi\n"
    )
    assert guarded_command(guarded, "REPO_HEALTH_VERIFY_RELEASES", "gh release list")
    assert FORBIDDEN_ACTIONS["destructive git reset"].search("git reset --hard HEAD")
    assert SECRET_PATTERNS["private key"].search(
        "-----BEGIN OPENSSH PRIVATE KEY-----"
    )
    print("PASS: check-trust.py self-tests")
    return 0


def main() -> int:
    if len(sys.argv) > 1 and sys.argv[1] == "--self-test":
        return run_self_tests()
    errors = validate_repo()
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("PASS: skill security and trust contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
