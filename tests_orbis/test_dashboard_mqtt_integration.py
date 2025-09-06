#!/usr/bin/env python3
"""
Unit Test: Dashboard MQTT Integration Problem
Simuliert das echte Problem aus dem Dashboard
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add src_orbis to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src_orbis"))


class TestDashboardMqttIntegration(unittest.TestCase):
    """Testet Dashboard MQTT Integration Probleme"""

    def setUp(self):
        """Setup für jeden Test"""
        # Mock Streamlit session_state
        self.mock_session_state = {}

    def test_dashboard_mqtt_client_flow(self):
        """Simuliert den Dashboard MQTT-Client Flow"""
        try:
            from src_orbis.omf.tools.mqtt_client import get_omf_mqtt_client

            print("🔍 Dashboard MQTT-Client Flow Simulation:")
            print("=" * 50)

            # Test-Konfiguration (wie im Dashboard)
            test_config = {
                "host": "192.168.0.100",
                "port": 1883,
                "username": "default",
                "password": "default",
                "client_id": "dashboard_test",
            }

            # Schritt 1: Client erstellen (wie im Dashboard)
            print("📋 Schritt 1: MQTT-Client erstellen")
            client = get_omf_mqtt_client(test_config)
            print(f"   ✅ Client erstellt: {type(client).__name__}")
            print(f"   ✅ Client hat clear_history: {hasattr(client, 'clear_history')}")

            # Schritt 2: Client in Session State setzen (wie im Dashboard)
            print("\n📋 Schritt 2: Client in Session State setzen")
            self.mock_session_state["mqtt_client"] = client
            print(f"   ✅ Client in Session State gesetzt")

            # Schritt 3: Client aus Session State holen (wie in Message Center)
            print("\n📋 Schritt 3: Client aus Session State holen")
            retrieved_client = self.mock_session_state.get("mqtt_client")
            print(f"   ✅ Client aus Session State geholt: {retrieved_client is not None}")

            # Schritt 4: Prüfen ob Client die benötigten Methoden hat
            print("\n📋 Schritt 4: Client-Methoden prüfen")
            if retrieved_client:
                print(f"   ✅ Client gefunden: {type(retrieved_client).__name__}")
                print(f"   ✅ Hat clear_history: {hasattr(retrieved_client, 'clear_history')}")
                print(f"   ✅ Hat drain: {hasattr(retrieved_client, 'drain')}")
                print(f"   ✅ Hat publish: {hasattr(retrieved_client, 'publish')}")

                # Schritt 5: clear_history testen
                print("\n📋 Schritt 5: clear_history testen")
                if hasattr(retrieved_client, "clear_history"):
                    # Nachrichten hinzufügen (simuliert)
                    if hasattr(retrieved_client, "_history"):
                        retrieved_client._history.append({"type": "test", "message": "test"})
                        print(f"   📊 Nachrichten vor clear_history: {len(retrieved_client._history)}")

                        # clear_history aufrufen
                        retrieved_client.clear_history()
                        print(f"   📊 Nachrichten nach clear_history: {len(retrieved_client._history)}")
                        print("   ✅ clear_history funktioniert!")
                    else:
                        print("   ⚠️ _history Attribut nicht verfügbar")
                else:
                    print("   ❌ clear_history Methode fehlt!")
            else:
                print("   ❌ Client nicht gefunden!")

        except Exception as e:
            self.fail(f"❌ Dashboard MQTT-Client Flow fehlgeschlagen: {e}")

    def test_session_state_persistence(self):
        """Testet Session State Persistenz"""
        try:
            from src_orbis.omf.tools.mqtt_client import get_omf_mqtt_client

            print("\n🔍 Session State Persistenz Test:")
            print("=" * 50)

            # Test-Konfiguration
            test_config = {
                "host": "192.168.0.100",
                "port": 1883,
                "username": "default",
                "password": "default",
                "client_id": "persistence_test",
            }

            # Client erstellen und in Session State setzen
            client = get_omf_mqtt_client(test_config)
            self.mock_session_state["mqtt_client"] = client

            # Nachrichten hinzufügen
            if hasattr(client, "_history"):
                client._history.append({"type": "received", "message": "test1"})
                client._history.append({"type": "sent", "message": "test2"})
                print(f"   📊 Nachrichten hinzugefügt: {len(client._history)}")

            # Client aus Session State holen
            retrieved_client = self.mock_session_state.get("mqtt_client")

            # Prüfen ob es der gleiche Client ist
            if retrieved_client is client:
                print("   ✅ Gleicher Client (Referenz-Identität)")
            else:
                print("   ❌ Unterschiedlicher Client (Referenz verloren)")

            # Prüfen ob Nachrichten erhalten sind
            if hasattr(retrieved_client, "_history"):
                print(f"   📊 Nachrichten im retrieved Client: {len(retrieved_client._history)}")
                if len(retrieved_client._history) == 2:
                    print("   ✅ Nachrichten sind erhalten")
                else:
                    print("   ❌ Nachrichten sind verloren")
            else:
                print("   ⚠️ _history Attribut nicht verfügbar")

        except Exception as e:
            self.fail(f"❌ Session State Persistenz Test fehlgeschlagen: {e}")

    def test_multiple_client_creation(self):
        """Testet mehrfache Client-Erstellung (Dashboard-Problem)"""
        try:
            from omf.tools.mqtt_client import get_omf_mqtt_client

            print("\n🔍 Mehrfache Client-Erstellung Test:")
            print("=" * 50)

            # Test-Konfiguration
            test_config = {
                "host": "192.168.0.100",
                "port": 1883,
                "username": "default",
                "password": "default",
                "client_id": "multiple_test",
            }

            # Ersten Client erstellen
            print("📋 Ersten Client erstellen")
            client1 = get_omf_mqtt_client(test_config)
            self.mock_session_state["mqtt_client"] = client1

            # Nachrichten hinzufügen
            if hasattr(client1, "_history"):
                client1._history.append({"type": "test", "message": "client1"})
                print(f"   📊 Nachrichten in Client1: {len(client1._history)}")

            # Zweiten Client erstellen (wie im Dashboard bei jedem Reload)
            print("\n📋 Zweiten Client erstellen (Dashboard Reload)")
            client2 = get_omf_mqtt_client(test_config)

            # Prüfen ob es der gleiche Client ist (Singleton)
            if client1 is client2:
                print("   ✅ Singleton funktioniert (gleicher Client)")
                print(f"   📊 Nachrichten erhalten: {len(client1._history)}")
            else:
                print("   ❌ Singleton funktioniert NICHT (unterschiedliche Clients)")
                print(f"   📊 Nachrichten in Client1: {len(client1._history)}")
                print(f"   📊 Nachrichten in Client2: {len(client2._history)}")

                # Session State überschreiben (Dashboard-Problem)
                print("\n📋 Session State überschreiben (Dashboard-Problem)")
                self.mock_session_state["mqtt_client"] = client2

                # Client aus Session State holen
                retrieved_client = self.mock_session_state.get("mqtt_client")
                if retrieved_client is client2:
                    print("   ✅ Neuer Client in Session State")
                    if hasattr(retrieved_client, "_history"):
                        print(f"   📊 Nachrichten im neuen Client: {len(retrieved_client._history)}")
                else:
                    print("   ❌ Falscher Client in Session State")

        except Exception as e:
            self.fail(f"❌ Mehrfache Client-Erstellung Test fehlgeschlagen: {e}")

    def test_clear_history_integration(self):
        """Testet clear_history Integration"""
        try:
            from omf.tools.mqtt_client import get_omf_mqtt_client

            print("\n🔍 clear_history Integration Test:")
            print("=" * 50)

            # Test-Konfiguration
            test_config = {
                "host": "192.168.0.100",
                "port": 1883,
                "username": "default",
                "password": "default",
                "client_id": "integration_test",
            }

            # Client erstellen und in Session State setzen
            client = get_omf_mqtt_client(test_config)
            self.mock_session_state["mqtt_client"] = client

            # Nachrichten hinzufügen
            if hasattr(client, "_history"):
                client._history.append({"type": "received", "message": "test1"})
                client._history.append({"type": "sent", "message": "test2"})
                client._history.append({"type": "received", "message": "test3"})
                print(f"   📊 Nachrichten hinzugefügt: {len(client._history)}")

            # clear_history aufrufen (wie im Dashboard)
            print("\n📋 clear_history aufrufen")
            if hasattr(client, "clear_history"):
                client.clear_history()
                print(f"   📊 Nachrichten nach clear_history: {len(client._history)}")

                if len(client._history) == 0:
                    print("   ✅ clear_history erfolgreich!")
                else:
                    print("   ❌ clear_history hat nicht funktioniert!")
            else:
                print("   ❌ clear_history Methode fehlt!")

        except Exception as e:
            self.fail(f"❌ clear_history Integration Test fehlgeschlagen: {e}")


if __name__ == "__main__":
    # Test ausführen
    print("🧪 Dashboard MQTT Integration Unit Tests")
    print("=" * 60)

    # Test Suite erstellen
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestDashboardMqttIntegration)

    # Tests ausführen
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)

    # Ergebnis zusammenfassen
    print("\n" + "=" * 60)
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

    print("\n💡 Analyse:")
    if result.wasSuccessful():
        print("   - MQTT-Client funktioniert grundsätzlich")
        print("   - Problem liegt wahrscheinlich in der Streamlit-Integration")
        print("   - Session State wird möglicherweise überschrieben")
    else:
        print("   - MQTT-Client hat grundlegende Probleme")
        print("   - Diese müssen zuerst behoben werden")
