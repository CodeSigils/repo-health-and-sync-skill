"""Shared utilities for repo-health-and-sync-skill scripts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> Any:
    """Read a UTF-8 JSON file and return parsed data."""
    return json.loads(path.read_text(encoding="utf-8"))


def resolve_profile_path(profile: dict[str, Any], dotted_path: str) -> Any:
    """Resolve a dotted evidence path (e.g. 'observed.vcs') in a profile dict."""
    value: Any = profile
    for part in dotted_path.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def validate_dimensions(
    active: list[dict[str, Any]],
    skipped: list[dict[str, Any]],
    expected: set[str],
    profile: dict[str, Any] | None = None,
    prefix: str = "",
    check_skip_status: bool = False,
) -> list[str]:
    """Validate active/skipped dimension lists against an expected set.

    Checks name types, duplicate detection, overlap prevention, activated_by
    evidence resolution, skip_reason presence, and full-set coverage.
    """
    errors: list[str] = []

    active_names: set[str] = set()
    for item in active:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            errors.append(f"{prefix}active dimension is malformed")
            continue
        name = item["name"]
        if name in active_names:
            errors.append(f"{prefix}active dimension {name} is duplicated")
        active_names.add(name)
        evidence = item.get("activated_by")
        if not isinstance(evidence, list) or not evidence:
            errors.append(f"{prefix}active dimension {name} lacks activated_by evidence")
            continue
        if profile is not None:
            for path in evidence:
                if not isinstance(path, str) or not resolve_profile_path(profile, path):
                    errors.append(
                        f"{prefix}active dimension {name} references missing profile evidence: {path}"
                    )

    skipped_names: set[str] = set()
    for item in skipped:
        if not isinstance(item, dict) or not isinstance(item.get("name"), str):
            errors.append(f"{prefix}skipped dimension is malformed")
            continue
        name = item["name"]
        if name in skipped_names:
            errors.append(f"{prefix}skipped dimension {name} is duplicated")
        skipped_names.add(name)
        if check_skip_status and item.get("status") != "SKIP":
            errors.append(f"{prefix}skipped dimension {name} is not marked SKIP")
        if (
            not isinstance(item.get("skip_reason"), str)
            or not item["skip_reason"].strip()
        ):
            errors.append(f"{prefix}skipped dimension {name} lacks a reason")

    overlap = active_names & skipped_names
    if overlap:
        errors.append(
            f"{prefix}dimensions cannot be active and skipped: {sorted(overlap)}"
        )
    accounted_for = active_names | skipped_names
    if accounted_for != expected:
        errors.append(
            f"{prefix}dimension accounting mismatch: "
            f"missing={sorted(expected - accounted_for)}, "
            f"unknown={sorted(accounted_for - expected)}"
        )
    return errors
