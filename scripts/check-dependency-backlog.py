"""
check-dependency-backlog.py — Report dependency pull requests that have gone stale.

A red check announces itself; a mergeable pull request that has been open for
weeks does not. This check turns that silent artifact into a signal: it lists
open dependency pull requests, reports the age of each, leaves one updatable
comment on any that have passed the age threshold, and exits non-zero so a
scheduled run notifies the maintainer.

The comment is edited in place rather than re-posted, so a pull request that
stays open does not accumulate one comment per week.

Usage:
    python3 scripts/check-dependency-backlog.py            # report only, no comments
    python3 scripts/check-dependency-backlog.py --post     # also post/update comments
    python3 scripts/check-dependency-backlog.py --days 14  # override the age threshold
    python3 scripts/check-dependency-backlog.py --repo OWNER/NAME
    python3 scripts/check-dependency-backlog.py --self-test  # run internal self-tests

Exit codes:
    0  no dependency pull request is older than the threshold
    1  at least one dependency pull request is older than the threshold
    2  the pull requests could not be listed (gh missing, unauthenticated, API error)
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

# First line of every comment this script owns. It is an HTML comment, so GitHub
# renders nothing for it, and it is how an existing comment is found again.
MARKER = "<!-- repo-health:dependency-backlog -->"
DEFAULT_DAYS = 7
BOT_LOGIN_RE = re.compile(r"dependabot", re.IGNORECASE)
REMOTE_REPO_RE = re.compile(r"github\.com[:/]+(?P<owner>[^/]+)/(?P<name>[^/\s]+?)(?:\.git)?$")


@dataclass(frozen=True)
class PullRequest:
    """One open dependency pull request, reduced to what a status comment needs."""

    number: int
    title: str
    url: str
    author: str
    created_at: datetime


@dataclass(frozen=True)
class Result:
    """A gh call that either produced output or failed with a reason.

    Separates "the answer is empty" from "the question could not be asked", so
    an API failure is never reported as a clean backlog.
    """

    ok: bool
    data: object = None
    detail: str | None = None


def parse_timestamp(value: object) -> datetime | None:
    """Parse an ISO 8601 timestamp as returned by the GitHub API."""
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip().replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed.astimezone(UTC)


def is_bot_login(login: object) -> bool:
    """Report whether a login belongs to a dependency bot.

    Matches both the REST form (`dependabot[bot]`) and the form the CLI reports
    (`app/dependabot`), so a rename on either side does not silently empty the
    report.
    """
    return isinstance(login, str) and bool(BOT_LOGIN_RE.search(login))


def parse_pulls(payload: object) -> tuple[list[PullRequest], list[str]]:
    """Reduce raw PR payloads to dependency PRs. Returns (pulls, problems).

    A malformed entry is reported rather than dropped: silently ignoring a pull
    request would defeat the purpose of the check.
    """
    if not isinstance(payload, list):
        return [], [f"gh returned {type(payload).__name__}, expected a list"]
    pulls: list[PullRequest] = []
    problems: list[str] = []
    for index, entry in enumerate(payload):
        if not isinstance(entry, dict):
            problems.append(f"entry {index} is not an object")
            continue
        author = entry.get("author")
        login = author.get("login") if isinstance(author, Mapping) else None
        if not is_bot_login(login):
            continue
        number = entry.get("number")
        created = parse_timestamp(entry.get("createdAt"))
        if not isinstance(number, int) or created is None:
            problems.append(f"pull request entry {index} has no usable number or createdAt")
            continue
        pulls.append(
            PullRequest(
                number=number,
                title=str(entry.get("title", "")),
                url=str(entry.get("url", "")),
                author=str(login),
                created_at=created,
            )
        )
    return pulls, problems


def age_in_days(created: datetime, now: datetime) -> int:
    """Whole days between two timestamps, never negative."""
    return max(0, (now - created).days)


def select_stale(
    pulls: Sequence[PullRequest], threshold_days: int, now: datetime
) -> list[tuple[PullRequest, int]]:
    """Return (pull, age) pairs at or over the threshold, oldest first."""
    aged = [(pull, age_in_days(pull.created_at, now)) for pull in pulls]
    stale = [item for item in aged if item[1] >= threshold_days]
    return sorted(stale, key=lambda item: (-item[1], item[0].number))


def render_comment(pull: PullRequest, age: int, threshold_days: int, now: datetime) -> str:
    """Build the single comment this script owns on a pull request."""
    return "\n".join(
        [
            MARKER,
            f"**Dependency backlog:** this pull request has been open {age} days.",
            "",
            f"- Opened: {pull.created_at.date().isoformat()}",
            f"- Age threshold: {threshold_days} days",
            f"- Checked: {now.date().isoformat()}",
            "",
            (
                "The scheduled `ci` run rewrites this comment rather than adding a new one, "
                "so a pull request that stays open does not collect one comment per week."
            ),
            "",
            (
                "Review and merge or close it. If this age is acceptable for this dependency, "
                "raise the threshold instead of ignoring the finding."
            ),
        ]
    )


def find_marker_comment(comments: object, marker: str = MARKER) -> Mapping[str, object] | None:
    """Return the newest comment carrying the marker, or None."""
    if not isinstance(comments, list):
        return None
    matches = [
        entry
        for entry in comments
        if isinstance(entry, Mapping) and isinstance(entry.get("body"), str) and marker in entry["body"]
    ]
    if not matches:
        return None
    return max(matches, key=lambda entry: (isinstance(entry.get("id"), int), entry.get("id") or 0))


def resolve_repo(
    explicit: str | None,
    env: Mapping[str, str] | None = None,
    remote: str | None = None,
) -> Result:
    """Resolve OWNER/NAME from the flag, the CI environment, then the git remote."""
    if explicit:
        return Result(True, explicit)
    environ = os.environ if env is None else env
    from_env = environ.get("GITHUB_REPOSITORY", "").strip()
    if from_env:
        return Result(True, from_env)
    if remote is None:
        remote = read_origin_remote()
    match = REMOTE_REPO_RE.search(remote) if remote else None
    if not match:
        return Result(False, detail="repository could not be resolved; pass --repo OWNER/NAME")
    return Result(True, f"{match.group('owner')}/{match.group('name')}")


def read_origin_remote() -> str:
    """Return the origin remote URL, or an empty string when it cannot be read."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return ""
    return result.stdout.strip() if result.returncode == 0 else ""


def run_gh(args: Sequence[str]) -> Result:
    """Run gh with the given arguments and return its parsed JSON output."""
    try:
        result = subprocess.run(["gh", *args], capture_output=True, text=True, check=False)
    except OSError as exc:
        return Result(False, detail=f"gh could not be run: {exc}")
    if result.returncode != 0:
        detail = result.stderr.strip() or f"gh exited {result.returncode}"
        return Result(False, detail=detail)
    try:
        return Result(True, json.loads(result.stdout))
    except json.JSONDecodeError as exc:
        return Result(False, detail=f"invalid gh JSON: {exc}")


def list_open_pulls(repo: str) -> Result:
    """List every open pull request in the repository."""
    return run_gh(
        [
            "pr",
            "list",
            "--repo",
            repo,
            "--state",
            "open",
            "--limit",
            "100",
            "--json",
            "number,title,url,author,createdAt",
        ]
    )


def list_comments(repo: str, number: int) -> Result:
    """List the comments on one pull request or issue."""
    return run_gh(["api", f"repos/{repo}/issues/{number}/comments?per_page=100"])


def create_comment(repo: str, number: int, body: str) -> Result:
    """Post a new comment. The body always starts with the marker, never '@'."""
    return run_gh(["api", "-X", "POST", f"repos/{repo}/issues/{number}/comments", "-f", f"body={body}"])


def update_comment(repo: str, comment_id: int, body: str) -> Result:
    """Replace the body of an existing comment."""
    return run_gh(["api", "-X", "PATCH", f"repos/{repo}/issues/comments/{comment_id}", "-f", f"body={body}"])


def publish(repo: str, pull: PullRequest, age: int, threshold_days: int, now: datetime) -> list[str]:
    """Post or update the status comment. Returns problem descriptions."""
    body = render_comment(pull, age, threshold_days, now)
    existing = list_comments(repo, pull.number)
    if not existing.ok:
        return [f"#{pull.number}: could not read comments ({existing.detail})"]
    current = find_marker_comment(existing.data)
    if current is None:
        posted = create_comment(repo, pull.number, body)
        if not posted.ok:
            return [f"#{pull.number}: could not comment ({posted.detail})"]
        return []
    comment_id = current.get("id")
    if not isinstance(comment_id, int):
        return [f"#{pull.number}: existing marker comment has no usable id"]
    updated = update_comment(repo, comment_id, body)
    if not updated.ok:
        return [f"#{pull.number}: could not update comment ({updated.detail})"]
    return []


def run_self_tests() -> int:
    """Exercise the pure helpers offline. Returns a non-zero count on failure."""
    errors = 0

    parsed = parse_timestamp("2026-09-14T06:20:34Z")
    if parsed is None or parsed.tzinfo is not UTC:
        print("FAIL: parse_timestamp did not normalize a Z timestamp to UTC")
        errors += 1
    if parse_timestamp("2026-09-14") is None or parse_timestamp("not a date") is not None:
        print("FAIL: parse_timestamp accepted or rejected the wrong inputs")
        errors += 1
    if parse_timestamp("") is not None or parse_timestamp(None) is not None:
        print("FAIL: parse_timestamp accepted an empty value")
        errors += 1
    print("  PASS  parse_timestamp tests")

    if not is_bot_login("dependabot[bot]") or not is_bot_login("app/dependabot"):
        print("FAIL: is_bot_login missed a dependabot login form")
        errors += 1
    if is_bot_login("CodeSigils") or is_bot_login(None) or is_bot_login(7):
        print("FAIL: is_bot_login accepted a non-bot login")
        errors += 1
    print("  PASS  is_bot_login tests")

    payload = [
        {"number": 1, "title": "a", "url": "u", "author": {"login": "app/dependabot"}, "createdAt": "2026-09-01T00:00:00Z"},
        {"number": 2, "title": "b", "url": "u", "author": {"login": "CodeSigils"}, "createdAt": "2026-09-20T00:00:00Z"},
        {"number": 3, "title": "c", "url": "u", "author": {"login": "dependabot[bot]"}, "createdAt": "2026-09-10T00:00:00Z"},
    ]
    pulls, problems = parse_pulls(payload)
    if problems or [p.number for p in pulls] != [1, 3]:
        print(f"FAIL: parse_pulls returned {[p.number for p in pulls]} with problems {problems}")
        errors += 1
    _, broken = parse_pulls([{"number": 4, "author": {"login": "app/dependabot"}}])
    if not broken:
        print("FAIL: parse_pulls did not report a pull request with no createdAt")
        errors += 1
    if parse_pulls("not a list")[1] == []:
        print("FAIL: parse_pulls accepted a non-list payload")
        errors += 1
    print("  PASS  parse_pulls tests")

    now = datetime(2026, 9, 26, 12, 0, tzinfo=UTC)
    stale = select_stale(pulls, DEFAULT_DAYS, now)
    if [(p.number, age) for p, age in stale] != [(1, 25), (3, 16)]:
        print(f"FAIL: select_stale returned {[(p.number, a) for p, a in stale]}")
        errors += 1
    if select_stale(pulls, 30, now):
        print("FAIL: select_stale kept a pull request under a high threshold")
        errors += 1
    print("  PASS  select_stale tests")

    comment = render_comment(stale[0][0], stale[0][1], DEFAULT_DAYS, now)
    if not comment.startswith(MARKER) or "#1" not in comment and "25 days" not in comment:
        print("FAIL: render_comment did not open with the marker and state the age")
        errors += 1
    if "2026-09-26" not in comment:
        print("FAIL: render_comment did not record the check date")
        errors += 1
    print("  PASS  render_comment tests")

    comments = [
        {"id": 4, "body": "unrelated review"},
        {"id": 9, "body": f"{MARKER}\nold body"},
        {"id": 11, "body": "another review"},
    ]
    found = find_marker_comment(comments)
    if not found or found["id"] != 9:
        print("FAIL: find_marker_comment did not locate the marked comment")
        errors += 1
    if find_marker_comment([{"id": 1, "body": "no marker"}]) is not None:
        print("FAIL: find_marker_comment matched a comment without the marker")
        errors += 1
    if find_marker_comment("not a list") is not None:
        print("FAIL: find_marker_comment accepted a non-list payload")
        errors += 1
    print("  PASS  find_marker_comment tests")

    if resolve_repo("owner/name", env={}).data != "owner/name":
        print("FAIL: resolve_repo ignored the explicit repository")
        errors += 1
    if resolve_repo(None, env={"GITHUB_REPOSITORY": "env/name"}).data != "env/name":
        print("FAIL: resolve_repo ignored GITHUB_REPOSITORY")
        errors += 1
    from_remote = resolve_repo(None, env={}, remote="git@github.com:owner/name.git")
    if from_remote.data != "owner/name":
        print(f"FAIL: resolve_repo read the remote as {from_remote.data}")
        errors += 1
    if resolve_repo(None, env={}, remote="").ok:
        print("FAIL: resolve_repo succeeded without any source")
        errors += 1
    print("  PASS  resolve_repo tests")

    print("  PASS  check-dependency-backlog.py self-tests")
    return errors


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="Report stale dependency pull requests")
    parser.add_argument("--self-test", action="store_true", help="Run internal self-tests")
    parser.add_argument("--post", action="store_true", help="Post or update the status comments")
    parser.add_argument("--days", type=int, default=DEFAULT_DAYS, help="Age threshold in days")
    parser.add_argument("--repo", help="Target repository as OWNER/NAME")
    args = parser.parse_args()

    if args.self_test:
        return run_self_tests()

    if args.days < 1:
        print("FAIL: --days must be at least 1", file=sys.stderr)
        return 2

    repo_result = resolve_repo(args.repo)
    if not repo_result.ok:
        print(f"FAIL: {repo_result.detail}", file=sys.stderr)
        return 2
    repo = str(repo_result.data)

    listed = list_open_pulls(repo)
    if not listed.ok:
        print(f"FAIL: could not list pull requests in {repo}: {listed.detail}", file=sys.stderr)
        return 2

    pulls, problems = parse_pulls(listed.data)
    now = datetime.now(tz=UTC)
    stale = select_stale(pulls, args.days, now)

    print(f"Repository: {repo}")
    print(f"Open dependency pull requests: {len(pulls)}")
    for pull in sorted(pulls, key=lambda p: p.created_at):
        age = age_in_days(pull.created_at, now)
        state = "STALE" if age >= args.days else "ok"
        print(f"  #{pull.number} {age:>3}d {state:<5} {pull.title}")

    if not pulls:
        print("PASS: no open dependency pull requests")
    elif not stale:
        print(f"PASS: no dependency pull request is {args.days} days old or older")
    else:
        print(
            f"STALE: {len(stale)} dependency pull request(s) at or over {args.days} days: "
            f"{', '.join(f'#{p.number} ({a}d)' for p, a in stale)}",
            file=sys.stderr,
        )

    for problem in problems:
        print(f"FAIL: {problem}", file=sys.stderr)

    if args.post:
        if not stale:
            print("NOTE: nothing to post")
        for pull, age in stale:
            for issue in publish(repo, pull, age, args.days, now):
                print(f"FAIL: {issue}", file=sys.stderr)
                problems.append(issue)
        if stale:
            print(f"NOTE: status comments written for {len(stale)} pull request(s)")
    elif stale:
        print("NOTE: run with --post to write the status comments onto the pull requests")

    if problems:
        return 1
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
