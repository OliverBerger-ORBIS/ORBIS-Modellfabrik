#!/usr/bin/env bash
# Legacy helper: sensor-around-ist queries were Postgres/Timescale.
# Active stack is MSSQL (env_sensor_snapshot). Port T-SQL before re-enabling.
#
# Until then, use Grafana dashboards sensor-snapshots / workpiece-trace.
set -euo pipefail
echo "sensor-around-ist.sh: not available — Postgres stack removed; queries not yet ported to MSSQL." >&2
echo "Use Grafana (env_sensor_snapshot) or re-port db/queries/sensor_around_ist_event*.sql to T-SQL." >&2
exit 1
