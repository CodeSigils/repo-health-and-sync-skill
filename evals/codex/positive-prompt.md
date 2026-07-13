Audit this repository before release. Before running repository probes,
identify and read any installed skill relevant to this request. Do not modify
files and do not use network access.

Follow the selected workflow exactly:

1. Emit the structured observed/inferred repository profile before selecting
   health dimensions.
2. Account for every candidate dimension defined by the workflow. Each active
   dimension must cite one or more exact profile paths in `activated_by`; each
   inactive dimension must have a concrete skip reason and `SKIP` status.
3. Report findings in blocking, warning, then informational order. Every
   finding must state concrete harm and remediation.

Return the final result using the supplied JSON schema. The fixture contains an
intentional repository-health defect, so do not return an empty findings list.
