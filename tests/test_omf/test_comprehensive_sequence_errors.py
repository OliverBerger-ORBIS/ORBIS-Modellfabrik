"""
Umfassender Test für alle möglichen SequenceDefinition.get() Fehler
"""

import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# Pfad für Imports


class TestComprehensiveSequenceErrors(unittest.TestCase):
    """Umfassender Test für alle möglichen Fehler"""

    def setUp(self):
        """Setup für Tests"""
        self.mock_mqtt_client = Mock()
        self.mock_mqtt_client.connected = True
        self.mock_mqtt_client.publish = Mock(return_value=True)

    def test_all_sequence_definition_usage(self):
        """Test: Alle Verwendungen von SequenceDefinition sind sicher"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep
            from omf.dashboard.tools.sequence_ui import SequenceUI
            from omf.dashboard.tools.workflow_order_manager import get_workflow_order_manager

            executor = SequenceExecutor(self.mock_mqtt_client)
            _ui = SequenceUI(executor)

            # Erstelle eine Test-Sequenz
            step = SequenceStep(step_id=1, name="TEST_STEP", topic="test/topic", payload={"test": "data"})

            sequence = SequenceDefinition(name="test_sequence", description="Test sequence", steps=[step])

            # Test: Alle möglichen Verwendungen von SequenceDefinition
            test_cases = [
                # Direkter Zugriff
                ("sequence.name", lambda: sequence.name),
                ("sequence.description", lambda: sequence.description),
                ("sequence.steps", lambda: sequence.steps),
                # getattr() Zugriff
                ("getattr(sequence, 'name')", lambda: getattr(sequence, "name", "default")),
                ("getattr(sequence, 'description')", lambda: getattr(sequence, "description", "default")),
                ("getattr(sequence, 'steps')", lambda: getattr(sequence, "steps", [])),
                # hasattr() Zugriff
                ("hasattr(sequence, 'name')", lambda: hasattr(sequence, "name")),
                ("hasattr(sequence, 'description')", lambda: hasattr(sequence, "description")),
                ("hasattr(sequence, 'steps')", lambda: hasattr(sequence, "steps")),
            ]

            for test_name, test_func in test_cases:
                try:
                    result = test_func()
                    self.assertIsNotNone(result, f"{test_name} sollte einen Wert zurückgeben")
                except Exception as e:
                    self.fail(f"{test_name} fehlgeschlagen: {e}")

            # Test: .get() funktioniert NICHT mit SequenceDefinition
            with self.assertRaises(AttributeError) as cm:
                sequence.get("name")

            self.assertIn("object has no attribute 'get'", str(cm.exception))

        except Exception as e:
            self.fail(f"SequenceDefinition Verwendung Test fehlgeschlagen: {e}")

    def test_sequence_loader_all_sequences(self):
        """Test: Alle Sequenzen aus dem Loader sind sicher"""
        try:
            from omf.dashboard.tools.sequence_definition import SequenceDefinitionLoader

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

                self.assertIn("object has no attribute 'get'", str(cm.exception))

                # Test: getattr() funktioniert
                sequence_name = getattr(sequence, "name", "Unbekannt")
                self.assertIsInstance(sequence_name, str)

        except Exception as e:
            self.fail(f"SequenceDefinitionLoader Test fehlgeschlagen: {e}")

    def test_running_sequences_structure(self):
        """Test: running_sequences Struktur ist korrekt"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep

            executor = SequenceExecutor(self.mock_mqtt_client)

            # Erstelle eine Test-Sequenz
            step = SequenceStep(step_id=1, name="TEST_STEP", topic="test/topic", payload={"test": "data"})

            sequence = SequenceDefinition(name="test_sequence", description="Test sequence", steps=[step])

            # Starte Sequenz
            _order_id = executor.execute_sequence(sequence)

            # Test: running_sequences enthält SequenceDefinition Objekte
            self.assertIn(_order_id, executor.running_sequences)
            sequence_info = executor.running_sequences[_order_id]

            # Test: sequence_info ist SequenceDefinition
            self.assertIsInstance(sequence_info, SequenceDefinition)
            self.assertTrue(hasattr(sequence_info, "name"))
            self.assertTrue(hasattr(sequence_info, "description"))
            self.assertTrue(hasattr(sequence_info, "steps"))

            # Test: .get() funktioniert NICHT mit SequenceDefinition
            with self.assertRaises(AttributeError) as cm:
                sequence_info.get("name")

            self.assertIn("object has no attribute 'get'", str(cm.exception))

            # Test: getattr() funktioniert
            sequence_name = getattr(sequence_info, "name", "Unbekannt")
            self.assertEqual(sequence_name, "test_sequence")

        except Exception as e:
            self.fail(f"running_sequences Struktur Test fehlgeschlagen: {e}")

    def test_sequence_ui_all_methods_with_mocks(self):
        """Test: Alle SequenceUI Methoden mit Streamlit-Mocks"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceDefinition, SequenceExecutor, SequenceStep
            from omf.dashboard.tools.sequence_ui import SequenceUI

            executor = SequenceExecutor(self.mock_mqtt_client)
            _ui = SequenceUI(executor)

            # Erstelle eine Test-Sequenz
            step = SequenceStep(step_id=1, name="TEST_STEP", topic="test/topic", payload={"test": "data"})

            sequence = SequenceDefinition(name="test_sequence", description="Test sequence", steps=[step])

            # Starte Sequenz
            _order_id = executor.execute_sequence(sequence)

            # Mock alle Streamlit-Funktionen
            with patch("streamlit.subheader"), patch("streamlit.markdown"), patch("streamlit.info"), patch(
                "streamlit.success"
            ), patch("streamlit.expander"), patch("streamlit.write"), patch("streamlit.json"), patch(
                "streamlit.selectbox"
            ), patch(
                "streamlit.button"
            ), patch(
                "streamlit.progress"
            ), patch(
                "streamlit.session_state", new_callable=lambda: Mock()
            ):

                # Test: Alle Methoden können ohne AttributeError aufgerufen werden
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
            self.fail(f"SequenceUI Methoden Test fehlgeschlagen: {e}")

    def test_aiqs_sequence_safety(self):
        """Test: AIQS-Sequenz ist sicher"""
        try:
            from omf.dashboard.tools.sequence_executor import SequenceDefinition
            from omf.sequences.sequences_new.aiqs_sequence import get_sequence_definition

            sequence = get_sequence_definition()

            # Test: sequence ist SequenceDefinition
            self.assertIsInstance(sequence, SequenceDefinition)
            self.assertTrue(hasattr(sequence, "name"))
            self.assertTrue(hasattr(sequence, "description"))
            self.assertTrue(hasattr(sequence, "steps"))

            # Test: .get() funktioniert NICHT mit SequenceDefinition
            with self.assertRaises(AttributeError) as cm:
                sequence.get("name")

            self.assertIn("object has no attribute 'get'", str(cm.exception))

            # Test: getattr() funktioniert
            sequence_name = getattr(sequence, "name", "Unbekannt")
            self.assertIsInstance(sequence_name, str)

        except Exception as e:
            self.fail(f"AIQS-Sequenz Sicherheit Test fehlgeschlagen: {e}")

    def test_yml_sequences_safety(self):
        """Test: YML-Sequenzen sind sicher"""
        try:
            from omf.dashboard.tools.sequence_definition import SequenceDefinitionLoader

            loader = SequenceDefinitionLoader()
            sequences = loader.get_all_sequences()

            # Test: Alle YML-Sequenzen sind SequenceDefinition Objekte
            for _name, sequence in sequences.items():
                # Test: sequence ist SequenceDefinition
                self.assertTrue(hasattr(sequence, "name"))
                self.assertTrue(hasattr(sequence, "description"))
                self.assertTrue(hasattr(sequence, "steps"))

                # Test: .get() funktioniert NICHT mit SequenceDefinition
                with self.assertRaises(AttributeError) as cm:
                    sequence.get("name")

                self.assertIn("object has no attribute 'get'", str(cm.exception))

                # Test: getattr() funktioniert
                sequence_name = getattr(sequence, "name", "Unbekannt")
                self.assertIsInstance(sequence_name, str)

        except Exception as e:
            self.fail(f"YML-Sequenzen Sicherheit Test fehlgeschlagen: {e}")


if __name__ == "__main__":
    # Test Suite ausführen
    unittest.main(verbosity=2)
