"""
Test: Payload-Integration mit echten Daten
Basiert auf data/aps-data/ aber verwendet Test-Payloads aus tests/test_payloads/
"""

import json
import unittest
from pathlib import Path


class TestPayloadIntegration(unittest.TestCase):
    """Test: Integration von echten Payload-Daten in Tests"""

    def setUp(self):
        """Setup: Test-Payloads laden"""
        self.test_payloads_dir = Path("tests/test_omf2/test_payloads")
        self.payload_files = [
            "module_state_payload.json",
            "ccu_order_request_payload.json",
            "txt_sensor_payload.json",
            "module_connection_payload.json",
            "ccu_global_payload.json",
        ]

    def test_payload_files_exist(self):
        """Test: Alle Test-Payload-Dateien existieren"""
        for payload_file in self.payload_files:
            payload_path = self.test_payloads_dir / payload_file
            self.assertTrue(payload_path.exists(), f"Test-Payload {payload_file} sollte existieren")
            self.assertTrue(payload_path.is_file(), f"Test-Payload {payload_file} sollte eine Datei sein")

    def test_payload_files_valid_json(self):
        """Test: Alle Test-Payload-Dateien sind gültiges JSON"""
        for payload_file in self.payload_files:
            payload_path = self.test_payloads_dir / payload_file
            try:
                with open(payload_path, encoding="utf-8") as f:
                    data = json.load(f)
                self.assertIsInstance(data, dict, f"Test-Payload {payload_file} sollte ein Dictionary sein")
                self.assertIn("topic", data, f"Test-Payload {payload_file} sollte 'topic' haben")
                self.assertIn("payload", data, f"Test-Payload {payload_file} sollte 'payload' haben")
            except json.JSONDecodeError as e:
                self.fail(f"Test-Payload {payload_file} ist kein gültiges JSON: {e}")

    def test_payload_structure_consistency(self):
        """Test: Payload-Struktur ist konsistent"""
        for payload_file in self.payload_files:
            payload_path = self.test_payloads_dir / payload_file
            with open(payload_path, encoding="utf-8") as f:
                data = json.load(f)

            # Prüfe Topic-Format
            topic = data["topic"]
            self.assertIsInstance(topic, str, f"Topic in {payload_file} sollte String sein")
            self.assertGreater(len(topic), 0, f"Topic in {payload_file} sollte nicht leer sein")

            # Prüfe Payload-Struktur
            payload = data["payload"]
            self.assertIsInstance(payload, dict, f"Payload in {payload_file} sollte Dictionary sein")
            self.assertGreater(len(payload), 0, f"Payload in {payload_file} sollte nicht leer sein")

    def test_payload_topic_mapping(self):
        """Test: Payload-Topics können gemappt werden"""
        from omf2.registry.manager.registry_manager import get_registry_manager

        registry_manager = get_registry_manager()

        # Nur Topics testen, die bekannte Schemas haben
        known_topic_mappings = {
            "module/v1/ff/SVR3QA0022/state": "module_v1_ff_serial_state.schema.json",
            "module/v1/ff/SVR3QA0022/connection": "module_v1_ff_serial_connection.schema.json",
            "ccu/order/request": "ccu_order_request.schema.json",
            "/j1/txt/1/i/bme680": "j1_txt_1_i_bme680.schema.json",
        }

        for payload_file in self.payload_files:
            payload_path = self.test_payloads_dir / payload_file
            with open(payload_path, encoding="utf-8") as f:
                data = json.load(f)

            topic = data["topic"]

            # Nur bekannte Topics testen
            if topic in known_topic_mappings:
                # Prüfe dass Schema für Topic gefunden wird
                schema = registry_manager.get_topic_schema(topic)
                self.assertIsNotNone(schema, f"Schema für Topic {topic} sollte gefunden werden")

                # Prüfe dass Description für Topic gefunden wird
                description = registry_manager.get_topic_description(topic)
                self.assertIsNotNone(description, f"Description für Topic {topic} sollte gefunden werden")

    def test_payload_validation(self):
        """Test: Payload-Validation funktioniert mit Test-Daten"""
        from omf2.registry.manager.registry_manager import get_registry_manager

        registry_manager = get_registry_manager()

        # Nur Topics testen, die bekannte Schemas haben
        known_topics = [
            "module/v1/ff/SVR3QA0022/state",
            "module/v1/ff/SVR3QA0022/connection",
            "ccu/order/request",
            "/j1/txt/1/i/bme680",
        ]

        for payload_file in self.payload_files:
            payload_path = self.test_payloads_dir / payload_file
            with open(payload_path, encoding="utf-8") as f:
                data = json.load(f)

            topic = data["topic"]
            payload = data["payload"]

            # Nur bekannte Topics testen
            if topic in known_topics:
                # Test Payload-Validation über MessageManager
                from omf2.common.message_manager import MessageManager

                message_manager = MessageManager("admin", registry_manager)
                validation_result = message_manager.validate_message(topic, payload)

                # Prüfe dass Validation-Result ein Dictionary ist
                self.assertIsInstance(validation_result, dict, f"Validation für {topic} sollte Dictionary zurückgeben")
                self.assertIn("errors", validation_result, f"Validation-Result für {topic} sollte 'errors' haben")
                self.assertIn("warnings", validation_result, f"Validation-Result für {topic} sollte 'warnings' haben")

                # Prüfe dass errors eine Liste ist
                self.assertIsInstance(
                    validation_result["errors"], list, f"Validation 'errors' für {topic} sollte Liste sein"
                )

    def test_payload_diversity(self):
        """Test: Payload-Diversität deckt verschiedene Topic-Typen ab"""
        topics = []

        for payload_file in self.payload_files:
            payload_path = self.test_payloads_dir / payload_file
            with open(payload_path, encoding="utf-8") as f:
                data = json.load(f)
            topics.append(data["topic"])

        # Prüfe dass verschiedene Topic-Patterns abgedeckt sind
        module_topics = [t for t in topics if t.startswith("module/")]
        ccu_topics = [t for t in topics if t.startswith("ccu/")]
        txt_topics = [t for t in topics if t.startswith("/j1/txt/")]

        self.assertGreater(len(module_topics), 0, "Module Topics sollten vorhanden sein")
        self.assertGreater(len(ccu_topics), 0, "CCU Topics sollten vorhanden sein")
        self.assertGreater(len(txt_topics), 0, "TXT Topics sollten vorhanden sein")

    def test_payload_real_world_simulation(self):
        """Test: Payloads simulieren echte Welt-Daten"""
        for payload_file in self.payload_files:
            payload_path = self.test_payloads_dir / payload_file
            with open(payload_path, encoding="utf-8") as f:
                data = json.load(f)

            topic = data["topic"]
            payload = data["payload"]

            # Prüfe dass Payloads realistische Strukturen haben
            if "module" in topic:
                # Module Topics sollten typische Felder haben
                if "state" in topic:
                    self.assertIn("loads", payload, f"Module State {topic} sollte 'loads' haben")
                elif "connection" in topic:
                    self.assertIn("clientId", payload, f"Module Connection {topic} sollte 'clientId' haben")

            elif "ccu" in topic:
                # CCU Topics sollten typische Felder haben
                if "order" in topic:
                    self.assertIn("orderType", payload, f"CCU Order {topic} sollte 'orderType' haben")
                elif "global" in topic:
                    self.assertIn("systemStatus", payload, f"CCU Global {topic} sollte 'systemStatus' haben")

            elif "txt" in topic:
                # TXT Topics sollten typische Felder haben
                if "bme680" in topic:
                    self.assertIn("t", payload, f"TXT BME680 {topic} sollte Temperatur 't' haben")
                    self.assertIn("h", payload, f"TXT BME680 {topic} sollte Luftfeuchtigkeit 'h' haben")


if __name__ == "__main__":
    unittest.main()
