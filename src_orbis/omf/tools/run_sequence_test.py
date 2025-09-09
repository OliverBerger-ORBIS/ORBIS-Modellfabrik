#!/usr/bin/env python3
"""
Einfache Test-App für Workflow-Sequenzen
Führt die Test-App aus ohne Streamlit-UI
"""

import os
import sys

from .sequence_definition import SequenceDefinitionLoader
from .sequence_executor import SequenceExecutor
from .workflow_order_manager import workflow_order_manager

# Pfad für Imports hinzufügen
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)


class MockMqttClient:
    """Mock MQTT Client für Tests"""

    def __init__(self):
        self.published_messages = []
        self.recent_messages = []

    def publish(self, topic, payload, qos=1):
        """Simuliert MQTT-Publish"""
        message = {"topic": topic, "payload": payload, "qos": qos}
        self.published_messages.append(message)
        print(f"📤 MQTT Publish: {topic} → {payload}")
        return True

    def get_recent_messages(self):
        """Gibt simulierte eingehende Nachrichten zurück"""
        return self.recent_messages

    def simulate_incoming_message(self, topic, payload):
        """Simuliert eingehende MQTT-Nachricht"""
        message = {"topic": topic, "payload": payload}
        self.recent_messages.append(message)
        print(f"📥 MQTT Receive: {topic} ← {payload}")


def test_sequence_loading():
    """Testet das Laden von Sequenz-Definitionen"""
    print("🔍 Teste Sequenz-Definitionen laden...")

    loader = SequenceDefinitionLoader()
    sequences = loader.get_all_sequences()

    print(f"✅ {len(sequences)} Sequenzen geladen:")
    for name, sequence in sequences.items():
        print(f"  - {name}: {len(sequence.steps)} Schritte")
        print(f"    Beschreibung: {sequence.description}")

    return sequences


def test_sequence_execution():
    """Testet die Sequenz-Ausführung"""
    print("\n🚀 Teste Sequenz-Ausführung...")

    # Mock MQTT Client
    mock_mqtt = MockMqttClient()

    # SequenceExecutor
    executor = SequenceExecutor(mock_mqtt)

    # Sequenzen laden
    loader = SequenceDefinitionLoader()
    sequences = loader.get_all_sequences()

    if not sequences:
        print("❌ Keine Sequenzen zum Testen verfügbar")
        return

    # Erste Sequenz testen
    sequence_name = list(sequences.keys())[0]
    sequence = sequences[sequence_name]

    print(f"📋 Teste Sequenz: {sequence.name}")

    # Sequenz starten
    order_id = executor.execute_sequence(sequence)
    print(f"✅ Sequenz gestartet mit Order ID: {order_id}")

    # Status abrufen
    status = executor.get_sequence_status(order_id)
    if status:
        print(f"📊 Status: {status['status']}")
        print(f"📊 Schritte: {status['current_step']}/{status['total_steps']}")

        # Ersten Schritt ausführen
        if status["steps"]:
            first_step = status["steps"][0]
            print(f"🎯 Führe ersten Schritt aus: {first_step['name']}")

            success = executor.execute_step(order_id, 0)
            if success:
                print("✅ Schritt erfolgreich ausgeführt")
            else:
                print("❌ Fehler beim Ausführen des Schritts")

    # Finaler Status
    final_status = executor.get_sequence_status(order_id)
    if final_status:
        print(f"📊 Finaler Status: {final_status['status']}")

    # MQTT-Nachrichten anzeigen
    print(f"\n📤 {len(mock_mqtt.published_messages)} MQTT-Nachrichten gesendet:")
    for msg in mock_mqtt.published_messages:
        print(f"  - {msg['topic']} → {msg['payload']}")


def test_workflow_order_manager():
    """Testet den WorkflowOrderManager"""
    print("\n🔄 Teste WorkflowOrderManager...")

    # Order erstellen
    order = workflow_order_manager.create_order("test_sequence")
    print(f"✅ Order erstellt: {order.order_id}")
    print(f"📊 Status: {order.status}")

    # Update ID inkrementieren
    update_id = workflow_order_manager.increment_update_id(order.order_id)
    print(f"📊 Update ID: {update_id}")

    # Schritt aktualisieren
    workflow_order_manager.update_step(order.order_id, 1, 3)
    print("📊 Schritt: 1/3")

    # Order abschließen
    workflow_order_manager.complete_order(order.order_id)
    print(f"📊 Finaler Status: {order.status}")

    # Alle Orders anzeigen
    all_orders = workflow_order_manager.get_all_orders()
    print(f"📊 Gesamt Orders: {len(all_orders)}")


def main():
    """Hauptfunktion"""
    print("🔄 Workflow Sequence Control - Test Suite")
    print("=" * 50)

    try:
        # Tests ausführen
        test_sequence_loading()
        test_workflow_order_manager()
        test_sequence_execution()

        print("\n✅ Alle Tests erfolgreich abgeschlossen!")

    except Exception as e:
        print(f"\n❌ Test-Fehler: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
