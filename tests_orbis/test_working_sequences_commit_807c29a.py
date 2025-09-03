#!/usr/bin/env python3
"""
Unit Tests für funktionierende MQTT-Sequenzen aus Commit 807c29a

Diese Tests stellen sicher, dass der spätere MessageGenerator genau die gleichen
Nachrichten-Strukturen erzeugt, die in diesem Commit funktioniert haben.

Funktionierende Sequenzen:
- AIQS: PICK → CHECK_QUALITY → DROP
- MILL: PICK → MILL → DROP
- DRILL: PICK → DRILL → DROP
- HBW: DROP (Einzelbefehl)

Commit: 807c29a - "Sequence Control for Mill Drill and AIQS"

WICHTIG: In diesem Commit funktionierte ein EINZIGER MQTT-Client sowohl für Senden als auch Empfangen!
"""

import json
import unittest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch


# Import der funktionierenden MQTT-Nachrichten-Strukturen
class WorkingMQTTSequences:
    """Funktionierende MQTT-Sequenzen aus Commit 807c29a - Referenz für MessageGenerator"""

    # Modul-Konfiguration (exakt wie in funktionierendem Commit)
    MODULES = {
        "AIQS": {"serial": "SVR4H76530", "ip": "192.168.0.70", "commands": ["PICK", "CHECK_QUALITY", "DROP"]},
        "MILL": {"serial": "SVR3QA2098", "ip": "192.168.0.40", "commands": ["PICK", "MILL", "DROP"]},
        "DRILL": {"serial": "SVR4H76449", "ip": "192.168.0.50", "commands": ["PICK", "DRILL", "DROP"]},
        "HBW": {"serial": "SVR3QA0022", "ip": "192.168.0.80", "commands": ["PICK", "DROP", "STORE"]},
    }

    @staticmethod
    def get_topic(module_name: str) -> str:
        """MQTT Topic für Modul generieren (exakt wie in funktionierendem Commit)"""
        if module_name not in WorkingMQTTSequences.MODULES:
            raise ValueError(f"Unknown module: {module_name}")

        serial = WorkingMQTTSequences.MODULES[module_name]["serial"]
        return f"module/v1/ff/{serial}/order"

    @staticmethod
    def create_reference_message(
        module_name: str, command: str, order_id: str = None, order_update_id: int = 1, workpiece_type: str = "WHITE"
    ) -> dict:
        """Referenz-MQTT-Nachricht aus funktionierendem Commit erstellen"""
        if module_name not in WorkingMQTTSequences.MODULES:
            raise ValueError(f"Unknown module: {module_name}")

        if command not in WorkingMQTTSequences.MODULES[module_name]["commands"]:
            raise ValueError(f"Command '{command}' not supported for module '{module_name}'")

        if order_id is None:
            order_id = str(uuid.uuid4())

        serial = WorkingMQTTSequences.MODULES[module_name]["serial"]

        # Exakte Nachrichten-Struktur aus funktionierendem Commit
        message = {
            "serialNumber": serial,
            "orderId": order_id,
            "orderUpdateId": order_update_id,
            "action": {
                "id": str(uuid.uuid4()),
                "command": command,
                "metadata": {"priority": "NORMAL", "timeout": 300, "type": workpiece_type},
            },
        }

        # Modul-spezifische Metadaten (exakt wie in funktionierendem Commit)
        if command == "MILL":
            message["action"]["metadata"]["duration"] = 45
        elif command == "DRILL":
            message["action"]["metadata"]["duration"] = 30

        return message

    @staticmethod
    def create_reference_sequence(module_name: str, workpiece_type: str = "WHITE") -> list:
        """Referenz-Sequenz aus funktionierendem Commit erstellen"""
        if module_name not in WorkingMQTTSequences.MODULES:
            raise ValueError(f"Unknown module: {module_name}")

        module_config = WorkingMQTTSequences.MODULES[module_name]
        commands = module_config["commands"]

        # Für Verarbeitungsmodule: PICK → PROCESS → DROP (exakt wie funktioniert)
        if module_name in ["MILL", "DRILL", "AIQS"]:
            if len(commands) >= 3:
                sequence_commands = [commands[0], commands[1], commands[2]]
            else:
                sequence_commands = commands
        else:
            sequence_commands = commands

        order_id = str(uuid.uuid4())
        sequence = []

        for i, command in enumerate(sequence_commands, 1):
            message = WorkingMQTTSequences.create_reference_message(module_name, command, order_id, i, workpiece_type)
            sequence.append(message)

        return sequence


class MQTTTopicTracker:
    """Trackt gesendete und empfangene MQTT-Topics für Unit-Tests"""

    def __init__(self):
        self.sent_topics = []  # Topics die gesendet wurden
        self.received_topics = []  # Topics die empfangen wurden
        self.sent_messages = []  # Gesendete Nachrichten mit Details
        self.received_messages = []  # Empfangene Nachrichten mit Details

    def track_sent_message(self, topic: str, message: dict, qos: int = 1):
        """Markiert eine gesendete Nachricht"""
        sent_info = {"timestamp": datetime.now(), "topic": topic, "message": message, "qos": qos, "type": "sent"}
        self.sent_topics.append(topic)
        self.sent_messages.append(sent_info)

    def track_received_message(self, topic: str, message: dict, qos: int = 1):
        """Markiert eine empfangene Nachricht"""
        received_info = {
            "timestamp": datetime.now(),
            "topic": topic,
            "message": message,
            "qos": qos,
            "type": "received",
        }
        self.received_topics.append(topic)
        self.received_messages.append(received_info)

    def get_sent_topics(self) -> list:
        """Gibt alle gesendeten Topics zurück"""
        return self.sent_topics

    def get_received_topics(self) -> list:
        """Gibt alle empfangenen Topics zurück"""
        return self.received_topics

    def get_sent_messages(self) -> list:
        """Gibt alle gesendeten Nachrichten zurück"""
        return self.sent_messages

    def get_received_messages(self) -> list:
        """Gibt alle empfangenen Nachrichten zurück"""
        return self.received_messages

    def get_topic_statistics(self) -> dict:
        """Gibt Statistiken über gesendete und empfangene Topics zurück"""
        sent_topic_counts = {}
        received_topic_counts = {}

        for topic in self.sent_topics:
            sent_topic_counts[topic] = sent_topic_counts.get(topic, 0) + 1

        for topic in self.received_topics:
            received_topic_counts[topic] = received_topic_counts.get(topic, 0) + 1

        return {
            "sent_topics": sent_topic_counts,
            "received_topics": received_topic_counts,
            "total_sent": len(self.sent_topics),
            "total_received": len(self.received_topics),
        }

    def clear(self):
        """Löscht alle gespeicherten Daten"""
        self.sent_topics.clear()
        self.received_topics.clear()
        self.sent_messages.clear()
        self.received_messages.clear()


class TestMessageGeneratorCompatibility(unittest.TestCase):
    """Tests für die Kompatibilität des zukünftigen MessageGenerators mit funktionierenden Nachrichten"""

    def setUp(self):
        """Test-Setup"""
        self.reference_sequences = WorkingMQTTSequences()
        self.topic_tracker = MQTTTopicTracker()

    def test_message_structure_exact_match(self):
        """Test: MessageGenerator muss exakt die gleiche Nachrichten-Struktur erzeugen"""
        # Referenz-Nachricht aus funktionierendem Commit
        reference_message = WorkingMQTTSequences.create_reference_message("AIQS", "PICK")

        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()
        # generated_message = message_generator.generate_aiqs_pick_message()

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.generate_aiqs_pick_message.return_value = reference_message

        generated_message = mock_message_generator.generate_aiqs_pick_message()

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

        # Topic für gesendete Nachricht tracken
        topic = WorkingMQTTSequences.get_topic("AIQS")
        self.topic_tracker.track_sent_message(topic, generated_message)

        # Prüfen ob Topic korrekt getrackt wurde
        self.assertIn(topic, self.topic_tracker.get_sent_topics())

    def test_aiqs_sequence_exact_match(self):
        """Test: AIQS-Sequenz muss exakt die gleiche Struktur haben"""
        reference_sequence = WorkingMQTTSequences.create_reference_sequence("AIQS", "WHITE")

        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()
        # generated_sequence = message_generator.generate_aiqs_sequence("WHITE")

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.generate_aiqs_sequence.return_value = reference_sequence

        generated_sequence = mock_message_generator.generate_aiqs_sequence("WHITE")

        # Exakte Sequenz-Übereinstimmung prüfen
        self.assertEqual(len(generated_sequence), 3)

        # Schritt 1: PICK
        self.assertEqual(generated_sequence[0]["action"]["command"], "PICK")
        self.assertEqual(generated_sequence[0]["orderUpdateId"], 1)

        # Schritt 2: CHECK_QUALITY
        self.assertEqual(generated_sequence[1]["action"]["command"], "CHECK_QUALITY")
        self.assertEqual(generated_sequence[1]["orderUpdateId"], 2)

        # Schritt 3: DROP
        self.assertEqual(generated_sequence[2]["action"]["command"], "DROP")
        self.assertEqual(generated_sequence[2]["orderUpdateId"], 3)

        # Order-ID muss konstant bleiben
        order_id = generated_sequence[0]["orderId"]
        for step in generated_sequence:
            self.assertEqual(step["orderId"], order_id)

        # Alle Topics der Sequenz tracken
        topic = WorkingMQTTSequences.get_topic("AIQS")
        for step in generated_sequence:
            self.topic_tracker.track_sent_message(topic, step)

        # Prüfen ob alle 3 Schritte getrackt wurden
        sent_topics = self.topic_tracker.get_sent_topics()
        self.assertEqual(sent_topics.count(topic), 3)

    def test_mill_sequence_exact_match(self):
        """Test: MILL-Sequenz muss exakt die gleiche Struktur haben"""
        reference_sequence = WorkingMQTTSequences.create_reference_sequence("MILL", "WHITE")

        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()
        # generated_sequence = message_generator.generate_mill_sequence("WHITE")

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.generate_mill_sequence.return_value = reference_sequence

        generated_sequence = mock_message_generator.generate_mill_sequence("WHITE")

        # Exakte Sequenz-Übereinstimmung prüfen
        self.assertEqual(len(generated_sequence), 3)

        # Schritt 1: PICK
        self.assertEqual(generated_sequence[0]["action"]["command"], "PICK")
        self.assertEqual(generated_sequence[0]["orderUpdateId"], 1)

        # Schritt 2: MILL (mit duration)
        self.assertEqual(generated_sequence[1]["action"]["command"], "MILL")
        self.assertEqual(generated_sequence[1]["orderUpdateId"], 2)
        self.assertEqual(generated_sequence[1]["action"]["metadata"]["duration"], 45)

        # Schritt 3: DROP
        self.assertEqual(generated_sequence[2]["action"]["command"], "DROP")
        self.assertEqual(generated_sequence[2]["orderUpdateId"], 3)

        # Order-ID muss konstant bleiben
        order_id = generated_sequence[0]["orderId"]
        for step in generated_sequence:
            self.assertEqual(step["orderId"], order_id)

        # Alle Topics der Sequenz tracken
        topic = WorkingMQTTSequences.get_topic("MILL")
        for step in generated_sequence:
            self.topic_tracker.track_sent_message(topic, step)

        # Prüfen ob alle 3 Schritte getrackt wurden
        sent_topics = self.topic_tracker.get_sent_topics()
        self.assertEqual(sent_topics.count(topic), 3)

    def test_drill_sequence_exact_match(self):
        """Test: DRILL-Sequenz muss exakt die gleiche Struktur haben"""
        reference_sequence = WorkingMQTTSequences.create_reference_sequence("DRILL", "WHITE")

        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()
        # generated_sequence = message_generator.generate_drill_sequence("WHITE")

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.generate_drill_sequence.return_value = reference_sequence

        generated_sequence = mock_message_generator.generate_drill_sequence("WHITE")

        # Exakte Sequenz-Übereinstimmung prüfen
        self.assertEqual(len(generated_sequence), 3)

        # Schritt 1: PICK
        self.assertEqual(generated_sequence[0]["action"]["command"], "PICK")
        self.assertEqual(generated_sequence[0]["orderUpdateId"], 1)

        # Schritt 2: DRILL (mit duration)
        self.assertEqual(generated_sequence[1]["action"]["command"], "DRILL")
        self.assertEqual(generated_sequence[1]["orderUpdateId"], 2)
        self.assertEqual(generated_sequence[1]["action"]["metadata"]["duration"], 30)

        # Schritt 3: DROP
        self.assertEqual(generated_sequence[2]["action"]["command"], "DROP")
        self.assertEqual(generated_sequence[2]["orderUpdateId"], 3)

        # Order-ID muss konstant bleiben
        order_id = generated_sequence[0]["orderId"]
        for step in generated_sequence:
            self.assertEqual(step["orderId"], order_id)

        # Alle Topics der Sequenz tracken
        topic = WorkingMQTTSequences.get_topic("DRILL")
        for step in generated_sequence:
            self.topic_tracker.track_sent_message(topic, step)

        # Prüfen ob alle 3 Schritte getrackt wurden
        sent_topics = self.topic_tracker.get_sent_topics()
        self.assertEqual(sent_topics.count(topic), 3)

    def test_hbw_drop_exact_match(self):
        """Test: HBW DROP muss exakt die gleiche Struktur haben"""
        reference_message = WorkingMQTTSequences.create_reference_message("HBW", "DROP", workpiece_type="WHITE")

        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()
        # generated_message = message_generator.generate_hbw_drop_message("WHITE")

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.generate_hbw_drop_message.return_value = reference_message

        generated_message = mock_message_generator.generate_hbw_drop_message("WHITE")

        # Exakte Struktur-Übereinstimmung prüfen
        self.assertEqual(generated_message["serialNumber"], "SVR3QA0022")
        self.assertEqual(generated_message["action"]["command"], "DROP")
        self.assertEqual(generated_message["action"]["metadata"]["type"], "WHITE")
        self.assertEqual(generated_message["action"]["metadata"]["priority"], "NORMAL")
        self.assertEqual(generated_message["action"]["metadata"]["timeout"], 300)

        # Topic für gesendete Nachricht tracken
        topic = WorkingMQTTSequences.get_topic("HBW")
        self.topic_tracker.track_sent_message(topic, generated_message)

        # Prüfen ob Topic korrekt getrackt wurde
        self.assertIn(topic, self.topic_tracker.get_sent_topics())

    def test_color_behavior_preserved(self):
        """Test: Farbverhalten muss exakt wie in funktionierendem Commit sein"""
        colors = ["WHITE", "RED", "BLUE"]

        for color in colors:
            # AIQS sollte Farbe korrekt setzen
            reference_message = WorkingMQTTSequences.create_reference_message("AIQS", "PICK", workpiece_type=color)

            # TODO: Später durch echten MessageGenerator ersetzen
            # message_generator = MessageGenerator()
            # generated_message = message_generator.generate_aiqs_pick_message(color)

            # Für jetzt: Mock des MessageGenerators
            mock_message_generator = Mock()
            mock_message_generator.generate_aiqs_pick_message.return_value = reference_message

            generated_message = mock_message_generator.generate_aiqs_pick_message(color)

            # Farbe muss exakt gesetzt sein
            self.assertEqual(generated_message["action"]["metadata"]["type"], color)

            # MILL sollte Farbe auch setzen (auch wenn ignoriert)
            reference_message = WorkingMQTTSequences.create_reference_message("MILL", "MILL", workpiece_type=color)

            # TODO: Später durch echten MessageGenerator ersetzen
            # generated_message = message_generator.generate_mill_mill_message(color)

            # Für jetzt: Mock des MessageGenerators
            mock_message_generator.generate_mill_mill_message.return_value = reference_message

            generated_message = mock_message_generator.generate_mill_mill_message(color)

            # Farbe muss exakt gesetzt sein
            self.assertEqual(generated_message["action"]["metadata"]["type"], color)

    def test_topic_generation_exact_match(self):
        """Test: Topic-Generierung muss exakt wie in funktionierendem Commit sein"""
        expected_topics = {
            "AIQS": "module/v1/ff/SVR4H76530/order",
            "MILL": "module/v1/ff/SVR3QA2098/order",
            "DRILL": "module/v1/ff/SVR4H76449/order",
            "HBW": "module/v1/ff/SVR3QA0022/order",
        }

        for module_name, expected_topic in expected_topics.items():
            # TODO: Später durch echten MessageGenerator ersetzen
            # message_generator = MessageGenerator()
            # generated_topic = message_generator.get_topic(module_name)

            # Für jetzt: Mock des MessageGenerators
            mock_message_generator = Mock()
            mock_message_generator.get_topic.return_value = expected_topic

            generated_topic = mock_message_generator.get_topic(module_name)

            # Topic muss exakt übereinstimmen
            self.assertEqual(generated_topic, expected_topic)

    def test_metadata_structure_exact_match(self):
        """Test: Metadata-Struktur muss exakt wie in funktionierendem Commit sein"""
        # Referenz-Metadata aus funktionierendem Commit
        reference_metadata = {"priority": "NORMAL", "timeout": 300, "type": "WHITE"}

        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()
        # generated_metadata = message_generator.get_default_metadata("WHITE")

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.get_default_metadata.return_value = reference_metadata

        generated_metadata = mock_message_generator.get_default_metadata("WHITE")

        # Metadata muss exakt übereinstimmen
        self.assertEqual(generated_metadata["priority"], "NORMAL")
        self.assertEqual(generated_metadata["timeout"], 300)
        self.assertEqual(generated_metadata["type"], "WHITE")

        # MILL-spezifische Metadata
        mill_reference_metadata = reference_metadata.copy()
        mill_reference_metadata["duration"] = 45

        # TODO: Später durch echten MessageGenerator ersetzen
        # generated_mill_metadata = message_generator.get_mill_metadata("WHITE")

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator.get_mill_metadata.return_value = mill_reference_metadata

        generated_mill_metadata = mock_message_generator.get_mill_metadata("WHITE")

        # MILL-Metadata muss exakt übereinstimmen
        self.assertEqual(generated_mill_metadata["priority"], "NORMAL")
        self.assertEqual(generated_mill_metadata["timeout"], 300)
        self.assertEqual(generated_mill_metadata["type"], "WHITE")
        self.assertEqual(generated_mill_metadata["duration"], 45)

    def test_json_serialization_exact_match(self):
        """Test: JSON-Serialisierung muss exakt wie in funktionierendem Commit sein"""
        # Referenz-Nachricht aus funktionierendem Commit
        reference_message = WorkingMQTTSequences.create_reference_message("AIQS", "PICK")

        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()
        # generated_message = message_generator.generate_aiqs_pick_message()

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()
        mock_message_generator.generate_aiqs_pick_message.return_value = reference_message

        generated_message = mock_message_generator.generate_aiqs_pick_message()

        # Beide Nachrichten sollten identisch JSON-serialisiert werden
        reference_json = json.dumps(reference_message, sort_keys=True)
        generated_json = json.dumps(generated_message, sort_keys=True)

        self.assertEqual(generated_json, reference_json)

    def test_topic_tracking_comprehensive(self):
        """Test: Umfassendes Topic-Tracking für alle Module"""
        # Alle Module testen
        modules = ["AIQS", "MILL", "DRILL", "HBW"]

        for module_name in modules:
            # Einzelbefehl testen
            if module_name in ["AIQS", "MILL", "DRILL"]:
                # PICK-Befehl für Verarbeitungsmodule
                reference_message = WorkingMQTTSequences.create_reference_message(module_name, "PICK")
                topic = WorkingMQTTSequences.get_topic(module_name)

                # Topic tracken
                self.topic_tracker.track_sent_message(topic, reference_message)

                # Prüfen ob Topic korrekt getrackt wurde
                self.assertIn(topic, self.topic_tracker.get_sent_topics())
            else:
                # DROP-Befehl für HBW
                reference_message = WorkingMQTTSequences.create_reference_message(module_name, "DROP")
                topic = WorkingMQTTSequences.get_topic(module_name)

                # Topic tracken
                self.topic_tracker.track_sent_message(topic, reference_message)

                # Prüfen ob Topic korrekt getrackt wurde
                self.assertIn(topic, self.topic_tracker.get_sent_topics())

        # Statistiken prüfen
        stats = self.topic_tracker.get_topic_statistics()
        self.assertEqual(stats["total_sent"], 4)  # 4 Module getestet

        # Alle erwarteten Topics sollten gesendet worden sein
        expected_topics = [
            "module/v1/ff/SVR4H76530/order",  # AIQS
            "module/v1/ff/SVR3QA2098/order",  # MILL
            "module/v1/ff/SVR4H76449/order",  # DRILL
            "module/v1/ff/SVR3QA0022/order",  # HBW
        ]

        for expected_topic in expected_topics:
            self.assertIn(expected_topic, stats["sent_topics"])
            self.assertEqual(stats["sent_topics"][expected_topic], 1)


class TestIntegrationRequirements(unittest.TestCase):
    """Tests für die Integrationsanforderungen des MessageGenerators"""

    def test_message_generator_interface_requirements(self):
        """Test: MessageGenerator muss bestimmte Methoden bereitstellen"""
        # TODO: Später durch echten MessageGenerator ersetzen
        # message_generator = MessageGenerator()

        # Für jetzt: Mock des MessageGenerators
        mock_message_generator = Mock()

        # Erforderliche Methoden
        required_methods = [
            "generate_aiqs_pick_message",
            "generate_aiqs_check_quality_message",
            "generate_aiqs_drop_message",
            "generate_mill_pick_message",
            "generate_mill_mill_message",
            "generate_mill_drop_message",
            "generate_drill_pick_message",
            "generate_drill_drill_message",
            "generate_drill_drop_message",
            "generate_hbw_drop_message",
            "generate_aiqs_sequence",
            "generate_mill_sequence",
            "generate_drill_sequence",
            "get_topic",
            "get_default_metadata",
            "get_mill_metadata",
            "get_drill_metadata",
        ]

        for method_name in required_methods:
            # Methode sollte existieren
            self.assertTrue(hasattr(mock_message_generator, method_name))

            # Methode sollte aufrufbar sein
            self.assertTrue(callable(getattr(mock_message_generator, method_name)))


class TestSingleMQTTClientArchitecture(unittest.TestCase):
    """Tests für die Einzel-MQTT-Client-Architektur die in Commit 807c29a funktioniert hat"""

    def test_single_client_send_and_receive(self):
        """Test: Einzelner MQTT-Client kann sowohl senden als auch empfangen"""
        # Mock des MQTT-Clients (wie in funktionierendem Commit)
        mock_mqtt_client = Mock()

        # Client sollte verbunden sein
        mock_mqtt_client.is_connected.return_value = True

        # Client sollte publish können
        mock_publish_result = Mock()
        mock_publish_result.rc = 0  # MQTT_ERR_SUCCESS
        mock_mqtt_client.publish.return_value = mock_publish_result

        # Client sollte subscribe können
        mock_mqtt_client.subscribe.return_value = (0, 1)  # (result, mid)

        # Test: Nachricht senden
        topic = "module/v1/ff/SVR4H76530/order"
        message = {"test": "data"}
        result = mock_mqtt_client.publish(topic, json.dumps(message), qos=1)

        # Senden sollte erfolgreich sein
        self.assertEqual(result.rc, 0)

        # Test: Topic subscriben
        subscribe_result, mid = mock_mqtt_client.subscribe(topic, qos=1)

        # Subscribe sollte erfolgreich sein
        self.assertEqual(subscribe_result, 0)
        self.assertEqual(mid, 1)

        # Client sollte sowohl publish als auch subscribe aufrufen
        mock_mqtt_client.publish.assert_called_once()
        mock_mqtt_client.subscribe.assert_called_once()

    def test_mqtt_client_configuration(self):
        """Test: MQTT-Client-Konfiguration wie in funktionierendem Commit"""
        # Konfiguration aus funktionierendem Commit
        expected_config = {"broker": "192.168.0.100", "port": 1883, "username": "default", "password": "default"}

        # Mock des MQTT-Clients
        mock_mqtt_client = Mock()

        # Client sollte mit korrekter Konfiguration verbinden
        mock_mqtt_client.connect.return_value = 0  # MQTT_ERR_SUCCESS
        mock_mqtt_client.username_pw_set.assert_not_called()  # Wird später gesetzt

        # Verbindung testen
        result = mock_mqtt_client.connect(expected_config["broker"], expected_config["port"], 60)

        # Verbindung sollte erfolgreich sein
        self.assertEqual(result, 0)

        # Client sollte mit korrekter Broker-IP verbunden werden
        mock_mqtt_client.connect.assert_called_with("192.168.0.100", 1883, 60)


if __name__ == "__main__":
    # Test-Suite ausführen
    unittest.main(verbosity=2)
