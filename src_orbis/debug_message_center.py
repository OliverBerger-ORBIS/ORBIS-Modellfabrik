#!/usr/bin/env python3
"""
Debug-Script für Message Center Problem
"""

import time

from src_orbis.omf.tools.mqtt_config import cfg_for
from src_orbis.omf.tools.mqtt_topics import PRIORITY_FILTERS, flatten_filters, get_priority_filters
from src_orbis.omf.tools.omf_mqtt_client import OmfMqttClient


def test_priority_filters():
    print("=== Priority Filters Test ===")
    print(f"PRIORITY_FILTERS: {PRIORITY_FILTERS}")
    print(f"\nPrio 5 (flatten_filters): {flatten_filters(5)}")
    print(f"Prio 5 (get_priority_filters): {get_priority_filters(5)}")
    print(f"Anzahl Prio 5 Filter: {len(flatten_filters(5))}")


def test_mqtt_connection():
    print("\n=== MQTT Connection Test ===")

    # Teste Replay-Konfiguration
    cfg = cfg_for("replay")
    print(f"Replay Config: {cfg.host}:{cfg.port}")

    # Erstelle Client
    client = OmfMqttClient(cfg)

    # Teste set_message_center_priority
    try:
        client.set_message_center_priority(5, PRIORITY_FILTERS)
        print("✅ set_message_center_priority erfolgreich")
    except Exception as e:
        print(f"❌ set_message_center_priority Fehler: {e}")

    # Teste subscribe_many
    try:
        priority_filters = flatten_filters(5)
        client.subscribe_many(priority_filters)
        print(f"✅ subscribe_many erfolgreich mit {len(priority_filters)} Filtern")
    except Exception as e:
        print(f"❌ subscribe_many Fehler: {e}")

    # Teste _matches_topic
    test_topics = ["ccu/state", "module/v1/ff/SVR3QA0022/state", "fts/v1/ff/5iO4/state", "/j1/txt/1/f/i/stock"]

    print("\n=== Topic Matching Test ===")
    for topic in test_topics:
        matches = []
        for pattern in priority_filters:
            if client._matches_topic(topic, pattern):
                matches.append(pattern)
        print(f"Topic '{topic}' matches: {matches}")

    return client


def test_message_reception(client):
    print("\n=== Message Reception Test ===")

    # Verbinde zum Broker
    try:
        client.connect()
        print("✅ MQTT Verbindung erfolgreich")

        # Warte auf Nachrichten
        print("Warte 10 Sekunden auf Nachrichten...")
        time.sleep(10)

        # Prüfe History
        history_count = len(client._history)
        print(f"📊 Nachrichten in History: {history_count}")

        if history_count > 0:
            print("Letzte 3 Nachrichten:")
            for i, msg in enumerate(list(client._history)[-3:], 1):
                print(f"  {i}. Topic: {msg.get('topic', 'N/A')}, Payload: {str(msg.get('payload', 'N/A'))[:50]}...")
        else:
            print("❌ Keine Nachrichten empfangen")

    except Exception as e:
        print(f"❌ MQTT Verbindung Fehler: {e}")
    finally:
        try:
            client.disconnect()
            print("✅ MQTT Verbindung getrennt")
        except Exception:
            pass


if __name__ == "__main__":
    test_priority_filters()
    client = test_mqtt_connection()
    test_message_reception(client)
