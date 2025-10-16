#!/usr/bin/env python3
"""
Test für OMF FTS Route Generator
Prüft die Generierung von FTS-MQTT-Messages aus YAML-Routen
"""

import unittest
from pathlib import Path
from unittest.mock import patch

# Add project root to path
project_root = Path(__file__).parent.parent


class TestFTSRouteGenerator(unittest.TestCase):
    """Test-Klasse für FTS Route Generator"""

    def setUp(self):
        """Setup für Tests"""
        from omf.tools.fts_route_generator import FTSRouteGenerator

        self.generator = FTSRouteGenerator()

    def test_fts_route_generator_import(self):
        """Test: FTS Route Generator kann importiert werden"""
        try:
            from omf.tools.fts_route_generator import FTSRouteGenerator, get_fts_route_generator

            self.assertTrue(callable(FTSRouteGenerator), "FTSRouteGenerator sollte aufrufbar sein")
            self.assertTrue(callable(get_fts_route_generator), "get_fts_route_generator sollte aufrufbar sein")
            print("✅ FTS Route Generator Import: OK")
        except Exception as e:
            self.fail(f"❌ FTS Route Generator Import failed: {e}")

    def test_get_route(self):
        """Test: Route kann anhand der Route-ID abgerufen werden"""
        try:
            # Mock der Konfiguration
            with patch.object(self.generator, "routes_config") as mock_config:
                mock_config.get.return_value = {
                    "DPS_HBW": {
                        "route_id": "DPS_HBW",
                        "from": "DPS",
                        "to": "HBW",
                        "mqtt_via": ["2", "1"],
                        "intersection_actions": [
                            {"intersection": "Intersection2", "mqtt_id": "2", "action": "PASS"},
                            {"intersection": "Intersection1", "mqtt_id": "1", "action": "PASS"},
                        ],
                    }
                }

                route = self.generator.get_route("DPS_HBW")
                self.assertIsNotNone(route, "Route sollte gefunden werden")
                self.assertEqual(route["route_id"], "DPS_HBW", "Route-ID sollte korrekt sein")
                self.assertEqual(route["from"], "DPS", "From-Modul sollte korrekt sein")
                self.assertEqual(route["to"], "HBW", "To-Modul sollte korrekt sein")

            print("✅ Get Route: OK")
        except Exception as e:
            self.fail(f"❌ Get Route failed: {e}")

    def test_find_route_between_modules(self):
        """Test: Route zwischen Modulen kann gefunden werden"""
        try:
            # Mock der Konfiguration
            with patch.object(self.generator, "routes_config") as mock_config:
                mock_config.get.return_value = {
                    "DPS_HBW": {"route_id": "DPS_HBW", "from": "DPS", "to": "HBW", "mqtt_via": ["2", "1"]}
                }

                route = self.generator.find_route_between_modules("DPS", "HBW")
                self.assertIsNotNone(route, "Route sollte gefunden werden")
                self.assertEqual(route["route_id"], "DPS_HBW", "Route-ID sollte korrekt sein")

                # Test für nicht existierende Route
                route = self.generator.find_route_between_modules("NONEXISTENT", "HBW")
                self.assertIsNone(route, "Nicht existierende Route sollte None zurückgeben")

            print("✅ Find Route Between Modules: OK")
        except Exception as e:
            self.fail(f"❌ Find Route Between Modules failed: {e}")

    def test_generate_fts_message_dps_to_hbw(self):
        """Test: FTS-Message für DPS → HBW Route wird korrekt generiert"""
        try:
            # Mock der Konfiguration
            with patch.object(self.generator, "routes_config") as mock_routes:
                with patch.object(self.generator, "layout_config") as mock_layout:
                    mock_routes.get.return_value = {
                        "DPS_HBW": {
                            "route_id": "DPS_HBW",
                            "from": "DPS",
                            "to": "HBW",
                            "mqtt_via": ["2", "1"],
                            "intersection_actions": [
                                {"intersection": "Intersection2", "mqtt_id": "2", "action": "PASS"},
                                {"intersection": "Intersection1", "mqtt_id": "1", "action": "PASS"},
                            ],
                        }
                    }

                    mock_layout.get.return_value = [
                        {"name": "DPS", "type": "MODULE", "module_serial": "SVR4H73275"},
                        {"name": "HBW", "type": "MODULE", "module_serial": "SVR3QA0022"},
                    ]

                    # Generiere FTS-Message
                    fts_message = self.generator.generate_fts_message("DPS_HBW")

                    self.assertIsNotNone(fts_message, "FTS-Message sollte generiert werden")
                    self.assertIn("timestamp", fts_message, "FTS-Message sollte timestamp enthalten")
                    self.assertIn("orderId", fts_message, "FTS-Message sollte orderId enthalten")
                    self.assertIn("orderUpdateId", fts_message, "FTS-Message sollte orderUpdateId enthalten")
                    self.assertIn("nodes", fts_message, "FTS-Message sollte nodes enthalten")
                    self.assertIn("edges", fts_message, "FTS-Message sollte edges enthalten")
                    self.assertIn("serialNumber", fts_message, "FTS-Message sollte serialNumber enthalten")

                    # Prüfe Nodes
                    nodes = fts_message["nodes"]
                    self.assertGreater(len(nodes), 0, "Nodes sollten vorhanden sein")

                    # Prüfe Edges
                    edges = fts_message["edges"]
                    self.assertGreater(len(edges), 0, "Edges sollten vorhanden sein")

                    # Prüfe Serial Number
                    self.assertEqual(fts_message["serialNumber"], "5iO4", "Serial Number sollte korrekt sein")

            print("✅ Generate FTS Message DPS to HBW: OK")
        except Exception as e:
            self.fail(f"❌ Generate FTS Message DPS to HBW failed: {e}")

    def test_generate_fts_message_with_custom_order_id(self):
        """Test: FTS-Message mit benutzerdefinierter Order-ID"""
        try:
            # Mock der Konfiguration
            with patch.object(self.generator, "routes_config") as mock_routes:
                with patch.object(self.generator, "layout_config") as mock_layout:
                    mock_routes.get.return_value = {
                        "DPS_HBW": {
                            "route_id": "DPS_HBW",
                            "from": "DPS",
                            "to": "HBW",
                            "mqtt_via": ["2", "1"],
                            "intersection_actions": [
                                {"intersection": "Intersection2", "mqtt_id": "2", "action": "PASS"},
                                {"intersection": "Intersection1", "mqtt_id": "1", "action": "PASS"},
                            ],
                        }
                    }

                    mock_layout.get.return_value = [
                        {"name": "DPS", "type": "MODULE", "module_serial": "SVR4H73275"},
                        {"name": "HBW", "type": "MODULE", "module_serial": "SVR3QA0022"},
                    ]

                    # Generiere FTS-Message mit benutzerdefinierter Order-ID
                    custom_order_id = "test-navigation-dps-to-hbw-wareneingang-001"
                    fts_message = self.generator.generate_fts_message("DPS_HBW", order_id=custom_order_id)

                    self.assertIsNotNone(fts_message, "FTS-Message sollte generiert werden")
                    self.assertEqual(fts_message["orderId"], custom_order_id, "Order-ID sollte korrekt sein")

            print("✅ Generate FTS Message with Custom Order ID: OK")
        except Exception as e:
            self.fail(f"❌ Generate FTS Message with Custom Order ID failed: {e}")

    def test_create_nodes_array(self):
        """Test: Nodes-Array wird korrekt erstellt"""
        try:
            # Mock der Konfiguration
            with patch.object(self.generator, "layout_config") as mock_layout:
                mock_layout.get.return_value = [
                    {"name": "DPS", "type": "MODULE", "module_serial": "SVR4H73275"},
                    {"name": "HBW", "type": "MODULE", "module_serial": "SVR3QA0022"},
                ]

                route = {
                    "from": "DPS",
                    "to": "HBW",
                    "mqtt_via": ["2", "1"],
                    "intersection_actions": [
                        {"intersection": "Intersection2", "mqtt_id": "2", "action": "PASS"},
                        {"intersection": "Intersection1", "mqtt_id": "1", "action": "PASS"},
                    ],
                }

                nodes = self.generator._create_nodes_array(route)

                self.assertIsInstance(nodes, list, "Nodes sollten eine Liste sein")
                self.assertGreater(len(nodes), 0, "Nodes sollten vorhanden sein")

                # Prüfe Start-Node
                start_node = nodes[0]
                self.assertEqual(start_node["id"], "SVR4H73275", "Start-Node sollte korrekte Serial haben")
                self.assertIn("linkedEdges", start_node, "Start-Node sollte linkedEdges haben")

                # Prüfe Kreuzungspunkt-Nodes
                for node in nodes[1:-1]:  # Alle außer Start und Ende
                    self.assertIn("id", node, "Node sollte ID haben")
                    self.assertIn("linkedEdges", node, "Node sollte linkedEdges haben")
                    self.assertIn("action", node, "Node sollte action haben")

                # Prüfe Ziel-Node
                end_node = nodes[-1]
                self.assertEqual(end_node["id"], "SVR3QA0022", "End-Node sollte korrekte Serial haben")
                self.assertIn("action", end_node, "End-Node sollte action haben")
                self.assertEqual(end_node["action"]["type"], "DOCK", "End-Node sollte DOCK action haben")

            print("✅ Create Nodes Array: OK")
        except Exception as e:
            self.fail(f"❌ Create Nodes Array failed: {e}")

    def test_create_edges_array(self):
        """Test: Edges-Array wird korrekt erstellt"""
        try:
            # Mock der Konfiguration
            with patch.object(self.generator, "layout_config") as mock_layout:
                mock_layout.get.return_value = [
                    {"name": "DPS", "type": "MODULE", "module_serial": "SVR4H73275"},
                    {"name": "HBW", "type": "MODULE", "module_serial": "SVR3QA0022"},
                ]

                route = {"from": "DPS", "to": "HBW", "mqtt_via": ["2", "1"]}

                edges = self.generator._create_edges_array(route)

                self.assertIsInstance(edges, list, "Edges sollten eine Liste sein")
                self.assertGreater(len(edges), 0, "Edges sollten vorhanden sein")

                # Prüfe Edge-Struktur
                for edge in edges:
                    self.assertIn("id", edge, "Edge sollte ID haben")
                    self.assertIn("length", edge, "Edge sollte length haben")
                    self.assertIn("linkedNodes", edge, "Edge sollte linkedNodes haben")
                    self.assertIsInstance(edge["linkedNodes"], list, "linkedNodes sollten eine Liste sein")
                    self.assertEqual(len(edge["linkedNodes"]), 2, "linkedNodes sollten 2 Elemente haben")

            print("✅ Create Edges Array: OK")
        except Exception as e:
            self.fail(f"❌ Create Edges Array failed: {e}")

    def test_get_module_serial(self):
        """Test: Modul-Serial kann abgerufen werden"""
        try:
            # Mock der Konfiguration
            with patch.object(self.generator, "layout_config") as mock_layout:
                mock_layout.get.return_value = [
                    {"name": "DPS", "type": "MODULE", "module_serial": "SVR4H73275"},
                    {"name": "HBW", "type": "MODULE", "module_serial": "SVR3QA0022"},
                    {"name": "Intersection1", "type": "INTERSECTION", "id": "Intersection1"},
                ]

                dps_serial = self.generator._get_module_serial("DPS")
                self.assertEqual(dps_serial, "SVR4H73275", "DPS Serial sollte korrekt sein")

                hbw_serial = self.generator._get_module_serial("HBW")
                self.assertEqual(hbw_serial, "SVR3QA0022", "HBW Serial sollte korrekt sein")

                # Test für nicht existierendes Modul
                nonexistent_serial = self.generator._get_module_serial("NONEXISTENT")
                self.assertIsNone(nonexistent_serial, "Nicht existierendes Modul sollte None zurückgeben")

            print("✅ Get Module Serial: OK")
        except Exception as e:
            self.fail(f"❌ Get Module Serial failed: {e}")

    def test_get_intersection_action(self):
        """Test: Kreuzungspunkt-Action wird korrekt abgerufen"""
        try:
            intersection_actions = [
                {"intersection": "Intersection2", "mqtt_id": "2", "action": "PASS"},
                {"intersection": "Intersection1", "mqtt_id": "1", "action": "PASS"},
            ]

            action = self.generator._get_intersection_action(intersection_actions, "2")
            self.assertIsNotNone(action, "Action sollte gefunden werden")
            self.assertEqual(action["type"], "PASS", "Action-Type sollte korrekt sein")
            self.assertIn("id", action, "Action sollte ID haben")

            # Test für nicht existierenden Kreuzungspunkt
            action = self.generator._get_intersection_action(intersection_actions, "99")
            self.assertIsNotNone(action, "Default Action sollte generiert werden")
            self.assertEqual(action["type"], "PASS", "Default Action-Type sollte PASS sein")

            print("✅ Get Intersection Action: OK")
        except Exception as e:
            self.fail(f"❌ Get Intersection Action failed: {e}")

    def test_validate_route(self):
        """Test: Route-Validierung funktioniert"""
        try:
            # Mock der Konfiguration
            with patch.object(self.generator, "layout_config") as mock_layout:
                mock_layout.get.return_value = [
                    {"name": "DPS", "type": "MODULE", "module_serial": "SVR4H73275"},
                    {"name": "HBW", "type": "MODULE", "module_serial": "SVR3QA0022"},
                ]

                with patch.object(self.generator, "get_route") as mock_get_route:
                    # Test für gültige Route
                    mock_get_route.return_value = {
                        "from": "DPS",
                        "to": "HBW",
                        "mqtt_via": ["2", "1"],
                        "intersection_actions": [
                            {"intersection": "Intersection2", "mqtt_id": "2", "action": "PASS"},
                            {"intersection": "Intersection1", "mqtt_id": "1", "action": "PASS"},
                        ],
                    }

                    is_valid = self.generator.validate_route("DPS_HBW")
                    self.assertTrue(is_valid, "Gültige Route sollte validiert werden")

                    # Test für ungültige Route
                    mock_get_route.return_value = None
                    is_valid = self.generator.validate_route("INVALID_ROUTE")
                    self.assertFalse(is_valid, "Ungültige Route sollte nicht validiert werden")

            print("✅ Validate Route: OK")
        except Exception as e:
            self.fail(f"❌ Validate Route failed: {e}")

    def test_get_available_routes(self):
        """Test: Verfügbare Routen können abgerufen werden"""
        try:
            # Mock der Konfiguration
            with patch.object(self.generator, "routes_config") as mock_config:
                mock_config.get.return_value = {
                    "DPS_HBW": {"route_id": "DPS_HBW"},
                    "HBW_DRILL": {"route_id": "HBW_DRILL"},
                    "MILL_AIQS": {"route_id": "MILL_AIQS"},
                }

                routes = self.generator.get_available_routes()
                self.assertIsInstance(routes, list, "Routen sollten eine Liste sein")
                self.assertGreater(len(routes), 0, "Routen sollten vorhanden sein")
                self.assertIn("DPS_HBW", routes, "DPS_HBW sollte in Routen enthalten sein")

            print("✅ Get Available Routes: OK")
        except Exception as e:
            self.fail(f"❌ Get Available Routes failed: {e}")

    def test_get_tested_routes(self):
        """Test: Getestete Routen können abgerufen werden"""
        try:
            # Mock der Konfiguration
            with patch.object(self.generator, "routes_config") as mock_config:
                mock_config.get.return_value = {
                    "DPS_HBW": {"route_id": "DPS_HBW", "tested": True},
                    "HBW_DRILL": {"route_id": "HBW_DRILL", "tested": False},
                    "MILL_AIQS": {"route_id": "MILL_AIQS", "tested": True},
                }

                tested_routes = self.generator.get_tested_routes()
                self.assertIsInstance(tested_routes, list, "Getestete Routen sollten eine Liste sein")
                self.assertIn("DPS_HBW", tested_routes, "DPS_HBW sollte in getesteten Routen enthalten sein")
                self.assertIn("MILL_AIQS", tested_routes, "MILL_AIQS sollte in getesteten Routen enthalten sein")
                self.assertNotIn(
                    "HBW_DRILL", tested_routes, "HBW_DRILL sollte nicht in getesteten Routen enthalten sein"
                )

            print("✅ Get Tested Routes: OK")
        except Exception as e:
            self.fail(f"❌ Get Tested Routes failed: {e}")


class TestFTSRouteGeneratorIntegration(unittest.TestCase):
    """Integration-Tests für FTS Route Generator"""

    def test_dps_to_hbw_message_structure(self):
        """Test: DPS → HBW Message-Struktur entspricht getesteter FTS-Order"""
        try:
            from omf.tools.fts_route_generator import FTSRouteGenerator

            # Mock der Konfiguration
            with patch.object(FTSRouteGenerator, "_load_routes_config") as mock_routes:
                with patch.object(FTSRouteGenerator, "_load_layout_config") as mock_layout:
                    mock_routes.return_value = {
                        "routes": {
                            "DPS_HBW": {
                                "route_id": "DPS_HBW",
                                "from": "DPS",
                                "to": "HBW",
                                "mqtt_via": ["2", "1"],
                                "intersection_actions": [
                                    {"intersection": "Intersection2", "mqtt_id": "2", "action": "PASS"},
                                    {"intersection": "Intersection1", "mqtt_id": "1", "action": "PASS"},
                                ],
                            }
                        }
                    }

                    mock_layout.return_value = {
                        "positions": [
                            {"name": "DPS", "type": "MODULE", "module_serial": "SVR4H73275"},
                            {"name": "HBW", "type": "MODULE", "module_serial": "SVR3QA0022"},
                        ]
                    }

                    generator = FTSRouteGenerator()
                    fts_message = generator.generate_fts_message("DPS_HBW")

                    # Prüfe Message-Struktur
                    self.assertIsNotNone(fts_message, "FTS-Message sollte generiert werden")

                    # Prüfe erforderliche Felder
                    required_fields = ["timestamp", "orderId", "orderUpdateId", "nodes", "edges", "serialNumber"]
                    for field in required_fields:
                        self.assertIn(field, fts_message, f"FTS-Message sollte {field} enthalten")

                    # Prüfe Nodes-Struktur
                    nodes = fts_message["nodes"]
                    self.assertGreaterEqual(len(nodes), 3, "Sollte mindestens 3 Nodes haben (Start, Kreuzungen, Ende)")

                    # Prüfe Edges-Struktur
                    edges = fts_message["edges"]
                    self.assertGreaterEqual(len(edges), 2, "Sollte mindestens 2 Edges haben")

                    # Prüfe Serial Number
                    self.assertEqual(fts_message["serialNumber"], "5iO4", "Serial Number sollte korrekt sein")

            print("✅ DPS to HBW Message Structure: OK")
        except Exception as e:
            self.fail(f"❌ DPS to HBW Message Structure failed: {e}")


if __name__ == "__main__":
    print("🧪 Running FTS Route Generator Tests...")
    print("=" * 60)

    # Test-Klassen ausführen
    test_classes = [TestFTSRouteGenerator, TestFTSRouteGeneratorIntegration]

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
    print("🎉 FTS Route Generator Tests completed!")
