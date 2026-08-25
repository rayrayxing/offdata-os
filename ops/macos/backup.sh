#!/bin/zsh
set -euo pipefail
ROOT="${OFFDATA_PACKAGE_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}";OUT="${OFFDATA_BACKUP_DIR:-$HOME/.offdata/backups}";mkdir -p "$OUT";TS=$(date +%Y%m%d-%H%M%S);TMP=$(mktemp -d);trap 'rm -rf "$TMP"' EXIT
if [[ -n "${OFFDATA_DATABASE_URL:-}" ]] && command -v pg_dump >/dev/null; then pg_dump "$OFFDATA_DATABASE_URL" -Fc -f "$TMP/venturebrain.dump"; else echo "database backup skipped: OFFDATA_DATABASE_URL/pg_dump unavailable" > "$TMP/database.WARNING"; fi
mkdir -p "$TMP/hermes" "$TMP/package-state"
cp -R "$HOME/.hermes/cron" "$TMP/hermes/" 2>/dev/null || true
cp -R "$HOME/.hermes/skills" "$TMP/hermes/" 2>/dev/null || true
cp -R "$ROOT/state"/. "$TMP/package-state/" 2>/dev/null || true
cp "$ROOT/CHECKSUMS.sha256" "$TMP/" 2>/dev/null || true
tar -czf "$OUT/offdata-$TS.tar.gz" -C "$TMP" .
find "$OUT" -name 'offdata-*.tar.gz' -mtime +14 -delete
printf 'OFF/DATA backup complete: %s\n' "$OUT/offdata-$TS.tar.gz"
