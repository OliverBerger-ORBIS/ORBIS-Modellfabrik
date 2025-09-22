#!/usr/bin/env python3
from omf.dashboard.tools.path_constants import CONFIG_DIR, PROJECT_ROOT, SESSIONS_DIR

"""
Test für OMF Shopfloor-Komponenten
Prüft alle Shopfloor-bezogenen Komponenten und YAML-Configs
"""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
project_root = PROJECT_ROOT


class TestShopfloorComponents(unittest.TestCase):
    """Test-Klasse für Shopfloor-Komponenten"""

    def test_shopfloor_component_import(self):
        """Test: Shopfloor-Komponente kann importiert werden"""
        try:
            from omf.dashboard.components.shopfloor import show_shopfloor

            self.assertTrue(callable(show_shopfloor), "show_shopfloor sollte aufrufbar sein")
            print("✅ Shopfloor-Komponente Import: OK")
        except Exception as e:
            self.fail(f"❌ Shopfloor-Komponente Import failed: {e}")

    def test_shopfloor_layout_component_import(self):
        """Test: Shopfloor-Layout-Komponente kann importiert werden"""
        try:
            from omf.dashboard.components.shopfloor_layout import show_shopfloor_layout

            self.assertTrue(callable(show_shopfloor_layout), "show_shopfloor_layout sollte aufrufbar sein")
            print("✅ Shopfloor-Layout-Komponente Import: OK")
        except Exception as e:
            self.fail(f"❌ Shopfloor-Layout-Komponente Import failed: {e}")

    def test_shopfloor_routes_component_import(self):
        """Test: Shopfloor-Routes-Komponente kann importiert werden"""
        try:
            from omf.dashboard.components.shopfloor_routes import show_shopfloor_routes

            self.assertTrue(callable(show_shopfloor_routes), "show_shopfloor_routes sollte aufrufbar sein")
            print("✅ Shopfloor-Routes-Komponente Import: OK")
        except Exception as e:
            self.fail(f"❌ Shopfloor-Routes-Komponente Import failed: {e}")

    def test_shopfloor_positioning_component_import(self):
        """Test: Shopfloor-Positioning-Komponente kann importiert werden"""
        try:
            from omf.dashboard.components.shopfloor_positioning import show_shopfloor_positioning

            self.assertTrue(callable(show_shopfloor_positioning), "show_shopfloor_positioning sollte aufrufbar sein")
            print("✅ Shopfloor-Positioning-Komponente Import: OK")
        except Exception as e:
            self.fail(f"❌ Shopfloor-Positioning-Komponente Import failed: {e}")

    def test_shopfloor_config_loading(self):
        """Test: Shopfloor-Konfiguration kann geladen werden"""
        try:
            from omf.dashboard.components.shopfloor_utils import load_shopfloor_config

            # Mock der YAML-Dateien
            mock_config = {
                "layout": {"metadata": {"version": "3.0.0"}, "positions": []},
                "routes": {"metadata": {"version": "3.0.0"}, "routes": []},
            }

            with patch("omf.dashboard.components.shopfloor_utils.Path") as mock_path:
                mock_path.return_value.exists.return_value = True
                with patch("builtins.open", MagicMock()):
                    with patch("yaml.safe_load", return_value=mock_config["layout"]):
                        config = load_shopfloor_config()
                        self.assertIsInstance(config, dict, "Config sollte ein Dictionary sein")
                        self.assertIn("layout", config, "Config sollte 'layout' enthalten")
                        self.assertIn("routes", config, "Config sollte 'routes' enthalten")

            print("✅ Shopfloor-Config-Loading: OK")
        except Exception as e:
            self.fail(f"❌ Shopfloor-Config-Loading failed: {e}")

    def test_shopfloor_metadata(self):
        """Test: Shopfloor-Metadaten können abgerufen werden"""
        try:
            from omf.dashboard.components.shopfloor_utils import get_shopfloor_metadata

            # Mock der Konfiguration
            with patch("omf.dashboard.components.shopfloor_utils.load_shopfloor_config") as mock_load:
                mock_load.return_value = {
                    "layout": {"metadata": {"version": "3.0.0", "grid_size": "4x3"}},
                    "routes": {"metadata": {"fts_serial": "5iO4"}},
                }

                metadata = get_shopfloor_metadata()
                self.assertIsInstance(metadata, dict, "Metadaten sollten ein Dictionary sein")
                self.assertIn("version", metadata, "Metadaten sollten 'version' enthalten")
                self.assertIn("grid_size", metadata, "Metadaten sollten 'grid_size' enthalten")

            print("✅ Shopfloor-Metadaten: OK")
        except Exception as e:
            self.fail(f"❌ Shopfloor-Metadaten failed: {e}")

    def test_module_positions(self):
        """Test: Modul-Positionen können abgerufen werden"""
        try:
            from omf.dashboard.components.shopfloor_utils import get_module_positions

            # Mock der Konfiguration
            with patch("omf.dashboard.components.shopfloor_utils.load_shopfloor_config") as mock_load:
                mock_load.return_value = {
                    "layout": {
                        "positions": [
                            {"type": "MODULE", "name": "HBW", "position": [1, 0]},
                            {"type": "INTERSECTION", "name": "1", "position": [1, 1]},
                        ]
                    }
                }

                positions = get_module_positions()
                self.assertIsInstance(positions, list, "Positionen sollten eine Liste sein")
                self.assertEqual(len(positions), 2, "Sollte 2 Positionen haben")

            print("✅ Modul-Positionen: OK")
        except Exception as e:
            self.fail(f"❌ Modul-Positionen failed: {e}")

    def test_fts_routes(self):
        """Test: FTS-Routen können abgerufen werden"""
        try:
            from omf.dashboard.components.shopfloor_utils import get_fts_routes

            # Mock der Konfiguration
            with patch("omf.dashboard.components.shopfloor_utils.load_shopfloor_config") as mock_load:
                mock_load.return_value = {
                    "routes": {"routes": [{"route_id": "HBW_DRILL", "from": "HBW", "to": "DRILL", "distance": 760}]}
                }

                routes = get_fts_routes()
                self.assertIsInstance(routes, list, "Routen sollten eine Liste sein")
                self.assertEqual(len(routes), 1, "Sollte 1 Route haben")
                # Prüfe ob eine Route mit der erwarteten ID existiert
                route_found = False
                for route in routes:
                    if route.get("route_id") == "HBW_DRILL":
                        route_found = True
                        break
                self.assertTrue(route_found, "Route HBW_DRILL sollte existieren")

            print("✅ FTS-Routen: OK")
        except Exception as e:
            self.fail(f"❌ FTS-Routen failed: {e}")

    def test_route_search(self):
        """Test: Route-Suche funktioniert"""
        try:
            from omf.dashboard.components.shopfloor_utils import find_route_between_modules

            # Mock der Konfiguration
            with patch("omf.dashboard.components.shopfloor_utils.get_fts_routes") as mock_routes:
                mock_routes.return_value = [{"route_id": "HBW_DRILL", "from": "HBW", "to": "DRILL", "distance": 760}]

                route = find_route_between_modules("HBW", "DRILL")
                self.assertIsNotNone(route, "Route sollte gefunden werden")
                self.assertEqual(route["route_id"], "HBW_DRILL", "Route-ID sollte korrekt sein")

                # Test für nicht existierende Route
                route = find_route_between_modules("HBW", "NONEXISTENT")
                self.assertIsNone(route, "Nicht existierende Route sollte None zurückgeben")

            print("✅ Route-Suche: OK")
        except Exception as e:
            self.fail(f"❌ Route-Suche failed: {e}")

    def test_shopfloor_statistics(self):
        """Test: Shopfloor-Statistiken können berechnet werden"""
        try:
            from omf.dashboard.components.shopfloor_utils import get_shopfloor_statistics

            # Mock der Konfiguration
            with patch("omf.dashboard.components.shopfloor_utils.get_module_positions") as mock_positions:
                with patch("omf.dashboard.components.shopfloor_utils.get_fts_routes") as mock_routes:
                    with patch("omf.dashboard.components.shopfloor_utils.get_product_routes") as mock_product_routes:
                        mock_positions.return_value = [
                            {"type": "MODULE", "enabled": True},
                            {"type": "INTERSECTION", "enabled": True},
                            {"type": "EMPTY", "enabled": False},
                        ]
                        mock_routes.return_value = [{"route_id": "TEST"}]
                        mock_product_routes.return_value = [{"product_id": "BLUE"}]

                        stats = get_shopfloor_statistics()
                        self.assertIsInstance(stats, dict, "Statistiken sollten ein Dictionary sein")
                        self.assertIn("modules", stats, "Statistiken sollten 'modules' enthalten")
                        self.assertIn("modules", stats, "Statistiken sollten 'modules' enthalten")
                        self.assertIn("routes", stats, "Statistiken sollten 'routes' enthalten")

            print("✅ Shopfloor-Statistiken: OK")
        except Exception as e:
            self.fail(f"❌ Shopfloor-Statistiken failed: {e}")


class TestShopfloorYAMLConfigs(unittest.TestCase):
    """Test-Klasse für Shopfloor YAML-Konfigurationen"""

    def test_product_catalog_yaml_exists(self):
        """Test: Produktkatalog YAML-Datei existiert"""
        try:
            # Verwende das aktuelle Arbeitsverzeichnis als Basis
            config_file = Path.cwd() / "omf" / "omf" / "config" / "products" / "product_catalog.yml"
            self.assertTrue(config_file.exists(), "product_catalog.yml sollte existieren")
            print("✅ Produktkatalog YAML existiert: OK")
        except Exception as e:
            self.fail(f"❌ Produktkatalog YAML existiert failed: {e}")

    def test_shopfloor_layout_yaml_exists(self):
        """Test: Shopfloor-Layout YAML-Datei existiert"""
        try:
            config_file = Path.cwd() / "omf" / "omf" / "config" / "shopfloor" / "layout.yml"
            self.assertTrue(config_file.exists(), "layout.yml sollte existieren")
            print("✅ Shopfloor-Layout YAML existiert: OK")
        except Exception as e:
            self.fail(f"❌ Shopfloor-Layout YAML existiert failed: {e}")

    def test_shopfloor_routes_yaml_exists(self):
        """Test: Shopfloor-Routes YAML-Datei existiert"""
        try:
            config_file = Path.cwd() / "omf" / "omf" / "config" / "shopfloor" / "routes.yml"
            self.assertTrue(config_file.exists(), "routes.yml sollte existieren")
            print("✅ Shopfloor-Routes YAML existiert: OK")
        except Exception as e:
            self.fail(f"❌ Shopfloor-Routes YAML existiert failed: {e}")

    def test_production_workflows_yaml_exists(self):
        """Test: Produktions-Workflows YAML-Datei existiert"""
        try:
            config_file = Path.cwd() / "omf" / "omf" / "config" / "production" / "workflows.yml"
            self.assertTrue(config_file.exists(), "workflows.yml sollte existieren")
            print("✅ Produktions-Workflows YAML existiert: OK")
        except Exception as e:
            self.fail(f"❌ Produktions-Workflows YAML existiert failed: {e}")

    def test_yaml_files_are_valid(self):
        """Test: YAML-Dateien sind gültig"""
        try:
            import yaml

            yaml_files = [
                "omf/config/products/product_catalog.yml",
                "omf/config/shopfloor/layout.yml",
                "omf/config/shopfloor/routes.yml",
                "omf/config/production/workflows.yml",
            ]

            for yaml_file in yaml_files:
                file_path = Path.cwd() / yaml_file
                with open(file_path, encoding="utf-8") as f:
                    data = yaml.safe_load(f)
                    self.assertIsInstance(data, dict, f"{yaml_file} sollte ein Dictionary sein")
                    self.assertIn("metadata", data, f"{yaml_file} sollte 'metadata' enthalten")

            print("✅ YAML-Dateien sind gültig: OK")
        except Exception as e:
            self.fail(f"❌ YAML-Dateien sind gültig failed: {e}")


if __name__ == "__main__":
    print("🧪 Running Shopfloor Component Tests...")
    print("=" * 60)

    # Test-Klassen ausführen
    test_classes = [TestShopfloorComponents, TestShopfloorYAMLConfigs]

    for test_class in test_classes:
        print(f"\n🔍 Testing {test_class.__name__}...")
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=0)
        result = runner.run(suite)

        if result.wasSuccessful():
            print(f"✅ {test_class.__name__}: ALL TESTS PASSED")
        else:
            print(f"❌ {test_class.__name__}: {len(result.failures)} FAILURES, {len(result.errors)} ERRORS")

    print("\n" + "=" * 60)
    print("🎉 Shopfloor Component Tests completed!")
