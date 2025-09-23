"""
OMF Shopfloor Manager
Verwaltet Shopfloor-Layout und -Routen aus der Registry (schreibgeschützt)
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

from omf.dashboard.tools.path_constants import REGISTRY_DIR
from omf.dashboard.tools.logging_config import get_logger


class OmfShopfloorManager:
    """Manager für Shopfloor-Konfigurationen aus der Registry"""

    def __init__(self, layout_path: Optional[str] = None, routes_path: Optional[str] = None):
        """Initialisiert den Shopfloor Manager"""
        self.logger = get_logger("tools.shopfloor_manager")
        self.layout_path = layout_path or self._get_default_layout_path()
        self.routes_path = routes_path or self._get_default_routes_path()
        self.layout_config = self._load_layout_config()
        self.routes_config = self._load_routes_config()

    def _get_default_layout_path(self) -> str:
        """Get default path to Registry v1 shopfloor configuration"""
        registry_path = REGISTRY_DIR / "model" / "v1" / "shopfloor.yml"
        if registry_path.exists():
            self.logger.info(f"✅ Using registry v1 shopfloor: {registry_path}")
            return str(registry_path)
        raise FileNotFoundError(f"Registry shopfloor configuration not found at {registry_path}")

    def _get_default_routes_path(self) -> str:
        """Get default path to Registry v1 routes configuration"""
        registry_path = REGISTRY_DIR / "model" / "v1" / "routes.yml"
        if registry_path.exists():
            self.logger.info(f"✅ Using registry v1 routes: {registry_path}")
            return str(registry_path)
        raise FileNotFoundError(f"Registry routes configuration not found at {registry_path}")

    def _load_layout_config(self) -> Dict[str, Any]:
        """Lädt die Shopfloor-Layout-Konfiguration"""
        try:
            with open(self.layout_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                self.logger.info(f"✅ Shopfloor layout loaded: {len(config.get('positions', []))} positions")
                return config
        except Exception as e:
            self.logger.error(f"❌ Error loading shopfloor layout: {e}")
            raise

    def _load_routes_config(self) -> Dict[str, Any]:
        """Lädt die Routes-Konfiguration"""
        try:
            with open(self.routes_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                self.logger.info(f"✅ Routes loaded: {len(config.get('routes', {}))} routes")
                return config
        except Exception as e:
            self.logger.error(f"❌ Error loading routes: {e}")
            raise

    # Layout-Methoden
    def get_grid_layout(self) -> Dict[str, Any]:
        """Gibt die Grid-Layout-Konfiguration zurück"""
        return self.layout_config.get("grid", {})

    def get_all_positions(self) -> List[Dict[str, Any]]:
        """Gibt alle Positionen zurück"""
        return self.layout_config.get("positions", [])

    def get_module_positions(self) -> List[Dict[str, Any]]:
        """Gibt alle Modul-Positionen zurück"""
        positions = self.get_all_positions()
        return [pos for pos in positions if pos.get("type") == "MODULE"]

    def get_intersections(self) -> List[Dict[str, Any]]:
        """Gibt alle Kreuzungen zurück"""
        positions = self.get_all_positions()
        return [pos for pos in positions if pos.get("type") == "INTERSECTION"]

    def get_empty_positions(self) -> List[Dict[str, Any]]:
        """Gibt alle leeren Positionen zurück"""
        positions = self.get_all_positions()
        return [pos for pos in positions if pos.get("type") == "EMPTY"]

    def get_position_by_id(self, position_id: str) -> Optional[Dict[str, Any]]:
        """Gibt eine spezifische Position zurück"""
        positions = self.get_all_positions()
        return next((pos for pos in positions if pos.get("id") == position_id), None)

    def get_position_by_coordinates(self, row: int, col: int) -> Optional[Dict[str, Any]]:
        """Gibt eine Position anhand der Koordinaten zurück"""
        positions = self.get_all_positions()
        return next((pos for pos in positions if pos.get("position") == [row, col]), None)

    # Routes-Methoden
    def get_all_routes(self) -> Dict[str, Any]:
        """Gibt alle Routen zurück"""
        return self.routes_config.get("routes", {})

    def get_route_by_id(self, route_id: str) -> Optional[Dict[str, Any]]:
        """Gibt eine spezifische Route zurück"""
        routes = self.get_all_routes()
        return routes.get(route_id)

    def get_routes_from_module(self, module_id: str) -> List[Dict[str, Any]]:
        """Gibt alle Routen von einem Modul zurück"""
        routes = self.get_all_routes()
        return [route for route in routes.values() if route.get("from") == module_id]

    def get_routes_to_module(self, module_id: str) -> List[Dict[str, Any]]:
        """Gibt alle Routen zu einem Modul zurück"""
        routes = self.get_all_routes()
        return [route for route in routes.values() if route.get("to") == module_id]

    def get_product_routes(self) -> Dict[str, Any]:
        """Gibt alle Produkt-spezifischen Routen zurück"""
        return self.routes_config.get("product_routes", {})

    def get_product_route(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Gibt die Route für ein spezifisches Produkt zurück"""
        product_routes = self.get_product_routes()
        return product_routes.get(f"{product_id.lower()}_route")

    def get_fts_config(self) -> Dict[str, Any]:
        """Gibt die FTS-Konfiguration zurück"""
        return self.routes_config.get("fts", {})

    # Statistiken
    def get_layout_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über das Layout zurück"""
        positions = self.get_all_positions()
        modules = self.get_module_positions()
        intersections = self.get_intersections()
        empty_positions = self.get_empty_positions()

        return {
            "total_positions": len(positions),
            "module_positions": len(modules),
            "intersections": len(intersections),
            "empty_positions": len(empty_positions),
            "enabled_modules": len([m for m in modules if m.get("enabled", False)]),
            "grid_size": self.get_grid_layout().get("total_cells", 0)
        }

    def get_routes_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über die Routen zurück"""
        routes = self.get_all_routes()
        product_routes = self.get_product_routes()

        return {
            "total_routes": len(routes),
            "enabled_routes": len([r for r in routes.values() if r.get("enabled", False)]),
            "tested_routes": len([r for r in routes.values() if r.get("tested", False)]),
            "product_routes": len(product_routes),
            "fts_serial": self.get_fts_config().get("serial_number", "unknown")
        }

    def validate_config(self) -> bool:
        """Validiert die Shopfloor-Konfiguration"""
        try:
            # Layout validieren
            positions = self.get_all_positions()
            if not positions:
                self.logger.warning("⚠️ No positions found in layout configuration")
                return False

            # Routes validieren
            routes = self.get_all_routes()
            if not routes:
                self.logger.warning("⚠️ No routes found in routes configuration")
                return False

            self.logger.info("✅ Shopfloor configuration validation successful")
            return True
        except Exception as e:
            self.logger.error(f"❌ Shopfloor configuration validation failed: {e}")
            return False


# Singleton-Instanz
_shopfloor_manager = None


def get_omf_shopfloor_manager() -> OmfShopfloorManager:
    """Gibt die Singleton-Instanz des Shopfloor Managers zurück"""
    global _shopfloor_manager
    if _shopfloor_manager is None:
        _shopfloor_manager = OmfShopfloorManager()
    return _shopfloor_manager
