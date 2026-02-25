#!/usr/bin/env bash
# Beobachtet ccu/order/* Topics in Echtzeit – hilft bei der Diagnose, ob Orders publiziert werden.
# Nutzung: ./scripts/watch-order-topics.sh
# In einem anderen Terminal: ./scripts/run-correlation-test.sh ausführen

set -e
HOST=${MQTT_HOST:-localhost}
PORT=${MQTT_PORT:-1883}

echo "=== Watch ccu/order/* (Host: $HOST, Port: $PORT) ==="
echo "Starte Correlation-Test in anderem Terminal: ./scripts/run-correlation-test.sh"
echo ""

mosquitto_sub -h "$HOST" -p "$PORT" -t 'ccu/order/#' -v
