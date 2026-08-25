#!/bin/zsh
set -euo pipefail
[[ $# -ge 2 && "$1" == "--confirm" ]] || { echo 'Usage: restore.sh --confirm /path/offdata-backup.tar.gz'; exit 2; }
ARCHIVE="$2";[[ -f "$ARCHIVE" ]] || { echo 'archive missing'; exit 2; };[[ -n "${RESTORE_DATABASE_URL:-}" ]] || { echo 'RESTORE_DATABASE_URL required'; exit 2; }
if [[ "${RESTORE_DATABASE_URL}" == "${OFFDATA_DATABASE_URL:-}" && "${ALLOW_INPLACE_RESTORE:-NO}" != "YES" ]]; then echo 'refusing in-place restore without ALLOW_INPLACE_RESTORE=YES'; exit 3; fi
TMP=$(mktemp -d);trap 'rm -rf "$TMP"' EXIT;tar -xzf "$ARCHIVE" -C "$TMP"
[[ -f "$TMP/venturebrain.dump" ]] && pg_restore --clean --if-exists --no-owner -d "$RESTORE_DATABASE_URL" "$TMP/venturebrain.dump"
echo 'Database restored to RESTORE_DATABASE_URL. Hermes/profile state is intentionally not overwritten automatically; inspect archive/hermes before copying.'
