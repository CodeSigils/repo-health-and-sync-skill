"""Validate local repo-health behavioral eval contracts."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any

from _common import read_json, validate_dimensions

# Activation predicates the eval fixtures can be checked against, keyed by
# dimension. A dimension whose predicate the profile does not satisfy cannot be
# active: the probe would skip it at runtime, so the fixture would claim work
# that never happens.
#
# Only observed fields appear here, because that is all validate_activation
# reads. The remaining dimensions are excluded deliberately: history_hygiene is
# unconditional, external_reference_health needs an environment flag no fixture
# records, and cross_platform also reads inferred.platform_requirements.
ACTIVATION_PREDICATES = {
    "version_alignment": lambda observed: len(observed.get("version_sources") or []) >= 2,
    "shell_correctness": lambda observed: bool(observed.get("shell_files")),
    "commit_quality": lambda observed: bool(observed.get("recent_commits")),
    "ci_efficiency": lambda observed: bool(observed.get("ci")),
    "file_coverage": lambda observed: bool(observed.get("gitignore")),
    "reliability_test_gaps": lambda observed: bool(
        observed.get("reliability_audit_requested")
    ),
    "attribution_drift": lambda observed: bool(
        observed.get("branch_commits_outside_base")
    ),
}

DEFAULT_CASE = Path("evals/cases/repo-health-scan.json")
DIMENSIONS = {
    "history_hygiene",
    "shell_correctness",
    "version_alignment",
    "commit_quality",
    "ci_efficiency",
    "cross_platform",
    "attribution_drift",
    "file_coverage",
    "external_reference_health",
    "reliability_test_gaps",
}

REQUIRED_OBSERVED_FIELDS = {
    "vcs",
    "languages",
    "package_managers",
    "ci",
    "shell_files",
    "recent_commits",
    "gitignore",
    "version_sources",
    "script_surface",
    "reliability_audit_requested",
    "shipped_payload",
}


def validate_activation(
    active: list[dict[str, Any]],
    observed: Any,
    prefix: str = "",
) -> list[str]:
    """Return errors for active dimensions the profile cannot activate."""
    if not isinstance(observed, dict):
        return []
    errors: list[str] = []
    for item in active:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        predicate = ACTIVATION_PREDICATES.get(name) if isinstance(name, str) else None
        if predicate is not None and not predicate(observed):
            errors.append(
                f"{prefix}active dimension {name} is not activated by the profile"
            )
    return errors


def validate_case(data: Any) -> list[str]:
    """Return structural and behavioral-contract errors."""
    if not isinstance(data, dict):
        return ["case root must be an object"]

    errors: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    if data.get("skill_name") != "repo-health-scan":
        errors.append("skill_name must be repo-health-scan")

    trigger = data.get("trigger")
    if not isinstance(trigger, dict):
        errors.append("trigger must be an object")
    else:
        for kind in ("positive", "negative"):
            prompts = trigger.get(kind)
            if not isinstance(prompts, list) or not prompts:
                errors.append(f"trigger.{kind} must be a non-empty list")
                continue
            for index, prompt in enumerate(prompts):
                if not isinstance(prompt, dict) or not isinstance(
                    prompt.get("prompt"), str
                ):
                    errors.append(f"trigger.{kind}[{index}] must contain a prompt")
                    continue
                if kind == "positive" and (
                    not isinstance(prompt.get("top_k"), int) or prompt["top_k"] < 1
                ):
                    errors.append(
                        f"trigger.positive[{index}].top_k must be a positive integer"
                    )
                if kind == "negative" and not isinstance(prompt.get("owner"), str):
                    errors.append(f"trigger.negative[{index}] must contain an owner")

    contract = data.get("workflow_contract")
    if not isinstance(contract, dict):
        errors.append("workflow_contract must be an object")
    else:
        if contract.get("ordered_events") != ["profile", "dimension_checks", "report"]:
            errors.append(
                "workflow_contract.ordered_events must preserve profile -> dimension_checks -> report"
            )
        if contract.get("profile_before_dimension_checks") is not True:
            errors.append(
                "workflow_contract must require a profile before dimension checks"
            )
        if contract.get("require_activation_evidence") is not True:
            errors.append(
                "workflow_contract must require dimension activation evidence"
            )
        if contract.get("account_for_all_dimensions") is not True:
            errors.append(
                "workflow_contract must account for every candidate dimension"
            )
        required_report_fields = {
            "concrete_harm",
            "remediation",
            "blocking_findings_first",
            "no_pass_for_skipped_dimensions",
        }
        report_requirements = contract.get("report_requirements")
        if not isinstance(
            report_requirements, list
        ) or not required_report_fields.issubset(report_requirements):
            errors.append(
                "workflow_contract.report_requirements must contain all required reporting fields"
            )

    fixtures = data.get("fixtures")
    if not isinstance(fixtures, list) or len(fixtures) < 2:
        errors.append("fixtures must contain at least two repository profiles")
        return errors

    repo_types: set[str] = set()
    for index, fixture in enumerate(fixtures):
        prefix = f"fixtures[{index}]"
        if not isinstance(fixture, dict):
            errors.append(f"{prefix} must be an object")
            continue

        profile = fixture.get("profile")
        if not isinstance(profile, dict):
            errors.append(f"{prefix}.profile must be an object")
            continue
        observed = profile.get("observed")
        inferred = profile.get("inferred")
        if not isinstance(observed, dict) or not observed:
            errors.append(f"{prefix}.profile.observed must be a non-empty object")
        else:
            missing = sorted(REQUIRED_OBSERVED_FIELDS - observed.keys())
            if missing:
                errors.append(
                    f"{prefix}.profile.observed is missing required fields: {missing}"
                )
        if not isinstance(inferred, dict) or not inferred:
            errors.append(f"{prefix}.profile.inferred must be a non-empty object")
            continue
        repo_type = inferred.get("repo_type")
        if isinstance(repo_type, str):
            repo_types.add(repo_type)

        expected = fixture.get("expected")
        if not isinstance(expected, dict):
            errors.append(f"{prefix}.expected must be an object")
            continue
        active = expected.get("active_dimensions")
        skipped = expected.get("skipped_dimensions")
        if not isinstance(active, list) or not active:
            errors.append(f"{prefix}.expected.active_dimensions must be non-empty")
            active = []
        if not isinstance(skipped, list) or not skipped:
            errors.append(f"{prefix}.expected.skipped_dimensions must be non-empty")
            skipped = []

        errors.extend(validate_dimensions(
            active, skipped, DIMENSIONS, profile, prefix=f"{prefix}.",
        ))
        errors.extend(validate_activation(active, observed, prefix=f"{prefix}."))

    if "skill-pack" not in repo_types:
        errors.append("fixtures must include a skill-pack profile")
    if repo_types == {"skill-pack"}:
        errors.append("fixtures must include a non-skill repository profile")
    return errors


def run_self_tests() -> int:
    """Exercise success and missing-activation-evidence failures."""
    # An independent literal, not derived from the constant it locks: a fixture
    # only has to be a superset of the required fields, so dropping a name from
    # REQUIRED_OBSERVED_FIELDS weakens every check without failing any.
    expected_required = {
        "vcs",
        "languages",
        "package_managers",
        "ci",
        "shell_files",
        "recent_commits",
        "gitignore",
        "version_sources",
        "script_surface",
        "reliability_audit_requested",
        "shipped_payload",
    }
    assert REQUIRED_OBSERVED_FIELDS == expected_required, (
        f"REQUIRED_OBSERVED_FIELDS drifted: {sorted(REQUIRED_OBSERVED_FIELDS)}"
    )
    observed_defaults = {
        "vcs": "git",
        "languages": [],
        "package_managers": [],
        "ci": None,
        "shell_files": False,
        "recent_commits": False,
        "gitignore": False,
        "version_sources": [],
        "script_surface": "none",
        "reliability_audit_requested": False,
        "shipped_payload": "none",
    }
    valid = {
        "schema_version": 1,
        "skill_name": "repo-health-scan",
        "trigger": {
            "positive": [{"prompt": "audit", "top_k": 1}],
            "negative": [{"prompt": "fix", "owner": "implementation"}],
        },
        "workflow_contract": {
            "ordered_events": ["profile", "dimension_checks", "report"],
            "profile_before_dimension_checks": True,
            "require_activation_evidence": True,
            "account_for_all_dimensions": True,
            "report_requirements": [
                "concrete_harm",
                "remediation",
                "blocking_findings_first",
                "no_pass_for_skipped_dimensions",
            ],
        },
        "fixtures": [
            {
                "profile": {
                    "observed": observed_defaults.copy(),
                    "inferred": {"repo_type": "skill-pack"},
                },
                "expected": {
                    "active_dimensions": [
                        {"name": "history_hygiene", "activated_by": ["observed.vcs"]}
                    ],
                    "skipped_dimensions": [
                        {"name": name, "skip_reason": "not activated"}
                        for name in sorted(DIMENSIONS - {"history_hygiene"})
                    ],
                },
            },
            {
                "profile": {
                    "observed": observed_defaults.copy(),
                    "inferred": {"repo_type": "library"},
                },
                "expected": {
                    "active_dimensions": [
                        {"name": "history_hygiene", "activated_by": ["observed.vcs"]}
                    ],
                    "skipped_dimensions": [
                        {"name": name, "skip_reason": "not activated"}
                        for name in sorted(DIMENSIONS - {"history_hygiene"})
                    ],
                },
            },
        ],
    }
    assert validate_case(valid) == []
    for field in sorted(expected_required):
        without = copy.deepcopy(valid)
        del without["fixtures"][0]["profile"]["observed"][field]
        assert any(
            "missing required fields" in error and field in error
            for error in validate_case(without)
        ), f"profile.observed.{field} is declared required but not enforced"
    valid["fixtures"][0]["expected"]["active_dimensions"][0]["activated_by"] = []
    assert any("lacks activated_by evidence" in error for error in validate_case(valid))

    # Every predicate must reject a profile that does not satisfy it, or the
    # guard is decorative. Defaults above satisfy nothing, so each dimension is
    # added as active against a profile that leaves its predicate false.
    for name, predicate in sorted(ACTIVATION_PREDICATES.items()):
        unsatisfied = copy.deepcopy(valid)
        unsatisfied["fixtures"][0]["expected"]["active_dimensions"].append(
            {"name": name, "activated_by": ["observed.vcs"]}
        )
        assert not predicate(observed_defaults), (
            f"{name} predicate is satisfied by the empty default profile"
        )
        assert any(
            f"active dimension {name} is not activated by the profile" in error
            for error in validate_case(unsatisfied)
        ), f"{name} activation is not enforced"

    # And a satisfied profile must not produce the error.
    satisfied = copy.deepcopy(valid)
    satisfied["fixtures"][0]["profile"]["observed"].update(
        {
            "version_sources": ["pyproject.toml", "package.json"],
            "shell_files": True,
            "recent_commits": True,
            "ci": "GitHub Actions",
            "gitignore": True,
            "reliability_audit_requested": True,
            "branch_commits_outside_base": 1,
        }
    )
    satisfied["fixtures"][0]["expected"]["active_dimensions"] = [
        {"name": name, "activated_by": ["observed.vcs"]}
        for name in sorted(ACTIVATION_PREDICATES)
    ]
    satisfied["fixtures"][0]["expected"]["skipped_dimensions"] = [
        {"name": name, "skip_reason": "not activated"}
        for name in sorted(DIMENSIONS - set(ACTIVATION_PREDICATES))
    ]
    assert validate_case(satisfied) == [], validate_case(satisfied)

    print("PASS: validate-evals.py self-tests")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", nargs="?", type=Path, default=DEFAULT_CASE)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        return run_self_tests()
    try:
        data = read_json(args.case)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: cannot read {args.case}: {exc}", file=sys.stderr)
        return 1
    errors = validate_case(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"PASS: eval contract valid: {args.case}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
