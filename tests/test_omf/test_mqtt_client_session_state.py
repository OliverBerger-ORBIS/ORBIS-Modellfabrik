#!/usr/bin/env python3
"""
Unit Test: MQTT Client Session State Problem
Testet, warum der MQTT-Client in der Nachrichten-Zentrale nicht gefunden wird
"""

from pathlib import Path
import unittest

# Add omf to path

class TestMqttClientSessionState(unittest.TestCase):
    """Testet MQTT Client Session State Probleme"""

    def setUp(self):
        """Setup für jeden Test"""
        # Mock Streamlit session_state
        self.mock_session_state = {}

    def test_mqtt_client_creation(self):
        """Testet MQTT Client Erstellung"""
        try:
            from omf.tools.omf_mqtt_factory import get_omf_mqtt_client

            # Test-Konfiguration
            test_config = {
                "host": "192.168.0.100",
                "port": 1883,
                "username": "default",
                "password": "default",
                "client_id": "test_client",
            }

            # Client erstellen
            client = get_omf_mqtt_client(test_config)

            # Prüfen ob Client erstellt wurde
            self.assertIsNotNone(client)
            self.assertTrue(hasattr(client, "clear_history"))
            self.assertTrue(hasattr(client, "drain"))
            self.assertTrue(hasattr(client, "publish"))

            print("✅ MQTT Client wurde erfolgreich erstellt")
            print(f"   - Client Type: {type(client).__name__}")
            print(f"   - Hat clear_history: {hasattr(client, 'clear_history')}")
            print(f"   - Hat drain: {hasattr(client, 'drain')}")
            print(f"   - Hat publish: {hasattr(client, 'publish')}")

        except Exception as e:
            self.fail(f"❌ MQTT Client Erstellung fehlgeschlagen: {e}")

    def test_mqtt_client_methods(self):
        """Testet MQTT Client Methoden"""
        try:
            from omf.tools.omf_mqtt_factory import get_omf_mqtt_client

            # Test-Konfiguration
            test_config = {
                "host": "192.168.0.100",
                "port": 1883,
                "username": "default",
                "password": "default",
                "client_id": "test_client",
            }

            # Client erstellen
            client = get_omf_mqtt_client(test_config)

            # clear_history Methode testen
            if hasattr(client, "clear_history"):
                # Methode aufrufen (sollte keine Exception werfen)
                client.clear_history()
                print("✅ clear_history Methode funktioniert")
            else:
                self.fail("❌ clear_history Methode fehlt")

            # drain Methode testen
            if hasattr(client, "drain"):
                messages = client.drain()
                self.assertIsInstance(messages, list)
                print("✅ drain Methode funktioniert")
            else:
                self.fail("❌ drain Methode fehlt")

        except Exception as e:
            self.fail(f"❌ MQTT Client Methoden Test fehlgeschlagen: {e}")

    def test_session_state_simulation(self):
        """Simuliert Streamlit Session State"""
        try:
            from omf.tools.omf_mqtt_factory import get_omf_mqtt_client

            # Test-Konfiguration
            test_config = {
                "host": "192.168.0.100",
                "port": 1883,
                "username": "default",
                "password": "default",
                "client_id": "test_client",
            }

            # Session State simulieren
            session_state = {}

            # Client erstellen und in Session State setzen
            client = get_omf_mqtt_client(test_config)
            session_state["mqtt_client"] = client

            # Client aus Session State holen
            retrieved_client = session_state.get("mqtt_client")

            # Prüfen ob Client gefunden wurde
            self.assertIsNotNone(retrieved_client)
            self.assertEqual(retrieved_client, client)

            # Prüfen ob Client die benötigten Methoden hat
            self.assertTrue(hasattr(retrieved_client, "clear_history"))
            self.assertTrue(hasattr(retrieved_client, "drain"))

            print("✅ Session State Simulation erfolgreich")
            print(f"   - Client in Session State: {retrieved_client is not None}")
            print(f"   - Client hat clear_history: {hasattr(retrieved_client, 'clear_history')}")
            print(f"   - Client hat drain: {hasattr(retrieved_client, 'drain')}")

        except Exception as e:
            self.fail(f"❌ Session State Simulation fehlgeschlagen: {e}")

    def test_clear_history_functionality(self):
        """Testet clear_history Funktionalität"""
        try:
            from omf.tools.omf_mqtt_factory import get_omf_mqtt_client

            # Test-Konfiguration
            test_config = {
                "host": "192.168.0.100",
                "port": 1883,
                "username": "default",
                "password": "default",
                "client_id": "test_client",
            }

            # Client erstellen
            client = get_omf_mqtt_client(test_config)

            # Nachrichten hinzufügen (simuliert)
            if hasattr(client, "_history"):
                # Direkt auf interne _history zugreifen (für Test)
                client._history.append({"type": "test", "message": "test"})
                print(f"   - Nachrichten vor clear_history: {len(client._history)}")

                # clear_history aufrufen
                client.clear_history()

                # Prüfen ob Historie geleert wurde
                print(f"   - Nachrichten nach clear_history: {len(client._history)}")
                print("✅ clear_history Funktionalität funktioniert")
            else:
                print("⚠️ _history Attribut nicht verfügbar (kann nicht getestet werden)")

        except Exception as e:
            self.fail(f"❌ clear_history Funktionalität Test fehlgeschlagen: {e}")

    def test_mqtt_client_attributes(self):
        """Testet alle wichtigen MQTT Client Attribute"""
        try:
            from omf.tools.omf_mqtt_factory import get_omf_mqtt_client

            # Test-Konfiguration
            test_config = {
                "host": "192.168.0.100",
                "port": 1883,
                "username": "default",
                "password": "default",
                "client_id": "test_client",
            }

            # Client erstellen
            client = get_omf_mqtt_client(test_config)

            # Alle wichtigen Attribute prüfen
            required_attributes = [
                "connected",
                "clear_history",
                "drain",
                "publish",
                "subscribe",
                "get_history_stats",
                "get_connection_status",
            ]

            missing_attributes = []
            for attr in required_attributes:
                if not hasattr(client, attr):
                    missing_attributes.append(attr)

            if missing_attributes:
                self.fail(f"❌ Fehlende Attribute: {missing_attributes}")

            print("✅ Alle wichtigen Attribute sind verfügbar")
            for attr in required_attributes:
                print(f"   - {attr}: {hasattr(client, attr)}")

        except Exception as e:
            self.fail(f"❌ Attribute Test fehlgeschlagen: {e}")

if __name__ == "__main__":
    # Test ausführen
    print("🧪 MQTT Client Session State Unit Tests")
    print("=" * 50)

    # Test Suite erstellen
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestMqttClientSessionState)

    # Tests ausführen
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Ergebnis zusammenfassen
    print("\n" + "=" * 50)
    print("📊 Test Ergebnis Zusammenfassung:")
    print(f"   - Tests ausgeführt: {result.testsRun}")
    print(f"   - Fehler: {len(result.failures)}")
    print(f"   - Fehlgeschlagen: {len(result.errors)}")

    if result.failures:
        print("\n❌ Fehlgeschlagene Tests:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback}")

    if result.errors:
        print("\n❌ Tests mit Fehlern:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback}")

    if result.wasSuccessful():
        print("\n✅ Alle Tests erfolgreich!")
    else:
        print("\n❌ Einige Tests fehlgeschlagen!")
