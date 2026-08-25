#!/bin/zsh
set -u
ROOT="${OFFDATA_PACKAGE_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"
issues=()
command -v hermes >/dev/null || issues+=("hermes-missing")
if command -v hermes >/dev/null; then hermes cron status >/tmp/offdata-cron-status.$$ 2>&1 || issues+=("cron-unhealthy"); fi
if command -v pg_isready >/dev/null && [[ -n "${OFFDATA_DATABASE_URL:-}" ]]; then pg_isready -d "$OFFDATA_DATABASE_URL" >/dev/null 2>&1 || issues+=("postgres-unready"); fi
disk=$(df -Pk "$ROOT" | awk 'NR==2{gsub("%","",$5);print $5}')
[[ ${disk:-0} -ge 90 ]] && issues+=("disk-${disk}pct")
backup_dir="${OFFDATA_BACKUP_DIR:-$HOME/.offdata/backups}";latest=$(ls -t "$backup_dir"/offdata-*.tar.gz 2>/dev/null | head -1 || true)
if [[ -z "$latest" ]]; then issues+=("backup-missing"); else age=$(( $(date +%s) - $(stat -f %m "$latest") )); [[ $age -gt 172800 ]] && issues+=("backup-stale"); fi
if (( ${#issues[@]} )); then echo "OFF/DATA HEALTH ALERT: ${issues[*]}"; exit 2; fi
exit 0
