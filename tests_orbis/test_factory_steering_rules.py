#!/usr/bin/env python3
"""
Unit Tests für Factory Steering Regeln

Diese Tests validieren die aktuellen Regeln in steering_factory.py:
- Topic-Konformität (korrekte MQTT-Topics)
- Message-Struktur (UUIDs, orderUpdateId, etc.)
- Sequenz-Regeln (orderId bleibt konstant, orderUpdateId zählt hoch)

WICHTIG: Diese Tests testen die AKTUELLE Implementierung, nicht historische Commits!
"""

import os

# Import der aktuellen factory_steering Komponente
import sys
import unittest
import uuid
from unittest.mock import patch

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src_orbis"))

from src_orbis.omf.dashboard.components.steering_factory import (
    _prepare_fts_message,
    _prepare_module_sequence_message,
    _prepare_module_step_message,
)


class TestFactorySteeringRules(unittest.TestCase):
    """Testet die aktuellen Regeln in steering_factory.py"""

    def setUp(self):
        """Test-Setup"""
        # Mock session_state für Tests
        self.mock_session_state = {}

        # Patch st.session_state
        self.session_state_patcher = patch(
            "omf.dashboard.components.steering_factory.st.session_state", self.mock_session_state
        )
        self.session_state_patcher.start()

    def tearDown(self):
        """Test-Cleanup"""
        self.session_state_patcher.stop()

    def test_module_topics_are_correct(self):
        """Test: Modul-Topics müssen dem korrekten Pattern folgen"""
        # Test für alle Module
        test_cases = [
            ("AIQS", "SVR4H76530", "module/v1/ff/SVR4H76530/order"),
            ("MILL", "SVR3QA2098", "module/v1/ff/SVR3QA2098/order"),
            ("DRILL", "SVR4H76449", "module/v1/ff/SVR4H76449/order"),
        ]

        for module_name, _, expected_topic in test_cases:
            with self.subTest(module_name=module_name):
                # Nachricht vorbereiten
                _prepare_module_step_message(module_name, "PICK")

                # Topic prüfen
                actual_topic = self.mock_session_state["pending_message"]["topic"]
                self.assertEqual(actual_topic, expected_topic, f"Topic für {module_name} ist falsch")

    def test_fts_topic_is_correct(self):
        """Test: FTS-Topic muss korrekt sein"""
        # FTS-Nachricht vorbereiten
        _prepare_fts_message("startCharging")

        # Topic prüfen
        actual_topic = self.mock_session_state["pending_message"]["topic"]
        expected_topic = "fts/v1/ff/5iO4/instantAction"
        self.assertEqual(actual_topic, expected_topic, "FTS-Topic ist falsch")

    def test_order_id_is_uuid(self):
        """Test: orderId muss ein gültiger UUID sein"""
        # Nachricht vorbereiten
        _prepare_module_step_message("DRILL", "PICK")

        # orderId prüfen
        order_id = self.mock_session_state["pending_message"]["payload"]["orderId"]

        # UUID-Validierung
        try:
            uuid.UUID(order_id)
            is_valid_uuid = True
        except ValueError:
            is_valid_uuid = False

        self.assertTrue(is_valid_uuid, f"orderId ist kein gültiger UUID: {order_id}")

    def test_action_id_is_uuid(self):
        """Test: action.id muss ein gültiger UUID sein"""
        # Nachricht vorbereiten
        _prepare_module_step_message("MILL", "MILL")

        # action.id prüfen
        action_id = self.mock_session_state["pending_message"]["payload"]["action"]["id"]

        # UUID-Validierung
        try:
            uuid.UUID(action_id)
            is_valid_uuid = True
        except ValueError:
            is_valid_uuid = False

        self.assertTrue(is_valid_uuid, f"action.id ist kein gültiger UUID: {action_id}")

    def test_order_update_id_increments(self):
        """Test: orderUpdateId muss hochzählen"""
        # Mehrere Nachrichten nacheinander vorbereiten
        _prepare_module_step_message("AIQS", "PICK")
        first_update_id = self.mock_session_state["pending_message"]["payload"]["orderUpdateId"]

        _prepare_module_step_message("AIQS", "CHECK_QUALITY")
        second_update_id = self.mock_session_state["pending_message"]["payload"]["orderUpdateId"]

        _prepare_module_step_message("AIQS", "DROP")
        third_update_id = self.mock_session_state["pending_message"]["payload"]["orderUpdateId"]

        # orderUpdateId muss hochzählen
        self.assertEqual(first_update_id, 1, "Erster orderUpdateId muss 1 sein")
        self.assertEqual(second_update_id, 2, "Zweiter orderUpdateId muss 2 sein")
        self.assertEqual(third_update_id, 3, "Dritter orderUpdateId muss 3 sein")

    def test_sequence_order_id_consistency(self):
        """Test: orderId muss in einer Sequenz konstant bleiben"""
        # Sequenz vorbereiten
        _prepare_module_sequence_message("DRILL")

        # orderId aus der Sequenz extrahieren
        sequence_order_id = self.mock_session_state["pending_message"]["payload"]["orderId"]

        # UUID-Validierung
        try:
            uuid.UUID(sequence_order_id)
            is_valid_uuid = True
        except ValueError:
            is_valid_uuid = False

        self.assertTrue(is_valid_uuid, f"Sequenz orderId ist kein gültiger UUID: {sequence_order_id}")

    def test_message_structure_compliance(self):
        """Test: Message-Struktur muss den Regeln entsprechen"""
        # Nachricht vorbereiten
        _prepare_module_step_message("MILL", "MILL")

        payload = self.mock_session_state["pending_message"]["payload"]

        # Pflichtfelder prüfen
        required_fields = ["serialNumber", "orderId", "orderUpdateId", "action"]
        for field in required_fields:
            self.assertIn(field, payload, f"Pflichtfeld {field} fehlt")

        # Action-Struktur prüfen
        action = payload["action"]
        required_action_fields = ["id", "command", "metadata"]
        for field in required_action_fields:
            self.assertIn(field, action, f"Action-Feld {field} fehlt")

        # Metadata-Struktur prüfen
        metadata = action["metadata"]
        required_metadata_fields = ["priority", "timeout", "type"]
        for field in required_metadata_fields:
            self.assertIn(field, metadata, f"Metadata-Feld {field} fehlt")

    def test_fts_message_structure_compliance(self):
        """Test: FTS-Message-Struktur muss den im Dashboard erzeugten Payloads entsprechen"""
        # FTS-Nachricht vorbereiten
        _prepare_fts_message("findInitialDockPosition")

        payload = self.mock_session_state["pending_message"]["payload"]

        # Pflichtfelder prüfen (entsprechend Dashboard-Logik)
        required_fields = ["serialNumber", "timestamp", "actions"]
        for field in required_fields:
            self.assertIn(field, payload, f"FTS-Pflichtfeld {field} fehlt")

        # SerialNumber muss korrekt sein
        self.assertEqual(payload["serialNumber"], "5iO4", "FTS serialNumber ist falsch")

        # Actions-Struktur prüfen
        self.assertIsInstance(payload["actions"], list, "FTS actions sollte eine Liste sein")
        self.assertGreater(len(payload["actions"]), 0, "FTS actions sollte mindestens ein Element enthalten")
        action = payload["actions"][0]
        self.assertIn("actionType", action, "FTS actions[0] actionType fehlt")
        self.assertEqual(action["actionType"].lower(), "findinitialdockposition", "FTS actionType ist falsch")
        self.assertIn("actionId", action, "FTS actions[0] actionId fehlt")


class TestModuleSequenceRules(unittest.TestCase):
    """Testet die kombinierten Regeln für Modul-Sequenzen"""

    def setUp(self):
        """Test-Setup"""
        self.mock_session_state = {}
        self.session_state_patcher = patch(
            "omf.dashboard.components.steering_factory.st.session_state", self.mock_session_state
        )
        self.session_state_patcher.start()

    def tearDown(self):
        """Test-Cleanup"""
        self.session_state_patcher.stop()

    def test_drill_sequence_compliance(self):
        """Test: DRILL-Sequenz muss allen Regeln entsprechen"""
        # DRILL-Sequenz vorbereiten
        _prepare_module_sequence_message("DRILL")

        message = self.mock_session_state["pending_message"]

        # Topic-Regel prüfen
        expected_topic = "module/v1/ff/SVR4H76449/order"
        self.assertEqual(message["topic"], expected_topic, "DRILL-Topic ist falsch")

        # Message-Regel prüfen
        payload = message["payload"]
        self.assertEqual(payload["serialNumber"], "SVR4H76449", "DRILL serialNumber ist falsch")
        self.assertEqual(payload["action"]["command"], "PICK", "DRILL-Sequenz startet mit PICK")

        # UUID-Regel prüfen
        try:
            uuid.UUID(payload["orderId"])
            uuid.UUID(payload["action"]["id"])
            uuids_valid = True
        except ValueError:
            uuids_valid = False

        self.assertTrue(uuids_valid, "DRILL-Sequenz UUIDs sind ungültig")

    def test_mill_sequence_compliance(self):
        """Test: MILL-Sequenz muss allen Regeln entsprechen"""
        # MILL-Sequenz vorbereiten
        _prepare_module_sequence_message("MILL")

        message = self.mock_session_state["pending_message"]

        # Topic-Regel prüfen
        expected_topic = "module/v1/ff/SVR3QA2098/order"
        self.assertEqual(message["topic"], expected_topic, "MILL-Topic ist falsch")

        # Message-Regel prüfen
        payload = message["payload"]
        self.assertEqual(payload["serialNumber"], "SVR3QA2098", "MILL serialNumber ist falsch")
        self.assertEqual(payload["action"]["command"], "PICK", "MILL-Sequenz startet mit PICK")

        # UUID-Regel prüfen
        try:
            uuid.UUID(payload["orderId"])
            uuid.UUID(payload["action"]["id"])
            uuids_valid = True
        except ValueError:
            uuids_valid = False

        self.assertTrue(uuids_valid, "MILL-Sequenz UUIDs sind ungültig")

    def test_aiqs_sequence_compliance(self):
        """Test: AIQS-Sequenz muss allen Regeln entsprechen"""
        # AIQS-Sequenz vorbereiten
        _prepare_module_sequence_message("AIQS")

        message = self.mock_session_state["pending_message"]

        # Topic-Regel prüfen
        expected_topic = "module/v1/ff/SVR4H76530/order"
        self.assertEqual(message["topic"], expected_topic, "AIQS-Topic ist falsch")

        # Message-Regel prüfen
        payload = message["payload"]
        self.assertEqual(payload["serialNumber"], "SVR4H76530", "AIQS serialNumber ist falsch")
        self.assertEqual(payload["action"]["command"], "PICK", "AIQS-Sequenz startet mit PICK")

        # UUID-Regel prüfen
        try:
            uuid.UUID(payload["orderId"])
            uuid.UUID(payload["action"]["id"])
            uuids_valid = True
        except ValueError:
            uuids_valid = False

        self.assertTrue(uuids_valid, "AIQS-Sequenz UUIDs sind ungültig")


if __name__ == "__main__":
    # Test-Suite ausführen
    unittest.main(verbosity=2)
