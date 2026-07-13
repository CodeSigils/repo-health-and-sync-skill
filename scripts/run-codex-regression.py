#!/usr/bin/env python3
"""Run isolated positive and negative Codex skill regressions."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SKILL_SOURCE = REPO_ROOT / "skills/repo-health-and-sync-skill/SKILL.md"
POSITIVE_PROMPT = REPO_ROOT / "evals/codex/positive-prompt.md"
NEGATIVE_PROMPT = REPO_ROOT / "evals/codex/negative-prompt.md"
RESULT_SCHEMA = REPO_ROOT / "evals/codex/positive-result.schema.json"
GRADER = REPO_ROOT / "scripts/grade-codex-transcript.py"


def run_checked(command: list[str], cwd: Path) -> None:
    """Run a fixture setup command and surface its stderr on failure."""
    result = subprocess.run(
        command, cwd=cwd, capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RuntimeError(f"command failed ({' '.join(command)}): {detail}")


def prepare_fixture(root: Path) -> None:
    """Create a small Python repository with one intentional health defect."""
    if root.exists():
        raise FileExistsError(f"fixture path already exists: {root}")
    (root / ".agents/skills/repo-health-and-sync-skill").mkdir(parents=True)
    (root / ".github/workflows").mkdir(parents=True)
    (root / "src/example").mkdir(parents=True)
    (root / "tests").mkdir(parents=True)

    shutil.copy2(
        SKILL_SOURCE,
        root / ".agents/skills/repo-health-and-sync-skill/SKILL.md",
    )
    files = {
        "README.md": "# Example Parser\n\nSmall Python parsing library.\n",
        ".gitignore": ".venv/\n__pycache__/\n.pytest_cache/\n",
        "pyproject.toml": (
            "[project]\n"
            'name = "example-parser"\n'
            'version = "0.1.0"\n'
            'requires-python = ">=3.11"\n\n'
            "[tool.uv]\n"
            "package = true\n"
        ),
        "src/example/__init__.py": '"""Example parser package."""\n',
        "src/example/parser.py": (
            '"""Parse a key/value line."""\n\n'
            "def parse_line(value: str) -> tuple[str, str]:\n"
            '    return tuple(value.split("="))\n'
        ),
        "tests/test_parser.py": (
            "from example.parser import parse_line\n\n\n"
            "def test_value_may_contain_separator():\n"
            '    assert parse_line("url=https://example.test?a=1") == (\n'
            '        "url",\n'
            '        "https://example.test?a=1",\n'
            "    )\n"
        ),
        ".github/workflows/ci.yml": (
            "name: ci\n"
            "on: [push]\n"
            "jobs:\n"
            "  test:\n"
            "    runs-on: ubuntu-latest\n"
            "    steps:\n"
            "      - uses: actions/checkout@v5\n"
            "      - run: uv run pytest\n"
        ),
    }
    for relative, content in files.items():
        (root / relative).write_text(content, encoding="utf-8")

    run_checked(["git", "init", "-b", "main"], root)
    run_checked(["git", "config", "user.name", "Codex Eval"], root)
    run_checked(["git", "config", "user.email", "codex-eval@example.invalid"], root)
    run_checked(["git", "config", "commit.gpgsign", "false"], root)
    run_checked(["git", "add", "."], root)
    run_checked(["git", "commit", "-m", "feat: add example parser"], root)

    # Seed a visible health finding after the clean baseline commit.
    (root / "scratch.txt").write_text(
        "untracked release scratch file\n", encoding="utf-8"
    )


def codex_command(
    codex_bin: str,
    fixture: Path,
    prompt: Path,
    output: Path,
    schema: Path | None = None,
) -> list[str]:
    """Build the controlled non-interactive Codex invocation."""
    command = [
        codex_bin,
        "exec",
        "--json",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--sandbox",
        "read-only",
        "--cd",
        str(fixture),
        "--output-last-message",
        str(output),
    ]
    if schema is not None:
        command.extend(["--output-schema", str(schema)])
    command.append(prompt.read_text(encoding="utf-8"))
    return command


def run_codex(
    command: list[str], transcript: Path, stderr_path: Path, timeout_seconds: int
) -> None:
    """Capture Codex stdout as JSONL and diagnostics separately."""
    transcript.parent.mkdir(parents=True, exist_ok=True)
    with (
        transcript.open("w", encoding="utf-8") as stdout_file,
        stderr_path.open("w", encoding="utf-8") as stderr_file,
    ):
        try:
            result = subprocess.run(
                command,
                cwd=REPO_ROOT,
                stdin=subprocess.DEVNULL,
                stdout=stdout_file,
                stderr=stderr_file,
                text=True,
                check=False,
                timeout=timeout_seconds,
                env=os.environ.copy(),
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError(
                f"Codex exceeded {timeout_seconds}s; see {stderr_path} and {transcript}"
            ) from exc
    if result.returncode != 0:
        raise RuntimeError(
            f"Codex exited {result.returncode}; see {stderr_path} and {transcript}"
        )


def grade(output_dir: Path) -> int:
    """Run the deterministic grader over both model scenarios."""
    command = [
        sys.executable,
        str(GRADER),
        "--positive-result",
        str(output_dir / "positive-result.json"),
        "--negative-result",
        str(output_dir / "negative-result.txt"),
        "--positive-transcript",
        str(output_dir / "positive-transcript.jsonl"),
        "--negative-transcript",
        str(output_dir / "negative-transcript.jsonl"),
        "--output",
        str(output_dir / "grade.json"),
    ]
    return subprocess.run(command, cwd=REPO_ROOT, check=False).returncode


def run_self_tests() -> int:
    """Verify fixture shape and controlled command construction without a model call."""
    with tempfile.TemporaryDirectory() as directory:
        fixture = Path(directory) / "fixture"
        prepare_fixture(fixture)
        assert (
            fixture / ".agents/skills/repo-health-and-sync-skill/SKILL.md"
        ).is_file()
        assert "uv" in (fixture / "pyproject.toml").read_text(encoding="utf-8")
        status = subprocess.run(
            ["git", "status", "--short"],
            cwd=fixture,
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        assert status == "?? scratch.txt\n"
        command = codex_command(
            "codex", fixture, POSITIVE_PROMPT, fixture / "result.json", RESULT_SCHEMA
        )
        assert isinstance(json.loads(RESULT_SCHEMA.read_text(encoding="utf-8")), dict)
        for flag in ("--json", "--ephemeral", "--ignore-user-config", "read-only"):
            assert flag in command
    print("PASS: run-codex-regression.py self-tests")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-dir", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--codex-bin", default="codex")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--keep-fixture", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        return run_self_tests()

    temporary: tempfile.TemporaryDirectory[str] | None = None
    if args.fixture_dir is None:
        temporary = tempfile.TemporaryDirectory(prefix="repo-health-codex-eval-")
        fixture = Path(temporary.name) / "fixture"
    else:
        fixture = args.fixture_dir.resolve()
    try:
        prepare_fixture(fixture)
        if args.prepare_only:
            print(f"Prepared Codex regression fixture: {fixture}")
            return 0

        timestamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
        output_dir = (
            args.output_dir or REPO_ROOT / "artifacts/codex-regression" / timestamp
        )
        output_dir = output_dir.resolve()
        output_dir.mkdir(parents=True, exist_ok=True)

        positive = codex_command(
            args.codex_bin,
            fixture,
            POSITIVE_PROMPT,
            output_dir / "positive-result.json",
            RESULT_SCHEMA,
        )
        run_codex(
            positive,
            output_dir / "positive-transcript.jsonl",
            output_dir / "positive-stderr.log",
            args.timeout_seconds,
        )
        negative = codex_command(
            args.codex_bin,
            fixture,
            NEGATIVE_PROMPT,
            output_dir / "negative-result.txt",
        )
        run_codex(
            negative,
            output_dir / "negative-transcript.jsonl",
            output_dir / "negative-stderr.log",
            args.timeout_seconds,
        )
        result = grade(output_dir)
        print(f"Codex regression artifacts: {output_dir}")
        return result
    except (FileExistsError, OSError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    finally:
        if temporary is not None and not args.keep_fixture:
            temporary.cleanup()


if __name__ == "__main__":
    sys.exit(main())
