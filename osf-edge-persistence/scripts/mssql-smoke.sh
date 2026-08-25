#!/usr/bin/env bash
# Smoke-check: local SQL Server (compose profile mssql) accepts connections.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ -f .env ]]; then
  # shellcheck disable=SC1091
  set -a && source .env && set +a
fi

PASS="${MSSQL_SA_PASSWORD:-Osf_Edge_Dev1!}"
PORT="${MSSQL_EXTERNAL_PORT:-1433}"
NAME="${MSSQL_CONTAINER:-osf-edge-mssql}"

if ! docker ps --format '{{.Names}}' | grep -qx "$NAME"; then
  echo "Container $NAME is not running. Start with:"
  echo "  cd osf-edge-persistence && docker compose --profile mssql up -d mssql"
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

docker exec "$NAME" /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "$PASS" -C \
  -Q "SELECT @@VERSION AS version; SELECT name FROM sys.databases ORDER BY name;"

echo "OK: SQL Server reachable on localhost:${PORT} (container ${NAME})."
echo "Apply schema: bash scripts/mssql-init-schema.sh (DB ${MSSQL_DB:-osf_edge})."
