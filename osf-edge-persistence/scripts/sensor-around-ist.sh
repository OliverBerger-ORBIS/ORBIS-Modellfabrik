#!/usr/bin/env bash
# Query-time join: last-known sensor values around Ist shopfloor events.
# Does not write related_event_id. Grafana is not involved.
#
# Usage (from repo root or this directory):
#   bash osf-edge-persistence/scripts/sensor-around-ist.sh
#   bash osf-edge-persistence/scripts/sensor-around-ist.sh --nfc 92e0ad91595f63
#   bash osf-edge-persistence/scripts/sensor-around-ist.sh --anchors --hours 6
#   bash osf-edge-persistence/scripts/sensor-around-ist.sh --long --limit 50
#
set -euo pipefail

CONTAINER="${OSF_EDGE_POSTGRES_CONTAINER:-osf-edge-postgres}"
PGUSER="${POSTGRES_USER:-osf}"
PGDB="${POSTGRES_DB:-osf}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
QUERY_DIR="${SCRIPT_DIR}/../db/queries"

WINDOW_SECONDS=30
GRACE_SECONDS=5
LOOKBACK_HOURS=6
NFC_REGEX='.*'
ROW_LIMIT=200
ANCHORS_ONLY=0
LONG=0

usage() {
  sed -n '2,14p' "$0"
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --window)
      WINDOW_SECONDS="${2:-}"
      shift 2
      ;;
    --grace)
      GRACE_SECONDS="${2:-}"
      shift 2
      ;;
    --hours)
      LOOKBACK_HOURS="${2:-}"
      shift 2
      ;;
    --nfc)
      NFC_REGEX="${2:-}"
      shift 2
      ;;
    --nfc=*)
      NFC_REGEX="${1#--nfc=}"
      shift
      ;;
    --limit)
      ROW_LIMIT="${2:-}"
      shift 2
      ;;
    --anchors)
      ANCHORS_ONLY=1
      shift
      ;;
    --long)
      LONG=1
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

for name in WINDOW_SECONDS GRACE_SECONDS LOOKBACK_HOURS ROW_LIMIT ANCHORS_ONLY; do
  val="${!name}"
  if [[ ! "$val" =~ ^[0-9]+$ ]]; then
    echo "Invalid $name (need a non-negative integer): $val" >&2
    exit 1
  fi
done

if [[ ! "$NFC_REGEX" =~ ^[A-Za-z0-9._*|+-]+$ ]]; then
  echo "Invalid --nfc (allowed: letters, digits, . _ * | + -)." >&2
  exit 1
fi

if [[ "$NFC_REGEX" != '.*' && ! "$NFC_REGEX" =~ [\.\*\|\+] ]]; then
  NFC_REGEX="^${NFC_REGEX}$"
fi

if ! docker ps --format '{{.Names}}' | grep -qx "$CONTAINER"; then
  echo "Postgres container '$CONTAINER' is not running." >&2
  echo "Start Replay stack first: cd osf-edge-persistence && cp env.replay .env && docker compose up -d" >&2
  exit 1
fi

if [[ "$LONG" -eq 1 ]]; then
  SQL_FILE="${QUERY_DIR}/sensor_around_ist_event_long.sql"
else
  SQL_FILE="${QUERY_DIR}/sensor_around_ist_event.sql"
fi

{
  echo "\\pset pager off"
  echo "\\set window_seconds ${WINDOW_SECONDS}"
  echo "\\set grace_seconds ${GRACE_SECONDS}"
  echo "\\set lookback_hours ${LOOKBACK_HOURS}"
  echo "\\set nfc_regex ${NFC_REGEX}"
  echo "\\set row_limit ${ROW_LIMIT}"
  echo "\\set anchors_only ${ANCHORS_ONLY}"
  cat "$SQL_FILE"
} | docker exec -i "$CONTAINER" psql -U "$PGUSER" -d "$PGDB" -v ON_ERROR_STOP=1
