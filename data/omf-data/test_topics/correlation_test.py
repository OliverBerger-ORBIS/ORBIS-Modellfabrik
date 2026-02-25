#!/usr/bin/env python3
"""
Correlation-Test: Simuliert DSP-Antwort (dsp/correlation/info) für eine Order.

Nutzung:
  python correlation_test.py <orderId>              # Publiziert dsp/correlation/info für orderId
  python correlation_test.py --from-order          # Führt Order-Test aus, publiziert danach Correlation-Info

Voraussetzung: Mosquitto auf localhost:1883, optional CCU für --from-order.
OSF-UI in Replay/Live-Modus: Nach Ausführung erscheint die ERP-Info in Order-Tab und Track & Trace.
"""
from __future__ import annotations

import argparse
import json
import sys
import threading
import time
from pathlib import Path
from typing import Optional

try:
    import paho.mqtt.client as mqtt
except ImportError:
    print("❌ paho-mqtt fehlt. Bitte: pip install paho-mqtt")
    sys.exit(1)

HOST = "localhost"
PORT = 1883
SCRIPT_DIR = Path(__file__).resolve().parent

response_received = threading.Event()
response_payload: list = []


def on_message(client, userdata, msg):
    response_payload.append(msg.payload.decode("utf-8"))
    response_received.set()


def publish_correlation_info(client: mqtt.Client, order_id: str, order_type: str = "CUSTOMER") -> None:
    """Publiziert dsp/correlation/info als simulierte DSP-Antwort."""
    if order_type.upper() == "PURCHASE":
        payload = {
            "ccuOrderId": order_id,
            "requestId": f"PO-{order_id[:8]}",
            "orderType": "PURCHASE",
            "purchaseOrderId": "ERP-PO-TEST-001",
            "supplierId": "SUP-DEMO",
            "orderDate": "2026-02-24T08:00:00.000Z",
            "orderAmount": 1,
            "plannedDeliveryDate": "2026-03-01T12:00:00.000Z",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
        }
    else:
        payload = {
            "ccuOrderId": order_id,
            "requestId": "CO-TEST-001",
            "orderType": "CUSTOMER",
            "customerOrderId": "ERP-CO-4711",
            "customerId": "CUST-001",
            "orderDate": "2026-02-24T08:00:00.000Z",
            "orderAmount": 1,
            "plannedDeliveryDate": "2026-03-01T12:00:00.000Z",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
        }
    client.publish("dsp/correlation/info", json.dumps(payload), qos=1, retain=False)
    print(f"  dsp/correlation/info publiziert für orderId={order_id}")


def run_order_flow(client: mqtt.Client) -> Optional[str]:
    """Führt Order-Test aus (Reset, Layout, Order), gibt orderId aus Response zurück."""
    layout_path = SCRIPT_DIR / "layout_hbw_demo.json"
    if not layout_path.exists():
        print("⚠️ layout_hbw_demo.json fehlt – Order-Test übersprungen")
        return None

    client.subscribe("ccu/order/response", qos=2)
    time.sleep(0.5)

    # 0. Reset (optional, CCU kann bereits laufen)
    print("  0. Soft Reset")
    client.publish("ccu/set/reset", json.dumps({"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())}), qos=2)
    time.sleep(2)

    # 1. Layout
    print("  1. Layout")
    layout = json.loads(layout_path.read_text())
    client.publish("ccu/set/layout", json.dumps(layout), qos=2)
    time.sleep(2)

    # 2. Preloads (HBW-Modul für CCU erforderlich)
    print("  2. Preloads")
    preloads_dir = SCRIPT_DIR / "preloads"
    for name in [
        "module_v1_ff_HBW-DEMO_connection.json",
        "module_v1_ff_HBW-DEMO_state.json",
        "module_v1_ff_HBW-DEMO_factsheet.json",
    ]:
        path = preloads_dir / name
        if path.exists():
            data = json.loads(path.read_text())
            topic = data["topic"]
            payload = data["payload"]
            if isinstance(payload, dict):
                payload = json.dumps(payload)
            client.publish(
                topic,
                payload,
                qos=data.get("qos", 1),
                retain=data.get("retain", False),
            )
            time.sleep(0.5)
    time.sleep(2)

    # 3. Order senden
    print("  3. Order senden")
    response_received.clear()
    response_payload.clear()
    request_id = "correlation-test-request-001"
    order = {
        "type": "BLUE",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
        "orderType": "PRODUCTION",
        "requestId": request_id,
    }
    client.publish("ccu/order/request", json.dumps(order), qos=2)

    if not response_received.wait(timeout=15):
        print("⚠️ Keine Order-Response – Correlation wird nicht publiziert")
        return None

    resp = json.loads(response_payload[0])
    order_id = resp.get("orderId")
    if order_id:
        print(f"  Order-Response erhalten, orderId={order_id}")
    return order_id


def main():
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning, module="paho.mqtt")

    parser = argparse.ArgumentParser(description="Correlation-Test: dsp/correlation/info publizieren")
    parser.add_argument(
        "order_id",
        nargs="?",
        help="CCU-Order-ID (ccuOrderId). Ohne Angabe: --from-order erforderlich.",
    )
    parser.add_argument(
        "--from-order",
        action="store_true",
        help="Order-Test ausführen und Correlation-Info für erhaltene orderId publizieren",
    )
    parser.add_argument(
        "--type",
        choices=["CUSTOMER", "PURCHASE"],
        default="CUSTOMER",
        help="Order-Typ (CUSTOMER=Produktion, PURCHASE=Lager)",
    )
    parser.add_argument("--host", default=HOST, help=f"MQTT-Host (default: {HOST})")
    parser.add_argument("--port", type=int, default=PORT, help=f"MQTT-Port (default: {PORT})")
    args = parser.parse_args()

    order_id = args.order_id
    if not order_id and not args.from_order:
        parser.error("order_id angeben oder --from-order verwenden")

    print("=== Correlation-Test ===")
    client = mqtt.Client(client_id="correlation-test")
    client.on_connect = lambda c, u, f, rc: print("  MQTT verbunden" if rc == 0 else sys.exit(1))
    client.connect(args.host, args.port, 60)
    client.loop_start()
    time.sleep(1)

    if args.from_order:
        print("=== 1. Order-Test ausführen ===")
        order_id = run_order_flow(client)
        if not order_id:
            return 1
        print("=== 2. Correlation-Info publizieren ===")
    else:
        print("=== Correlation-Info publizieren ===")

    publish_correlation_info(client, order_id, args.type)
    time.sleep(0.5)

    print("\n✅ Fertig. OSF-UI (Replay/Live) sollte jetzt ERP-Info in Order-Tab und Track & Trace anzeigen.")
    print("   Hinweis: Environment auf 'Replay' stellen (nicht Mock!), Status 'Verbunden' prüfen.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
