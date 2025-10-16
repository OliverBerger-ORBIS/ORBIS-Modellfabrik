"""
OMF2 Product Manager
Verwaltet Produktkonfigurationen aus der Registry (schreibgeschützt)
Kopiert und angepasst von omf/tools/product_manager.py
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from omf2.common.logger import get_logger


class Omf2ProductManager:
    """Manager für Produktkonfigurationen aus der Registry"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialisiert den Product Manager"""
        self.logger = get_logger(__name__)
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()

    def _get_default_config_path(self) -> str:
        """Get default path to Registry products configuration"""
        # Verwende Registry products.yml (direkt in omf2/registry/)
        registry_path = Path(__file__).parent.parent / "registry" / "products.yml"
        if registry_path.exists():
            self.logger.info(f"✅ Using registry: {registry_path}")
            return str(registry_path)
        raise FileNotFoundError(f"Registry products configuration not found at {registry_path}")

    def _load_config(self) -> Dict[str, Any]:
        """Lädt die Produktkonfiguration aus der YAML-Datei"""
        try:
            with open(self.config_path, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                self.logger.info(f"✅ Product configuration loaded: {len(config.get('products', {}))} products")
                return config
        except Exception as e:
            self.logger.error(f"❌ Error loading product configuration: {e}")
            raise

    def get_all_products(self) -> Dict[str, Any]:
        """Gibt alle Produkte zurück"""
        return self.config.get("products", {})

    def get_product_by_id(self, product_id: str) -> Optional[Dict[str, Any]]:
        """Gibt ein spezifisches Produkt zurück"""
        products = self.get_all_products()
        return products.get(product_id.lower())

    def get_enabled_products(self) -> Dict[str, Any]:
        """Gibt nur aktivierte Produkte zurück"""
        all_products = self.get_all_products()
        return {k: v for k, v in all_products.items() if v.get("enabled", True)}

    def get_manufacturing_steps(self, product_id: str) -> List[Dict[str, Any]]:
        """Gibt die Fertigungsschritte für ein Produkt zurück"""
        product = self.get_product_by_id(product_id)
        if product:
            return product.get("manufacturing_steps", [])
        return []

    def get_fts_route(self, product_id: str) -> List[Dict[str, Any]]:
        """Gibt die FTS-Route für ein Produkt zurück"""
        product = self.get_product_by_id(product_id)
        if product:
            return product.get("fts_route", [])
        return []

    def get_product_icon(self, product_id: str) -> str:
        """Gibt das Icon für ein Produkt zurück"""
        product = self.get_product_by_id(product_id)
        if product:
            return product.get("icon", "❓")
        return "❓"

    def get_catalog_metadata(self) -> Dict[str, Any]:
        """Gibt die Produktkatalog-Metadaten zurück"""
        return self.config.get("catalog_metadata", {})

    def get_total_products_count(self) -> int:
        """Gibt die Gesamtanzahl der Produkte zurück"""
        metadata = self.get_catalog_metadata()
        return metadata.get("total_products", 0)

    def get_enabled_products_count(self) -> int:
        """Gibt die Anzahl der aktivierten Produkte zurück"""
        metadata = self.get_catalog_metadata()
        return metadata.get("enabled_products", 0)


# Singleton Factory
_omf2_product_manager = None


def get_omf2_product_manager(config_path: Optional[str] = None) -> Omf2ProductManager:
    """Factory-Funktion für den OMF2 Product Manager (Singleton)"""
    global _omf2_product_manager

    if _omf2_product_manager is None:
        _omf2_product_manager = Omf2ProductManager(config_path)

    return _omf2_product_manager
