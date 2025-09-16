"""
Unit-Test: Sequenz-Nachrichten vs. Factory-Steuerung-Nachrichten
Überprüft, ob die Sequenz-Nachrichten identisch mit den Factory-Steuerung-Nachrichten sind
"""

import json
import os
import sys
import unittest
import uuid
from unittest.mock import Mock, patch

# Pfad für Imports hinzufügen
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "omf"))

from omf.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep, StepStatus
from omf.tools.workflow_order_manager import WorkflowOrderManager


# Factory-Steuerung-Logik direkt implementieren (ohne Streamlit-Abhängigkeiten)
def _prepare_factory_message(module_name: str, step: str, order_update_id: int = 1):
    """Bereitet Factory-Steuerung-Nachricht vor (ohne Streamlit)"""
    # Modul-spezifische Serial Numbers
    module_serials = {"AIQS": "SVR4H76530", "MILL": "SVR3QA2098", "DRILL": "SVR4H76449"}

    serial_number = module_serials.get(module_name, "UNKNOWN")

    # Topic generieren
    topic = f"module/v1/ff/{serial_number}/order"

    # Payload generieren
    payload = {
        "serialNumber": serial_number,
        "orderId": str(uuid.uuid4()),
        "orderUpdateId": order_update_id,
        "action": {
            "id": str(uuid.uuid4()),
            "command": step,
            "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
        },
    }

    return {"topic": topic, "payload": payload}


class TestSequenceVsFactorySteering(unittest.TestCase):
    """Test-Klasse für Sequenz vs. Factory-Steuerung Vergleich"""

    def setUp(self):
        """Setup für jeden Test"""
        self.mock_mqtt_client = Mock()
        self.executor = SequenceExecutor(self.mock_mqtt_client)
        self.workflow_manager = WorkflowOrderManager()

        # DRILL-Modul-Konfiguration
        self.drill_serial = "SVR4H76449"
        self.drill_module = "DRILL"

    def test_drill_sequence_vs_factory_steering_pick(self):
        """Test: DRILL PICK - Sequenz vs. Factory-Steuerung"""
        # Factory-Steuerung Nachricht generieren
        factory_message = _prepare_factory_message(self.drill_module, "PICK", 1)
        factory_topic = factory_message["topic"]
        factory_payload = factory_message["payload"]

        # Sequenz-Schritt erstellen
        sequence_step = SequenceStep(
            step_id="pick_step",
            name="PICK",
            topic=f"module/v1/ff/{self.drill_serial}/order",
            payload={
                "serialNumber": self.drill_serial,
                "orderId": "{{orderId}}",
                "orderUpdateId": "{{orderUpdateId}}",
                "action": {
                    "id": "{{action_id}}",
                    "command": "PICK",
                    "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                },
            },
        )

        # Kontext für Variable-Resolution
        test_order_id = str(uuid.uuid4())
        test_action_id = str(uuid.uuid4())
        context = {
            "module_serial": self.drill_serial,
            "orderId": test_order_id,
            "orderUpdateId": 1,
            "action_id": test_action_id,
        }

        # Variable-Resolution durchführen
        resolved_topic = self.executor._resolve_variables(sequence_step.topic, context)
        resolved_payload = self.executor._resolve_variables(sequence_step.payload, context)

        # Topics vergleichen
        self.assertEqual(
            resolved_topic,
            factory_topic,
            f"Topics stimmen nicht überein:\nSequenz: {resolved_topic}\nFactory: {factory_topic}",
        )

        # Payloads vergleichen (ohne UUIDs, da diese unterschiedlich sind)
        self.assertEqual(
            resolved_payload["serialNumber"], factory_payload["serialNumber"], "serialNumber stimmt nicht überein"
        )
        self.assertEqual(
            int(resolved_payload["orderUpdateId"]),
            factory_payload["orderUpdateId"],
            "orderUpdateId stimmt nicht überein",
        )
        self.assertEqual(
            resolved_payload["action"]["command"],
            factory_payload["action"]["command"],
            "action.command stimmt nicht überein",
        )
        self.assertEqual(
            resolved_payload["action"]["metadata"],
            factory_payload["action"]["metadata"],
            "action.metadata stimmt nicht überein",
        )

        # UUIDs sollten vorhanden sein
        self.assertIsNotNone(resolved_payload["orderId"], "orderId sollte vorhanden sein")
        self.assertIsNotNone(resolved_payload["action"]["id"], "action.id sollte vorhanden sein")

        print("✅ PICK Test erfolgreich:")
        print(f"   Topic: {resolved_topic}")
        print(f"   Command: {resolved_payload['action']['command']}")
        print(f"   SerialNumber: {resolved_payload['serialNumber']}")

    def test_drill_sequence_vs_factory_steering_drill(self):
        """Test: DRILL DRILL - Sequenz vs. Factory-Steuerung"""
        # Factory-Steuerung Nachricht generieren
        factory_message = _prepare_factory_message(self.drill_module, "DRILL", 2)
        factory_topic = factory_message["topic"]
        factory_payload = factory_message["payload"]

        # Sequenz-Schritt erstellen
        sequence_step = SequenceStep(
            step_id="drill_step",
            name="DRILL",
            topic=f"module/v1/ff/{self.drill_serial}/order",
            payload={
                "serialNumber": self.drill_serial,
                "orderId": "{{orderId}}",
                "orderUpdateId": "{{orderUpdateId}}",
                "action": {
                    "id": "{{action_id}}",
                    "command": "DRILL",
                    "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                },
            },
        )

        # Kontext für Variable-Resolution
        test_order_id = str(uuid.uuid4())
        test_action_id = str(uuid.uuid4())
        context = {
            "module_serial": self.drill_serial,
            "orderId": test_order_id,
            "orderUpdateId": 2,
            "action_id": test_action_id,
        }

        # Variable-Resolution durchführen
        resolved_topic = self.executor._resolve_variables(sequence_step.topic, context)
        resolved_payload = self.executor._resolve_variables(sequence_step.payload, context)

        # Topics vergleichen
        self.assertEqual(
            resolved_topic,
            factory_topic,
            f"Topics stimmen nicht überein:\nSequenz: {resolved_topic}\nFactory: {factory_topic}",
        )

        # Payloads vergleichen
        self.assertEqual(
            resolved_payload["serialNumber"], factory_payload["serialNumber"], "serialNumber stimmt nicht überein"
        )
        self.assertEqual(
            int(resolved_payload["orderUpdateId"]),
            factory_payload["orderUpdateId"],
            "orderUpdateId stimmt nicht überein",
        )
        self.assertEqual(
            resolved_payload["action"]["command"],
            factory_payload["action"]["command"],
            "action.command stimmt nicht überein",
        )
        self.assertEqual(
            resolved_payload["action"]["metadata"],
            factory_payload["action"]["metadata"],
            "action.metadata stimmt nicht überein",
        )

        print("✅ DRILL Test erfolgreich:")
        print(f"   Topic: {resolved_topic}")
        print(f"   Command: {resolved_payload['action']['command']}")
        print(f"   SerialNumber: {resolved_payload['serialNumber']}")

    def test_drill_sequence_vs_factory_steering_drop(self):
        """Test: DRILL DROP - Sequenz vs. Factory-Steuerung"""
        # Factory-Steuerung Nachricht generieren
        factory_message = _prepare_factory_message(self.drill_module, "DROP", 3)
        factory_topic = factory_message["topic"]
        factory_payload = factory_message["payload"]

        # Sequenz-Schritt erstellen
        sequence_step = SequenceStep(
            step_id="drop_step",
            name="DROP",
            topic=f"module/v1/ff/{self.drill_serial}/order",
            payload={
                "serialNumber": self.drill_serial,
                "orderId": "{{orderId}}",
                "orderUpdateId": "{{orderUpdateId}}",
                "action": {
                    "id": "{{action_id}}",
                    "command": "DROP",
                    "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                },
            },
        )

        # Kontext für Variable-Resolution
        test_order_id = str(uuid.uuid4())
        test_action_id = str(uuid.uuid4())
        context = {
            "module_serial": self.drill_serial,
            "orderId": test_order_id,
            "orderUpdateId": 3,
            "action_id": test_action_id,
        }

        # Variable-Resolution durchführen
        resolved_topic = self.executor._resolve_variables(sequence_step.topic, context)
        resolved_payload = self.executor._resolve_variables(sequence_step.payload, context)

        # Topics vergleichen
        self.assertEqual(
            resolved_topic,
            factory_topic,
            f"Topics stimmen nicht überein:\nSequenz: {resolved_topic}\nFactory: {factory_topic}",
        )

        # Payloads vergleichen
        self.assertEqual(
            resolved_payload["serialNumber"], factory_payload["serialNumber"], "serialNumber stimmt nicht überein"
        )
        self.assertEqual(
            int(resolved_payload["orderUpdateId"]),
            factory_payload["orderUpdateId"],
            "orderUpdateId stimmt nicht überein",
        )
        self.assertEqual(
            resolved_payload["action"]["command"],
            factory_payload["action"]["command"],
            "action.command stimmt nicht überein",
        )
        self.assertEqual(
            resolved_payload["action"]["metadata"],
            factory_payload["action"]["metadata"],
            "action.metadata stimmt nicht überein",
        )

        print("✅ DROP Test erfolgreich:")
        print(f"   Topic: {resolved_topic}")
        print(f"   Command: {resolved_payload['action']['command']}")
        print(f"   SerialNumber: {resolved_payload['serialNumber']}")

    def test_complete_drill_sequence_structure(self):
        """Test: Komplette DRILL-Sequenz-Struktur"""
        # Factory-Steuerung Nachrichten für alle Schritte
        factory_messages = []
        for i, command in enumerate(["PICK", "DRILL", "DROP"]):
            factory_message = _prepare_factory_message(self.drill_module, command, i + 1)
            factory_messages.append(factory_message)

        # Sequenz-Definition erstellen
        sequence = SequenceDefinition(
            name="drill_complete_sequence",
            description="Komplette DRILL-Sequenz: PICK → DRILL → DROP",
            context={"module_serial": self.drill_serial, "module_type": self.drill_module},
            steps=[
                SequenceStep(
                    step_id="pick_step",
                    name="PICK",
                    topic=f"module/v1/ff/{self.drill_serial}/order",
                    payload={
                        "serialNumber": self.drill_serial,
                        "orderId": "{{orderId}}",
                        "orderUpdateId": "{{orderUpdateId}}",
                        "action": {
                            "id": "{{action_id}}",
                            "command": "PICK",
                            "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                        },
                    },
                ),
                SequenceStep(
                    step_id="drill_step",
                    name="DRILL",
                    topic=f"module/v1/ff/{self.drill_serial}/order",
                    payload={
                        "serialNumber": self.drill_serial,
                        "orderId": "{{orderId}}",
                        "orderUpdateId": "{{orderUpdateId}}",
                        "action": {
                            "id": "{{action_id}}",
                            "command": "DRILL",
                            "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                        },
                    },
                ),
                SequenceStep(
                    step_id="drop_step",
                    name="DROP",
                    topic=f"module/v1/ff/{self.drill_serial}/order",
                    payload={
                        "serialNumber": self.drill_serial,
                        "orderId": "{{orderId}}",
                        "orderUpdateId": "{{orderUpdateId}}",
                        "action": {
                            "id": "{{action_id}}",
                            "command": "DROP",
                            "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                        },
                    },
                ),
            ],
        )

        # Teste jeden Schritt
        for i, (step, factory_message) in enumerate(zip(sequence.steps, factory_messages)):
            # Kontext für Variable-Resolution
            test_order_id = str(uuid.uuid4())
            test_action_id = str(uuid.uuid4())
            context = {
                "module_serial": self.drill_serial,
                "orderId": test_order_id,
                "orderUpdateId": i + 1,
                "action_id": test_action_id,
            }

            # Variable-Resolution durchführen
            resolved_topic = self.executor._resolve_variables(step.topic, context)
            resolved_payload = self.executor._resolve_variables(step.payload, context)

            # Topics vergleichen
            self.assertEqual(
                resolved_topic, factory_message["topic"], f"Schritt {i+1} ({step.name}) - Topics stimmen nicht überein"
            )

            # Payloads vergleichen
            self.assertEqual(
                resolved_payload["serialNumber"],
                factory_message["payload"]["serialNumber"],
                f"Schritt {i+1} ({step.name}) - serialNumber stimmt nicht überein",
            )
            self.assertEqual(
                int(resolved_payload["orderUpdateId"]),
                factory_message["payload"]["orderUpdateId"],
                f"Schritt {i+1} ({step.name}) - orderUpdateId stimmt nicht überein",
            )
            self.assertEqual(
                resolved_payload["action"]["command"],
                factory_message["payload"]["action"]["command"],
                f"Schritt {i+1} ({step.name}) - action.command stimmt nicht überein",
            )
            self.assertEqual(
                resolved_payload["action"]["metadata"],
                factory_message["payload"]["action"]["metadata"],
                f"Schritt {i+1} ({step.name}) - action.metadata stimmt nicht überein",
            )

            print(f"✅ Schritt {i+1} ({step.name}) - Struktur identisch mit Factory-Steuerung")

        print("🎉 Komplette DRILL-Sequenz-Struktur ist identisch mit Factory-Steuerung!")

    def test_mill_sequence_vs_factory_steering(self):
        """Test: MILL-Sequenz vs. Factory-Steuerung"""
        mill_serial = "SVR3QA2098"
        mill_module = "MILL"

        # Teste alle MILL-Befehle
        for command in ["PICK", "MILL", "DROP"]:
            # Factory-Steuerung Nachricht generieren
            factory_message = _prepare_factory_message(mill_module, command, 1)

            # Sequenz-Schritt erstellen
            sequence_step = SequenceStep(
                step_id=f"{command.lower()}_step",
                name=command,
                topic=f"module/v1/ff/{mill_serial}/order",
                payload={
                    "serialNumber": mill_serial,
                    "orderId": "{{orderId}}",
                    "orderUpdateId": "{{orderUpdateId}}",
                    "action": {
                        "id": "{{action_id}}",
                        "command": command,
                        "metadata": {"priority": "NORMAL", "timeout": 300, "type": "WHITE"},
                    },
                },
            )

            # Kontext für Variable-Resolution
            test_order_id = str(uuid.uuid4())
            test_action_id = str(uuid.uuid4())
            context = {
                "module_serial": mill_serial,
                "orderId": test_order_id,
                "orderUpdateId": 1,
                "action_id": test_action_id,
            }

            # Variable-Resolution durchführen
            resolved_topic = self.executor._resolve_variables(sequence_step.topic, context)
            resolved_payload = self.executor._resolve_variables(sequence_step.payload, context)

            # Topics vergleichen
            self.assertEqual(resolved_topic, factory_message["topic"], f"MILL {command} - Topics stimmen nicht überein")

            # Payloads vergleichen
            self.assertEqual(
                resolved_payload["serialNumber"],
                factory_message["payload"]["serialNumber"],
                f"MILL {command} - serialNumber stimmt nicht überein",
            )
            self.assertEqual(
                resolved_payload["action"]["command"],
                factory_message["payload"]["action"]["command"],
                f"MILL {command} - action.command stimmt nicht überein",
            )
            self.assertEqual(
                resolved_payload["action"]["metadata"],
                factory_message["payload"]["action"]["metadata"],
                f"MILL {command} - action.metadata stimmt nicht überein",
            )

            print(f"✅ MILL {command} - Struktur identisch mit Factory-Steuerung")


if __name__ == "__main__":
    # Test-Suite ausführen
    unittest.main(verbosity=2)
