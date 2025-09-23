"""
OMF Product Manager
Verwaltet Produktkonfigurationen aus der Registry (schreibgeschützt)
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

from omf.dashboard.tools.path_constants import REGISTRY_DIR
from omf.dashboard.tools.logging_config import get_logger


class OmfProductManager:
    """Manager für Produktkonfigurationen aus der Registry"""

    def __init__(self, config_path: Optional[str] = None):
        """Initialisiert den Product Manager"""
        self.logger = get_logger("tools.product_manager")
        self.config_path = config_path or self._get_default_config_path()
        self.config = self._load_config()

    def _get_default_config_path(self) -> str:
        """Get default path to Registry v1 products configuration"""
        registry_path = REGISTRY_DIR / "model" / "v1" / "products.yml"
        if registry_path.exists():
            self.logger.info(f"✅ Using registry v1: {registry_path}")
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

    def get_products_by_color(self, color: str) -> List[Dict[str, Any]]:
        """Gibt Produkte nach Farbe zurück"""
        products = self.get_all_products()
        return [product for product in products.values() 
                if product.get("id", "").upper() == color.upper()]

    def get_manufacturing_steps(self, product_id: str) -> List[Dict[str, Any]]:
        """Gibt die Fertigungsschritte für ein Produkt zurück"""
        product = self.get_product_by_id(product_id)
        if product:
            return product.get("manufacturing_steps", [])
        return []

    def get_fts_routes(self, product_id: str) -> List[Dict[str, Any]]:
        """Gibt die FTS-Routen für ein Produkt zurück"""
        product = self.get_product_by_id(product_id)
        if product:
            return product.get("fts_route", [])
        return []

    def get_enabled_products(self) -> List[Dict[str, Any]]:
        """Gibt alle aktivierten Produkte zurück"""
        products = self.get_all_products()
        return [product for product in products.values() 
                if product.get("enabled", False)]

    def get_product_statistics(self) -> Dict[str, Any]:
        """Gibt Statistiken über die Produkte zurück"""
        products = self.get_all_products()
        enabled_products = self.get_enabled_products()
        
        return {
            "total_products": len(products),
            "enabled_products": len(enabled_products),
            "disabled_products": len(products) - len(enabled_products),
            "products_by_color": {
                "RED": len([p for p in enabled_products if p.get("id") == "RED"]),
                "BLUE": len([p for p in enabled_products if p.get("id") == "BLUE"]),
                "WHITE": len([p for p in enabled_products if p.get("id") == "WHITE"]),
            }
        }

    def validate_config(self) -> bool:
        """Validiert die Produktkonfiguration"""
        try:
            products = self.get_all_products()
            if not products:
                self.logger.warning("⚠️ No products found in configuration")
                return False

            for product_id, product in products.items():
                required_fields = ["id", "name", "manufacturing_steps", "fts_route"]
                for field in required_fields:
                    if field not in product:
                        self.logger.error(f"❌ Product {product_id} missing required field: {field}")
                        return False

            self.logger.info("✅ Product configuration validation successful")
            return True
        except Exception as e:
            self.logger.error(f"❌ Product configuration validation failed: {e}")
            return False


# Singleton-Instanz
_product_manager = None


def get_omf_product_manager() -> OmfProductManager:
    """Gibt die Singleton-Instanz des Product Managers zurück"""
    global _product_manager
    if _product_manager is None:
        _product_manager = OmfProductManager()
    return _product_manager
