# B2/B8/B10 — `.githooks/` Integration Points

This reference documents where `.githooks/` detection should be inserted
into the SKILL.md body. These changes are in the canonical repo source
(`~/projects/repo-health-and-sync-skill/skills/repo-health-and-sync-skill/`)
but NOT yet in the installed SKILL.md due to a name-collision blocker.

## B2 integration (Shellcheck)

Replace the current `find` command and skip logic with a dual-path search:

```bash
find . -name '*.sh' -not -path '*/.git/*'
find . -path './.githooks/*' -type f -not -path '*/.git/*'
```

Combine both lists, deduplicate, and shellcheck every file.
The `.githooks/` files use shebangs not `.sh` extensions.

The "If no .sh files are found, skip this step" guard must also
check `.githooks/` — skip only when BOTH are empty.

## B8 integration (Cross-platform shell audit)

Extend the `.sh` file scan to also find `.githooks/*` files.
The same portable-pattern detection applies.

The "If no .sh files are found, skip this step" at the end of B8
must be updated to include `.githooks/` files in the check.

## B10 integration (gitignore audit)

Add a seventh category:

```
| 7 | `.githooks/` tracked dir | If `.githooks/` exists, verify it is NOT gitignored. These are intentionally-versioned hook scripts. Flag as WARNING if gitignored; if absent, skip silently. |
```

## References section

Add entries:
- `.githooks/ Audit Reference` → `references/dot-githooks-audit.md`
- `Cross-Repo Survey (July 2026)` → `references/cross-repo-survey-2026-07.md`
