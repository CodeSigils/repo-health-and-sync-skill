#!/usr/bin/env bash
# sync-payload.sh — Regenerate the skill payload directory from source.
#
# Reads scripts/payload-manifest.json and syncs each declared file/directory
# into skills/repo-health-and-sync-skill/. Removes orphaned files.
#
# Usage:
#   bash scripts/sync-payload.sh               # sync in-place
#   bash scripts/sync-payload.sh --ci           # exit 1 on drift (CI mode)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="$ROOT/scripts/payload-manifest.json"
PAYLOAD_DIR="$ROOT/skills/repo-health-and-sync-skill"
CI_MODE=false

[ "${1:-}" = "--ci" ] && CI_MODE=true

if [ ! -f "$MANIFEST" ]; then
    echo "FAIL: $MANIFEST not found"
    exit 1
fi

if $CI_MODE; then
    SYNC_DIR=$(mktemp -d /tmp/repo-health-payload-check-XXXXXX)
    trap 'rm -rf "$SYNC_DIR"' EXIT HUP INT TERM
    echo "Checking skill payload against manifest..."
else
    SYNC_DIR="$PAYLOAD_DIR"
    echo "Syncing skill payload from manifest..."
fi
DRIFT=false

# Helper: compute relative path and check if file is covered by manifest
is_covered() {
    local rel="$1"
    # files entries are relative to root
    for f in $(python3 -c "import json; d=json.load(open('$MANIFEST')); print('\n'.join(str(x) for x in d.get('files',[])))" 2>/dev/null); do
        [ "$rel" = "$f" ] && return 0
    done
    # scripts entries are relative to scripts/ dir
    for s in $(python3 -c "import json; d=json.load(open('$MANIFEST')); print('\n'.join(str(x) for x in d.get('scripts',[])))" 2>/dev/null); do
        [ "$rel" = "scripts/$s" ] && return 0
    done
    # references is "*" = mirror everything from references/
    local ref_mode
    ref_mode=$(python3 -c "import json; d=json.load(open('$MANIFEST')); r=d.get('references',''); print(r if isinstance(r,str) else '')" 2>/dev/null)
    if [ "$ref_mode" = "*" ]; then
        case "$rel" in
            references/*) return 0 ;;
        esac
    fi
    return 1
}

# --- Sync individual files ---
echo "  Files..."
for f in $(python3 -c "
import json
d=json.load(open('$MANIFEST'))
print('\n'.join(str(x) for x in d.get('files',[])))
" 2>/dev/null); do
    source="$ROOT/$f"
    target="$SYNC_DIR/$f"
    if [ ! -f "$source" ]; then
        echo "    MISSING source: $f"
        DRIFT=true
        continue
    fi
    mkdir -p "$(dirname "$target")"
    install -m 644 "$source" "$target"
done

# --- Sync scripts ---
echo "  Scripts..."
for s in $(python3 -c "
import json
d=json.load(open('$MANIFEST'))
print('\n'.join(str(x) for x in d.get('scripts',[])))
" 2>/dev/null); do
    source="$ROOT/scripts/$s"
    target="$SYNC_DIR/scripts/$s"
    if [ ! -f "$source" ]; then
        echo "    MISSING source: scripts/$s"
        DRIFT=true
        continue
    fi
    mkdir -p "$(dirname "$target")"
    # Preserve execute permission if set
    if [ -x "$source" ]; then
        install -m 755 "$source" "$target"
    else
        install -m 644 "$source" "$target"
    fi
done

# --- Sync references directory (mirror) ---
ref_mode=$(python3 -c "
import json
d=json.load(open('$MANIFEST'))
r=d.get('references','')
if isinstance(r,str) and r == '*':
    print('mirror')
" 2>/dev/null)
if [ "$ref_mode" = "mirror" ]; then
    echo "  References (mirror)..."
    mkdir -p "$SYNC_DIR/references"
    # Remove existing reference files first to catch deletions
    find "$SYNC_DIR/references" -type f -delete 2>/dev/null || true
    cp "$ROOT/skills/repo-health-and-sync-skill/references/"*.md "$SYNC_DIR/references/"
fi

# --- Remove orphaned files ---
if $CI_MODE; then
    echo "  Comparing payload..."
    if ! diff -rq "$SYNC_DIR" "$PAYLOAD_DIR" >/tmp/repo-health-payload-diff.$$ 2>&1; then
        sed 's/^/    /' /tmp/repo-health-payload-diff.$$
        rm -f /tmp/repo-health-payload-diff.$$
        DRIFT=true
    else
        rm -f /tmp/repo-health-payload-diff.$$
    fi
    orphans=0
else
    echo "  Cleaning orphaned files..."
    orphans=0
    while IFS= read -r -d '' f; do
        relpath="$f"
        # shellcheck disable=SC2295
        rel="${relpath#$PAYLOAD_DIR/}"
        if ! is_covered "$rel"; then
            echo "    ORPHANED: $rel"
            rm -f "$f"
            orphans=$((orphans + 1))
        fi
    done < <(find "$PAYLOAD_DIR" -type f -print0)

    # Clean empty directories
    find "$PAYLOAD_DIR" -type d -empty -delete 2>/dev/null || true
fi

echo ""
if [ "$orphans" -gt 0 ]; then
    echo "Removed $orphans orphaned file(s)"
    DRIFT=true
fi
if $DRIFT; then
    echo ""
    echo "DRIFT DETECTED — see above"
    if $CI_MODE; then
        exit 1
    fi
else
    echo "Payload is in sync with manifest"
fi
