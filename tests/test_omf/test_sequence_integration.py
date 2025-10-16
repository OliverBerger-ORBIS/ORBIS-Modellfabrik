"""
Integration Tests für Sequenz-Steuerung
Erkennt häufige Fehler wie AttributeError, TypeError, ImportError
"""

import unittest
from unittest.mock import Mock

# Pfad für Imports


class TestSequenceIntegration(unittest.TestCase):
    """Integration Tests für Sequenz-Steuerung"""

    def setUp(self):
        """Setup für Tests"""
        self.mock_mqtt_client = Mock()
        self.mock_mqtt_client.connected = True
        self.mock_mqtt_client.publish = Mock(return_value=True)

    def test_import_sequence_ui(self):
        """Test: SequenceUI kann importiert werden"""
        try:
            from omf.dashboard.tools.sequence_ui import SequenceUI

            self.assertTrue(True, "SequenceUI Import erfolgreich")
        except ImportError as e:
            self.fail(f"SequenceUI Import fehlgeschlagen: {e}")

    def test_import_sequence_executor(self):
        """Test: SequenceExecutor kann importiert werden"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep

            self.assertTrue(True, "SequenceExecutor Import erfolgreich")
        except ImportError as e:
            self.fail(f"SequenceExecutor Import fehlgeschlagen: {e}")

    def test_import_workflow_order_manager(self):
        """Test: WorkflowOrderManager kann importiert werden"""
        try:
            from omf.dashboard.tools.workflow_order_manager import WorkflowOrder, get_workflow_order_manager

            self.assertTrue(True, "WorkflowOrderManager Import erfolgreich")
        except ImportError as e:
            self.fail(f"WorkflowOrderManager Import fehlgeschlagen: {e}")

    def test_sequence_executor_initialization(self):
        """Test: SequenceExecutor kann initialisiert werden"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceExecutor

            executor = SequenceExecutor(self.mock_mqtt_client)
            self.assertIsNotNone(executor)
            self.assertEqual(executor.mqtt_client, self.mock_mqtt_client)
        except Exception as e:
            self.fail(f"SequenceExecutor Initialisierung fehlgeschlagen: {e}")

    def test_sequence_ui_initialization(self):
        """Test: SequenceUI kann initialisiert werden"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceExecutor
            from omf.dashboard.tools.sequence_ui import SequenceUI

            executor = SequenceExecutor(self.mock_mqtt_client)
            ui = SequenceUI(executor)
            self.assertIsNotNone(ui)
            self.assertEqual(ui.executor, executor)
        except Exception as e:
            self.fail(f"SequenceUI Initialisierung fehlgeschlagen: {e}")

    def test_sequence_definition_creation(self):
        """Test: SequenceDefinition kann erstellt werden"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceDefinition, SequenceStep

            step = SequenceStep(step_id=1, name="TEST_STEP", topic="test/topic", payload={"test": "data"})

            sequence = SequenceDefinition(name="test_sequence", description="Test sequence", steps=[step])

            self.assertEqual(sequence.name, "test_sequence")
            self.assertEqual(len(sequence.steps), 1)
            self.assertEqual(sequence.steps[0].name, "TEST_STEP")
        except Exception as e:
            self.fail(f"SequenceDefinition Erstellung fehlgeschlagen: {e}")

    def test_workflow_order_creation(self):
        """Test: WorkflowOrder kann erstellt werden"""
        try:
            from omf.dashboard.tools.workflow_order_manager import get_workflow_order_manager

            manager = get_workflow_order_manager()
            order = manager.create_order("test_sequence")

            self.assertIsNotNone(order)
            self.assertEqual(order.sequence_name, "test_sequence")
            self.assertEqual(order.status, "running")
        except Exception as e:
            self.fail(f"WorkflowOrder Erstellung fehlgeschlagen: {e}")

    def test_sequence_executor_execute_sequence(self):
        """Test: execute_sequence Methode funktioniert"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep

            executor = SequenceExecutor(self.mock_mqtt_client)

            step = SequenceStep(step_id=1, name="TEST_STEP", topic="test/topic", payload={"test": "data"})

            sequence = SequenceDefinition(name="test_sequence", description="Test sequence", steps=[step])

            # Test: execute_sequence nimmt nur sequence als Parameter
            order_id = executor.execute_sequence(sequence)
            self.assertIsNotNone(order_id)
            self.assertIsInstance(order_id, str)
        except Exception as e:
            self.fail(f"execute_sequence fehlgeschlagen: {e}")

    def test_sequence_ui_methods_exist(self):
        """Test: Alle benötigten SequenceUI Methoden existieren"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceExecutor
            from omf.dashboard.tools.sequence_ui import SequenceUI

            executor = SequenceExecutor(self.mock_mqtt_client)
            ui = SequenceUI(executor)

            # Test: Alle benötigten Methoden existieren
            required_methods = [
                "show_sequence_selector",
                "show_sequence_status",
                "show_active_sequences",
                "show_sequence_history",
                "show_debug_info",
            ]

            for method_name in required_methods:
                self.assertTrue(hasattr(ui, method_name), f"SequenceUI fehlt Methode: {method_name}")
                self.assertTrue(
                    callable(getattr(ui, method_name)), f"SequenceUI Methode {method_name} ist nicht aufrufbar"
                )
        except Exception as e:
            self.fail(f"SequenceUI Methoden Test fehlgeschlagen: {e}")

    def test_sequence_definition_loader(self):
        """Test: SequenceDefinitionLoader kann Sequenzen laden"""
        try:
            from omf.dashboard.tools.sequence_definition import SequenceDefinitionLoader

            loader = SequenceDefinitionLoader()
            sequences = loader.get_all_sequences()

            # Test: get_all_sequences gibt ein Dictionary zurück
            self.assertIsInstance(sequences, dict)

            # Test: Jede Sequenz hat die richtige Struktur
            for name, sequence in sequences.items():
                self.assertIsInstance(name, str)
                self.assertTrue(hasattr(sequence, "name"))
                self.assertTrue(hasattr(sequence, "description"))
                self.assertTrue(hasattr(sequence, "steps"))
                self.assertIsInstance(sequence.steps, list)
        except Exception as e:
            self.fail(f"SequenceDefinitionLoader Test fehlgeschlagen: {e}")

    def test_dashboard_component_import(self):
        """Test: Dashboard-Komponente kann importiert werden"""
        try:
            from omf.dashboard.components.admin.steering_sequence import show_sequence_steering

            self.assertTrue(callable(show_sequence_steering))
        except Exception as e:
            self.fail(f"Dashboard-Komponente Import fehlgeschlagen: {e}")

    def test_aiqs_sequence_import(self):
        """Test: AIQS-Sequenz kann importiert werden"""
        try:
            from omf.sequences.sequences_new.aiqs_sequence import get_sequence_definition

            sequence = get_sequence_definition()
            self.assertIsNotNone(sequence)
            self.assertTrue(hasattr(sequence, "name"))
        except Exception as e:
            self.fail(f"AIQS-Sequenz Import fehlgeschlagen: {e}")

    def test_sequence_ui_mqtt_client_handling(self):
        """Test: SequenceUI kann MQTT-Client korrekt handhaben"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceExecutor
            from omf.dashboard.tools.sequence_ui import SequenceUI

            executor = SequenceExecutor(self.mock_mqtt_client)
            ui = SequenceUI(executor)

            # Test: MQTT-Client kann gesetzt werden
            ui.mqtt_client = self.mock_mqtt_client
            self.assertEqual(ui.mqtt_client, self.mock_mqtt_client)

            # Test: MQTT-Client kann an Executor weitergegeben werden
            if not ui.executor.mqtt_client:
                ui.executor.mqtt_client = ui.mqtt_client
            self.assertEqual(ui.executor.mqtt_client, self.mock_mqtt_client)
        except Exception as e:
            self.fail(f"SequenceUI MQTT-Client Handling fehlgeschlagen: {e}")

    def test_sequence_ui_object_attributes(self):
        """Test: SequenceUI Objekte haben korrekte Attribute"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceExecutor
            from omf.dashboard.tools.sequence_ui import SequenceUI

            executor = SequenceExecutor(self.mock_mqtt_client)
            ui = SequenceUI(executor)

            # Test: Alle erwarteten Attribute existieren
            expected_attributes = ["executor", "loader", "mqtt_client"]
            for attr in expected_attributes:
                self.assertTrue(hasattr(ui, attr), f"SequenceUI fehlt Attribut: {attr}")
        except Exception as e:
            self.fail(f"SequenceUI Attribute Test fehlgeschlagen: {e}")


class TestSequenceErrorHandling(unittest.TestCase):
    """Tests für Fehlerbehandlung in Sequenz-Steuerung"""

    def test_sequence_executor_without_mqtt(self):
        """Test: SequenceExecutor funktioniert ohne MQTT-Client"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceExecutor

            executor = SequenceExecutor(None)
            self.assertIsNotNone(executor)
            self.assertIsNone(executor.mqtt_client)
        except Exception as e:
            self.fail(f"SequenceExecutor ohne MQTT fehlgeschlagen: {e}")

    def test_sequence_ui_without_mqtt(self):
        """Test: SequenceUI funktioniert ohne MQTT-Client"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceExecutor
            from omf.dashboard.tools.sequence_ui import SequenceUI

            executor = SequenceExecutor(None)
            ui = SequenceUI(executor)
            ui.mqtt_client = None

            # Test: UI kann ohne MQTT-Client initialisiert werden
            self.assertIsNotNone(ui)
            self.assertIsNone(ui.mqtt_client)
        except Exception as e:
            self.fail(f"SequenceUI ohne MQTT fehlgeschlagen: {e}")

    def test_sequence_definition_validation(self):
        """Test: SequenceDefinition Validierung"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceDefinition, SequenceStep

            # Test: Leere Sequenz
            empty_sequence = SequenceDefinition(name="empty", description="Empty sequence", steps=[])
            self.assertEqual(len(empty_sequence.steps), 0)

            # Test: Sequenz mit ungültigen Schritten
            invalid_step = SequenceStep(step_id=1, name="", topic="", payload={})
            sequence_with_invalid_step = SequenceDefinition(
                name="invalid", description="Invalid sequence", steps=[invalid_step]
            )
            self.assertEqual(len(sequence_with_invalid_step.steps), 1)
        except Exception as e:
            self.fail(f"SequenceDefinition Validierung fehlgeschlagen: {e}")


if __name__ == "__main__":
    # Test Suite ausführen
    unittest.main(verbosity=2)
