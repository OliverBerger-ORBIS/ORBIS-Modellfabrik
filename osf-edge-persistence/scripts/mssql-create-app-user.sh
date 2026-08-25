#!/usr/bin/env bash
# Create DB osf_edge (if needed) + login/user osf_edge with reader/writer/execute.
# Default target: local compose container osf-edge-mssql (sa).
#
# Usage:
#   bash scripts/mssql-create-app-user.sh
#   OSF_EDGE_PASSWORD='OsfEdge_App9#' bash scripts/mssql-create-app-user.sh
#   OSF_EDGE_RESET_PASSWORD=1 bash scripts/mssql-create-app-user.sh   # rotate password
#
# On DSP VE .201 (FT-LAN), as pocadm:
#   docker exec -i rittal_sqlserver /opt/mssql-tools18/bin/sqlcmd \
#     -S localhost -U sa -P '<sa-password>' -C -b \
#     -v OSF_EDGE_PASSWORD='<app-password>' -v OSF_EDGE_RESET_PASSWORD=0 \
#     -i /dev/stdin < db/mssql/010_app_user.sql
# (copy file onto the VE or pipe from laptop via ssh)
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

# Local Dev default only — change for .201 (must meet SQL complexity; avoid shell-special !)
PASS="${OSF_EDGE_PASSWORD:-OsfEdge_App9#}"
RESET="${OSF_EDGE_RESET_PASSWORD:-0}"
SA_PASS="${MSSQL_SA_PASSWORD:-Osf_Edge_Dev1!}"
NAME="${MSSQL_CONTAINER:-osf-edge-mssql}"

if ! docker ps --format '{{.Names}}' | grep -qx "$NAME"; then
  echo "Container $NAME is not running."
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

echo "→ 010_app_user.sql (login/user osf_edge)"
docker exec -i "$NAME" /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U sa -P "$SA_PASS" -C -b \
  -v "OSF_EDGE_PASSWORD=${PASS}" \
  -v "OSF_EDGE_RESET_PASSWORD=${RESET}" \
  <db/mssql/010_app_user.sql

docker exec "$NAME" /opt/mssql-tools18/bin/sqlcmd \
  -S localhost -U osf_edge -P "$PASS" -C -d osf_edge \
  -Q "SELECT dp.name AS db_user, r.name AS role_name
      FROM sys.database_role_members m
      JOIN sys.database_principals r ON m.role_principal_id = r.principal_id
      JOIN sys.database_principals dp ON m.member_principal_id = dp.principal_id
      WHERE dp.name = N'osf_edge'
      ORDER BY r.name;
      SELECT HAS_PERMS_BY_NAME(N'dbo', N'SCHEMA', N'EXECUTE') AS has_execute_on_dbo;"

echo "OK: app user osf_edge on database osf_edge."
echo "Set MSSQL_USER=osf_edge MSSQL_PASSWORD='…' (Persistence/Grafana). Dev default password used unless OSF_EDGE_PASSWORD was set."
