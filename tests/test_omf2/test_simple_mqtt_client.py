#!/usr/bin/env python3
"""
Einfacher MQTT Client Test - Funktioniert das grundsätzlich?
"""

import time

import paho.mqtt.client as mqtt

# Broker-Einstellungen
BROKER_HOST = "localhost"  # oder IP-Adresse des Mosquitto-Brokers
BROKER_PORT = 1883

# Liste der Topics, die abonniert werden sollen
TOPICS = [("ccu/set/reset", 0), ("module/xy/v1/SVRRxxxx/state", 0)]


# Callback, wenn Verbindung hergestellt wird
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Verbunden mit Broker")
        # Topics abonnieren
        for topic, qos in TOPICS:
            client.subscribe(topic, qos)
            print(f"➡️  Subscribed to topic: {topic}")
    else:
        print(f"❌ Verbindung fehlgeschlagen (Code {rc})")


# Callback, wenn Nachricht empfangen wird
def on_message(client, userdata, msg):
    print(f"📨 Nachricht empfangen: Topic='{msg.topic}' | Payload='{msg.payload.decode()}'")


def main():
    print("🧪 Einfacher MQTT Client Test")
    print("=" * 40)

    client = mqtt.Client(client_id="example_subscriber")
    client.on_connect = on_connect
    client.on_message = on_message

    print(f"🔌 Verbinde zu {BROKER_HOST}:{BROKER_PORT}...")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)

    # Starte Netzwerk-Loop (non-blocking)
    client.loop_start()

    print("⏳ Warte 5 Sekunden...")
    time.sleep(5)

    print("🔌 Trenne Verbindung...")
    client.loop_stop()
    client.disconnect()

    print("✅ Test abgeschlossen!")


if __name__ == "__main__":
    main()
