"""Ensure the duplicated deterministic workflow jobs stay equivalent."""

from __future__ import annotations

import argparse
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]


def normalized_job(workflow_path: Path, job_name: str) -> str:
    """Return a workflow job without comments or blank lines for comparison."""
    lines = workflow_path.read_text(encoding="utf-8").splitlines()
    header = f"  {job_name}:"
    try:
        start = lines.index(header)
    except ValueError as exc:
        raise RuntimeError(f"{workflow_path} has no {job_name!r} job") from exc

    job_lines: list[str] = []
    for line in lines[start:]:
        if job_lines and line.startswith("  ") and not line.startswith("    ") and line.endswith(":"):
            break
        without_comment = line.split("#", 1)[0].rstrip()
        if without_comment:
            job_lines.append(without_comment)

    job_lines[0] = "  job:"
    return "\n".join(job_lines)


def workflows_match(ci_path: Path, range_path: Path) -> bool:
    """Return whether lint and python-range have the same deterministic steps."""
    return normalized_job(ci_path, "lint") == normalized_job(range_path, "python-range")


def run_self_tests() -> int:
    """Exercise equivalent and divergent workflow jobs without touching the repo."""
    ci_job = "  lint:\n    steps:\n      - run: python3 scripts/check.py # comment\n"
    range_job = "  python-range:\n    steps:\n      - run: python3 scripts/check.py\n"
    divergent_job = "  python-range:\n    steps:\n      - run: python3 scripts/other.py\n"

    with TemporaryDirectory() as temporary_directory:
        fixture_dir = Path(temporary_directory)
        ci_path = fixture_dir / "ci.yml"
        range_path = fixture_dir / "range.yml"
        ci_path.write_text(ci_job, encoding="utf-8")
        range_path.write_text(range_job, encoding="utf-8")
        assert workflows_match(ci_path, range_path)
        range_path.write_text(divergent_job, encoding="utf-8")
        assert not workflows_match(ci_path, range_path)

    print("PASS: check-python-range-parity.py self-tests")
    return 0


def main() -> int:
    """Check the repository's two intentionally duplicated workflow jobs."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run internal self-tests")
    args = parser.parse_args()
    if args.self_test:
        return run_self_tests()

    ci_path = ROOT / ".github/workflows/ci.yml"
    range_path = ROOT / ".github/workflows/python-range.yml"
    if workflows_match(ci_path, range_path):
        print("PASS: lint and python-range workflow jobs match")
        return 0
    print("ERROR: lint and python-range workflow jobs differ")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
