#!/usr/bin/env python3
"""Validate script quality for repo-health scripts."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent

# Python scripts that should have --self-test
PY_SCRIPTS_WITH_SELF_TEST = [
    "check-portability.py",
    "verify-urls.py",
    "doc-audit.py",
    "check-expiry.py",
    "extract-tests.py",
]

# All scripts to check for quality
ALL_SCRIPTS = [
    "check-portability.py",
    "verify-urls.py",
    "doc-audit.py",
    "check-expiry.py",
    "extract-tests.py",
    "verify.sh",
]

REQUIRED_PATTERNS = [
    (r"def (?:do_self_test|run_self_tests|check_self_test|self_test)\(\)", "missing --self-test function"),
    (r"if __name__ == \"__main__\"", "missing main entry point"),
    (r"encoding=\"utf-8\"", "missing UTF-8 encoding on open()"),
]

FORBIDDEN_PATTERNS = [
    (r"except:\s*$", "bare except: clause"),
    (r"except Exception:\s*pass", "catch-all pass"),
    (r"subprocess\.run\([^)]*shell=True", "shell=True without justification"),
]

SHELL_SCRIPTS = {"verify.sh"}


def check_script(script_path: Path) -> list[str]:
    """Check a single script for quality issues."""
    errors = []
    content = script_path.read_text(encoding="utf-8")
    lines = content.splitlines()

    # Skip Python-specific checks for shell scripts
    if script_path.suffix == ".sh":
        if not lines[0].startswith("#!/usr/bin/env bash"):
            errors.append(f"{script_path.name}: missing #!/usr/bin/env bash shebang")
        if "set -euo pipefail" not in content:
            errors.append(f"{script_path.name}: missing 'set -euo pipefail'")
        return errors

    # Python script checks
    for pattern, msg in REQUIRED_PATTERNS:
        if not re.search(pattern, content):
            errors.append(f"{script_path.name}: {msg}")

    for pattern, msg in FORBIDDEN_PATTERNS:
        if re.search(pattern, content):
            errors.append(f"{script_path.name}: {msg}")

    # Check for encoding on open() calls (but not urllib.request.urlopen)
    open_calls = re.findall(r"open\([^)]+\)", content)
    for call in open_calls:
        # Check if this is urllib.request.urlopen (not a plain open() call)
        for i, line in enumerate(lines, 1):
            if call in line:
                # Skip if this is urllib.request.urlopen
                if "urllib.request.urlopen" in line or "urllib.request.Request" in line:
                    break
                if "encoding=" not in line and "rb" not in line and "wb" not in line:
                    errors.append(f"{script_path.name}:{i}: open() missing encoding=")
                break

    # Check for shebang
    if not lines[0].startswith("#!/usr/bin/env python3"):
        errors.append(f"{script_path.name}: missing #!/usr/bin/env python3 shebang")

    return errors


def run_self_tests() -> list[str]:
    """Run --self-test on all scripts that should have it and verify they pass."""
    errors = []
    for script in PY_SCRIPTS_WITH_SELF_TEST:
        script_path = SCRIPTS_DIR / script
        if not script_path.exists():
            continue
        result = subprocess.run(
            [sys.executable, str(script_path), "--self-test"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode != 0:
            errors.append(f"{script}: self-test failed: {result.stderr}")
    return errors


def check_all_scripts() -> list[str]:
    """Check all scripts for quality issues."""
    all_errors = []
    for script in ALL_SCRIPTS:
        script_path = SCRIPTS_DIR / script
        if script_path.exists():
            all_errors.extend(check_script(script_path))
    return all_errors


def main() -> int:
    all_errors = []

    # Check all scripts
    all_errors.extend(check_all_scripts())

    # Run self-tests
    all_errors.extend(run_self_tests())

    if all_errors:
        for error in all_errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("OK: all script validations passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())