#!/usr/bin/env python3
"""
Debug Script: Dashboard MQTT Problem
Simuliert das echte Problem aus dem Dashboard
"""

import os
import sys

# Add src_orbis to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src_orbis"))


def debug_dashboard_problem():
    """Debuggt das Dashboard MQTT-Problem"""

    print("🔍 Dashboard MQTT Problem Debug")
    print("=" * 50)

    try:
        # Import der Dashboard-Komponenten
        from src_orbis.omf.config.config import LIVE_CFG
        from src_orbis.omf.tools.mqtt_client import get_omf_mqtt_client

        print("✅ Imports erfolgreich")
        print(f"   - LIVE_CFG: {LIVE_CFG}")

        # Simuliere Dashboard-Flow
        print("\n📋 Simuliere Dashboard-Flow:")

        # Schritt 1: Ersten Client erstellen (Dashboard-Start)
        print("   📋 Schritt 1: Ersten Client erstellen")
        client1 = get_omf_mqtt_client(LIVE_CFG)
        print(f"      ✅ Client1 erstellt: {type(client1).__name__}")
        print(f"      ✅ Client1 ID: {id(client1)}")
        print(f"      ✅ Client1 hat clear_history: {hasattr(client1, 'clear_history')}")

        # Nachrichten hinzufügen
        if hasattr(client1, "_history"):
            client1._history.append({"type": "test", "message": "dashboard_start"})
            print(f"      📊 Nachrichten in Client1: {len(client1._history)}")

        # Schritt 2: Zweiten Client erstellen (Dashboard-Reload)
        print("\n   📋 Schritt 2: Zweiten Client erstellen (Dashboard-Reload)")
        client2 = get_omf_mqtt_client(LIVE_CFG)
        print(f"      ✅ Client2 erstellt: {type(client2).__name__}")
        print(f"      ✅ Client2 ID: {id(client2)}")
        print(f"      ✅ Client2 hat clear_history: {hasattr(client2, 'clear_history')}")

        # Prüfen ob es der gleiche Client ist
        if client1 is client2:
            print("      ✅ Singleton funktioniert (gleicher Client)")
            print(f"      📊 Nachrichten erhalten: {len(client1._history)}")
        else:
            print("      ❌ Singleton funktioniert NICHT (unterschiedliche Clients)")
            print(f"      📊 Nachrichten in Client1: {len(client1._history)}")
            print(f"      📊 Nachrichten in Client2: {len(client2._history)}")

        # Schritt 3: Session State simulieren
        print("\n   📋 Schritt 3: Session State simulieren")
        session_state = {}

        # Ersten Client in Session State setzen
        session_state["mqtt_client"] = client1
        print("      ✅ Client1 in Session State gesetzt")

        # Client aus Session State holen
        retrieved_client1 = session_state.get("mqtt_client")
        print(f"      ✅ Client1 aus Session State geholt: {retrieved_client1 is not None}")
        print(f"      ✅ Gleicher Client: {retrieved_client1 is client1}")

        # Zweiten Client in Session State setzen (Dashboard-Problem)
        print("\n   📋 Schritt 4: Zweiten Client in Session State setzen (Dashboard-Problem)")
        session_state["mqtt_client"] = client2
        print("      ✅ Client2 in Session State gesetzt")

        # Client aus Session State holen
        retrieved_client2 = session_state.get("mqtt_client")
        print(f"      ✅ Client2 aus Session State geholt: {retrieved_client2 is not None}")
        print(f"      ✅ Gleicher Client: {retrieved_client2 is client2}")
        print(f"      ✅ Client1 überschrieben: {retrieved_client2 is not client1}")

        # Schritt 5: clear_history testen
        print("\n   📋 Schritt 5: clear_history testen")
        if retrieved_client2 and hasattr(retrieved_client2, "clear_history"):
            print("      ✅ clear_history verfügbar")

            # Nachrichten zählen
            if hasattr(retrieved_client2, "_history"):
                print(f"      📊 Nachrichten vor clear_history: {len(retrieved_client2._history)}")

                # clear_history aufrufen
                retrieved_client2.clear_history()
                print(f"      📊 Nachrichten nach clear_history: {len(retrieved_client2._history)}")

                if len(retrieved_client2._history) == 0:
                    print("      ✅ clear_history erfolgreich!")
                else:
                    print("      ❌ clear_history hat nicht funktioniert!")
            else:
                print("      ⚠️ _history Attribut nicht verfügbar")
        else:
            print("      ❌ clear_history nicht verfügbar")

        # Schritt 6: Problem-Analyse
        print("\n🔍 Problem-Analyse:")
        if client1 is not client2:
            print("   ❌ PROBLEM GEFUNDEN: Singleton funktioniert nicht!")
            print("   💡 Ursache: Dashboard erstellt bei jedem Reload einen neuen Client")
            print("   💡 Lösung: Session State wird überschrieben, alter Client geht verloren")
        else:
            print("   ✅ Singleton funktioniert - Problem liegt woanders")

        if retrieved_client2 is not client1:
            print("   ❌ PROBLEM GEFUNDEN: Session State wird überschrieben!")
            print("   💡 Ursache: Neuer Client überschreibt alten Client in session_state")
            print("   💡 Lösung: Client nur einmal initialisieren")
        else:
            print("   ✅ Session State bleibt erhalten")

    except Exception as e:
        print(f"❌ Fehler beim Debuggen: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_dashboard_problem()
