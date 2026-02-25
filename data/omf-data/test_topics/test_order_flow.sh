#!/usr/bin/env bash
# Testablauf: Layout → Preloads → Order → Response prüfen
# Voraussetzung: Mosquitto + CCU laufen (MQTT localhost:1883)

set -e
HOST=localhost
PORT=1883
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"
RESP_FILE=$(mktemp)
trap 'rm -f "$RESP_FILE"' EXIT

# Subscriber ganz am Anfang starten – hat dann die gesamte Setup-Phase zum Verbinden
(mosquitto_sub -h $HOST -p $PORT -t "ccu/order/response" -C 1 -W 25 > "$RESP_FILE" 2>/dev/null &)
SUB_PID=$!
sleep 1

echo "=== 0. (Optional) Soft Reset – alte Orders löschen ==="
mosquitto_pub -h $HOST -p $PORT -t "ccu/set/reset" -m '{"timestamp":"2026-02-24T10:00:00.000Z"}' -q 2 2>/dev/null || true
sleep 2

echo ""
echo "=== 1. Layout mit HBW-DEMO setzen ==="
mosquitto_pub -h $HOST -p $PORT -t "ccu/set/layout" -f "$PROJECT_ROOT/data/omf-data/test_topics/layout_hbw_demo.json" -q 2
echo "Layout gesendet."
sleep 2

echo ""
echo "=== 2. Preloads für HBW-DEMO senden (connection, state, factsheet) ==="
PRELOADS="$SCRIPT_DIR/preloads"
# Reihenfolge: connection → state → factsheet (State zuerst = pending-Stock-Fix greift)
for f in "$PRELOADS/module_v1_ff_HBW-DEMO_connection.json" "$PRELOADS/module_v1_ff_HBW-DEMO_state.json" "$PRELOADS/module_v1_ff_HBW-DEMO_factsheet.json"; do
  sleep 0.5
  if [ -f "$f" ]; then
    TOPIC=$(jq -r '.topic' "$f")
    PAYLOAD=$(jq -c '.payload' "$f")
    QOS=$(jq -r '.qos // 1' "$f")
    RETAIN=""
    [ "$(jq -r '.retain // false' "$f")" = "true" ] && RETAIN="-r"
    mosquitto_pub -h $HOST -p $PORT -t "$TOPIC" -m "$PAYLOAD" -q $QOS $RETAIN
  fi
done
echo "Preloads gesendet."
sleep 2

echo ""
echo "=== 3. Order senden und Response abwarten ==="
mosquitto_pub -h $HOST -p $PORT -t "ccu/order/request" -m '{"type":"BLUE","timestamp":"2026-02-24T10:15:00.000Z","orderType":"PRODUCTION"}' -q 2
wait $SUB_PID 2>/dev/null || true

echo ""
if [ -s "$RESP_FILE" ]; then
  echo "=== Response empfangen ==="
  cat "$RESP_FILE" | head -1
  echo ""
  echo "✅ Test erfolgreich: Order-Response erhalten"
else
  echo "❌ Keine Response empfangen. Mögliche Ursachen:"
  echo "   - CCU lehnt ab (kein Lagerbestand?)"
  echo "   - CCU-Log prüfen: 'No workpiece available to create order'"
fi
echo ""
echo "=== Ende ==="
