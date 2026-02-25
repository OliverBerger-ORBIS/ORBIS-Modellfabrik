#!/usr/bin/env bash
# Correlation-Test: Simuliert DSP-Antwort (dsp/correlation/info).
#
# Nutzung:
#   ./scripts/run-correlation-test.sh                    # Order-Test + Correlation (volle Abfolge)
#   ./scripts/run-correlation-test.sh <orderId>           # Nur Correlation für bestehende orderId
#   ./scripts/run-correlation-test.sh --no-order <orderId>  # Alias für "nur Correlation"
#
# Voraussetzung: Mosquitto auf localhost (TCP 1883). Für volle Abfolge: CCU lauffähig.
# OSF-UI: Environment auf Replay (nicht Mock!), Verbindung zu localhost:9001 (WebSocket).

set -e
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOST=${MQTT_HOST:-localhost}
PORT=${MQTT_PORT:-1883}

cd "$PROJECT_ROOT"

# Prüfe Mosquitto
if ! mosquitto_pub -h "$HOST" -p "$PORT" -t "test/ping" -m "" -q 0 2>/dev/null; then
  echo "❌ Mosquitto nicht erreichbar ($HOST:$PORT)"
  echo "   Start: brew services start mosquitto"
  exit 1
fi

TEST_PY="$PROJECT_ROOT/data/omf-data/test_topics/correlation_test.py"
PY_CMD=""
[[ -f "$PROJECT_ROOT/.venv/bin/python" ]] && PY_CMD="$PROJECT_ROOT/.venv/bin/python"
[[ -z "$PY_CMD" ]] && PY_CMD="python3"

if [[ ! -f "$TEST_PY" ]]; then
  echo "❌ $TEST_PY nicht gefunden"
  exit 1
fi

if ! $PY_CMD -c "import paho.mqtt.client" 2>/dev/null; then
  echo "❌ paho-mqtt fehlt. Bitte: pip install paho-mqtt"
  exit 1
fi

if [[ -n "${1:-}" && "${1}" != "--from-order" ]]; then
  # orderId als erstes Argument → nur Correlation publizieren
  $PY_CMD "$TEST_PY" "$1" --host "$HOST" --port "$PORT"
else
  # Kein orderId → Order-Test ausführen und danach Correlation publizieren
  $PY_CMD "$TEST_PY" --from-order --host "$HOST" --port "$PORT"
fi
