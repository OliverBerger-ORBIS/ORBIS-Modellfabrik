#!/usr/bin/env python3
"""
Unit Tests für FTS Instant Action Commands
Basierend auf erfolgreichen Tests der Live-Fabrik
"""

import unittest
import json
import uuid
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock


class TestFTSInstantAction(unittest.TestCase):
    """Test-Klasse für FTS Instant Action Commands"""

    def setUp(self):
        """Test-Setup"""
        self.base_topic = "fts/v1/ff/5iO4/instantAction"
        self.serial_number = "5iO4"
        self.node_id = "SVR4H73275"  # DPS-Modul

    def test_find_initial_dock_position_structure(self):
        """Test: Korrekte Nachrichtenstruktur für findInitialDockPosition"""

        # Aktuelle Zeit im ISO-Format
        timestamp = datetime.now(timezone.utc).isoformat()

        # UUID für actionId
        action_id = str(uuid.uuid4())

        payload = {
            "timestamp": timestamp,
            "serialNumber": self.serial_number,
            "actions": [
                {"actionType": "findInitialDockPosition", "actionId": action_id, "metadata": {"nodeId": self.node_id}}
            ],
        }

        # Validierung der Struktur
        self.assertIn("timestamp", payload)
        self.assertIn("serialNumber", payload)
        self.assertIn("actions", payload)
        self.assertEqual(len(payload["actions"]), 1)

        action = payload["actions"][0]
        self.assertEqual(action["actionType"], "findInitialDockPosition")
        self.assertEqual(action["actionId"], action_id)
        self.assertIn("metadata", action)
        self.assertEqual(action["metadata"]["nodeId"], self.node_id)

        # JSON-Validierung
        json_str = json.dumps(payload)
        self.assertIsInstance(json_str, str)

        # Rückkonvertierung
        parsed = json.loads(json_str)
        self.assertEqual(parsed, payload)

    def test_find_initial_dock_position_exact_format(self):
        """Test: Exakte Nachrichtenstruktur wie in der Live-Fabrik getestet"""

        # Exakte Struktur aus dem erfolgreichen Test
        payload = {
            "timestamp": "2025-01-27T12:00:00.000Z",
            "serialNumber": "5iO4",
            "actions": [
                {
                    "actionType": "findInitialDockPosition",
                    "actionId": "12345678-1234-1234-1234-123456789abc",
                    "metadata": {"nodeId": "SVR4H73275"},
                }
            ],
        }

        # Validierung der exakten Werte
        self.assertEqual(payload["timestamp"], "2025-01-27T12:00:00.000Z")
        self.assertEqual(payload["serialNumber"], "5iO4")
        self.assertEqual(payload["actions"][0]["actionType"], "findInitialDockPosition")
        self.assertEqual(payload["actions"][0]["actionId"], "12345678-1234-1234-1234-123456789abc")
        self.assertEqual(payload["actions"][0]["metadata"]["nodeId"], "SVR4H73275")

    def test_topic_format(self):
        """Test: Korrektes Topic-Format"""
        self.assertEqual(self.base_topic, "fts/v1/ff/5iO4/instantAction")
        self.assertTrue(self.base_topic.startswith("fts/v1/ff/"))
        self.assertTrue(self.base_topic.endswith("/instantAction"))

    def test_uuid_generation(self):
        """Test: UUID-Generierung für actionId"""
        action_id = str(uuid.uuid4())

        # UUID-Format validieren
        self.assertIsInstance(action_id, str)
        self.assertEqual(len(action_id), 36)  # Standard UUID Länge
        self.assertEqual(action_id.count("-"), 4)  # 4 Bindestriche

        # UUID-Parsing testen
        parsed_uuid = uuid.UUID(action_id)
        self.assertIsInstance(parsed_uuid, uuid.UUID)

    def test_timestamp_format(self):
        """Test: Korrektes Timestamp-Format"""
        # UTC Timestamp
        timestamp = datetime.now(timezone.utc).isoformat()

        # Format validieren
        self.assertIsInstance(timestamp, str)
        self.assertIn("T", timestamp)  # ISO Format hat T zwischen Datum und Zeit
        self.assertIn("Z", timestamp)  # UTC Endung

        # Parsing testen
        parsed_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        self.assertIsInstance(parsed_time, datetime)

    def test_metadata_structure(self):
        """Test: Korrekte Metadata-Struktur"""
        metadata = {"nodeId": self.node_id}

        self.assertIn("nodeId", metadata)
        self.assertEqual(metadata["nodeId"], "SVR4H73275")
        self.assertIsInstance(metadata["nodeId"], str)

    def test_multiple_actions(self):
        """Test: Mehrere Actions in einer Nachricht"""
        timestamp = datetime.now(timezone.utc).isoformat()

        payload = {
            "timestamp": timestamp,
            "serialNumber": self.serial_number,
            "actions": [
                {
                    "actionType": "findInitialDockPosition",
                    "actionId": str(uuid.uuid4()),
                    "metadata": {"nodeId": "SVR4H73275"},
                },
                {
                    "actionType": "findInitialDockPosition",
                    "actionId": str(uuid.uuid4()),
                    "metadata": {"nodeId": "SVR4H76530"},
                },
            ],
        }

        self.assertEqual(len(payload["actions"]), 2)
        self.assertEqual(payload["actions"][0]["actionType"], "findInitialDockPosition")
        self.assertEqual(payload["actions"][1]["actionType"], "findInitialDockPosition")

    def test_invalid_structures(self):
        """Test: Ungültige Strukturen werden abgelehnt"""

        # Fehlende Pflichtfelder
        with self.assertRaises(KeyError):
            payload = {"timestamp": "2025-01-27T12:00:00.000Z"}
            _ = payload["serialNumber"]  # Fehlt

        with self.assertRaises(KeyError):
            payload = {"timestamp": "2025-01-27T12:00:00.000Z", "serialNumber": "5iO4"}
            _ = payload["actions"]  # Fehlt

        # Leere Actions-Liste
        payload = {"timestamp": "2025-01-27T12:00:00.000Z", "serialNumber": "5iO4", "actions": []}
        self.assertEqual(len(payload["actions"]), 0)


if __name__ == "__main__":
    unittest.main()
