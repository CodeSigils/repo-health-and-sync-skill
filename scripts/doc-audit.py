#!/usr/bin/env python3
"""doc-audit.py — Manifest-driven documentation completeness checker.

Reads a JSON manifest declaring required patterns in documentation files
and checks each file against its requirements. Exit 0 if all pass, non-zero
with failure details otherwise.

Usage:
    python3 scripts/doc-audit.py               # default: docs/doc-standards.json
    python3 scripts/doc-audit.py --self-test   # verify manifest + self-integrity
"""

import json
import re
import sys
from pathlib import Path


def load_manifest(manifest_path):
    """Load and return the JSON manifest as a dict."""
    with open(manifest_path, encoding="utf-8") as f:
        return json.load(f)


def check_regex(filepath, pattern):
    """Return True if *pattern* (as regex) matches anywhere in *filepath*."""
    if not filepath.exists():
        return False
    content = filepath.read_text(encoding="utf-8")
    return bool(re.search(pattern, content))


def check_contains_all(filepath, items):
    """Return True if all *items* appear as literal substrings in *filepath*."""
    if not filepath.exists():
        return False
    content = filepath.read_text(encoding="utf-8")
    return all(item in content for item in items)


def run_checks(manifest_path, repo_root):
    """Run all checks defined in *manifest_path* against *repo_root* files.

    Returns (passed: int, failed: int).
    """
    manifest = load_manifest(manifest_path)

    passed = 0
    failed = 0

    for filename, checks in manifest.items():
        filepath = repo_root / filename
        for check in checks:
            cid = check["id"]
            desc = check.get("description", cid)
            ctype = check.get("type", "regex")

            if ctype == "regex":
                ok = check_regex(filepath, check["pattern"])
            elif ctype == "contains-all":
                ok = check_contains_all(filepath, check["items"])
            else:
                print(f"  FAIL  Doc: {desc} ({cid}) — unknown type '{ctype}'")
                failed += 1
                continue

            if ok:
                print(f"  PASS  Doc: {desc}")
                passed += 1
            else:
                print(f"  FAIL  Doc: {desc} ({cid})")
                failed += 1

    return passed, failed


def self_test():
    """Validate manifest schema and self-integrity. Exit 0 on success."""
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent
    manifest_path = repo_root / "docs" / "doc-standards.json"

    if not manifest_path.exists():
        print(f"  FAIL  Self-test: manifest not found at {manifest_path}")
        return 1

    manifest = load_manifest(manifest_path)

    if not isinstance(manifest, dict):
        print("  FAIL  Self-test: manifest must be a JSON object")
        return 1

    for filename, checks in manifest.items():
        if not isinstance(checks, list):
            print(f"  FAIL  Self-test: checks for '{filename}' must be a list")
            return 1
        for check in checks:
            if "id" not in check or "type" not in check:
                print(f"  FAIL  Self-test: check in '{filename}' missing 'id' or 'type'")
                return 1
            if check["type"] == "regex":
                if "pattern" not in check:
                    print(f"  FAIL  Self-test: regex check '{check['id']}' missing 'pattern'")
                    return 1
                try:
                    re.compile(check["pattern"])
                except re.error as e:
                    print(f"  FAIL  Self-test: regex check '{check['id']}' invalid: {e}")
                    return 1
            elif check["type"] == "contains-all":
                if "items" not in check or not isinstance(check["items"], list):
                    print(f"  FAIL  Self-test: contains-all check '{check['id']}' missing 'items' list")
                    return 1

    print("  PASS  Self-test: doc-audit.py manifest valid")
    return 0


def main():
    if "--self-test" in sys.argv:
        sys.exit(self_test())

    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent                     # scripts/ is one level deep
    manifest_path = repo_root / "docs" / "doc-standards.json"

    if not manifest_path.exists():
        print(f"  FAIL  Manifest not found: {manifest_path}")
        sys.exit(1)

    passed, failed = run_checks(manifest_path, repo_root)
    print(f"  ({passed}/{passed + failed} doc checks pass)")
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
