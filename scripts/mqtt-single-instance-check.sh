#!/usr/bin/env bash
set -euo pipefail

MQTT_PORT="${1:-1883}"
WS_PORT="${2:-9001}"

if ! command -v lsof >/dev/null 2>&1; then
  echo "ERROR: lsof is required for mqtt-single-instance-check.sh"
  exit 2
fi

port_pids() {
  local port="$1"
  lsof -nP -iTCP:"${port}" -sTCP:LISTEN 2>/dev/null | awk 'NR>1 {print $2}' | sort -u
}

readarray -t mqtt_pids < <(port_pids "${MQTT_PORT}")
readarray -t ws_pids < <(port_pids "${WS_PORT}")

if [ "${#mqtt_pids[@]}" -eq 0 ]; then
  echo "WARN: No listener found on MQTT port ${MQTT_PORT}"
  exit 1
fi

if [ "${#mqtt_pids[@]}" -gt 1 ]; then
  echo "ERROR: Duplicate listeners on MQTT port ${MQTT_PORT}: ${mqtt_pids[*]}"
  exit 1
fi

if [ "${#ws_pids[@]}" -gt 1 ]; then
  echo "ERROR: Duplicate listeners on WebSocket port ${WS_PORT}: ${ws_pids[*]}"
  exit 1
fi

if [ "${#ws_pids[@]}" -eq 1 ] && [ "${mqtt_pids[0]}" != "${ws_pids[0]}" ]; then
  echo "ERROR: MQTT port ${MQTT_PORT} (pid ${mqtt_pids[0]}) and WS port ${WS_PORT} (pid ${ws_pids[0]}) are served by different processes"
  exit 1
fi

echo "OK: Single broker instance detected (pid ${mqtt_pids[0]} on ${MQTT_PORT}${ws_pids:+ and ${WS_PORT}})"
