#!/usr/bin/env python3
"""
FTS Route Generator - Praktisches Beispiel
Zeigt die Generierung von FTS-MQTT-Messages aus YAML-Routen
"""

import json
import sys
from pathlib import Path

from omf.tools.fts_route_generator import FTSRouteGenerator

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    """Hauptfunktion für FTS Route Generator Beispiel"""
    print("🚛 FTS Route Generator - Praktisches Beispiel")
    print("=" * 60)

    # FTS Route Generator initialisieren
    generator = FTSRouteGenerator()

    # Verfügbare Routen anzeigen
    print("\n📋 Verfügbare Routen:")
    available_routes = generator.get_available_routes()
    for route_id in available_routes:
        print(f"  - {route_id}")

    # Getestete Routen anzeigen
    print("\n✅ Getestete Routen:")
    tested_routes = generator.get_tested_routes()
    for route_id in tested_routes:
        print(f"  - {route_id}")

    # DPS → HBW Route generieren (getestete Route)
    print("\n🎯 Generiere FTS-Message für DPS → HBW Route:")
    print("-" * 40)

    try:
        # Generiere FTS-Message mit Validierung
        fts_message = generator.generate_fts_message_with_validation(
            route_id="dps_to_hbw", order_id="test-navigation-dps-to-hbw-wareneingang-001", order_update_id=0
        )

        if fts_message:
            print("✅ FTS-Message erfolgreich generiert!")

            # Message-Struktur anzeigen
            print("\n📊 Message-Struktur:")
            print(f"  - Timestamp: {fts_message['timestamp']}")
            print(f"  - Order ID: {fts_message['orderId']}")
            print(f"  - Order Update ID: {fts_message['orderUpdateId']}")
            print(f"  - Serial Number: {fts_message['serialNumber']}")
            print(f"  - Nodes: {len(fts_message['nodes'])}")
            print(f"  - Edges: {len(fts_message['edges'])}")

            # Nodes anzeigen
            print("\n🔗 Nodes:")
            for i, node in enumerate(fts_message["nodes"]):
                node_type = "Start" if i == 0 else "End" if i == len(fts_message["nodes"]) - 1 else "Intersection"
                print(f"  {i+1}. {node_type}: {node['id']}")
                if "action" in node:
                    print(f"     Action: {node['action']['type']}")

            # Edges anzeigen
            print("\n🛣️ Edges:")
            for i, edge in enumerate(fts_message["edges"]):
                print(
                    f"  {i+1}. {edge['id']}: {edge['linkedNodes'][0]} → {edge['linkedNodes'][1]} ({edge['length']}cm)"
                )

            # JSON-Output
            print("\n📄 JSON-Output:")
            print(json.dumps(fts_message, indent=2))

            # MQTT-Topic
            print("\n📡 MQTT-Topic:")
            print(f"  fts/v1/ff/{fts_message['serialNumber']}/order")

        else:
            print("❌ Fehler beim Generieren der FTS-Message")

    except Exception as e:
        print(f"❌ Fehler: {e}")

    # Route-Validierung
    print("\n🔍 Route-Validierung:")
    print("-" * 40)

    for route_id in ["dps_to_hbw", "hbw_to_drill", "INVALID_ROUTE"]:
        is_valid = generator.validate_route(route_id)
        status = "✅ Gültig" if is_valid else "❌ Ungültig"
        print(f"  - {route_id}: {status}")

    print("\n🎉 Beispiel abgeschlossen!")


if __name__ == "__main__":
    main()
