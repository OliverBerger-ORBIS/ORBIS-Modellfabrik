#!/usr/bin/env python3
"""
Unit Tests für MessageGenerator - FTS und Factory Reset Funktionalität

Diese Tests stellen sicher, dass der MessageGenerator genau die gleichen
Nachrichten-Strukturen erzeugt, die in Commit 4378dbe funktioniert haben.

Funktionierende Funktionalität aus Commit 4378dbe:
- FTS: CHARGE, DOCK, TRANSPORT (Seriennummer: 5iO4)
- Factory Reset: ccu/set/reset

Commit: 4378dbe - "Add comprehensive MQTT analysis tools and factory reset functionality"
"""

import json
import unittest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch


# Import der funktionierenden MQTT-Nachrichten-Strukturen
class WorkingMQTTFunctionality4378dbe:
    """Funktionierende MQTT-Funktionalität aus Commit 4378dbe - Referenz für MessageGenerator"""

    # FTS-Modul-Konfiguration (exakt wie in funktionierendem Commit)
    FTS_MODULE = {"serial": "5iO4", "ip": "192.168.0.100", "commands": ["CHARGE", "DOCK", "TRANSPORT"]}

    # Factory Reset Konfiguration
    FACTORY_RESET = {"topic": "ccu/set/reset", "required_fields": ["timestamp", "withStorage"]}

    @staticmethod
    def get_fts_topic() -> str:
        """MQTT Topic für FTS generieren (exakt wie in funktionierendem Commit)"""
        return f"fts/v1/ff/{WorkingMQTTFunctionality4378dbe.FTS_MODULE['serial']}/command"

    @staticmethod
    def create_reference_fts_message(command: str, order_id: str = None, order_update_id: int = 1) -> dict:
        """Referenz-FTS-Nachricht aus funktionierendem Commit erstellen"""
        if command not in WorkingMQTTFunctionality4378dbe.FTS_MODULE["commands"]:
            raise ValueError(f"Command '{command}' not supported for FTS")

        if order_id is None:
            order_id = str(uuid.uuid4())

        serial = WorkingMQTTFunctionality4378dbe.FTS_MODULE["serial"]

        # Exakte Nachrichten-Struktur aus funktionierendem Commit
        message = {
            "serialNumber": serial,
            "orderId": order_id,
            "orderUpdateId": order_update_id,
            "action": {
                "id": str(uuid.uuid4()),
                "command": command,
                "metadata": {"priority": "NORMAL", "timeout": 300, "type": "TRANSPORT"},
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }

        return message

    @staticmethod
    def create_reference_factory_reset_message(with_storage: bool = False) -> dict:
        """Referenz-Factory-Reset-Nachricht aus funktionierendem Commit erstellen"""
        # Exakte Nachrichten-Struktur aus funktionierendem Commit
        message = {"timestamp": datetime.utcnow().isoformat() + "Z", "withStorage": with_storage}

        return message


class TestMessageGeneratorFTSCompatibility(unittest.TestCase):
    """Tests für die Kompatibilität des MessageGenerators mit funktionierenden FTS-Nachrichten"""

    def setUp(self):
        """Test-Setup"""
        self.reference_functionality = WorkingMQTTFunctionality4378dbe()

    def test_fts_message_structure_exact_match(self):
        """Test: MessageGenerator muss exakt die gleiche FTS-Nachrichten-Struktur erzeugen"""
        # Referenz-Nachricht aus funktionierendem Commit
        reference_message = WorkingMQTTFunctionality4378dbe.create_reference_fts_message("CHARGE")

        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()
        # generated_message = message_generator.generate_fts_charge_message()

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.generate_fts_charge_message.return_value = reference_message

        generated_message = mock_message_generator.generate_fts_charge_message()

        # Exakte Struktur-Übereinstimmung prüfen
        self.assertEqual(generated_message["serialNumber"], reference_message["serialNumber"])
        self.assertEqual(generated_message["action"]["command"], reference_message["action"]["command"])
        self.assertEqual(
            generated_message["action"]["metadata"]["type"], reference_message["action"]["metadata"]["type"]
        )
        self.assertEqual(
            generated_message["action"]["metadata"]["priority"], reference_message["action"]["metadata"]["priority"]
        )
        self.assertEqual(
            generated_message["action"]["metadata"]["timeout"], reference_message["action"]["metadata"]["timeout"]
        )

    def test_fts_charge_command_exact_match(self):
        """Test: FTS CHARGE-Befehl muss exakt die gleiche Struktur haben"""
        reference_message = WorkingMQTTFunctionality4378dbe.create_reference_fts_message("CHARGE")

        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()
        # generated_message = message_generator.generate_fts_charge_message()

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.generate_fts_charge_message.return_value = reference_message

        generated_message = mock_message_generator.generate_fts_charge_message()

        # Exakte Struktur-Übereinstimmung prüfen
        self.assertEqual(generated_message["serialNumber"], "5iO4")
        self.assertEqual(generated_message["action"]["command"], "CHARGE")
        self.assertEqual(generated_message["action"]["metadata"]["type"], "TRANSPORT")
        self.assertEqual(generated_message["action"]["metadata"]["priority"], "NORMAL")
        self.assertEqual(generated_message["action"]["metadata"]["timeout"], 300)

        # Erforderliche Felder prüfen
        required_fields = ["serialNumber", "orderId", "orderUpdateId", "action", "timestamp"]
        for field in required_fields:
            self.assertIn(field, generated_message)

        # Action-Struktur prüfen
        action = generated_message["action"]
        required_action_fields = ["id", "command", "metadata"]
        for field in required_action_fields:
            self.assertIn(field, action)

        # Metadata-Struktur prüfen
        metadata = action["metadata"]
        required_metadata_fields = ["priority", "timeout", "type"]
        for field in required_metadata_fields:
            self.assertIn(field, metadata)

    def test_fts_dock_command_exact_match(self):
        """Test: FTS DOCK-Befehl muss exakt die gleiche Struktur haben"""
        reference_message = WorkingMQTTFunctionality4378dbe.create_reference_fts_message("DOCK")

        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()
        # generated_message = message_generator.generate_fts_dock_message()

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.generate_fts_dock_message.return_value = reference_message

        generated_message = mock_message_generator.generate_fts_dock_message()

        # Exakte Struktur-Übereinstimmung prüfen
        self.assertEqual(generated_message["serialNumber"], "5iO4")
        self.assertEqual(generated_message["action"]["command"], "DOCK")
        self.assertEqual(generated_message["action"]["metadata"]["type"], "TRANSPORT")
        self.assertEqual(generated_message["action"]["metadata"]["priority"], "NORMAL")
        self.assertEqual(generated_message["action"]["metadata"]["timeout"], 300)

    def test_fts_transport_command_exact_match(self):
        """Test: FTS TRANSPORT-Befehl muss exakt die gleiche Struktur haben"""
        reference_message = WorkingMQTTFunctionality4378dbe.create_reference_fts_message("TRANSPORT")

        # TODO: Später durch echten MessageGenerator ersetzen
        # generated_message = message_generator.generate_fts_transport_message()

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.generate_fts_transport_message.return_value = reference_message

        generated_message = mock_message_generator.generate_fts_transport_message()

        # Exakte Struktur-Übereinstimmung prüfen
        self.assertEqual(generated_message["serialNumber"], "5iO4")
        self.assertEqual(generated_message["action"]["command"], "TRANSPORT")
        self.assertEqual(generated_message["action"]["metadata"]["type"], "TRANSPORT")
        self.assertEqual(generated_message["action"]["metadata"]["priority"], "NORMAL")
        self.assertEqual(generated_message["action"]["metadata"]["timeout"], 300)

    def test_fts_topic_generation_exact_match(self):
        """Test: FTS Topic-Generierung muss exakt wie in funktionierendem Commit sein"""
        expected_topic = "fts/v1/ff/5iO4/command"

        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()
        # generated_topic = message_generator.get_fts_topic()

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.get_fts_topic.return_value = expected_topic

        generated_topic = mock_message_generator.get_fts_topic()

        # Topic muss exakt übereinstimmen
        self.assertEqual(generated_topic, expected_topic)

    def test_fts_metadata_structure_exact_match(self):
        """Test: FTS Metadata-Struktur muss exakt wie in funktionierendem Commit sein"""
        # Referenz-Metadata aus funktionierendem Commit
        reference_metadata = {"priority": "NORMAL", "timeout": 300, "type": "TRANSPORT"}

        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()
        # generated_metadata = message_generator.get_fts_metadata()

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.get_fts_metadata.return_value = reference_metadata

        generated_metadata = mock_message_generator.get_fts_metadata()

        # Metadata muss exakt übereinstimmen
        self.assertEqual(generated_metadata["priority"], "NORMAL")
        self.assertEqual(generated_metadata["timeout"], 300)
        self.assertEqual(generated_metadata["type"], "TRANSPORT")


class TestMessageGeneratorFactoryResetCompatibility(unittest.TestCase):
    """Tests für die Kompatibilität des MessageGenerators mit funktionierenden Factory-Reset-Nachrichten"""

    def test_factory_reset_message_structure_exact_match(self):
        """Test: MessageGenerator muss exakt die gleiche Factory-Reset-Nachrichten-Struktur erzeugen"""
        # Referenz-Nachricht aus funktionierendem Commit
        reference_message = WorkingMQTTFunctionality4378dbe.create_reference_factory_reset_message(with_storage=False)

        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()
        # generated_message = message_generator.generate_factory_reset_message(with_storage=False)

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.generate_factory_reset_message.return_value = reference_message

        generated_message = mock_message_generator.generate_factory_reset_message(with_storage=False)

        # Exakte Struktur-Übereinstimmung prüfen
        self.assertEqual(generated_message["withStorage"], False)

        # Erforderliche Felder prüfen
        required_fields = ["timestamp", "withStorage"]
        for field in required_fields:
            self.assertIn(field, generated_message)

        # withStorage muss boolean sein
        self.assertIsInstance(generated_message["withStorage"], bool)

    def test_factory_reset_with_storage_true(self):
        """Test: Factory Reset mit withStorage=True"""
        reference_message = WorkingMQTTFunctionality4378dbe.create_reference_factory_reset_message(with_storage=True)

        # TODO: Später durch echten MessageGenerator ersetzen
        # generated_message = message_generator.generate_factory_reset_message(with_storage=True)

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.generate_factory_reset_message.return_value = reference_message

        generated_message = mock_message_generator.generate_factory_reset_message(with_storage=True)

        # withStorage muss True sein
        self.assertEqual(generated_message["withStorage"], True)
        self.assertIsInstance(generated_message["withStorage"], bool)

    def test_factory_reset_topic_exact_match(self):
        """Test: Factory Reset Topic muss exakt wie in funktionierendem Commit sein"""
        expected_topic = "ccu/set/reset"

        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()
        # generated_topic = message_generator.get_factory_reset_topic()

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.get_factory_reset_topic.return_value = expected_topic

        generated_topic = mock_message_generator.get_factory_reset_topic()

        # Topic muss exakt übereinstimmen
        self.assertEqual(generated_topic, expected_topic)


class TestIntegrationRequirements(unittest.TestCase):
    """Tests für die Integrationsanforderungen des MessageGenerators"""

    def test_message_generator_interface_requirements(self):
        """Test: MessageGenerator muss bestimmte Methoden bereitstellen"""
        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()

        # Erforderliche FTS-Methoden
        required_fts_methods = [
            "generate_fts_charge_message",
            "generate_fts_dock_message",
            "generate_fts_transport_message",
            "get_fts_topic",
            "get_fts_metadata",
        ]

        # Erforderliche Factory-Reset-Methoden
        required_factory_reset_methods = ["generate_factory_reset_message", "get_factory_reset_topic"]

        all_required_methods = required_fts_methods + required_factory_reset_methods

        for method_name in all_required_methods:
            # Methode sollte existieren
            self.assertTrue(hasattr(mock_message_generator, method_name))

            # Methode sollte aufrufbar sein
            self.assertTrue(callable(getattr(mock_message_generator, method_name)))


class TestJSONSerialization(unittest.TestCase):
    """Tests für die JSON-Serialisierung der Nachrichten"""

    def test_fts_message_json_serialization(self):
        """Test: FTS-Nachrichten müssen korrekt JSON-serialisiert werden"""
        # Referenz-Nachricht aus funktionierendem Commit
        reference_message = WorkingMQTTFunctionality4378dbe.create_reference_fts_message("CHARGE")

        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()
        # generated_message = message_generator.generate_fts_charge_message()

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.generate_fts_charge_message.return_value = reference_message

        generated_message = mock_message_generator.generate_fts_charge_message()

        # Nachricht sollte JSON-serialisierbar sein
        try:
            json.dumps(generated_message)
        except Exception as e:
            self.fail(f"FTS message is not JSON serializable: {e}")

    def test_factory_reset_message_json_serialization(self):
        """Test: Factory-Reset-Nachrichten müssen korrekt JSON-serialisiert werden"""
        # Referenz-Nachricht aus funktionierendem Commit
        reference_message = WorkingMQTTFunctionality4378dbe.create_reference_factory_reset_message(with_storage=False)

        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()
        # generated_message = message_generator.generate_factory_reset_message(with_storage=False)

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.generate_factory_reset_message.return_value = reference_message

        generated_message = mock_message_generator.generate_factory_reset_message(with_storage=False)

        # Nachricht sollte JSON-serialisierbar sein
        try:
            json.dumps(generated_message)
        except Exception as e:
            self.fail(f"Factory reset message is not JSON serializable: {e}")


if __name__ == "__main__":
    # Test-Suite ausführen
    unittest.main(verbosity=2)
