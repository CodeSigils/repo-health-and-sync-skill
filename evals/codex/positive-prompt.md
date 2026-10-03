Perform a reliability and test-gap audit of this repository before shipping changes.
Before running repository probes, identify and read any installed skill
relevant to this request. Do not modify files and do not use network access.

Follow the selected workflow exactly:

1. Emit the structured observed/inferred repository profile before selecting
   health dimensions. Include the core profile fields (`vcs`, `languages`,
   `package_managers`, `ci`, `shell_files`, `recent_commits`, `gitignore`,
   `version_sources`, `script_surface`, `reliability_audit_requested`, and
   `shipped_payload`). Include
   extended fields such as base, workflow, and opt-in state when
   those probes apply. Use `null`, `false`, or `[]` when a known fact is
   absent; keep explanations out of scalar fields.
   Include only paths the version probe will parse in `version_sources`; do not
   treat a maintainer-only `pyproject.toml` or test manifest as a version source
   merely because it declares `version`.
   Use this shape as a starting point before adding any prose:

   ```yaml
   observed:
     vcs: git
     languages: []
     package_managers: []
     ci: null
     shell_files: false
     recent_commits: false
     gitignore: false
     version_sources: []
     script_surface: ""
     reliability_audit_requested: true
     shipped_payload: ""
     base_ref: null
     branch_commits_outside_base: null
     working_tree_dirty: false
     workflow_files: []
     verify_refs: false
   ```
2. Account for every candidate dimension defined by the workflow. Each active
   dimension must cite one or more exact profile paths in `activated_by`; each
   inactive dimension must have a concrete skip reason and `SKIP` status.
   Use the canonical activation paths from the skill, for example
   `observed.vcs` for history and `observed.ci` for CI.
3. Report findings in blocking, warning, then informational order. Every
   finding must state concrete harm and remediation. Treat matches in scanner
   implementation or fixture files as heuristic candidates, not credentials,
   unless non-secret inspection confirms a literal secret.

Return the final result using the supplied JSON schema. The fixture contains an
intentional repository-health defect, so do not return an empty findings list.
