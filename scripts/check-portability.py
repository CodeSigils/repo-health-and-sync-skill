#!/usr/bin/env python3
"""Check for agent-specific references in portable skill files.

A generalized portability gate for agentskills.io-compatible skill repos.
Copy this script into .github/scripts/check-portability.py and add a CI step.

Scans all skills/**/*.md for platform-specific tool names, CLI commands,
config paths, and directory patterns that would silently break non-Hermes
agents (Claude Code, Codex CLI, Gemini CLI, OpenCode, Cursor).

Single-runtime skills are allowed to mention their own platform. Portable
skills can exempt documentation-only references with
'# portability: allow-platform-ref'.

"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = REPO_ROOT / "skills"
CONFIG_PATH = REPO_ROOT / ".repo-health.json"
SINGLE_RUNTIME_COMPAT = {"hermes", "codex", "claude", "gemini", "opencode", "cursor"}

FORBIDDEN_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("Hermes tool name", re.compile(r"\bskill_(?:view|manage)\b", re.IGNORECASE)),
    ("Hermes Python import", re.compile(r"from hermes_tools\b", re.IGNORECASE)),
    ("Hermes config path", re.compile(r"~/\\.hermes(?:/|\b)", re.IGNORECASE)),
    (
        "Hermes CLI command",
        re.compile(
            r"\bhermes\s+(?:skills?|config|tools?|setup|help|doctor|gateway|run|serve|cron)\b",
            re.IGNORECASE,
        ),
    ),
    ("Claude Code agent reference", re.compile(r"\bClaude\(\)", re.IGNORECASE)),
    ("Gemini CLI command", re.compile(r"\bgemini\s+skills?\b", re.IGNORECASE)),
    ("Codex CLI command", re.compile(r"\bcodex\s+run\b", re.IGNORECASE)),
    (
        "Platform-specific path",
        re.compile(r"\.(?:claude|cursor|codex|opencode|gemini)/"),
    ),
)


def repo_allows_platform_refs() -> bool:
    """Return true when the repo explicitly declares platform refs intentional."""
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    portability = data.get("portability", {})
    return isinstance(portability, dict) and portability.get("allow_platform_ref") is True


def frontmatter_value(text: str, key: str) -> str | None:
    """Extract a simple top-level YAML frontmatter value."""
    if not text.startswith("---\n"):
        return None
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None
    for line in parts[1].splitlines():
        match = re.match(rf"^{re.escape(key)}:\s*['\"]?([^'\"\s#]+)", line)
        if match:
            return match.group(1).strip().lower()
    return None


def is_single_runtime_skill(path: Path) -> bool:
    """Return true when this markdown file belongs to a declared single-runtime skill."""
    try:
        rel = path.relative_to(SKILLS_DIR)
    except ValueError:
        return False
    parts = rel.parts
    if not parts:
        return False
    skill_file = SKILLS_DIR / parts[0] / "SKILL.md"
    try:
        skill_text = skill_file.read_text(encoding="utf-8")
    except OSError:
        return False
    compatibility = frontmatter_value(skill_text, "compatibility")
    return compatibility in SINGLE_RUNTIME_COMPAT


def scan_file(path: Path) -> list[tuple[Path, int, str, str]]:
    violations: list[tuple[Path, int, str, str]] = []
    if is_single_runtime_skill(path):
        return violations
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    # File-level exemption: if marker appears in first 3 lines (frontmatter), skip entire file
    file_exempt = any("# portability: allow-platform-ref" in line for line in lines[:3])
    if file_exempt:
        return violations
    for line_no, line in enumerate(lines, start=1):
        # Line-level exemption for documentation-only platform references.
        if "# portability: allow-platform-ref" in line:
            continue
        for label, pattern in FORBIDDEN_PATTERNS:
            if pattern.search(line):
                violations.append((path, line_no, label, line.rstrip()))
    return violations


def main() -> int:
    if repo_allows_platform_refs():
        print("PASS: platform-specific references explicitly allowed by .repo-health.json")
        return 0

    violations: list[tuple[Path, int, str, str]] = []
    for path in sorted(SKILLS_DIR.rglob("*.md")):
        try:
            violations.extend(scan_file(path))
        except OSError as exc:
            print(f"FAIL: could not read {path}: {exc}", file=sys.stderr)
            return 1

    if violations:
        print("FAIL: agent-specific references found in skills/ — will break non-Hermes agents:")
        for path, line_no, label, line in violations:
            print(f"  {path}:{line_no}: {label}: {line}")
        return 1

    print("PASS: no agent-specific references in skills/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
