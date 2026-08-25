#!/usr/bin/env bash
# Apply T-SQL schema to local osf-edge-mssql (create DB + tables + indexes).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  set -a && source .env && set +a
elif [[ -f env.live ]]; then
  # shellcheck disable=SC1091
  set -a && source env.live && set +a
fi

PASS="${MSSQL_SA_PASSWORD:-Osf_Edge_Dev1!}"
NAME="${MSSQL_CONTAINER:-osf-edge-mssql}"
DB="${MSSQL_DB:-osf_edge}"

if ! docker ps --format '{{.Names}}' | grep -qx "$NAME"; then
  echo "Container $NAME is not running. Start with:"
  echo "  docker compose --env-file env.live --profile mssql up -d mssql"
  exit 1
fi

echo "Waiting for SQL Server health ($NAME)…"
for _ in $(seq 1 40); do
  status="$(docker inspect -f '{{.State.Health.Status}}' "$NAME" 2>/dev/null || echo starting)"
  if [[ "$status" == "healthy" ]]; then
    break
  fi
  sleep 3
done

run_sql() {
  local file="$1"
  echo "→ $(basename "$file")"
  docker exec -i "$NAME" /opt/mssql-tools18/bin/sqlcmd \
    -S localhost -U sa -P "$PASS" -C -b <"$file"
}

run_sql db/mssql/001_create_database.sql
run_sql db/mssql/002_schema.sql
run_sql db/mssql/003_indexes.sql

docker exec "$NAME" /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "$PASS" -C -d "$DB" \
  -Q "SELECT TABLE_SCHEMA, TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE='BASE TABLE' ORDER BY 1, 2;"

echo "OK: schema applied on database ${DB}."
