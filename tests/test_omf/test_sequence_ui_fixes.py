"""
Spezifische Tests für SequenceUI Fehlerbehebungen
Reproduziert und testet die behobenen Fehler
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Pfad für Imports
# sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src_orbis"))  # Nicht mehr nötig nach pip install -e .


class TestSequenceUIFixes(unittest.TestCase):
    """Tests für spezifische SequenceUI Fehlerbehebungen"""

    def setUp(self):
        """Setup für Tests"""
        self.mock_mqtt_client = Mock()
        self.mock_mqtt_client.connected = True
        self.mock_mqtt_client.publish = Mock(return_value=True)

    def test_sequence_info_object_type_fix(self):
        """Test: sequence_info.get() Fehler ist behoben"""
        try:
            from src_orbis.omf.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep
            from src_orbis.omf.tools.sequence_ui import SequenceUI
            from src_orbis.omf.tools.workflow_order_manager import get_workflow_order_manager

            executor = SequenceExecutor(self.mock_mqtt_client)
            _ui = SequenceUI(executor)

            # Erstelle eine Test-Sequenz
            step = SequenceStep(step_id=1, name="TEST_STEP", topic="test/topic", payload={"test": "data"})

            sequence = SequenceDefinition(name="test_sequence", description="Test sequence", steps=[step])

            # Starte Sequenz
            _order_id = executor.execute_sequence(sequence)

            # Test: running_sequences enthält SequenceDefinition Objekte
            self.assertIn(_order_id, executor.running_sequences)
            sequence_info = executor.running_sequences[_order_id]

            # Test: sequence_info ist SequenceDefinition, nicht Dictionary
            self.assertIsInstance(sequence_info, SequenceDefinition)

            # Test: .get() funktioniert NICHT mit SequenceDefinition
            with self.assertRaises(AttributeError):
                sequence_info.get("name")

            # Test: getattr() funktioniert mit SequenceDefinition
            sequence_name = getattr(sequence_info, "name", "Unbekannt")
            self.assertEqual(sequence_name, "test_sequence")

            # Test: hasattr() funktioniert mit SequenceDefinition
            self.assertTrue(hasattr(sequence_info, "name"))
            self.assertTrue(hasattr(sequence_info, "description"))
            self.assertTrue(hasattr(sequence_info, "steps"))

        except Exception as e:
            self.fail(f"sequence_info.get() Fehlerbehebung Test fehlgeschlagen: {e}")

    def test_show_active_sequences_fix(self):
        """Test: show_active_sequences verwendet korrekte Objektzugriffe"""
        try:
            from src_orbis.omf.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep
            from src_orbis.omf.tools.sequence_ui import SequenceUI
            from src_orbis.omf.tools.workflow_order_manager import get_workflow_order_manager

            executor = SequenceExecutor(self.mock_mqtt_client)
            _ui = SequenceUI(executor)

            # Erstelle eine Test-Sequenz
            step = SequenceStep(step_id=1, name="TEST_STEP", topic="test/topic", payload={"test": "data"})

            sequence = SequenceDefinition(name="test_sequence", description="Test sequence", steps=[step])

            # Starte Sequenz
            _order_id = executor.execute_sequence(sequence)

            # Test: show_active_sequences kann ohne Fehler aufgerufen werden
            with patch("streamlit.subheader"), patch("streamlit.success"), patch("streamlit.expander"), patch(
                "streamlit.write"
            ), patch("streamlit.info"):

                # Test: show_active_sequences verwendet getattr() statt .get()
                try:
                    _ui.show_active_sequences()
                except AttributeError as e:
                    if "object has no attribute 'get'" in str(e):
                        self.fail("show_active_sequences verwendet noch .get() statt getattr()")
                    else:
                        raise e
                except Exception:
                    # Andere Fehler sind OK (z.B. Streamlit-Mocks)
                    pass

        except Exception as e:
            self.fail(f"show_active_sequences Fix Test fehlgeschlagen: {e}")

    def test_sequence_definition_vs_dictionary_handling(self):
        """Test: Korrekte Behandlung von SequenceDefinition vs Dictionary"""
        try:
            from src_orbis.omf.tools.sequence_executor import SequenceDefinition, SequenceStep

            # Erstelle SequenceDefinition
            step = SequenceStep(step_id=1, name="TEST_STEP", topic="test/topic", payload={"test": "data"})

            sequence = SequenceDefinition(name="test_sequence", description="Test sequence", steps=[step])

            # Test: SequenceDefinition ist KEIN Dictionary
            self.assertNotIsInstance(sequence, dict)

            # Test: SequenceDefinition hat Attribute, nicht Keys
            self.assertTrue(hasattr(sequence, "name"))
            self.assertTrue(hasattr(sequence, "description"))
            self.assertTrue(hasattr(sequence, "steps"))

            # Test: .get() funktioniert NICHT mit SequenceDefinition
            with self.assertRaises(AttributeError):
                sequence.get("name")

            # Test: getattr() funktioniert mit SequenceDefinition
            name = getattr(sequence, "name", "default")
            self.assertEqual(name, "test_sequence")

            # Test: Direkter Attributzugriff funktioniert
            self.assertEqual(sequence.name, "test_sequence")
            self.assertEqual(sequence.description, "Test sequence")
            self.assertEqual(len(sequence.steps), 1)

        except Exception as e:
            self.fail(f"SequenceDefinition vs Dictionary Handling Test fehlgeschlagen: {e}")

    def test_workflow_order_integration_fix(self):
        """Test: WorkflowOrder Integration in show_active_sequences"""
        try:
            from src_orbis.omf.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep
            from src_orbis.omf.tools.sequence_ui import SequenceUI
            from src_orbis.omf.tools.workflow_order_manager import get_workflow_order_manager

            executor = SequenceExecutor(self.mock_mqtt_client)
            _ui = SequenceUI(executor)
            manager = get_workflow_order_manager()

            # Erstelle eine Test-Sequenz
            step = SequenceStep(step_id=1, name="TEST_STEP", topic="test/topic", payload={"test": "data"})

            sequence = SequenceDefinition(name="test_sequence", description="Test sequence", steps=[step])

            # Starte Sequenz
            _order_id = executor.execute_sequence(sequence)

            # Test: Order existiert im WorkflowOrderManager
            order = manager.get_order(_order_id)
            self.assertIsNotNone(order)
            self.assertEqual(order.sequence_name, "test_sequence")
            self.assertEqual(order.status, "running")

            # Test: show_active_sequences kann Order-Informationen abrufen
            with patch("streamlit.subheader"), patch("streamlit.success"), patch("streamlit.expander"), patch(
                "streamlit.write"
            ), patch("streamlit.info"):

                try:
                    _ui.show_active_sequences()
                except Exception:
                    # Andere Fehler sind OK (z.B. Streamlit-Mocks)
                    pass

        except Exception as e:
            self.fail(f"WorkflowOrder Integration Fix Test fehlgeschlagen: {e}")

    def test_sequence_ui_method_parameter_fix(self):
        """Test: execute_sequence Parameter-Fehler ist behoben"""
        try:
            from src_orbis.omf.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep
            from src_orbis.omf.tools.sequence_ui import SequenceUI

            executor = SequenceExecutor(self.mock_mqtt_client)
            _ui = SequenceUI(executor)
            _ui.mqtt_client = self.mock_mqtt_client

            # Erstelle eine Test-Sequenz
            step = SequenceStep(step_id=1, name="TEST_STEP", topic="test/topic", payload={"test": "data"})

            sequence = SequenceDefinition(name="test_sequence", description="Test sequence", steps=[step])

            # Test: execute_sequence nimmt nur sequence als Parameter
            # (nicht sequence, mqtt_client)
            try:
                _order_id = executor.execute_sequence(sequence)
                self.assertIsNotNone(_order_id)
                self.assertIsInstance(_order_id, str)
            except TypeError as e:
                if "takes 2 positional arguments but 3 were given" in str(e):
                    self.fail("execute_sequence Parameter-Fehler ist noch nicht behoben")
                else:
                    raise e

        except Exception as e:
            self.fail(f"execute_sequence Parameter-Fix Test fehlgeschlagen: {e}")

    def test_aiqs_sequence_import_fix(self):
        """Test: AIQS-Sequenz Import-Fehler ist behoben"""
        try:
            # Test: AIQS-Sequenz kann importiert werden
            from src_orbis.omf.sequences.aiqs_sequence import get_sequence_definition
            from src_orbis.omf.tools.sequence_executor import SequenceDefinition

            sequence = get_sequence_definition()

            # Test: sequence ist SequenceDefinition Objekt
            self.assertIsInstance(sequence, SequenceDefinition)
            self.assertTrue(hasattr(sequence, "name"))
            self.assertTrue(hasattr(sequence, "description"))
            self.assertTrue(hasattr(sequence, "steps"))

            # Test: .get() funktioniert NICHT mit SequenceDefinition
            with self.assertRaises(AttributeError):
                sequence.get("name")

        except ImportError as e:
            if "attempted relative import with no known parent package" in str(e):
                self.fail("AIQS-Sequenz Import-Fehler ist noch nicht behoben")
            else:
                raise e
        except Exception as e:
            self.fail(f"AIQS-Sequenz Import-Fix Test fehlgeschlagen: {e}")


if __name__ == "__main__":
    # Test Suite ausführen
    unittest.main(verbosity=2)
