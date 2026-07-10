# `.githooks/` Audit Reference

Many repos use `git config core.hooksPath .githooks` instead of the default
`.git/hooks/` directory. This lets them version-control hook scripts.

## Detection

```bash
test -d .githooks || echo 'no .githooks'
git config core.hooksPath 2>/dev/null || echo 'default hooks path'
```

## What to check

1. **Shellcheck**: `.githooks/*` files are shell scripts (shebang-based) even
   without `.sh` extensions. Run shellcheck on them.
2. **Portability**: Same cross-platform patterns as B8 — check for `which`,
   `grep -P`, `sed -i` without backup, `echo` with escapes, hardcoded
   `/bin/bash`, octal `\012`, `find -exit`, `flock`.
3. **Tracked (not gitignored)**: `.githooks/` is intentionally versioned.
   It MUST NOT appear in `.gitignore`.
4. **Install command**: The repo should document how to enable the hooks:
   `git config core.hooksPath .githooks`
5. **Quality**: Hook scripts must handle all exit paths (success/failure).
   Pre-commit hooks should be fast. Commit-msg hooks must not modify the
   commit message file unexpectedly.

## Repos using `.githooks/` (from cross-repo survey, July 2026)

- `hermes-skill-hq` — `pre-push`, `commit-msg`, etc.
- `neovim-latest-ubuntu` — `prepare-commit-msg`
- `zero-md-formatter` — `.githooks/` directory
