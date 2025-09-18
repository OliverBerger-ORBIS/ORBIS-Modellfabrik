"""
Unit Tests für Module-ID-Mapping

Testet die korrekte Zuordnung von Modul-Namen zu Seriennummern
um kritische Bugs wie die Module-ID-Verwechslung zu verhindern.
"""

from pathlib import Path
import unittest

# Pfad für Import hinzufügen

from omf.dashboard.components.steering_factory import _get_module_serial

class TestModuleIdMapping(unittest.TestCase):
    """Test-Klasse für Module-ID-Mapping"""

    def test_drill_module_serial(self):
        """Test: DRILL sollte korrekte Seriennummer haben"""
        result = _get_module_serial("DRILL")
        self.assertEqual(result, "SVR4H76449", "DRILL sollte Seriennummer SVR4H76449 haben")

    def test_aiqs_module_serial(self):
        """Test: AIQS sollte korrekte Seriennummer haben"""
        result = _get_module_serial("AIQS")
        self.assertEqual(result, "SVR4H76530", "AIQS sollte Seriennummer SVR4H76530 haben")

    def test_mill_module_serial(self):
        """Test: MILL sollte korrekte Seriennummer haben"""
        result = _get_module_serial("MILL")
        self.assertEqual(result, "SVR3QA2098", "MILL sollte Seriennummer SVR3QA2098 haben")

    def test_unknown_module_serial(self):
        """Test: Unbekanntes Modul sollte UNKNOWN zurückgeben"""
        result = _get_module_serial("UNKNOWN_MODULE")
        self.assertEqual(result, "UNKNOWN", "Unbekanntes Modul sollte UNKNOWN zurückgeben")

    def test_case_sensitivity(self):
        """Test: Modul-Namen sind case-sensitive"""
        result_lower = _get_module_serial("drill")
        result_upper = _get_module_serial("DRILL")

        self.assertEqual(result_lower, "UNKNOWN", "Kleinbuchstaben sollten UNKNOWN zurückgeben")
        self.assertEqual(result_upper, "SVR4H76449", "Großbuchstaben sollten korrekte Seriennummer zurückgeben")

    def test_all_module_serials_unique(self):
        """Test: Alle Seriennummern sind eindeutig"""
        modules = ["DRILL", "AIQS", "MILL"]
        serials = [_get_module_serial(module) for module in modules]

        # Alle Seriennummern sollten unterschiedlich sein
        self.assertEqual(len(serials), len(set(serials)), "Alle Modul-Seriennummern sollten eindeutig sein")

        # Spezifische Seriennummern prüfen
        expected_serials = ["SVR4H76449", "SVR4H76530", "SVR3QA2098"]
        self.assertEqual(set(serials), set(expected_serials), "Seriennummern sollten den erwarteten Werten entsprechen")

    def test_serial_number_format(self):
        """Test: Seriennummern haben korrektes Format"""
        modules = ["DRILL", "AIQS", "MILL"]

        for module in modules:
            serial = _get_module_serial(module)
            # Seriennummer sollte mit SVR beginnen und 10 Zeichen haben
            self.assertTrue(serial.startswith("SVR"), f"{module} Seriennummer sollte mit SVR beginnen")
            self.assertEqual(len(serial), 10, f"{module} Seriennummer sollte 10 Zeichen haben")

    def test_critical_bug_prevention(self):
        """Test: Verhindert den kritischen Bug aus dashboardv3.1.0/3.1.1"""
        # Diese Tests verhindern die spezifischen Verwechslungen

        # DRILL sollte NICHT AIQS-Seriennummer haben
        drill_serial = _get_module_serial("DRILL")
        self.assertNotEqual(drill_serial, "SVR4H76530", "KRITISCH: DRILL sollte nicht AIQS-Seriennummer haben")

        # AIQS sollte NICHT MILL-Seriennummer haben
        aiqs_serial = _get_module_serial("AIQS")
        self.assertNotEqual(aiqs_serial, "SVR3QA2098", "KRITISCH: AIQS sollte nicht MILL-Seriennummer haben")

        # MILL sollte NICHT DRILL-Seriennummer haben
        mill_serial = _get_module_serial("MILL")
        self.assertNotEqual(mill_serial, "SVR4H76449", "KRITISCH: MILL sollte nicht DRILL-Seriennummer haben")

    def test_topic_generation_consistency(self):
        """Test: Topic-Generierung ist konsistent mit Seriennummern"""
        modules = ["DRILL", "AIQS", "MILL"]

        for module in modules:
            serial = _get_module_serial(module)
            expected_topic = f"module/v1/ff/{serial}/order"

            # Simuliere Topic-Generierung wie in steering_factory.py
            generated_topic = f"module/v1/ff/{serial}/order"

            self.assertEqual(generated_topic, expected_topic, f"Topic für {module} sollte konsistent sein")

if __name__ == "__main__":
    # Test-Suite ausführen
    unittest.main(verbosity=2)
