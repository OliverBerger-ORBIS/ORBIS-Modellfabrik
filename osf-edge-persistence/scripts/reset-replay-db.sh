#!/usr/bin/env bash
# Manual reset of the *local* edge-persistence DB (Replay scratch).
# Never invoked automatically on replay start — different sessions with
# different NFC ids are meant to accumulate. Run this only when you want
# a clean slate or to drop a repeated replay of the same NFC.
#
# Usage (from repo root or this directory):
#   bash osf-edge-persistence/scripts/reset-replay-db.sh
#   bash osf-edge-persistence/scripts/reset-replay-db.sh --nfc 92e0ad91595f63,78d10489b38ed8
#   bash osf-edge-persistence/scripts/reset-replay-db.sh --yes
#
set -euo pipefail

CONTAINER="${OSF_EDGE_POSTGRES_CONTAINER:-osf-edge-postgres}"
PGUSER="${POSTGRES_USER:-osf}"
PGDB="${POSTGRES_DB:-osf}"
YES=0
NFC_LIST=""

usage() {
  sed -n '2,14p' "$0"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes|-y)
      YES=1
      shift
      ;;
    --nfc)
      NFC_LIST="${2:-}"
      shift 2
      ;;
    --nfc=*)
      NFC_LIST="${1#--nfc=}"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage
      exit 1
      ;;
  esac
done

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "Postgres container '$CONTAINER' is not running." >&2
  echo "Start Replay stack first: cd osf-edge-persistence && cp env.replay .env && docker compose up -d" >&2
  exit 1
fi

run_sql() {
  docker exec -i "$CONTAINER" psql -U "$PGUSER" -d "$PGDB" -v ON_ERROR_STOP=1
}

confirm() {
  local prompt="$1"
  if [[ "$YES" -eq 1 ]]; then
    return 0
  fi
  read -r -p "$prompt [y/N] " answer
  [[ "$answer" == "y" || "$answer" == "Y" ]]
}

if [[ -n "$NFC_LIST" ]]; then
  if [[ ! "$NFC_LIST" =~ ^[A-Za-z0-9,_-]+$ ]]; then
    echo "Invalid --nfc list (allowed: letters, digits, comma, underscore, hyphen)." >&2
    exit 1
  fi
  IFS=',' read -r -a nfc_ids <<< "$NFC_LIST"
  quoted=""
  for id in "${nfc_ids[@]}"; do
    [[ -z "$id" ]] && continue
    if [[ -n "$quoted" ]]; then
      quoted+=", "
    fi
    quoted+="'${id}'"
  done
  if [[ -z "$quoted" ]]; then
    echo "No NFC ids after parsing --nfc." >&2
    exit 1
  fi
  confirm "Delete local traces for NFC: ${quoted}?" || exit 0
  run_sql <<SQL
BEGIN;
DELETE FROM shopfloor_event WHERE workpiece_id IN (${quoted});
DELETE FROM sensor_snapshot WHERE workpiece_id IN (${quoted});
DELETE FROM production_step
  WHERE order_id IN (SELECT order_id FROM production_order WHERE workpiece_id IN (${quoted}));
DELETE FROM production_order WHERE workpiece_id IN (${quoted});
DELETE FROM workpiece WHERE workpiece_id IN (${quoted});
COMMIT;
SQL
  echo "Removed traces for NFC: ${quoted}"
  exit 0
fi

confirm "TRUNCATE ALL local persistence tables (Grafana Replay scratch)?" || exit 0
run_sql <<'SQL'
TRUNCATE TABLE
  shopfloor_event,
  production_order,
  production_step,
  workpiece,
  sensor_snapshot,
  mqtt_raw_message
RESTART IDENTITY CASCADE;
SQL
echo "Local persistence DB emptied."
