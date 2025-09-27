"""
OMF FTS Route Generator
Generiert MQTT-Messages für FTS-Routen aus YAML-Konfiguration
Integriert mit bestehendem MessageGenerator für Validierung
Version: 3.3.0
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

# Import des bestehenden MessageTemplateManagers
from .message_template_manager import get_omf_message_template_manager


class FTSRouteGenerator:
    """Generiert FTS-MQTT-Messages aus YAML-Routen-Konfiguration"""

    def __init__(self, config_dir: Optional[Path] = None):
        """Initialisiert den FTS Route Generator"""
        if config_dir is None:
            config_dir = Path(__file__).parent.parent / "config" / "shopfloor"

        self.config_dir = config_dir
        self.routes_config = self._load_routes_config()
        self.layout_config = self._load_layout_config()

        # Integration mit bestehendem MessageTemplateManager
        self.message_template_manager = get_omf_message_template_manager()

    def _load_routes_config(self) -> Dict[str, Any]:
        """Lädt die Routen-Konfiguration"""
        try:
            routes_file = self.config_dir / "routes.yml"
            if routes_file.exists():
                with open(routes_file, encoding="utf-8") as f:
                    return yaml.safe_load(f)
            return {}
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der Routen-Konfiguration: {e}")
            return {}

    def _load_layout_config(self) -> Dict[str, Any]:
        """Lädt die Layout-Konfiguration"""
        try:
            layout_file = self.config_dir / "layout.yml"
            if layout_file.exists():
                with open(layout_file, encoding="utf-8") as f:
                    return yaml.safe_load(f)
            return {}
        except Exception as e:
            print(f"⚠️ Fehler beim Laden der Layout-Konfiguration: {e}")
            return {}

    def get_route(self, route_id: str) -> Optional[Dict[str, Any]]:
        """Gibt eine Route anhand der Route-ID zurück"""
        routes = self.routes_config.get("routes", {})
        return routes.get(route_id)

    def find_route_between_modules(self, from_module: str, to_module: str) -> Optional[Dict[str, Any]]:
        """Findet eine Route zwischen zwei Modulen"""
        routes = self.routes_config.get("routes", {})

        for route in routes.values():
            if route.get("from") == from_module and route.get("to") == to_module:
                return route
        return None

    def generate_fts_message(
        self,
        route_id: str,
        order_id: Optional[str] = None,
        order_update_id: int = 0,
        load_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Generiert eine FTS-MQTT-Message aus einer Route"""
        route = self.get_route(route_id)
        if not route:
            print(f"❌ Route {route_id} nicht gefunden")
            return None

        # Generiere Order-ID falls nicht vorhanden
        if not order_id:
            order_id = f"fts-route-{route_id.lower()}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

        # Erstelle Nodes-Array
        nodes = self._create_nodes_array(route)

        # Erstelle Edges-Array
        edges = self._create_edges_array(route)

        # Erstelle FTS-Message
        fts_message = {
            "timestamp": datetime.now().isoformat() + "Z",
            "orderId": order_id,
            "orderUpdateId": order_update_id,
            "nodes": nodes,
            "edges": edges,
            "serialNumber": "5iO4",  # FTS Serial Number
        }

        return fts_message

    def generate_fts_message_with_validation(
        self,
        route_id: str,
        order_id: Optional[str] = None,
        order_update_id: int = 0,
        load_metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """Generiert eine FTS-MQTT-Message mit Validierung über MessageGenerator"""
        try:
            # Generiere FTS-Message
            fts_message = self.generate_fts_message(route_id, order_id, order_update_id, load_metadata)
            if not fts_message:
                return None

            # Validiere über MessageTemplateManager (falls FTS-Template existiert)
            try:
                # Versuche FTS-Template zu validieren
                validation_result = self.message_template_manager.validate_message("fts/navigation", fts_message)
                if validation_result:
                    print(f"⚠️ Validierungswarnungen für FTS-Message: {validation_result}")
            except Exception as e:
                print(f"ℹ️ FTS-Template-Validierung nicht verfügbar: {e}")
                # Das ist OK - FTS-Template existiert möglicherweise noch nicht

            return fts_message

        except Exception as e:
            print(f"❌ Fehler bei FTS-Message-Generierung mit Validierung: {e}")
            return None

    def _create_nodes_array(self, route: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Erstellt das Nodes-Array für die FTS-Message"""
        nodes = []

        # Start-Node (From-Modul)
        from_module = route.get("from")
        from_serial = self._get_module_serial(from_module)
        if from_serial:
            nodes.append({"id": from_serial, "linkedEdges": [f"{from_serial}-{route.get('mqtt_via', [])[0]}"]})

        # Kreuzungspunkt-Nodes
        mqtt_via = route.get("mqtt_via", [])
        intersection_actions = route.get("intersection_actions", [])

        for i, intersection_id in enumerate(mqtt_via):
            # Bestimme linkedEdges
            linked_edges = []
            if i == 0:  # Erste Kreuzung
                linked_edges.append(f"{from_serial}-{intersection_id}")
            else:  # Weitere Kreuzungen
                linked_edges.append(f"{mqtt_via[i-1]}-{intersection_id}")

            if i < len(mqtt_via) - 1:  # Nicht die letzte Kreuzung
                linked_edges.append(f"{intersection_id}-{mqtt_via[i+1]}")
            else:  # Letzte Kreuzung
                to_module = route.get("to")
                to_serial = self._get_module_serial(to_module)
                if to_serial:
                    linked_edges.append(f"{intersection_id}-{to_serial}")

            # Bestimme Action
            action = self._get_intersection_action(intersection_actions, intersection_id)

            node = {"id": intersection_id, "linkedEdges": linked_edges, "action": action}
            nodes.append(node)

        # Ziel-Node (To-Modul)
        to_module = route.get("to")
        to_serial = self._get_module_serial(to_module)
        if to_serial:
            # Bestimme linkedEdges für Ziel-Node
            linked_edges = []
            if mqtt_via:
                linked_edges.append(f"{mqtt_via[-1]}-{to_serial}")

            # Bestimme Action für Ziel-Node
            action = {
                "type": "DOCK",
                "id": f"dock-at-{to_module.lower()}-{uuid.uuid4().hex[:8]}",
                "metadata": {
                    "loadId": "04798eca341290",  # Default Load ID
                    "loadType": "WHITE",  # Default Load Type
                    "loadPosition": "1",  # Default Load Position
                },
            }

            nodes.append({"id": to_serial, "linkedEdges": linked_edges, "action": action})

        return nodes

    def _create_edges_array(self, route: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Erstellt das Edges-Array für die FTS-Message"""
        edges = []

        from_module = route.get("from")
        from_serial = self._get_module_serial(from_module)
        mqtt_via = route.get("mqtt_via", [])
        to_module = route.get("to")
        to_serial = self._get_module_serial(to_module)

        # Edge von Start-Modul zur ersten Kreuzung
        if from_serial and mqtt_via:
            edges.append(
                {
                    "id": f"{from_serial}-{mqtt_via[0]}",
                    "length": 380,  # Standard-Länge
                    "linkedNodes": [from_serial, mqtt_via[0]],
                }
            )

        # Edges zwischen Kreuzungspunkten
        for i in range(len(mqtt_via) - 1):
            edges.append(
                {
                    "id": f"{mqtt_via[i]}-{mqtt_via[i+1]}",
                    "length": 360,  # Standard-Länge
                    "linkedNodes": [mqtt_via[i], mqtt_via[i + 1]],
                }
            )

        # Edge von letzter Kreuzung zum Ziel-Modul
        if mqtt_via and to_serial:
            edges.append(
                {
                    "id": f"{mqtt_via[-1]}-{to_serial}",
                    "length": 380,  # Standard-Länge
                    "linkedNodes": [mqtt_via[-1], to_serial],
                }
            )

        return edges

    def _get_module_serial(self, module_name: str) -> Optional[str]:
        """Gibt die Serial Number eines Moduls zurück"""
        positions = self.layout_config.get("positions", [])

        for position in positions:
            if position.get("name") == module_name and position.get("type") == "MODULE":
                return position.get("module_serial")
        return None

    def _get_intersection_action(
        self, intersection_actions: List[Dict[str, Any]], intersection_id: str
    ) -> Dict[str, Any]:
        """Gibt die Action für einen Kreuzungspunkt zurück"""
        for action in intersection_actions:
            if action.get("mqtt_id") == intersection_id:
                return {
                    "id": f"pass-through-{intersection_id}-{uuid.uuid4().hex[:8]}",
                    "type": action.get("action", "PASS"),
                }

        # Default Action
        return {"id": f"pass-through-{intersection_id}-{uuid.uuid4().hex[:8]}", "type": "PASS"}

    def get_available_routes(self) -> List[str]:
        """Gibt alle verfügbaren Route-IDs zurück"""
        routes = self.routes_config.get("routes", {})
        return list(routes.keys())

    def get_tested_routes(self) -> List[str]:
        """Gibt alle getesteten Route-IDs zurück"""
        routes = self.routes_config.get("routes", {})
        tested_routes = []

        for route_id, route in routes.items():
            if route.get("tested", False):
                tested_routes.append(route_id)

        return tested_routes

    def validate_route(self, route_id: str) -> bool:
        """Validiert eine Route"""
        route = self.get_route(route_id)
        if not route:
            return False

        # Prüfe erforderliche Felder
        required_fields = ["from", "to", "mqtt_via", "intersection_actions"]
        for field in required_fields:
            if field not in route:
                return False

        # Prüfe ob Module existieren
        from_serial = self._get_module_serial(route.get("from"))
        to_serial = self._get_module_serial(route.get("to"))

        if not from_serial or not to_serial:
            return False

        return True


def get_fts_route_generator() -> FTSRouteGenerator:
    """Singleton-Instanz des FTS Route Generators"""
    if not hasattr(get_fts_route_generator, "_instance"):
        get_fts_route_generator._instance = FTSRouteGenerator()
    return get_fts_route_generator._instance
