#!/usr/bin/env python3
"""Verify reachable HTTP(S) URLs referenced by docs and skill files.

The URL list lives in docs/evidence-urls.json so the research evidence base has
one machine-readable source of truth. If the doc adds or removes URLs, update
that manifest instead of editing this script's code.

v3 schema adds: status tracking, source_type classification, domain tagging,
last_verified (ISO), versioned_url for versioned references.

Usage:
  python3 scripts/verify-urls.py
  python3 scripts/verify-urls.py --self-test
  python3 scripts/verify-urls.py --summary

Outputs a table of URL -> final status with drift annotations.
Exit code 0 = all URLs match documented expected state.
Exit code 1 = one or more URLs differs from the manifest.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "docs" / "evidence-urls.json"

VALID_STATUS_VALUES = {"active", "retracted", "moved", "deprecated", "unknown"}
VALID_SOURCE_TYPES = {
    "official_docs", "specification", "academic", "community",
    "pinned_snapshot", "versioned_release", "mirror",
}


def load_manifest(path: Path = MANIFEST_PATH) -> tuple[int, str, list[dict[str, Any]]]:
    """Load URL entries from the evidence manifest. Returns (version, description, urls)."""
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"FAIL: could not read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"FAIL: invalid JSON in {path}: {exc}") from exc

    version = manifest.get("version")
    if version not in (1, 2, 3):
        raise SystemExit(f"FAIL: manifest version must be 1, 2, or 3; got {version}")
    description = manifest.get("description", "")
    urls = manifest.get("urls")
    if not isinstance(urls, list):
        raise SystemExit(f"FAIL: {path} must contain a top-level 'urls' list")
    return version, description, urls


def validate_entry_v1(entry: dict[str, Any]) -> None:
    """Validate one v1 manifest entry."""
    required = ("name", "url", "expected_statuses")
    missing = [key for key in required if key not in entry]
    if missing:
        raise ValueError(f"missing required field(s): {', '.join(missing)}")
    if not isinstance(entry["expected_statuses"], list) or not entry["expected_statuses"]:
        raise ValueError("expected_statuses must be a non-empty list")
    for status in entry["expected_statuses"]:
        if not isinstance(status, int):
            raise ValueError("expected_statuses must contain integers")


def validate_entry_v3(entry: dict[str, Any]) -> None:
    """Validate one v3 manifest entry. Extends v1 with new fields."""
    validate_entry_v1(entry)

    # status tracking
    status = entry.get("status")
    if status is not None and status not in VALID_STATUS_VALUES:
        raise ValueError(
            f"status must be one of {sorted(VALID_STATUS_VALUES)}; got {status!r}"
        )

    # source_type classification
    source_type = entry.get("source_type")
    if source_type is not None and source_type not in VALID_SOURCE_TYPES:
        raise ValueError(
            f"source_type must be one of {sorted(VALID_SOURCE_TYPES)}; got {source_type!r}"
        )

    # domain_tag (string if present)
    domain_tag = entry.get("domain_tag")
    if domain_tag is not None and not isinstance(domain_tag, str):
        raise ValueError("domain_tag must be a string")

    # last_verified (ISO date format)
    last_verified = entry.get("last_verified")
    if last_verified is not None:
        if not isinstance(last_verified, str):
            raise ValueError("last_verified must be a string")
        # Validate ISO date format (YYYY-MM-DD)
        parts = last_verified.split("-")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise ValueError(
                f"last_verified must be ISO date (YYYY-MM-DD); got {last_verified!r}"
            )


def validate_entry(entry: dict[str, Any], version: int = 1) -> None:
    """Validate one manifest entry based on version."""
    if version >= 3:
        validate_entry_v3(entry)
    else:
        validate_entry_v1(entry)


def check_url(url: str, content_type: str | None = None) -> tuple[int | str, int, str | None]:
    """Return (final_status_code, redirect_count, content_or_error) for one URL.

    When content_type is "json", captures response body and validates JSON.
    """
    request = urllib.request.Request(
        url,
        method="GET",
        headers={"User-Agent": "repo-health-and-sync-skill-url-check"},
    )

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            status = response.status
            redirect_count = len(response.headers.get("Location", "").split("\n")) if "Location" in response.headers else 0

            if content_type == "json":
                body = response.read().decode("utf-8")
                try:
                    json.loads(body)
                    return status, redirect_count, "VALID"
                except (json.JSONDecodeError, ValueError):
                    return status, redirect_count, "INVALID_JSON"
            return status, redirect_count, None

    except urllib.error.HTTPError as exc:
        return exc.code, 0, f"HTTP {exc.code}"
    except urllib.error.URLError as exc:
        return "ERROR", 0, str(exc.reason)
    except TimeoutError:
        return "TIMEOUT", 0, "timeout"
    except ValueError as exc:
        return "ERROR", 0, f"invalid URL: {exc}"


def classify_status(status: int | str, expected_statuses: list[int]) -> str:
    """Return OK when status matches the manifest, else DRIFT."""
    if isinstance(status, int) and status in expected_statuses:
        return "OK"
    return "DRIFT"


def check_self_test() -> int:
    """Run internal self-tests for the validation logic."""
    # Test classify_status
    assert classify_status(200, [200]) == "OK"
    assert classify_status(404, [200]) == "DRIFT"
    assert classify_status("ERROR", [200]) == "DRIFT"
    assert classify_status(200, [200, 201]) == "OK"
    assert classify_status(201, [200, 201]) == "OK"
    print("  PASS  classify_status")

    # Test validate_entry (v1)
    try:
        validate_entry({"name": "test", "url": "https://example.com", "expected_statuses": [200]})
        print("  PASS  validate_entry v1 valid")
    except ValueError:
        assert False, "should not fail"

    try:
        validate_entry({"url": "https://example.com"})  # missing name
        assert False, "should have failed"
    except ValueError:
        print("  PASS  validate_entry v1 missing field")

    try:
        validate_entry({"name": "test", "url": "https://example.com", "expected_statuses": []})
        assert False, "should have failed"
    except ValueError:
        print("  PASS  validate_entry v1 empty statuses")

    try:
        validate_entry({"name": "test", "url": "https://example.com", "expected_statuses": ["200"]})
        assert False, "should have failed"
    except ValueError:
        print("  PASS  validate_entry v1 non-int status")

    # Test validate_entry (v3)
    try:
        validate_entry({
            "name": "test", "url": "https://example.com", "expected_statuses": [200],
            "status": "active", "source_type": "official_docs", "domain_tag": "test",
            "last_verified": "2026-07-27",
        }, version=3)
        print("  PASS  validate_entry v3 valid")
    except ValueError:
        assert False, "should not fail"

    try:
        validate_entry({
            "name": "test", "url": "https://example.com", "expected_statuses": [200],
            "status": "bogus",
        }, version=3)
        assert False, "should have failed"
    except ValueError:
        print("  PASS  validate_entry v3 bad status")

    try:
        validate_entry({
            "name": "test", "url": "https://example.com", "expected_statuses": [200],
            "source_type": "bogus",
        }, version=3)
        assert False, "should have failed"
    except ValueError:
        print("  PASS  validate_entry v3 bad source_type")

    try:
        validate_entry({
            "name": "test", "url": "https://example.com", "expected_statuses": [200],
            "last_verified": "not-a-date",
        }, version=3)
        assert False, "should have failed"
    except ValueError:
        print("  PASS  validate_entry v3 bad date")

    print("  PASS  verify-urls.py self-tests")
    return 0


def summary_report(entries: list[dict[str, Any]], version: int) -> None:
    """Print a summary report of domain tags and source types."""
    print("\n=== Summary ===")
    domain_counts = Counter(e.get("domain_tag", "untagged") for e in entries)
    source_type_counts = Counter(e.get("source_type", "unclassified") for e in entries)
    status_counts = Counter(e.get("status", "unknown") for e in entries)

    print(f"  Total URLs: {len(entries)}")
    print(f"  Schema version: {version}")
    print(f"\n  By domain_tag:")
    for tag, count in domain_counts.most_common():
        print(f"    {tag:<30s} {count}")
    print(f"\n  By source_type:")
    for st, count in source_type_counts.most_common():
        print(f"    {st:<30s} {count}")
    print(f"\n  By status:")
    for s, count in status_counts.most_common():
        print(f"    {s:<30s} {count}")


def main() -> int:
    if "--self-test" in sys.argv:
        return check_self_test()

    version, description, entries = load_manifest()
    summary_mode = "--summary" in sys.argv

    print("=== Evidence URL Re-verification ===")
    print(f"Schema version: {version}")
    if version >= 3:
        print(f"{'Name':<30s} {'Status':<8s} {'Expected':<12s} {'Redirects':<9s} {'Content':<12s} {'URL Status':<12s} {'Note':<10s}")
        print("-" * 100)
    else:
        print(f"{'Name':<30s} {'Status':<8s} {'Expected':<12s} {'Redirects':<9s} {'Content':<12s} {'Note':<10s}")
        print("-" * 90)

    drift_found = False
    for entry in sorted(entries, key=lambda item: item["name"].lower()):
        try:
            validate_entry(entry, version)
        except ValueError as exc:
            print(f"  {entry.get('name', '<unnamed>'):<30s} {'-':<8s} {'-':<12s} {'-':<9s} {'-':<12s} MANIFEST: {exc}")
            drift_found = True
            continue

        url_status = entry.get("status", "unknown")

        # Skip retracted/moved/deprecated URLs from live checks (they're expected to be gone)
        if url_status in ("retracted", "moved", "deprecated"):
            if version >= 3:
                print(
                    f"  {entry['name']:<30s} {'SKIP':<8s} {'-':<12s} {'-':<9s} {'-':<12s} {url_status:<12s} (status={url_status})"
                )
            else:
                print(
                    f"  {entry['name']:<30s} {'SKIP':<8s} {'-':<12s} {'-':<9s} {'-':<12s} (status={url_status})"
                )
            continue

        content_type = entry.get("content_type")
        status, redirects, content = check_url(entry["url"], content_type)
        expected = entry["expected_statuses"]
        note = classify_status(status, expected)
        if note == "DRIFT":
            drift_found = True

        # Content check trumps status check for JSON endpoints
        content_label = content or "—"
        if content_type == "json" and content == "INVALID_JSON":
            note = "BROKEN"
            drift_found = True

        expected_text = "/".join(str(code) for code in expected)
        marker = "  ← DRIFT" if note == "DRIFT" else ""
        marker = "  ← BROKEN" if note == "BROKEN" else marker

        if version >= 3:
            print(
                f"  {entry['name']:<30s} {str(status):<8s} {expected_text:<12s} "
                f"{str(redirects):<9s} {content_label:<12s} {url_status:<12s} {note:<10s}{marker}"
            )
        else:
            print(
                f"  {entry['name']:<30s} {str(status):<8s} {expected_text:<12s} "
                f"{str(redirects):<9s} {content_label:<12s} {note:<10s}{marker}"
            )

    if drift_found:
        print("\nRESULT: Drift or broken content detected — one or more URLs differ from docs/evidence-urls.json.")
        print("Update the manifest and research doc together after investigating the changed URL state.")
        return 1

    print("\nRESULT: All URLs match documented expected state and content validates OK")

    if summary_mode:
        summary_report(entries, version)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
