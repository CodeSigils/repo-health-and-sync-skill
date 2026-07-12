#!/usr/bin/env python3
"""Check version consistency across SKILL.md frontmatter, GitHub releases, and tags."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


def get_skill_version() -> str | None:
    """Extract version from SKILL.md frontmatter."""
    skill_path = Path("skills/repo-health-and-sync-skill/SKILL.md")
    try:
        content = skill_path.read_text(encoding="utf-8")
    except OSError:
        return None

    # Extract frontmatter version
    match = re.search(r'version:\s*"([^"]+)"', content)
    if match:
        return match.group(1)
    return None


def get_latest_tag() -> str | None:
    """Get the latest git tag (v*)."""
    try:
        result = subprocess.run(
            ["git", "tag", "--list", "v*", "--sort=-version:refname"],
            capture_output=True,
            text=True,
            check=True,
        )
        tags = result.stdout.strip().split()
        return tags[0] if tags else None
    except subprocess.CalledProcessError:
        return None


def get_latest_release() -> str | None:
    """Get the latest GitHub release tag."""
    try:
        result = subprocess.run(
            ["gh", "release", "list", "--limit", "1", "--json", "tagName"],
            capture_output=True,
            text=True,
            check=True,
        )
        data = json.loads(result.stdout)
        if data:
            return data[0]["tagName"]
    except (subprocess.CalledProcessError, json.JSONDecodeError, KeyError, IndexError):
        pass
    return None


def normalize_version(version: str) -> str:
    """Normalize version string for comparison (strip leading 'v')."""
    return version.lstrip("v")


def main() -> int:
    skill_version = get_skill_version()
    latest_tag = get_latest_tag()
    latest_release = get_latest_release()

    errors = []

    if not skill_version:
        errors.append("Could not extract version from SKILL.md frontmatter")
    else:
        print(f"SKILL.md version: {skill_version}")

    if latest_tag:
        print(f"Latest tag: {latest_tag}")
        if skill_version and normalize_version(skill_version) != normalize_version(latest_tag):
            errors.append(
                f"SKILL.md version ({skill_version}) != latest tag ({latest_tag})"
            )
    else:
        print("No tags found")

    if latest_release:
        print(f"Latest GitHub release: {latest_release}")
        if skill_version and normalize_version(skill_version) != normalize_version(latest_release):
            errors.append(
                f"SKILL.md version ({skill_version}) != latest release ({latest_release})"
            )
    else:
        print("No GitHub releases found")

    # Also check tag vs release consistency
    if latest_tag and latest_release and normalize_version(latest_tag) != normalize_version(latest_release):
        errors.append(f"Latest tag ({latest_tag}) != latest release ({latest_release})")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("OK: All version sources are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())