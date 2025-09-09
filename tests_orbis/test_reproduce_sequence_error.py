"""
Test um den genauen SequenceDefinition.get() Fehler zu reproduzieren
"""

import os
import sys
import unittest
from unittest.mock import Mock, patch

# Pfad für Imports
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src_orbis"))


class TestReproduceSequenceError(unittest.TestCase):
    """Test um den genauen Fehler zu reproduzieren"""

    def setUp(self):
        """Setup für Tests"""
        self.mock_mqtt_client = Mock()
        self.mock_mqtt_client.connected = True
        self.mock_mqtt_client.publish = Mock(return_value=True)

    def test_reproduce_sequence_definition_get_error(self):
        """Test: Reproduziert den genauen AttributeError"""
        try:
            from omf.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep
            from omf.tools.sequence_ui import SequenceUI
            from omf.tools.workflow_order_manager import get_workflow_order_manager

            executor = SequenceExecutor(self.mock_mqtt_client)
            _ui = SequenceUI(executor)

            # Erstelle eine Test-Sequenz
            step = SequenceStep(step_id=1, name="TEST_STEP", topic="test/topic", payload={"test": "data"})

            sequence = SequenceDefinition(name="test_sequence", description="Test sequence", steps=[step])

            # Starte Sequenz
            _order_id = executor.execute_sequence(sequence)

            # Test: Reproduziere den genauen Fehler
            # Der Fehler tritt auf, wenn sequence_info.get() aufgerufen wird
            # sequence_info ist ein SequenceDefinition Objekt

            # Simuliere den Code aus show_active_sequences
            if hasattr(executor, "running_sequences") and executor.running_sequences:
                for _order_id_iter, sequence_info in executor.running_sequences.items():
                    # Test: sequence_info ist SequenceDefinition
                    self.assertIsInstance(sequence_info, SequenceDefinition)

                    # Test: .get() funktioniert NICHT mit SequenceDefinition
                    with self.assertRaises(AttributeError) as cm:
                        sequence_info.get("name")

                    # Test: Fehlermeldung enthält den erwarteten Text
                    self.assertIn("object has no attribute 'get'", str(cm.exception))

                    # Test: getattr() funktioniert
                    sequence_name = getattr(sequence_info, "name", "Unbekannt")
                    self.assertEqual(sequence_name, "test_sequence")

        except Exception as e:
            self.fail(f"Fehler-Reproduktion fehlgeschlagen: {e}")

    def test_show_active_sequences_method_safety(self):
        """Test: show_active_sequences verwendet korrekte Objektzugriffe"""
        try:
            from omf.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep
            from omf.tools.sequence_ui import SequenceUI

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
            self.fail(f"show_active_sequences Sicherheit Test fehlgeschlagen: {e}")

    def test_sequence_ui_all_methods_safety(self):
        """Test: Alle SequenceUI Methoden sind sicher"""
        try:
            from omf.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep
            from omf.tools.sequence_ui import SequenceUI

            executor = SequenceExecutor(self.mock_mqtt_client)
            _ui = SequenceUI(executor)

            # Erstelle eine Test-Sequenz
            step = SequenceStep(step_id=1, name="TEST_STEP", topic="test/topic", payload={"test": "data"})

            sequence = SequenceDefinition(name="test_sequence", description="Test sequence", steps=[step])

            # Starte Sequenz
            _order_id = executor.execute_sequence(sequence)

            # Test: Alle Methoden können ohne AttributeError aufgerufen werden
            with patch("streamlit.subheader"), patch("streamlit.markdown"), patch("streamlit.info"), patch(
                "streamlit.success"
            ), patch("streamlit.expander"), patch("streamlit.write"), patch("streamlit.json"), patch(
                "streamlit.selectbox"
            ), patch(
                "streamlit.button"
            ), patch(
                "streamlit.progress"
            ):

                methods_to_test = [
                    "show_sequence_selector",
                    "show_sequence_status",
                    "show_active_sequences",
                    "show_sequence_history",
                    "show_debug_info",
                ]

                for method_name in methods_to_test:
                    method = getattr(_ui, method_name)
                    try:
                        method()
                    except AttributeError as e:
                        if "object has no attribute 'get'" in str(e):
                            self.fail(f"SequenceUI Methode {method_name} verwendet noch .get() statt getattr()")
                        else:
                            # Andere AttributeError sind OK
                            pass
                    except Exception:
                        # Andere Fehler sind OK (z.B. Streamlit-Mocks)
                        pass

        except Exception as e:
            self.fail(f"SequenceUI Methoden Sicherheit Test fehlgeschlagen: {e}")

    def test_sequence_definition_loader_safety(self):
        """Test: SequenceDefinitionLoader gibt sichere Objekte zurück"""
        try:
            from omf.tools.sequence_definition import SequenceDefinitionLoader

            loader = SequenceDefinitionLoader()
            sequences = loader.get_all_sequences()

            # Test: Alle Sequenzen sind SequenceDefinition Objekte
            for _name, sequence in sequences.items():
                # Test: sequence ist SequenceDefinition
                self.assertTrue(hasattr(sequence, "name"))
                self.assertTrue(hasattr(sequence, "description"))
                self.assertTrue(hasattr(sequence, "steps"))

                # Test: .get() funktioniert NICHT mit SequenceDefinition
                with self.assertRaises(AttributeError) as cm:
                    sequence.get("name")

                # Test: Fehlermeldung enthält den erwarteten Text
                self.assertIn("object has no attribute 'get'", str(cm.exception))

                # Test: getattr() funktioniert
                sequence_name = getattr(sequence, "name", "Unbekannt")
                self.assertIsInstance(sequence_name, str)

        except Exception as e:
            self.fail(f"SequenceDefinitionLoader Sicherheit Test fehlgeschlagen: {e}")


if __name__ == "__main__":
    # Test Suite ausführen
    unittest.main(verbosity=2)
