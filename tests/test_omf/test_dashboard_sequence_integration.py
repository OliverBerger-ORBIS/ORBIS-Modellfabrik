"""
Dashboard Integration Tests für Sequenz-Steuerung
Erkennt spezifische Dashboard-Integration Fehler
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

# Pfad für Imports


class TestDashboardSequenceIntegration(unittest.TestCase):
    """Tests für Dashboard-Sequenz-Integration"""

    def setUp(self):
        """Setup für Tests"""
        self.mock_mqtt_client = Mock()
        self.mock_mqtt_client.connected = True
        self.mock_mqtt_client.publish = Mock(return_value=True)

        # Mock Streamlit Session State
        self.mock_session_state = {
            "mqtt_client": self.mock_mqtt_client,
            "sequence_executor": None,
            "active_sequence": None,
            "show_step_details": {},
        }

    @patch("streamlit.session_state", new_callable=lambda: Mock())
    def test_steering_sequence_component_import(self, mock_session_state):
        """Test: Steering Sequence Komponente kann importiert werden"""
        try:
            from omf.dashboard.components.admin.steering_sequence import show_sequence_steering

            self.assertTrue(callable(show_sequence_steering))
        except Exception as e:
            self.fail(f"Steering Sequence Komponente Import fehlgeschlagen: {e}")

    @patch("streamlit.session_state", new_callable=lambda: Mock())
    def test_steering_component_import(self, mock_session_state):
        """Test: Steering Komponente kann importiert werden"""
        try:
            from omf.dashboard.components.admin.steering import show_steering

            self.assertTrue(callable(show_steering))
        except Exception as e:
            self.fail(f"Steering Komponente Import fehlgeschlagen: {e}")

    def test_sequence_ui_method_signatures(self):
        """Test: SequenceUI Methoden haben korrekte Signaturen"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceExecutor
            from omf.dashboard.tools.sequence_ui import SequenceUI

            _executor = SequenceExecutor(self.mock_mqtt_client)
            _ui = SequenceUI(_executor)

            # Test: show_sequence_selector hat keine Parameter
            import inspect

            sig = inspect.signature(_ui.show_sequence_selector)
            self.assertEqual(len(sig.parameters), 0, "show_sequence_selector sollte keine Parameter haben")

            # Test: show_sequence_status hat keine Parameter
            sig = inspect.signature(_ui.show_sequence_status)
            self.assertEqual(len(sig.parameters), 0, "show_sequence_status sollte keine Parameter haben")

            # Test: show_active_sequences hat keine Parameter
            sig = inspect.signature(_ui.show_active_sequences)
            self.assertEqual(len(sig.parameters), 0, "show_active_sequences sollte keine Parameter haben")
        except Exception as e:
            self.fail(f"SequenceUI Method Signaturen Test fehlgeschlagen: {e}")

    def test_sequence_executor_running_sequences_structure(self):
        """Test: running_sequences hat korrekte Struktur"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep

            _executor = SequenceExecutor(self.mock_mqtt_client)

            # Test: running_sequences ist ein Dictionary
            self.assertIsInstance(_executor.running_sequences, dict)

            # Test: running_sequences kann SequenceDefinition Objekte speichern
            step = SequenceStep(step_id=1, name="TEST_STEP", topic="test/topic", payload={"test": "data"})

            sequence = SequenceDefinition(name="test_sequence", description="Test sequence", steps=[step])

            order_id = _executor.execute_sequence(sequence)
            self.assertIn(order_id, _executor.running_sequences)

            # Test: Gespeichertes Objekt ist eine SequenceDefinition
            stored_sequence = _executor.running_sequences[order_id]
            self.assertIsInstance(stored_sequence, SequenceDefinition)
            self.assertEqual(stored_sequence.name, "test_sequence")
        except Exception as e:
            self.fail(f"running_sequences Struktur Test fehlgeschlagen: {e}")

    def test_workflow_order_manager_integration(self):
        """Test: WorkflowOrderManager Integration"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep
            from omf.dashboard.tools.workflow_order_manager import WorkflowOrder, get_workflow_order_manager

            manager = get_workflow_order_manager()
            _executor = SequenceExecutor(self.mock_mqtt_client)

            # Test: Order kann erstellt werden
            order = manager.create_order("test_sequence")
            self.assertIsInstance(order, WorkflowOrder)

            # Test: Order kann abgerufen werden
            retrieved_order = manager.get_order(order.order_id)
            self.assertEqual(retrieved_order.order_id, order.order_id)

            # Test: Alle Orders können abgerufen werden
            all_orders = manager.get_all_orders()
            self.assertIsInstance(all_orders, dict)
            self.assertIn(order.order_id, all_orders)
        except Exception as e:
            self.fail(f"WorkflowOrderManager Integration Test fehlgeschlagen: {e}")

    def test_sequence_ui_object_type_handling(self):
        """Test: SequenceUI behandelt Objekttypen korrekt"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep
            from omf.dashboard.tools.sequence_ui import SequenceUI
            from omf.dashboard.tools.workflow_order_manager import get_workflow_order_manager

            _executor = SequenceExecutor(self.mock_mqtt_client)
            _ui = SequenceUI(_executor)

            # Test: sequence_info ist SequenceDefinition, nicht Dictionary
            step = SequenceStep(step_id=1, name="TEST_STEP", topic="test/topic", payload={"test": "data"})

            sequence = SequenceDefinition(name="test_sequence", description="Test sequence", steps=[step])

            # Test: getattr funktioniert mit SequenceDefinition
            sequence_name = getattr(sequence, "name", "Unbekannt")
            self.assertEqual(sequence_name, "test_sequence")

            # Test: hasattr funktioniert mit SequenceDefinition
            self.assertTrue(hasattr(sequence, "name"))
            self.assertTrue(hasattr(sequence, "description"))
            self.assertTrue(hasattr(sequence, "steps"))

            # Test: .get() funktioniert NICHT mit SequenceDefinition
            with self.assertRaises(AttributeError):
                sequence.get("name")
        except Exception as e:
            self.fail(f"SequenceUI Objekttyp Handling Test fehlgeschlagen: {e}")

    def test_sequence_definition_loader_error_handling(self):
        """Test: SequenceDefinitionLoader Fehlerbehandlung"""
        try:
            from omf.dashboard.tools.sequence_definition import SequenceDefinitionLoader

            loader = SequenceDefinitionLoader()

            # Test: get_all_sequences gibt Dictionary zurück
            sequences = loader.get_all_sequences()
            self.assertIsInstance(sequences, dict)

            # Test: Jede Sequenz ist eine SequenceDefinition
            for name, sequence in sequences.items():
                self.assertIsInstance(name, str)
                # Test: sequence ist SequenceDefinition Objekt
                self.assertTrue(hasattr(sequence, "name"))
                self.assertTrue(hasattr(sequence, "description"))
                self.assertTrue(hasattr(sequence, "steps"))

                # Test: .get() funktioniert NICHT mit SequenceDefinition
                with self.assertRaises(AttributeError):
                    sequence.get("name")
        except Exception as e:
            self.fail(f"SequenceDefinitionLoader Fehlerbehandlung Test fehlgeschlagen: {e}")

    def test_aiqs_sequence_import_fix(self):
        """Test: AIQS-Sequenz Import-Fix funktioniert"""
        try:
            # Test: AIQS-Sequenz kann importiert werden
            from omf.sequences.sequences_new.aiqs_sequence import get_sequence_definition

            sequence = get_sequence_definition()

            # Test: sequence ist SequenceDefinition Objekt
            self.assertTrue(hasattr(sequence, "name"))
            self.assertTrue(hasattr(sequence, "description"))
            self.assertTrue(hasattr(sequence, "steps"))

            # Test: .get() funktioniert NICHT mit SequenceDefinition
            with self.assertRaises(AttributeError):
                sequence.get("name")
        except Exception as e:
            self.fail(f"AIQS-Sequenz Import-Fix Test fehlgeschlagen: {e}")

    def test_sequence_ui_method_call_safety(self):
        """Test: SequenceUI Methodenaufrufe sind sicher"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceExecutor
            from omf.dashboard.tools.sequence_ui import SequenceUI

            _executor = SequenceExecutor(self.mock_mqtt_client)
            _ui = SequenceUI(_executor)

            # Test: Alle Methoden können ohne Parameter aufgerufen werden
            # (Mock Streamlit um Fehler zu vermeiden)
            with patch("streamlit.subheader"), patch("streamlit.markdown"), patch("streamlit.info"), patch(
                "streamlit.success"
            ), patch("streamlit.expander"), patch("streamlit.write"), patch("streamlit.json"):

                # Test: show_sequence_selector
                try:
                    _ui.show_sequence_selector()
                except Exception as e:
                    self.fail(f"show_sequence_selector Aufruf fehlgeschlagen: {e}")

                # Test: show_sequence_status
                try:
                    _ui.show_sequence_status()
                except Exception as e:
                    self.fail(f"show_sequence_status Aufruf fehlgeschlagen: {e}")

                # Test: show_active_sequences
                try:
                    _ui.show_active_sequences()
                except Exception as e:
                    self.fail(f"show_active_sequences Aufruf fehlgeschlagen: {e}")
        except Exception as e:
            self.fail(f"SequenceUI Methodenaufruf Sicherheit Test fehlgeschlagen: {e}")


if __name__ == "__main__":
    # Test Suite ausführen
    unittest.main(verbosity=2)
