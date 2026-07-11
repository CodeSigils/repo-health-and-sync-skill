#!/usr/bin/env python3
"""Extract test fixtures from script self-tests.

Parses the do_self_test() function of a script and extracts test cases
into the review-fixtures.json format.

Usage:
    python3 scripts/extract-tests.py --script check-commit-body.py --output test-fixtures.json
    python3 scripts/extract-tests.py --script check-commit-body.py --output test-fixtures.json
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path


def extract_test_cases(script_path: Path) -> list[dict]:
    """Extract test cases from a script's do_self_test() function."""
    content = script_path.read_text(encoding="utf-8")
    tree = ast.parse(content)

    # Find do_self_test function
    test_func = None
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "do_self_test":
            test_func = node
            break

    if not test_func:
        return []

    # Find test assignments in the function
    tests = []
    pattern = None

    for node in ast.walk(test_func):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ("tests", "tests_pattern"):
                    # Found test list assignment
                    if isinstance(node.value, ast.List):
                        for elt in node.value.elts:
                            if isinstance(elt, ast.Tuple) and len(elt.elts) >= 3:
                                # Extract label, message, config, expected
                                label = ast.literal_eval(elt.elts[0]) if isinstance(elt.elts[0], ast.Constant) else None
                                message = ast.literal_eval(elt.elts[1]) if isinstance(elt.elts[1], ast.Constant) else None
                                expected = ast.literal_eval(elt.elts[3]) if len(elt.elts) > 3 and isinstance(elt.elts[3], ast.Constant) else None
                                if label and message is not None and expected is not None:
                                    tests.append({
                                        "label": label,
                                        "message": message,
                                        "expected": expected
                                    })
                    if target.id == "tests_pattern":
                        pattern = "pattern"

    return tests


def create_fixtures(script_name: str, tests: list[dict]) -> list[dict]:
    """Create test fixture entries from extracted test cases."""
    fixtures = []

    for test in tests:
        label = test["label"]
        message = test["message"]
        expected = test["expected"]

        fixture = {
            "name": label,
            "python_version": "3.13",
            "maturity": "automation",
            "toolchain": ["ruff", "shellcheck"],
            "changed_files": [
                {
                    "path": f"scripts/{Path(sys.argv[1]).name}",
                    "content": message
                }
            ],
            "expected_scripts": ["check-commit-body"],
            "expected_rules": [],
        }

        if expected > 0:
            # Infer rule names from label
            rule_names = label.lower().replace(" ", "-").replace(",", "").replace("/", "-")
            fixture["expected_rules"] = [rule_names]

        fixtures.append(fixture)

    return fixtures


def main() -> int:
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="Extract test fixtures from script self-tests")
    parser.add_argument("--script", help="Script name in scripts/ directory")
    parser.add_argument("--output", default="test-fixtures.json")
    parser.add_argument("--self-test", action="store_true", help="Run internal self-tests")
    args = parser.parse_args()

    if args.self_test:
        return run_self_tests()

    if not args.script:
        print("Error: --script required", file=sys.stderr)
        return 1

    script_path = Path(__file__).resolve().parents[1] / "scripts" / args.script
    if not script_path.exists():
        print(f"Script not found: {script_path}", file=sys.stderr)
        return 1

    tests = extract_test_cases(script_path)
    if not tests:
        print(f"No test cases found in {args.script}", file=sys.stderr)
        return 1

    fixtures = create_fixtures(args.script, tests)

    output_path = Path(args.output)
    output_path.write_text(json.dumps(fixtures, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Extracted {len(fixtures)} fixtures to {output_path}")
    return 0


def run_self_tests() -> int:
    """Run internal self-tests for the extractor logic."""
    # Test extract_test_cases with known patterns
    test_content = '''
def do_self_test():
    tests = [
        ("valid what/why", "feat: x\\n\\nwhat: x\\nwhy: y\\n", CommitBodyConfig(["what", "why"], None), 0),
        ("missing what", "feat: x\\n\\nwhy: y\\n", CommitBodyConfig(["what", "why"], None), 1),
    ]
    custom_pattern = re.compile(r"^what: .+\\nwhy:  .+$", re.MULTILINE)
    tests_pattern = [
        ("pattern matches", "feat: x\\n\\nwhat: added thing\\nwhy:  reason\\n", 0),
        ("pattern fails spacing", "feat: x\\n\\nwhat: added thing\\nwhy: reason\\n", 1),
    ]
    '''
    
    test_path = Path("/tmp/test_extract.py")
    test_path.write_text(test_content)
    
    # Test extract_test_cases
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_content)
        f.flush()
        tests = extract_test_cases(Path(f.name))
        assert len(tests) >= 1
    
    print("PASS: extract-tests.py self-tests")
    return 0