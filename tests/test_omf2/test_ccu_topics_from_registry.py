#!/usr/bin/env python3
"""
CCU Topics aus Registry Test - Funktioniert das mit echten CCU Topics?
"""

import time

import paho.mqtt.client as mqtt

from omf2.registry.manager.registry_manager import get_registry_manager

# Broker-Einstellungen
BROKER_HOST = "localhost"
BROKER_PORT = 1883


# Topics aus Registry laden
def load_ccu_topics_from_registry():
    """Lädt CCU Topics aus Registry"""
    try:
        registry_manager = get_registry_manager()
        mqtt_clients = registry_manager.get_mqtt_clients()
        ccu_client = mqtt_clients.get("ccu_mqtt_client", {})
        topics = ccu_client.get("subscribed_topics", [])
        print(f"📥 Loaded {len(topics)} CCU topics from registry")
        return topics
    except Exception as e:
        print(f"❌ Failed to load CCU topics: {e}")
        return []


# Callback, wenn Verbindung hergestellt wird
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("✅ Verbunden mit Broker")
        # Topics abonnieren
        for topic in TOPICS:
            client.subscribe(topic, 0)
            print(f"➡️  Subscribed to topic: {topic}")
    else:
        print(f"❌ Verbindung fehlgeschlagen (Code {rc})")


# Callback, wenn Nachricht empfangen wird
def on_message(client, userdata, msg):
    print(f"📨 Nachricht empfangen: Topic='{msg.topic}' | Payload='{msg.payload.decode()}'")


def main():
    print("🧪 CCU Topics aus Registry Test")
    print("=" * 40)

    # Topics aus Registry laden
    global TOPICS
    TOPICS = load_ccu_topics_from_registry()

    if not TOPICS:
        print("❌ Keine Topics gefunden!")
        return

    print(f"📋 Topics zum Subscriben: {len(TOPICS)}")
    print(f"📋 Erste 5 Topics: {TOPICS[:5]}")

    client = mqtt.Client(client_id="ccu_test_subscriber")
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
