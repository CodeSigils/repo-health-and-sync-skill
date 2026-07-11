#!/usr/bin/env python3
"""
Shared commit-trailer checker: used by both local commit-msg hooks and CI.

Detects *-by: attribution trailers (Co-authored-by:, Signed-off-by:,
Helped-by:, Reviewed-by:, etc.) in commit messages using a generic pattern.

Bypass via ALLOW_ATTRIBUTION_TRAILERS=1 environment variable.
Self-test mode via --self-test for CI-verifiable integrity.

Exit codes:
  0 — no violations (or bypass enabled)
  1 — violations found
  2 — internal error (file not found, etc.)
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

TRAILER_PATTERN = re.compile(
    r"^[A-Za-z][A-Za-z0-9-]*:[ \t]*\S[^\r\n]*$",
    re.MULTILINE | re.IGNORECASE,
)

# Trailers that are ALWAYS allowed (standard git trailers, not suspicious attributions)
ALLOWED_TRAILERS = {
    "fixes",
    "closes",
    "resolves",
    "refs",
    "see-also",
    "related",
    "breaking-change",
    "deprecated",
    "note",
    "issue",
    "pull-request",
    "merge",
    "see",
    "based-on",
    "link",
    # Legitimate open-source attribution trailers
    "signed-off-by",
    "reviewed-by",
    "tested-by",
    "suggested-by",
}


def find_violations(message: str) -> list[str]:
    """Return list of unauthorized *-by: trailer lines found in message."""
    all_trailers = TRAILER_PATTERN.findall(message)
    violations = []
    for trailer in all_trailers:
        key = trailer.split(":", 1)[0].strip().lower()
        # Only flag *-by: patterns (anything-by:)
        if not key.endswith("-by"):
            continue
        # *-by: trailers are violations unless explicitly allowed
        if key in ALLOWED_TRAILERS:
            continue
        violations.append(trailer)
    return violations


def is_bypass() -> bool:
    return os.environ.get("ALLOW_ATTRIBUTION_TRAILERS", "").lower() in {"1", "true", "yes"}


def do_self_test() -> int:
    """Run internal unit tests. Returns 0 on pass, 1 on fail."""
    tests = [
        # (label, message, expected_violation_count)
        ("co-authored-by basic", "Some commit\n\nCo-authored-by: User <user@x.com>\n", 1),
        ("signed-off-by basic", "Commit\n\nSigned-off-by: User <user@x.com>\n", 0),
        ("helped-by", "Commit\n\nHelped-by: User <user@x.com>\n", 1),
        ("reviewed-by", "Commit\n\nReviewed-by: User <user@x.com>\n", 0),
        ("tested-by", "Commit\n\nTested-by: User <user@x.com>\n", 0),
        ("suggested-by", "Commit\n\nSuggested-by: User <user@x.com>\n", 0),
        ("no violation", "feat: add widget\n\nImplements the widget.\n", 0),
        ("allowed trailer ignored", "Commit\n\nFixes: #42\n", 0),
        ("closes ignored", "Commit\n\nCloses: #100\n", 0),
        ("empty message", "", 0),
        ("multiple violations", "First\n\nCo-authored-by: A <a@x>\nCustom-by: B <b@x>\n", 2),
        ("bypass does not apply here", "Co-authored-by: X <x@x>\n", 1),
    ]
    failures = 0
    for label, msg, expected in tests:
        result = find_violations(msg)
        if len(result) != expected:
            print(f"  FAIL  {label}: expected {expected} violations, got {len(result)}: {result}")
            failures += 1
        else:
            print(f"  PASS  {label}")
    if failures:
        print(f"\n--- Self-test: {failures} failure(s) ---")
    else:
        print(f"\n--- Self-test: all {len(tests)} pass ---")
    return 1 if failures else 0


def check_file(path: str) -> int:
    """Check a commit message file for violations. Returns exit code."""
    path_obj = Path(path)
    if not path_obj.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 2
    with open(path_obj, encoding="utf-8") as f:
        message = f.read()
    return check_message(message)


def check_message(message: str) -> int:
    """Check a commit message string for violations. Returns exit code."""
    if is_bypass():
        return 0
    violations = find_violations(message)
    if not violations:
        return 0
    print("BLOCKING: unauthorized attribution trailer(s) detected:")
    for v in violations:
        print(f"  {v}")
    print("Remove them or set ALLOW_ATTRIBUTION_TRAILERS=1 to bypass.")
    return 1


def check_commit_range(base: str, head: str) -> int:
    """Check all commits in range base..head. Returns exit code."""
    if is_bypass():
        return 0
    result = subprocess.run(
        ["git", "log", "--format=%H %s", f"{base}..{head}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"error: git log failed: {result.stderr.strip()}", file=sys.stderr)
        return 2
    if not result.stdout.strip():
        return 0

    exit_code = 0
    # Fetch all commit messages in one call instead of per-commit
    commit_shas = [line.partition(" ")[0] for line in result.stdout.strip().split("\n")]
    if not commit_shas:
        return 0

    # Single git log call to get all bodies
    log_result = subprocess.run(
        ["git", "log", "--format=%H%n%B", "--no-walk"] + commit_shas,
        capture_output=True,
        text=True,
    )
    if log_result.returncode != 0:
        print(f"error: git log failed: {log_result.stderr.strip()}", file=sys.stderr)
        return 2

    # Parse the output: SHA followed by message body
    current_sha = None
    current_body = []
    exit_code = 0
    for line in log_result.stdout.splitlines():
        if re.match(r"^[a-f0-9]{40}$", line):
            # New commit SHA
            if current_sha is not None:
                violations = find_violations("\n".join(current_body))
                if violations:
                    print(f"BLOCKING: {current_sha} {' '.join(current_body[0].split()[:5])}")
                    for v in violations:
                        print(f"  {v}")
                    exit_code = 1
            current_sha = line
            current_body = []
        else:
            current_body.append(line)

    # Check last commit
    if current_sha is not None:
        violations = find_violations("\n".join(current_body))
        if violations:
            print(f"BLOCKING: {current_sha} {' '.join(current_body[0].split()[:5])}")
            for v in violations:
                print(f"  {v}")
            exit_code = 1

    return exit_code


def usage() -> None:
    print("usage: check-commit-trailers.py [--self-test] [<commit-message-file>]", file=sys.stderr)
    print("       check-commit-trailers.py --range <base>..<head>", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    if "--self-test" in sys.argv:
        return do_self_test()
    if "--range" in sys.argv:
        idx = sys.argv.index("--range")
        if idx + 1 >= len(sys.argv):
            usage()
        range_spec = sys.argv[idx + 1]
        if ".." not in range_spec:
            print("error: --range expects <base>..<head>", file=sys.stderr)
            return 2
        base, head = range_spec.split("..", 1)
        return check_commit_range(base, head)
    if len(sys.argv) > 2:
        usage()
    if len(sys.argv) == 2 and sys.argv[1] in ("-h", "--help"):
        usage()
    if len(sys.argv) == 2:
        return check_file(sys.argv[1])
    # No args: read from stdin (hook mode)
    message = sys.stdin.read()
    return check_message(message)


if __name__ == "__main__":
    sys.exit(main())