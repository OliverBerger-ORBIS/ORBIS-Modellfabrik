#!/usr/bin/env python3
"""
Unit Tests für Sequenz-Variable-Resolution
Testet ob Kontext-Variablen korrekt in Topics und Payloads ersetzt werden
"""

import os
import sys
import unittest
from unittest.mock import MagicMock, Mock

# Pfad für Imports hinzufügen
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src_orbis"))

from omf.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep, StepStatus
from omf.tools.workflow_order_manager import WorkflowOrder, WorkflowOrderManager


class TestSequenceVariableResolution(unittest.TestCase):
    """Testet die Variable-Resolution in Sequenzen"""

    def setUp(self):
        """Setup für jeden Test"""
        self.mock_mqtt_client = Mock()
        self.mock_mqtt_client.connected = True
        self.mock_mqtt_client.publish = Mock(return_value=True)

        self.executor = SequenceExecutor(self.mock_mqtt_client)

        # Mock WorkflowOrderManager
        self.original_manager = None

    def tearDown(self):
        """Cleanup nach jedem Test"""
        pass

    def test_variable_resolution_in_topic(self):
        """Testet ob Variablen in Topics korrekt ersetzt werden"""
        # Test-Daten
        context = {"module_serial": "SVR4H76449", "module_type": "DRILL"}

        # Test verschiedene Variable-Formate
        test_cases = [
            ("module/v1/ff/{{module_serial}}/order", "module/v1/ff/SVR4H76449/order"),
            ("module/v1/ff/{{module_type}}/{{module_serial}}/state", "module/v1/ff/DRILL/SVR4H76449/state"),
            ("ccu/control/{{module_serial}}", "ccu/control/SVR4H76449"),
            ("no_variables_here", "no_variables_here"),  # Keine Variablen
            ("{{unknown_var}}/test", "{{unknown_var}}/test"),  # Unbekannte Variable
        ]

        for input_topic, expected_topic in test_cases:
            with self.subTest(input_topic=input_topic):
                result = self.executor._resolve_variables(input_topic, context)
                self.assertEqual(result, expected_topic, f"Variable-Ersetzung fehlgeschlagen für: {input_topic}")

    def test_variable_resolution_in_payload(self):
        """Testet ob Variablen in Payloads korrekt ersetzt werden"""
        context = {"module_serial": "SVR3QA2098", "orderId": "test-order-123", "orderUpdateId": 1}

        # Test Payload mit Variablen
        payload = {
            "orderId": "{{orderId}}",
            "orderUpdateId": "{{orderUpdateId}}",
            "moduleId": "{{module_serial}}",
            "command": "PICK",
            "timestamp": "2025-01-01T12:00:00Z",
        }

        expected_payload = {
            "orderId": "test-order-123",
            "orderUpdateId": 1,
            "moduleId": "SVR3QA2098",
            "command": "PICK",
            "timestamp": "2025-01-01T12:00:00Z",
        }

        result = self.executor._resolve_variables(payload, context)
        self.assertEqual(result, expected_payload)

    def test_variable_resolution_in_nested_structures(self):
        """Testet Variable-Resolution in verschachtelten Strukturen"""
        context = {"module_serial": "SVR4H76449", "workpiece_id": "WP001"}

        # Verschachtelte Struktur
        data = {
            "header": {"moduleId": "{{module_serial}}", "type": "order"},
            "payload": {
                "workpiece": "{{workpiece_id}}",
                "steps": ["{{module_serial}}_step1", "{{module_serial}}_step2"],
            },
        }

        expected = {
            "header": {"moduleId": "SVR4H76449", "type": "order"},
            "payload": {"workpiece": "WP001", "steps": ["SVR4H76449_step1", "SVR4H76449_step2"]},
        }

        result = self.executor._resolve_variables(data, context)
        self.assertEqual(result, expected)

    def test_sequence_context_transfer_to_order(self):
        """Testet ob Kontext-Variablen von SequenceDefinition zu WorkflowOrder übertragen werden"""
        # Mock SequenceDefinition mit Kontext
        sequence = Mock(spec=SequenceDefinition)
        sequence.name = "test_sequence"
        sequence.context = {"module_serial": "SVR4H76449", "module_type": "DRILL"}
        sequence.steps = []

        # Mock WorkflowOrderManager
        mock_order = Mock(spec=WorkflowOrder)
        mock_order.order_id = "test-order-123"
        mock_order.context = {}
        mock_order.total_steps = 0

        with unittest.mock.patch("omf.tools.sequence_executor.workflow_order_manager") as mock_manager:
            mock_manager.create_order.return_value = mock_order

            # Sequenz ausführen
            _order_id = self.executor.execute_sequence(sequence)

            # Prüfen ob Kontext übertragen wurde
            self.assertEqual(mock_order.context, sequence.context)
            mock_manager.create_order.assert_called_once_with("test_sequence")

    def test_real_sequence_execution_with_variables(self):
        """Testet echte Sequenz-Ausführung mit Variable-Resolution"""
        # Echte SequenceDefinition erstellen
        step = SequenceStep(
            step_id="step_1",
            name="PICK",
            topic="module/v1/ff/{{module_serial}}/order",
            payload={"orderId": "{{order_id}}", "moduleId": "{{module_serial}}", "command": "PICK"},
        )

        sequence = SequenceDefinition(
            name="test_sequence",
            description="Test-Sequenz",
            steps=[step],
            context={"module_serial": "SVR4H76449", "module_type": "DRILL"},
        )

        # Mock WorkflowOrderManager
        mock_order = Mock(spec=WorkflowOrder)
        mock_order.order_id = "test-order-123"
        mock_order.context = {}
        mock_order.total_steps = 1

        with unittest.mock.patch("omf.tools.sequence_executor.workflow_order_manager") as mock_manager:
            mock_manager.create_order.return_value = mock_order
            mock_manager.get_order.return_value = mock_order

            # Sequenz starten
            _order_id = self.executor.execute_sequence(sequence)

            # Prüfen ob MQTT-Nachricht mit korrekten Variablen gesendet wurde
            self.mock_mqtt_client.publish.assert_called_once()

            # Prüfen Topic und Payload
            call_args = self.mock_mqtt_client.publish.call_args
            topic = call_args[0][0]  # Erster Parameter
            payload = call_args[0][1]  # Zweiter Parameter

            # Topic sollte Variablen ersetzt haben
            self.assertNotIn("{{module_serial}}", topic)
            self.assertIn("SVR4H76449", topic)

            # Payload sollte Variablen ersetzt haben
            if isinstance(payload, str):
                payload_dict = eval(payload)  # JSON-String zu Dict
            else:
                payload_dict = payload

            self.assertNotIn("{{module_serial}}", str(payload_dict))
            self.assertIn("SVR4H76449", str(payload_dict))


if __name__ == "__main__":
    unittest.main()
