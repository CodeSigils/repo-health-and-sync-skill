#!/usr/bin/env python3
"""
Check commit message body for required fields (e.g., what:/why:).

Usage:
  check-commit-body.py [--self-test] [<commit-message-file>]
  check-commit-body.py --range <base>..<head>

Exit codes:
  0 — no violations (or bypass enabled)
  1 — violations found
  2 — internal error (file not found, etc.)

Environment:
  ALLOW_ATTRIBUTION_TRAILERS=1 — bypass all checking

Configuration:
  Reads .repo-health.json -> commit_body_format:
    - required_fields: list of field names (e.g., ["what", "why"])
    - pattern: optional regex to match the entire body
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

# Default configuration
DEFAULT_REQUIRED_FIELDS = ["what", "why"]
DEFAULT_PATTERN: re.Pattern[str] | None = None  # e.g., r"^what: .+\nwhy:  .+$"


@dataclass(frozen=True)
class CommitBodyConfig:
    """Immutable configuration for commit body validation."""
    required_fields: list[str]
    pattern: re.Pattern[str] | None

    @classmethod
    def from_file(cls, config_path: Path) -> CommitBodyConfig:
        """Load configuration from .repo-health.json."""
        if not config_path.is_file():
            return cls(DEFAULT_REQUIRED_FIELDS, DEFAULT_PATTERN)

        try:
            with open(config_path, encoding="utf-8") as f:
                data = json.load(f)
            body_format = data.get("commit_body_format", {})
            required = body_format.get("required_fields", ["what", "why"])
            pattern = body_format.get("pattern")
            compiled = re.compile(pattern, re.MULTILINE) if pattern else None
            return cls(required, compiled)
        except (OSError, json.JSONDecodeError, re.error):
            return cls(DEFAULT_REQUIRED_FIELDS, None)


def is_bypass() -> bool:
    return os.environ.get("ALLOW_ATTRIBUTION_TRAILERS", "").lower() in {"1", "true", "yes"}


def extract_body(message: str) -> str:
    """Extract commit body (lines after first blank line, excluding comments)."""
    lines = message.splitlines()
    body_start = 0
    for i, line in enumerate(lines):
        if line.strip() == "":
            body_start = i + 1
            break
    body_lines = lines[body_start:]
    body_lines = [line for line in body_lines if not line.startswith("#")]
    return "\n".join(body_lines).strip()


def find_violations(message: str, config: CommitBodyConfig) -> list[str]:
    """Return list of violation descriptions for a commit message with explicit config."""
    if is_bypass():
        return []

    body = extract_body(message)
    violations = []

    if not body:
        violations.append("empty commit body — required fields missing")
        return violations

    # Check required fields
    for field in config.required_fields:
        if not re.search(rf"^{re.escape(field)}:", body, re.MULTILINE):
            violations.append(f"missing required field: '{field}:'")

    # Check pattern if configured
    if config.pattern and not config.pattern.search(body):
        violations.append(f"body does not match required pattern: {config.pattern.pattern}")

    return violations


def do_self_test() -> int:
    """Run internal unit tests. Returns 0 on pass, 1 on fail."""
    tests = [
        # (label, message, config, expected_violation_count)
        (
            "valid what/why",
            "feat: add widget\n\nwhat: added widget\nwhy: user requested it\n",
            CommitBodyConfig(["what", "why"], None),
            0,
        ),
        (
            "missing what",
            "feat: add widget\n\nwhy: user requested it\n",
            CommitBodyConfig(["what", "why"], None),
            1,
        ),
        (
            "missing why",
            "feat: add widget\n\nwhat: added widget\n",
            CommitBodyConfig(["what", "why"], None),
            1,
        ),
        (
            "missing both",
            "feat: add widget\n\nadded widget\n",
            CommitBodyConfig(["what", "why"], None),
            2,
        ),
        (
            "empty body",
            "feat: add widget\n",
            CommitBodyConfig(["what", "why"], None),
            2,
        ),
        (
            "extra fields allowed",
            "feat: add widget\n\nwhat: added widget\nwhy: user requested it\nref: #123\n",
            CommitBodyConfig(["what", "why"], None),
            0,
        ),
        ("case sensitive field names", "feat: x\n\nWhat: a\nWhy: b\n", CommitBodyConfig(["what", "why"], None), 2),
        ("pattern mismatch (default no pattern)", "feat: x\n\nwhat: a\nwhy: b\n", CommitBodyConfig(["what", "why"], None), 0),
    ]

    # Test with custom pattern
    custom_pattern = re.compile(r"^what: .+\nwhy:  .+$", re.MULTILINE)
    tests_pattern = [
        ("pattern matches", "feat: x\n\nwhat: added thing\nwhy:  reason\n", CommitBodyConfig(["what", "why"], custom_pattern), 0),
        ("pattern fails spacing", "feat: x\n\nwhat: added thing\nwhy: reason\n", CommitBodyConfig(["what", "why"], custom_pattern), 1),
    ]

    failures = 0

    for label, msg, config, expected in tests:
        result = find_violations(msg, config)
        if len(result) != expected:
            print(f"  FAIL  {label}: expected {expected} violations, got {len(result)}: {result}")
            failures += 1
        else:
            print(f"  PASS  {label}")

    for label, msg, config, expected in tests_pattern:
        result = find_violations(msg, config)
        if len(result) != expected:
            print(f"  FAIL  {label}: expected {expected} violations, got {len(result)}: {result}")
            failures += 1
        else:
            print(f"  PASS  {label}")

    if failures:
        print(f"\n--- Self-test: {failures} failure(s) ---")
    else:
        print(f"\n--- Self-test: all {len(tests) + len(tests_pattern)} pass ---")
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
    config = CommitBodyConfig.from_file(Path(".repo-health.json"))
    violations = find_violations(message, config)
    if not violations:
        return 0
    print("BLOCKING: commit body format violations:")
    for v in violations:
        print(f"  {v}")
    print("Set ALLOW_ATTRIBUTION_TRAILERS=1 to bypass.")
    return 1


def check_commit_range(base: str, head: str) -> int:
    """Check all commits in range base..head. Returns exit code."""
    if is_bypass():
        return 0
    config = CommitBodyConfig.from_file(Path(".repo-health.json"))
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
                violations = find_violations("\n".join(current_body), config)
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
        violations = find_violations("\n".join(current_body), config)
        if violations:
            print(f"BLOCKING: {current_sha} {' '.join(current_body[0].split()[:5])}")
            for v in violations:
                print(f"  {v}")
            exit_code = 1

    return exit_code


def usage() -> None:
    print("usage: check-commit-body.py [--self-test] [<commit-message-file>]", file=sys.stderr)
    print("       check-commit-body.py --range <base>..<head>", file=sys.stderr)
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
