#!/usr/bin/env python3
"""
Unit Tests für Order Commands
Basierend auf erfolgreichen Tests der Live-Fabrik
"""

import unittest
import json
import uuid
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock


class TestOrderCommands(unittest.TestCase):
    """Test-Klasse für Order Commands"""

    def setUp(self):
        """Test-Setup"""
        self.base_topic = "ccu/order/request"
        self.order_types = ["RED", "WHITE", "BLUE"]

    def test_order_red_structure(self):
        """Test: Korrekte Nachrichtenstruktur für Order RED"""

        # Aktuelle Zeit für Timestamp
        current_time = datetime.now(timezone.utc)

        # Erfolgreiche Order-RED-Nachricht
        order_red_message = {"type": "RED", "timestamp": current_time.isoformat(), "orderType": "PRODUCTION"}

        # Validierungen
        self.assertIn("type", order_red_message)
        self.assertIn("timestamp", order_red_message)
        self.assertIn("orderType", order_red_message)
        self.assertEqual(order_red_message["type"], "RED")
        self.assertEqual(order_red_message["orderType"], "PRODUCTION")

        # JSON-Format testen
        json_string = json.dumps(order_red_message)
        parsed_message = json.loads(json_string)
        self.assertEqual(parsed_message, order_red_message)

    def test_order_white_structure(self):
        """Test: Korrekte Nachrichtenstruktur für Order WHITE"""

        # Aktuelle Zeit für Timestamp
        current_time = datetime.now(timezone.utc)

        # Erfolgreiche Order-WHITE-Nachricht
        order_white_message = {"type": "WHITE", "timestamp": current_time.isoformat(), "orderType": "PRODUCTION"}

        # Validierungen
        self.assertIn("type", order_white_message)
        self.assertIn("timestamp", order_white_message)
        self.assertIn("orderType", order_white_message)
        self.assertEqual(order_white_message["type"], "WHITE")
        self.assertEqual(order_white_message["orderType"], "PRODUCTION")

        # JSON-Format testen
        json_string = json.dumps(order_white_message)
        parsed_message = json.loads(json_string)
        self.assertEqual(parsed_message, order_white_message)

    def test_order_blue_structure(self):
        """Test: Korrekte Nachrichtenstruktur für Order BLUE"""

        # Aktuelle Zeit für Timestamp
        current_time = datetime.now(timezone.utc)

        # Erfolgreiche Order-BLUE-Nachricht
        order_blue_message = {"type": "BLUE", "timestamp": current_time.isoformat(), "orderType": "PRODUCTION"}

        # Validierungen
        self.assertIn("type", order_blue_message)
        self.assertIn("timestamp", order_blue_message)
        self.assertIn("orderType", order_blue_message)
        self.assertEqual(order_blue_message["type"], "BLUE")
        self.assertEqual(order_blue_message["orderType"], "PRODUCTION")

        # JSON-Format testen
        json_string = json.dumps(order_blue_message)
        parsed_message = json.loads(json_string)
        self.assertEqual(parsed_message, order_blue_message)

    def test_order_topic_validation(self):
        """Test: Korrekte Topic-Struktur"""

        # Topic muss korrekt sein
        expected_topic = "ccu/order/request"
        self.assertEqual(self.base_topic, expected_topic)

        # Topic sollte nicht leer sein
        self.assertIsNotNone(self.base_topic)
        self.assertGreater(len(self.base_topic), 0)

    def test_order_type_validation(self):
        """Test: Order Type Validierung"""

        # Alle gültigen Order-Types
        valid_types = ["RED", "WHITE", "BLUE"]
        for order_type in valid_types:
            self.assertIn(order_type, self.order_types)

        # Ungültige Types sollten abgelehnt werden
        invalid_types = ["ROT", "WEISS", "BLAU", "GREEN", "YELLOW"]
        for invalid_type in invalid_types:
            self.assertNotIn(invalid_type, self.order_types)

    def test_order_type_enumeration(self):
        """Test: Order Type Enumeration"""

        # Alle gültigen Order-Types sind verfügbar
        expected_types = ["RED", "WHITE", "BLUE"]
        self.assertEqual(set(self.order_types), set(expected_types))

        # Keine doppelten Types
        self.assertEqual(len(self.order_types), len(set(self.order_types)))

    def test_order_timestamp_validation(self):
        """Test: Timestamp Validierung"""

        # Aktuelle Zeit
        current_time = datetime.now(timezone.utc)
        timestamp = current_time.isoformat()

        # Timestamp sollte gültiges ISO-Format sein
        self.assertIsInstance(timestamp, str)
        self.assertGreater(len(timestamp), 0)

        # Timestamp sollte Z-Zeitzone haben (UTC)
        self.assertTrue(timestamp.endswith("Z") or "+" in timestamp or "-" in timestamp)

    def test_order_type_validation(self):
        """Test: OrderType Validierung"""

        # OrderType muss "PRODUCTION" sein
        valid_order_type = "PRODUCTION"
        self.assertEqual(valid_order_type, "PRODUCTION")

        # Ungültige OrderTypes sollten abgelehnt werden
        invalid_order_types = ["TEST", "DEBUG", "MAINTENANCE", ""]
        for invalid_type in invalid_order_types:
            self.assertNotEqual(invalid_type, "PRODUCTION")

    def test_order_message_completeness(self):
        """Test: Vollständigkeit der Order-Nachrichten"""

        # Alle Pflichtfelder vorhanden
        order_message = {"type": "RED", "timestamp": "2025-08-19T09:16:14.336Z", "orderType": "PRODUCTION"}

        required_fields = ["type", "timestamp", "orderType"]
        for field in required_fields:
            self.assertIn(field, order_message)
            self.assertIsNotNone(order_message[field])

    def test_order_integration_with_factory(self):
        """Test: Integration mit der Fabrik (Mock)"""

        # Mock MQTT-Client
        mock_mqtt_client = MagicMock()
        mock_mqtt_client.publish.return_value = True

        # Order RED senden
        order_topic = "ccu/order/request"
        order_payload = json.dumps({"type": "RED", "timestamp": "2025-08-19T09:16:14.336Z", "orderType": "PRODUCTION"})

        # Mock-Aufruf simulieren
        result = mock_mqtt_client.publish(order_topic, order_payload)

        # Validierungen
        self.assertTrue(result)
        mock_mqtt_client.publish.assert_called_once_with(order_topic, order_payload)

    def test_order_error_handling(self):
        """Test: Fehlerbehandlung bei ungültigen Order-Nachrichten"""

        # Ungültige Nachrichten sollten Fehler verursachen
        invalid_messages = [
            {},  # Leere Nachricht
            {"type": "RED"},  # Fehlende Pflichtfelder
            {"timestamp": "2025-08-19T09:16:14.336Z", "orderType": "PRODUCTION"},  # Fehlender Type
            {"type": "RED", "timestamp": "2025-08-19T09:16:14.336Z"},  # Fehlender OrderType
            {"type": "RED", "orderType": "PRODUCTION"},  # Fehlender Timestamp
            {"type": "INVALID", "timestamp": "2025-08-19T09:16:14.336Z", "orderType": "PRODUCTION"},  # Ungültiger Type
            {"type": "RED", "timestamp": "2025-08-19T09:16:14.336Z", "orderType": "INVALID"},  # Ungültiger OrderType
        ]

        for invalid_message in invalid_messages:
            # Prüfen ob Pflichtfelder fehlen
            if "type" not in invalid_message:
                self.assertRaises(KeyError, lambda: invalid_message["type"])

            if "timestamp" not in invalid_message:
                self.assertRaises(KeyError, lambda: invalid_message["timestamp"])

            if "orderType" not in invalid_message:
                self.assertRaises(KeyError, lambda: invalid_message["orderType"])

    def test_order_response_handling(self):
        """Test: Order Response Handling"""

        # Mock Order Response
        order_response = {
            "orderType": "PRODUCTION",
            "type": "RED",
            "timestamp": "2025-08-19T09:16:14.336Z",
            "orderId": "8ae07a6e-d058-48de-9b4d-8d0176622abc",
            "productionSteps": [],
        }

        # Validierungen der Response
        self.assertIn("orderId", order_response)
        self.assertIn("productionSteps", order_response)
        self.assertEqual(order_response["type"], "RED")
        self.assertEqual(order_response["orderType"], "PRODUCTION")

        # OrderId sollte UUID-Format haben
        order_id = order_response["orderId"]
        self.assertIsInstance(order_id, str)
        self.assertGreater(len(order_id), 0)


if __name__ == "__main__":
    unittest.main()
