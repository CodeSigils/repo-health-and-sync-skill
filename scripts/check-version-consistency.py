"""Check local versions against the latest git tag and GitHub release.

The tag and the GitHub release are frozen historical markers, not a moving
target a commit is expected to track; see docs/maintaining.md.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from _common import ROOT, read_json

LOCAL_VERSION_SOURCES = {
    "SKILL.md": ROOT / "skills/repo-health-scan/SKILL.md",
    "plugin.json": ROOT / ".codex-plugin/plugin.json",
    "CITATION.cff": ROOT / "CITATION.cff",
}


@dataclass(frozen=True)
class ReleaseQuery:
    """Result of querying the latest GitHub release."""

    status: str
    tag: str | None = None
    detail: str | None = None


def normalize_version(version: str) -> str:
    """Normalize a release version for comparison."""
    return version.removeprefix("v")


def read_skill_version(path: Path) -> str | None:
    """Extract metadata.version from SKILL.md frontmatter."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None
    frontmatter = content.split("---", 2)
    if len(frontmatter) < 3:
        return None
    match = re.search(r'(?m)^\s+version:\s*["\']([^"\']+)["\']\s*$', frontmatter[1])
    return match.group(1) if match else None


def read_plugin_version(path: Path) -> str | None:
    """Extract version from the Codex plugin manifest."""
    try:
        data = read_json(path)
    except (OSError, json.JSONDecodeError):
        return None
    version = data.get("version")
    return version if isinstance(version, str) and version else None


def read_citation_version(path: Path) -> str | None:
    """Extract the top-level version from CITATION.cff."""
    try:
        content = path.read_text(encoding="utf-8")
    except OSError:
        return None
    match = re.search(r'(?m)^version:\s*["\']?([^"\'\s#]+)', content)
    return match.group(1) if match else None


def get_local_versions() -> dict[str, str | None]:
    """Read every version-bearing local release file."""
    return {
        "SKILL.md": read_skill_version(LOCAL_VERSION_SOURCES["SKILL.md"]),
        "plugin.json": read_plugin_version(LOCAL_VERSION_SOURCES["plugin.json"]),
        "CITATION.cff": read_citation_version(LOCAL_VERSION_SOURCES["CITATION.cff"]),
    }


def get_latest_tag() -> tuple[str | None, str | None]:
    """Return the latest v-prefixed tag and an optional query error."""
    try:
        result = subprocess.run(
            ["git", "tag", "--list", "v*", "--sort=-version:refname"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return None, str(exc)
    if result.returncode != 0:
        return None, result.stderr.strip() or f"git exited {result.returncode}"
    tags = result.stdout.splitlines()
    return (tags[0], None) if tags else (None, None)


def get_latest_release() -> ReleaseQuery:
    """Distinguish a release, no releases, and a failed GitHub API query."""
    try:
        result = subprocess.run(
            ["gh", "release", "list", "--limit", "1", "--json", "tagName"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        return ReleaseQuery("error", detail=str(exc))
    if result.returncode != 0:
        detail = result.stderr.strip() or f"gh exited {result.returncode}"
        return ReleaseQuery("error", detail=detail)
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        return ReleaseQuery("error", detail=f"invalid gh JSON: {exc}")
    if not data:
        return ReleaseQuery("none")
    try:
        tag = data[0]["tagName"]
    except (KeyError, TypeError, IndexError):
        return ReleaseQuery("error", detail="gh response has no tagName")
    if not isinstance(tag, str) or not tag:
        return ReleaseQuery("error", detail="gh response has an invalid tagName")
    return ReleaseQuery("found", tag=tag)


def _drift_error(sources: dict[str, str]) -> str:
    rendered = ", ".join(f"{source}={v}" for source, v in sources.items())
    return f"Version drift: {rendered}"


def _record_tag_state(
    errors: list[str],
    latest_tag: str | None,
    tag_error: str | None,
) -> str | None:
    """Record tag status; return the normalized tag version or None."""
    if tag_error:
        errors.append(f"Could not query git tags: {tag_error}")
        return None
    if latest_tag:
        return normalize_version(latest_tag)
    errors.append("No v-prefixed git tags found")
    return None


def _record_release_state(
    errors: list[str],
    notes: list[str],
    release: ReleaseQuery,
    require_github_release_query: bool,
) -> str | None:
    """Record release-status notes/errors; return the normalized version or None."""
    if release.status == "found" and release.tag:
        return normalize_version(release.tag)
    if release.status == "none":
        notes.append("No GitHub releases found")
    elif release.status == "error":
        detail = release.detail or "unknown error"
        message = f"GitHub release query failed: {detail}"
        if require_github_release_query:
            errors.append(message)
        else:
            notes.append(f"SKIP: {message}")
    else:
        errors.append(f"Unknown GitHub release query status: {release.status}")
    return None


def validate_versions(
    local_versions: Mapping[str, str | None],
    latest_tag: str | None,
    tag_error: str | None,
    release: ReleaseQuery,
    require_github_release_query: bool,
) -> tuple[list[str], list[str]]:
    """Validate release state and return errors plus informational notes."""
    errors: list[str] = []
    notes: list[str] = []
    locals_normalized: dict[str, str] = {}

    for source in LOCAL_VERSION_SOURCES:
        version = local_versions.get(source)
        if not version:
            errors.append(f"Could not extract version from {source}")
        else:
            locals_normalized[source] = normalize_version(version)

    comparable = dict(locals_normalized)
    tag_version = _record_tag_state(errors, latest_tag, tag_error)
    if tag_version:
        comparable["latest tag"] = tag_version
    release_version = _record_release_state(
        errors, notes, release, require_github_release_query
    )
    if release_version:
        comparable["latest GitHub release"] = release_version

    if comparable and len(set(comparable.values())) > 1:
        errors.append(_drift_error(comparable))
    return errors, notes


def run_self_tests() -> int:
    """Cover aligned, drifted, release-free, and failed-query states."""
    aligned = {source: "0.2.0" for source in LOCAL_VERSION_SOURCES}

    errors, notes = validate_versions(
        aligned, "v0.2.0", None, ReleaseQuery("found", tag="v0.2.0"), True
    )
    assert errors == [] and notes == []

    drifted = {**aligned, "plugin.json": "0.3.0"}
    errors, _ = validate_versions(
        drifted, "v0.2.0", None, ReleaseQuery("found", tag="v0.2.0"), True
    )
    assert any(error.startswith("Version drift:") for error in errors)

    errors, notes = validate_versions(
        aligned, "v0.2.0", None, ReleaseQuery("none"), True
    )
    assert errors == [] and notes == ["No GitHub releases found"]

    query_error = ReleaseQuery("error", detail="authentication required")
    errors, notes = validate_versions(aligned, "v0.2.0", None, query_error, False)
    assert errors == [] and notes == [
        "SKIP: GitHub release query failed: authentication required"
    ]
    errors, _ = validate_versions(aligned, "v0.2.0", None, query_error, True)
    assert errors == ["GitHub release query failed: authentication required"]

    print("PASS: check-version-consistency.py self-tests")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--require-github-release-query",
        action="store_true",
        help="Fail when the GitHub release API cannot be queried",
    )
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_tests()

    local_versions = get_local_versions()
    latest_tag, tag_error = get_latest_tag()
    release = get_latest_release()
    for source, version in local_versions.items():
        print(f"{source} version: {version or 'unreadable'}")
    print(f"Latest tag: {latest_tag or 'none'}")
    if release.status == "found":
        print(f"Latest GitHub release: {release.tag}")

    errors, notes = validate_versions(
        local_versions,
        latest_tag,
        tag_error,
        release,
        args.require_github_release_query,
    )
    for note in notes:
        print(note)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    if release.status == "error":
        print("OK: local version sources are consistent; GitHub release unchecked")
    else:
        print("OK: all available version sources are consistent")
    return 0


if __name__ == "__main__":
    sys.exit(main())
