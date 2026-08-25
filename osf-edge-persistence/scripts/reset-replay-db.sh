#!/usr/bin/env bash
# Manual reset of the *local* edge-persistence MSSQL DB (Replay scratch).
# Never invoked automatically on replay start — different sessions with
# different NFC ids are meant to accumulate. Run this only when you want
# a clean slate or to drop a repeated replay of the same NFC.
#
# Full truncate also clears replay_session_ingest (session-gate list).
#
# Usage:
#   bash osf-edge-persistence/scripts/reset-replay-db.sh
#   bash osf-edge-persistence/scripts/reset-replay-db.sh --nfc 92e0ad91595f63,78d10489b38ed8
#   bash osf-edge-persistence/scripts/reset-replay-db.sh --yes
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  set -a && source .env && set +a
elif [[ -f env.replay ]]; then
  # shellcheck disable=SC1091
  set -a && source env.replay && set +a
fi

MSSQL_CONTAINER="${MSSQL_CONTAINER:-osf-edge-mssql}"
MSSQL_DB="${MSSQL_DB:-osf_edge}"
MSSQL_SA_PASSWORD="${MSSQL_SA_PASSWORD:-Osf_Edge_Dev1!}"
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

confirm() {
  local prompt="$1"
  if [[ "$YES" -eq 1 ]]; then
    return 0
  fi
  read -r -p "$prompt [y/N] " answer
  [[ "$answer" == "y" || "$answer" == "Y" ]]
}

run_mssql_sql() {
  docker exec -i "$MSSQL_CONTAINER" /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U sa -P "$MSSQL_SA_PASSWORD" -C -b -d "$MSSQL_DB"
}

if ! docker ps --format '{{.Names}}' | grep -qx "$MSSQL_CONTAINER"; then
  echo "MSSQL container '$MSSQL_CONTAINER' is not running." >&2
  echo "Start with: cd osf-edge-persistence && cp env.replay .env && docker compose up -d mssql" >&2
  exit 1
fi

run_mssql_sql <<'SQL'
IF OBJECT_ID(N'dbo.replay_session_ingest', N'U') IS NULL
BEGIN
  CREATE TABLE dbo.replay_session_ingest (
    session_id NVARCHAR(256) NOT NULL CONSTRAINT PK_replay_session_ingest PRIMARY KEY,
    ingested_at DATETIMEOFFSET NOT NULL CONSTRAINT DF_replay_session_ingest_ingested_at DEFAULT (SYSUTCDATETIME())
  );
END
SQL

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
    quoted+="N'${id}'"
  done
  if [[ -z "$quoted" ]]; then
    echo "No NFC ids after parsing --nfc." >&2
    exit 1
  fi
  confirm "Delete local traces for NFC: ${quoted}?" || exit 0
  run_mssql_sql <<SQL
BEGIN TRAN;
DELETE FROM dbo.shopfloor_event WHERE workpiece_id IN (${quoted});
DELETE FROM dbo.env_sensor_snapshot WHERE workpiece_id IN (${quoted});
DELETE FROM dbo.production_step
  WHERE order_id IN (SELECT order_id FROM dbo.shopfloor_order WHERE workpiece_id IN (${quoted}));
DELETE FROM dbo.shopfloor_order WHERE workpiece_id IN (${quoted});
DELETE FROM dbo.workpiece WHERE workpiece_id IN (${quoted});
COMMIT TRAN;
SQL
  echo "Removed traces for NFC: ${quoted}"
  echo "Note: replay_session_ingest unchanged (use full truncate to re-allow session ingest)."
  exit 0
fi

confirm "TRUNCATE ALL local persistence tables + replay_session_ingest (Grafana Replay scratch)?" || exit 0

run_mssql_sql <<'SQL'
DELETE FROM dbo.env_sensor_snapshot;
DELETE FROM dbo.shopfloor_event;
DELETE FROM dbo.production_step;
DELETE FROM dbo.shopfloor_order;
DELETE FROM dbo.workpiece;
DELETE FROM dbo.mqtt_raw_message;
DELETE FROM dbo.replay_session_ingest;
SQL

echo "Local persistence DB emptied (including replay_session_ingest)."
