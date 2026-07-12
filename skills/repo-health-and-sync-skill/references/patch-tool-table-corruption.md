# portability: allow-platform-ref
# Patch-Tool Table Pipe Corruption

The Hermes `patch` tool (find-and-replace text editor) can corrupt GFM table
rows when `|` (pipe) characters appear in the `old_string` or `new_string`.
This is not a formatter bug — the formatter correctly handles all GFM table
patterns including `||` adjacent pipes.

## Root cause

The `patch` tool matches and replaces raw byte sequences. In a table row like
`| B   | 30  |`, matching `| B   |` is ambiguous because `|` serves as both
a cell boundary and a literal character in the matching context. If the table
also contains adjacent pipes (`||`) nearby, the matching algorithm can anchor
on the wrong pipe, producing `|| B   |` instead of `| B   |`.

This is the same class of problem as backslash-escaping in `patch` (documented
in `safe-editing.md`). Both `\` and `|` have special meaning in `patch`'s
matching context.

## Symptoms

- Double-pipe `||` appears where a single `|` was intended in table rows
- Only appears after `write_file` or `patch` operations on files with tables
- The markdown formatter's `--check` correctly flags these as adjacent pipes
- Re-running format does not fix it — the corruption is in the source

## Defense layers

1. **Post-write hook** — Hermes `config.yaml` hook runs `--check` after every
   `write_file`, blocking corrupted tables before they reach git.
2. **Manual repair** — `node <skill-dir>/src/index.js --fix <file>` repairs.
3. **Prevention** — For table edits, prefer `write_file` with full file content
   over `patch` with pipe-containing anchors.

## References

- GFM spec §4.10: https://github.github.com/gfm/#tables-extension-