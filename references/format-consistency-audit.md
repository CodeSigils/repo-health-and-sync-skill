# Format Consistency Audit

Scan markdown files against a project-defined template standard.
Part of repo-health Phase B — complements B10 (metadata audit)
by checking file-internal structure rather than file existence.

## Why

Projects that define a document template or convention (frontmatter
fields, required sections, labelling rules) rely on agents and humans
following it. Without periodic audit, deviations accumulate silently.
One-off fixes don't scale — a systematic scan reveals the scope of drift.

## Checks (generalized)

Run these against every `.md` file in the project tree, excluding
auto-generated paths (`.git/`, `node_modules/`, `.venv/`, etc.):

| Check | What it looks for | Severity |
|-------|-------------------|----------|
| Frontmatter opener | File starts with `---` on line 1 | WARNING |
| Required frontmatter fields | e.g. `tags:`, `aliases:`, `created:`, `verified:` | WARNING |
| Forbidden path patterns | `~/`, `/home/`, `/root/` in content | WARNING |
| Code fence labelling | Every opening ``` has a language specifier | INFO |
| Sources section | `## Sources` table present | INFO (skip for root-level reflective notes) |
| Related section | `## Related` cross-references present | INFO (optional) |
| Open Questions section | `## Open Questions` with markers | INFO (optional) |
| Confidence markers | `✅ Confirmed:` / `🔶 Inferred:` correctly used | INFO |
| Unlabelled speculation | `Inferred:` claims without the `🔶` marker | WARNING |

## Severity guide

- **BLOCKING** when missing frontmatter would cause a runtime parser
  failure (no `name` or `description` in SKILL.md frontmatter).
- **WARNING** when deviation creates subtle drift (forbidden paths,
  missing required fields, unlabelled speculation). No runtime fails,
  but a future reader or agent loses context.
- **INFO** for optional conventions that the project prefers but
  doesn't strictly enforce.

## How to run

```bash
# 1. Identify the template standard (read NOTE-TEMPLATE.md, STYLE.md,
#    or the project's convention file first).
# 2. Scan all .md files:
find . -name '*.md' -not -path './.git/*' | while read -r f; do
  # Check frontmatter
  head -1 "$f" | grep -q '^---' || echo "MISSING FRONTMATTER: $f"
  # Check forbidden paths
  grep -n '~/' "$f" && echo "FORBIDDEN PATH: $f"
  # Check unlabelled code fences
  awk '/^```$/{print FILENAME":"NR": unlabelled fence"}' "$f"
done
```

## Open-question cross-reference

For projects with an aggregated open-questions index
(`OPEN-QUESTIONS.md`, `research-debt.md`, etc.):

1. Grep all source files for `❓` markers:
   ```bash
   grep -rn '❓' --include='*.md' . | grep -v OPEN-QUESTIONS.md
   ```
2. Compare each found question against the aggregator.
3. Report any ❓ marker that has no corresponding entry in the index.

This catches the common drift pattern where a note adds a new open
question but the aggregator is not updated.

## When to skip

- Projects with no formal document convention (plain prose, no template).
- Single-file repos where the convention is self-evident.
- Projects that explicitly opt out via `.repo-health.json`.
