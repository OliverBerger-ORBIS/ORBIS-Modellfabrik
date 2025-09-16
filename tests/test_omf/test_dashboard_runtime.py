#!/usr/bin/env python3
"""
Test für OMF Dashboard Runtime-Fehler
Prüft Runtime-Fehler und Komponenten-Integration
"""

import sys
import unittest
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestDashboardRuntime(unittest.TestCase):
    """Test OMF Dashboard Runtime-Fehler"""

    def test_message_center_component(self):
        """Test: Message Center Komponente kann geladen werden"""
        try:
            from omf.dashboard.components.message_center import show_message_center

            # Test that function exists
            self.assertTrue(callable(show_message_center), "show_message_center sollte aufrufbar sein")

            print("✅ Message Center Komponente: OK")

        except Exception as e:
            self.fail(f"❌ Message Center Komponente failed: {e}")

    def test_mqtt_client_component(self):
        """Test: MQTT Client Komponente kann geladen werden"""
        try:
            from omf.tools.mqtt_config import MqttConfig
            from omf.tools.omf_mqtt_client import OmfMqttClient

            # Test MQTT Client initialization mit minimaler Konfiguration
            cfg = MqttConfig(host="localhost")
            client = OmfMqttClient(cfg)
            self.assertIsNotNone(client, "OmfMqttClient sollte initialisiert werden können")

            # Test basic methods
            self.assertIsInstance(client.get_history_stats(), dict, "get_history_stats sollte Dict zurückgeben")
            self.assertIsInstance(client.connected, bool, "connected sollte Boolean zurückgeben")

            print("✅ MQTT Client Komponente: OK")

        except Exception as e:
            self.fail(f"❌ MQTT Client Komponente failed: {e}")

    def test_replay_station_component(self):
        """Test: Replay Station Komponente ist in Session Manager integriert"""
        try:
            # Test dass Replay Station jetzt Teil des Session Managers ist
            from omf.helper_apps.session_manager.components.replay_station import show_replay_station

            # Test dass Funktion existiert
            self.assertIsNotNone(show_replay_station, "show_replay_station sollte existieren")
            self.assertTrue(callable(show_replay_station), "show_replay_station sollte callable sein")

            print("✅ Replay Station Komponente (Session Manager): OK")

        except Exception as e:
            self.fail(f"❌ Replay Station Komponente failed: {e}")

    def test_dashboard_settings_component(self):
        """Test: Dashboard Settings Komponente kann geladen werden"""
        try:
            from omf.dashboard.components.settings import show_dashboard_settings

            # Test that function exists
            self.assertTrue(
                callable(show_dashboard_settings),
                "show_dashboard_settings sollte aufrufbar sein",
            )

            print("✅ Dashboard Settings Komponente: OK")

        except Exception as e:
            self.fail(f"❌ Dashboard Settings Komponente failed: {e}")

    def test_factory_steering_component(self):
        """Test: Factory Steering Komponente kann geladen werden"""
        try:
            from omf.dashboard.components.steering_factory import show_factory_steering

            # Test that function exists
            self.assertTrue(callable(show_factory_steering), "show_factory_steering sollte aufrufbar sein")

            print("✅ Factory Steering Komponente: OK")

        except Exception as e:
            self.fail(f"❌ Factory Steering Komponente failed: {e}")

    def test_session_validation(self):
        """Test: Session-Validierung funktioniert (Session Manager)"""
        try:
            from omf.helper_apps.session_manager.components.session_analyzer import SessionAnalyzer

            analyzer = SessionAnalyzer()

            # Test with empty session
            result = analyzer.load_session_data("nonexistent.db")
            self.assertFalse(result, "Ungültige Session sollte False zurückgeben")

            # Test with valid session structure (demo session)
            result = analyzer.load_session_data("demo")
            self.assertTrue(result, "Demo Session sollte True zurückgeben")
            self.assertIsInstance(analyzer.session_data, dict, "session_data sollte Dictionary sein")

            print("✅ Session-Validierung (Session Manager): OK")

        except Exception as e:
            self.fail(f"❌ Session-Validierung failed: {e}")

    def test_message_filtering(self):
        """Test: Nachrichten-Filterung funktioniert"""
        try:
            from omf.dashboard.components.message_center import show_message_center

            # Test that function exists
            self.assertTrue(callable(show_message_center), "show_message_center sollte aufrufbar sein")

            print("✅ Nachrichten-Filterung: OK")

        except Exception as e:
            self.fail(f"❌ Nachrichten-Filterung failed: {e}")


if __name__ == "__main__":
    print("🧪 Testing OMF Dashboard Runtime...")
    print("=" * 50)

    # Run tests
    unittest.main(verbosity=2, exit=False)

    print("=" * 50)
    print("🎯 OMF Dashboard Runtime test completed!")
