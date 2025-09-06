# Ermöglicht das direkte Ausführen der Tests mit Python
if __name__ == "__main__":
    import unittest

    unittest.main()
#!/usr/bin/env python3
"""
Unit Test für Factory Reset Funktionalität

Dieser Test ist kritisch - wenn Factory Reset nicht funktioniert,
können wir gar nicht mehr weitermachen.
"""

import json
import os
import sys
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

# Unused Mock import removed

# Add src_orbis to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src_orbis"))

from src_orbis.omf.tools.message_generator import MessageGenerator


class TestFactoryReset(unittest.TestCase):
    """Test-Klasse für Factory Reset Funktionalität"""

    def setUp(self):
        """Setup vor jedem Test"""
        self.message_generator = MessageGenerator()

    def test_factory_reset_message_structure(self):
        """Test: Factory Reset Message hat korrekte Struktur"""
        # Test mit withStorage=False
        message = self.message_generator.generate_factory_reset_message(with_storage=False)

        # Message darf nicht None sein
        self.assertIsNotNone(message, "Factory Reset Message darf nicht None sein")

        # Message muss Dict sein
        self.assertIsInstance(message, dict, "Factory Reset Message muss Dict sein")

        # Topic muss vorhanden und korrekt sein
        self.assertIn("topic", message, "Topic fehlt in Factory Reset Message")
        self.assertEqual(message["topic"], "ccu/set/reset", "Topic muss 'ccu/set/reset' sein")

        # Payload muss vorhanden und korrekt sein
        self.assertIn("payload", message, "Payload fehlt in Factory Reset Message")
        self.assertIsInstance(message["payload"], dict, "Payload muss Dict sein")

        # withStorage muss korrekt gesetzt sein
        self.assertIn("withStorage", message["payload"], "withStorage fehlt im Payload")
        self.assertFalse(message["payload"]["withStorage"], "withStorage muss False sein")

        # timestamp muss vorhanden und gültig sein
        self.assertIn("timestamp", message["payload"], "timestamp fehlt im Payload")
        self.assertIsInstance(message["payload"]["timestamp"], str, "timestamp muss String sein")

        # timestamp muss gültiges ISO-Format haben
        try:
            datetime.fromisoformat(message["payload"]["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            self.fail("timestamp hat kein gültiges ISO-Format")

    def test_factory_reset_with_storage_true(self):
        """Test: Factory Reset mit withStorage=True"""
        message = self.message_generator.generate_factory_reset_message(with_storage=True)

        self.assertIsNotNone(message, "Factory Reset Message darf nicht None sein")
        self.assertEqual(message["payload"]["withStorage"], True, "withStorage muss True sein")

    def test_factory_reset_with_storage_false(self):
        """Test: Factory Reset mit withStorage=False (Default)"""
        message = self.message_generator.generate_factory_reset_message(with_storage=False)

        self.assertIsNotNone(message, "Factory Reset Message darf nicht None sein")
        self.assertEqual(message["payload"]["withStorage"], False, "withStorage muss False sein")

    def test_factory_reset_default_parameter(self):
        """Test: Factory Reset mit Default-Parameter (withStorage=False)"""
        message = self.message_generator.generate_factory_reset_message()

        self.assertIsNotNone(message, "Factory Reset Message darf nicht None sein")
        self.assertEqual(message["payload"]["withStorage"], False, "Default withStorage muss False sein")

    def test_factory_reset_topic_consistency(self):
        """Test: Factory Reset Topic ist immer konsistent"""
        message1 = self.message_generator.generate_factory_reset_message(with_storage=False)
        message2 = self.message_generator.generate_factory_reset_message(with_storage=True)

        self.assertEqual(message1["topic"], message2["topic"], "Topic muss bei beiden Aufrufen gleich sein")
        self.assertEqual(message1["topic"], "ccu/set/reset", "Topic muss immer 'ccu/set/reset' sein")

    def test_factory_reset_payload_keys(self):
        """Test: Factory Reset Payload hat alle erforderlichen Keys"""
        message = self.message_generator.generate_factory_reset_message(with_storage=False)

        required_keys = ["timestamp", "withStorage"]
        for key in required_keys:
            self.assertIn(key, message["payload"], f"Key '{key}' fehlt im Payload")

    def test_factory_reset_timestamp_format(self):
        """Test: Factory Reset Timestamp hat korrektes Format"""
        message = self.message_generator.generate_factory_reset_message(with_storage=False)
        timestamp = message["payload"]["timestamp"]

        # Timestamp darf nicht leer sein
        self.assertGreater(len(timestamp), 0, "Timestamp darf nicht leer sein")

        # Timestamp muss gültiges ISO-Format haben
        try:
            # Entferne 'Z' am Ende und parse
            if timestamp.endswith("Z"):
                timestamp_clean = timestamp[:-1]
            else:
                timestamp_clean = timestamp

            parsed_time = datetime.fromisoformat(timestamp_clean)
            self.assertIsInstance(parsed_time, datetime, "Timestamp muss gültiges Datetime sein")
        except ValueError as e:
            self.fail(f"Timestamp '{timestamp}' hat kein gültiges ISO-Format: {e}")

    def test_factory_reset_message_serialization(self):
        """Test: Factory Reset Message kann zu JSON serialisiert werden"""
        message = self.message_generator.generate_factory_reset_message(with_storage=False)

        try:
            json_str = json.dumps(message)
            self.assertIsInstance(json_str, str, "Message muss zu JSON serialisierbar sein")

            # Teste Deserialisierung
            deserialized = json.loads(json_str)
            self.assertEqual(deserialized, message, "Deserialisierte Message muss gleich Original sein")
        except (TypeError, ValueError) as e:
            self.fail(f"Message kann nicht zu JSON serialisiert werden: {e}")

    def test_factory_reset_error_handling(self):
        """Test: Factory Reset behandelt Fehler korrekt"""
        # Mock datetime.now() um Fehler zu simulieren
        with patch("datetime.datetime") as mock_datetime:
            mock_datetime.now.side_effect = Exception("Simulierter Fehler")

            message = self.message_generator.generate_factory_reset_message(with_storage=False)

            # Auch bei Fehlern sollte eine gültige Message zurückgegeben werden
            # (da wir den Fallback-Code verwenden)
            self.assertIsNotNone(message, "Message sollte auch bei Fehlern zurückgegeben werden")

    def test_factory_reset_multiple_calls(self):
        """Test: Factory Reset funktioniert bei mehrfachen Aufrufen"""
        messages = []

        for i in range(5):
            message = self.message_generator.generate_factory_reset_message(with_storage=(i % 2 == 0))
            messages.append(message)

            # Jede Message muss gültig sein
            self.assertIsNotNone(message, f"Message {i} darf nicht None sein")
            self.assertEqual(message["topic"], "ccu/set/reset", f"Message {i} muss korrektes Topic haben")
            self.assertIn("withStorage", message["payload"], f"Message {i} muss withStorage haben")

        # Alle Messages sollten gültig sein
        self.assertEqual(len(messages), 5, "Alle 5 Messages sollten generiert worden sein")

    def test_factory_reset_critical_functionality(self):
        """KRITISCHER TEST: Factory Reset muss immer funktionieren"""
        # Dieser Test ist der wichtigste - wenn er fehlschlägt, können wir nicht weitermachen

        try:
            message = self.message_generator.generate_factory_reset_message(with_storage=False)

            # KRITISCHE PRÜFUNGEN
            self.assertIsNotNone(message, "KRITISCH: Factory Reset Message darf nicht None sein")
            self.assertEqual(message["topic"], "ccu/set/reset", "KRITISCH: Topic muss 'ccu/set/reset' sein")
            self.assertIn("withStorage", message["payload"], "KRITISCH: withStorage muss im Payload sein")
            self.assertIn("timestamp", message["payload"], "KRITISCH: timestamp muss im Payload sein")

            # Message muss gültiges JSON sein
            json.dumps(message)

            print("✅ KRITISCHER TEST BESTANDEN: Factory Reset funktioniert!")

        except Exception as e:
            self.fail(f"KRITISCHER FEHLER: Factory Reset funktioniert nicht mehr! Fehler: {e}")


if __name__ == "__main__":
    print("🧪 Starte Factory Reset Unit Tests...")
    print("⚠️  WARNUNG: Diese Tests sind kritisch - wenn sie fehlschlagen, können wir nicht weitermachen!")

    # Führe Tests aus
    unittest.main(verbosity=2, exit=False)

    print("\n" + "=" * 60)
    print("🎯 FAZIT: Factory Reset Tests abgeschlossen")
    print("=" * 60)
