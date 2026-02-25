#!/usr/bin/env bash
# Ein-Klick Order-Test: Aufräumen, CCU starten, Test ausführen
# Nach Cursor-Crash oder undefiniertem Zustand: definierter Neustart.
#
# Nutzung:
#   ./scripts/run-order-test.sh          # Standard: Clean + CCU + Test
#   ./scripts/run-order-test.sh --no-restart  # CCU läuft schon, nur Test

set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CCU_DIR="$PROJECT_ROOT/integrations/APS-CCU/central-control"
TEST_SCRIPT="$PROJECT_ROOT/data/omf-data/test_topics/test_order_flow.sh"
HOST=localhost
PORT=1883

cd "$PROJECT_ROOT"

do_restart=true
if [[ "${1:-}" == "--no-restart" ]]; then
  do_restart=false
fi

# --- 1. Mosquitto prüfen ---
if ! mosquitto_pub -h "$HOST" -p "$PORT" -t "test/ping" -m "" -q 0 2>/dev/null; then
  echo "❌ Mosquitto nicht erreichbar (localhost:1883)"
  echo "   Start: brew services start mosquitto  (oder: mosquitto -c /opt/homebrew/etc/mosquitto/mosquitto.conf)"
  exit 1
fi

# --- 2. Optional: Alte Prozesse beenden (Clean Slate) ---
if [[ "$do_restart" == "true" ]]; then
  echo "=== Aufräumen: Alte CCU- und Test-Prozesse beenden ==="
  # CCU (nodemon/ts-node aus central-control)
  pkill -f "APS-CCU/central-control" 2>/dev/null || true
  # Orphan mosquitto_sub von vorherigen Tests
  pkill -f "mosquitto_sub.*ccu/order" 2>/dev/null || true
  sleep 2
fi

# --- 3. CCU starten (falls nicht läuft) ---
ccu_running=false
if pgrep -f "APS-CCU/central-control" >/dev/null 2>&1; then
  ccu_running=true
  echo "=== CCU läuft bereits ==="
fi

if [[ "$ccu_running" == "false" ]]; then
  echo "=== CCU starten (Hintergrund) ==="
  cd "$CCU_DIR"
  nohup env MQTT_URL="mqtt://${HOST}:${PORT}" npm start >> /tmp/ccu-order-test.log 2>&1 &
  disown
  cd "$PROJECT_ROOT"
  echo "   CCU gestartet - warte 18 Sekunden auf Initialisierung..."
  sleep 18
fi

# --- 4. Order-Test ausführen ---
echo ""
echo "=== Order-Test ausführen ==="
TEST_PY="$PROJECT_ROOT/data/omf-data/test_topics/order_test.py"
PY_CMD=""
[[ -f "$PROJECT_ROOT/.venv/bin/python" ]] && PY_CMD="$PROJECT_ROOT/.venv/bin/python"
[[ -z "$PY_CMD" ]] && PY_CMD="python3"
if [[ -f "$TEST_PY" ]] && $PY_CMD -c "import paho.mqtt.client" 2>/dev/null; then
  $PY_CMD "$TEST_PY"
else
  # Fallback: Shell-Skript
  if [[ -x "$TEST_SCRIPT" ]]; then
    "$TEST_SCRIPT"
  else
    bash "$TEST_SCRIPT"
  fi
fi

echo ""
echo "=== Fertig ==="
echo "CCU läuft weiter im Hintergrund."
echo "  Log: tail -f /tmp/ccu-order-test.log"
echo "  Stoppen: pkill -f 'APS-CCU/central-control'"
