#!/usr/bin/env python3
"""
Order-Test: Reset, Layout, Preloads, Order → prüft Response.
Verwendet paho-mqtt im selben Prozess – kein Shell-Background, zuverlässiger.
"""
import json
import sys
import threading
import time
from pathlib import Path

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("❌ paho-mqtt fehlt. Bitte: pip install paho-mqtt")
    sys.exit(1)

HOST = "localhost"
PORT = 1883
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

response_received = threading.Event()
response_payload: list[str] = []


def on_connect(client, userdata, flags, rc):
    if rc != 0:
        print(f"❌ MQTT-Verbindung fehlgeschlagen: {rc}")
        sys.exit(1)


def on_message(client, userdata, msg):
    response_payload.append(msg.payload.decode("utf-8"))
    response_received.set()


def main():
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="paho.mqtt")
    print("=== Order-Test (Python/MQTT) ===")
    client = mqtt.Client(client_id="order-test")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(HOST, PORT, 60)
    client.loop_start()

    # Auf Response subscriben, bevor wir etwas senden
    client.subscribe("ccu/order/response", qos=2)
    time.sleep(1)

    # 0. Reset
    print("=== 0. Soft Reset ===")
    client.publish("ccu/set/reset", json.dumps({"timestamp": "2026-02-24T10:00:00.000Z"}), qos=2)
    time.sleep(2)

    # 1. Layout
    print("=== 1. Layout ===")
    layout_path = SCRIPT_DIR / "layout_hbw_demo.json"
    layout = json.loads(layout_path.read_text())
    client.publish("ccu/set/layout", json.dumps(layout), qos=2)
    time.sleep(2)

    # 2. Preloads
    print("=== 2. Preloads ===")
    preloads_dir = SCRIPT_DIR / "preloads"
    for name in ["module_v1_ff_HBW-DEMO_connection.json", "module_v1_ff_HBW-DEMO_state.json", "module_v1_ff_HBW-DEMO_factsheet.json"]:
        path = preloads_dir / name
        if path.exists():
            data = json.loads(path.read_text())
            topic = data["topic"]
            payload = data["payload"]
            if isinstance(payload, dict):
                payload = json.dumps(payload)
            client.publish(topic, payload, qos=data.get("qos", 1), retain=data.get("retain", False))
            time.sleep(0.5)
    time.sleep(2)

    # 3. Order senden
    print("=== 3. Order senden ===")
    response_received.clear()
    response_payload.clear()
    request_id = "order-test-request-001"
    order = {
        "type": "BLUE",
        "timestamp": "2026-02-24T10:15:00.000Z",
        "orderType": "PRODUCTION",
        "requestId": request_id,
    }
    print("Order Request:", json.dumps(order, indent=2))
    client.publish("ccu/order/request", json.dumps(order), qos=2)

    if response_received.wait(timeout=15):
        print("\n=== Response empfangen ===")
        resp = json.loads(response_payload[0])
        print(json.dumps(resp, indent=2, ensure_ascii=False))
        # requestId-Roundtrip prüfen
        if resp.get("requestId") == request_id:
            print(f"\n✅ Test erfolgreich (requestId-Roundtrip: {request_id})")
        else:
            print(f"\n⚠️ Response erhalten, aber requestId fehlt oder stimmt nicht (erwartet: {request_id})")
        return 0
    else:
        print("\n❌ Keine Response nach 15s. CCU-Log prüfen.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
