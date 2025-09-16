#!/usr/bin/env python3
"""
Test für FTS MQTT-Message-Generierung
Vergleicht generierte Messages mit getesteten FTS-Orders
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestFTSMessageGeneration(unittest.TestCase):
    """Test-Klasse für FTS MQTT-Message-Generierung"""

    def setUp(self):
        """Setup für Tests"""
        from omf.tools.fts_route_generator import FTSRouteGenerator

        self.generator = FTSRouteGenerator()

    def test_dps_to_hbw_message_generation(self):
        """Test: DPS → HBW Message-Generierung entspricht getesteter FTS-Order"""
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

                    # Prüfe Message-Struktur
                    self.assertIsNotNone(fts_message, "FTS-Message sollte generiert werden")

                    # Prüfe erforderliche Felder
                    self.assertIn("timestamp", fts_message, "FTS-Message sollte timestamp enthalten")
                    self.assertIn("orderId", fts_message, "FTS-Message sollte orderId enthalten")
                    self.assertIn("orderUpdateId", fts_message, "FTS-Message sollte orderUpdateId enthalten")
                    self.assertIn("nodes", fts_message, "FTS-Message sollte nodes enthalten")
                    self.assertIn("edges", fts_message, "FTS-Message sollte edges enthalten")
                    self.assertIn("serialNumber", fts_message, "FTS-Message sollte serialNumber enthalten")

                    # Prüfe Serial Number
                    self.assertEqual(fts_message["serialNumber"], "5iO4", "Serial Number sollte korrekt sein")

                    # Prüfe Nodes
                    nodes = fts_message["nodes"]
                    self.assertGreaterEqual(len(nodes), 3, "Sollte mindestens 3 Nodes haben")

                    # Prüfe Start-Node (DPS)
                    start_node = nodes[0]
                    self.assertEqual(start_node["id"], "SVR4H73275", "Start-Node sollte DPS Serial haben")

                    # Prüfe Kreuzungspunkt-Nodes
                    intersection_nodes = nodes[1:-1]
                    self.assertEqual(len(intersection_nodes), 2, "Sollte 2 Kreuzungspunkt-Nodes haben")

                    # Prüfe erste Kreuzung (2)
                    intersection_2 = intersection_nodes[0]
                    self.assertEqual(intersection_2["id"], "2", "Erste Kreuzung sollte ID '2' haben")
                    self.assertEqual(
                        intersection_2["action"]["type"], "PASS", "Erste Kreuzung sollte PASS action haben"
                    )

                    # Prüfe zweite Kreuzung (1)
                    intersection_1 = intersection_nodes[1]
                    self.assertEqual(intersection_1["id"], "1", "Zweite Kreuzung sollte ID '1' haben")
                    self.assertEqual(
                        intersection_1["action"]["type"], "PASS", "Zweite Kreuzung sollte PASS action haben"
                    )

                    # Prüfe End-Node (HBW)
                    end_node = nodes[-1]
                    self.assertEqual(end_node["id"], "SVR3QA0022", "End-Node sollte HBW Serial haben")
                    self.assertEqual(end_node["action"]["type"], "DOCK", "End-Node sollte DOCK action haben")

                    # Prüfe Edges
                    edges = fts_message["edges"]
                    self.assertGreaterEqual(len(edges), 2, "Sollte mindestens 2 Edges haben")

                    # Prüfe Edge-Struktur
                    for edge in edges:
                        self.assertIn("id", edge, "Edge sollte ID haben")
                        self.assertIn("length", edge, "Edge sollte length haben")
                        self.assertIn("linkedNodes", edge, "Edge sollte linkedNodes haben")
                        self.assertEqual(len(edge["linkedNodes"]), 2, "Edge sollte 2 linkedNodes haben")

            print("✅ DPS to HBW Message Generation: OK")
        except Exception as e:
            self.fail(f"❌ DPS to HBW Message Generation failed: {e}")

    def test_message_structure_comparison(self):
        """Test: Generierte Message-Struktur entspricht getesteter FTS-Order"""
        try:
            # Getestete FTS-Order (aus Dokumentation)
            expected_structure = {
                "timestamp": "2025-01-19T10:00:00.000Z",
                "orderId": "test-navigation-dps-to-hbw-wareneingang-001",
                "orderUpdateId": 0,
                "nodes": [
                    {"id": "SVR4H73275", "linkedEdges": ["SVR4H73275-2"]},
                    {
                        "id": "2",
                        "linkedEdges": ["SVR4H73275-2", "2-1"],
                        "action": {"id": "pass-through-2-001", "type": "PASS"},
                    },
                    {
                        "id": "1",
                        "linkedEdges": ["2-1", "1-SVR3QA0022"],
                        "action": {"id": "pass-through-1-001", "type": "PASS"},
                    },
                    {
                        "id": "SVR3QA0022",
                        "linkedEdges": ["1-SVR3QA0022"],
                        "action": {
                            "type": "DOCK",
                            "id": "dock-at-hbw-wareneingang-001",
                            "metadata": {"loadId": "04798eca341290", "loadType": "WHITE", "loadPosition": "1"},
                        },
                    },
                ],
                "edges": [
                    {"id": "SVR4H73275-2", "length": 380, "linkedNodes": ["SVR4H73275", "2"]},
                    {"id": "2-1", "length": 360, "linkedNodes": ["2", "1"]},
                    {"id": "1-SVR3QA0022", "length": 380, "linkedNodes": ["1", "SVR3QA0022"]},
                ],
                "serialNumber": "5iO4",
            }

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

                    # Prüfe Struktur-Ähnlichkeit
                    self.assertEqual(
                        len(fts_message["nodes"]),
                        len(expected_structure["nodes"]),
                        "Anzahl Nodes sollte übereinstimmen",
                    )
                    self.assertEqual(
                        len(fts_message["edges"]),
                        len(expected_structure["edges"]),
                        "Anzahl Edges sollte übereinstimmen",
                    )

                    # Prüfe Node-IDs
                    generated_node_ids = [node["id"] for node in fts_message["nodes"]]
                    expected_node_ids = [node["id"] for node in expected_structure["nodes"]]
                    self.assertEqual(generated_node_ids, expected_node_ids, "Node-IDs sollten übereinstimmen")

                    # Prüfe Edge-IDs
                    generated_edge_ids = [edge["id"] for edge in fts_message["edges"]]
                    expected_edge_ids = [edge["id"] for edge in expected_structure["edges"]]
                    self.assertEqual(generated_edge_ids, expected_edge_ids, "Edge-IDs sollten übereinstimmen")

                    # Prüfe Serial Number
                    self.assertEqual(
                        fts_message["serialNumber"],
                        expected_structure["serialNumber"],
                        "Serial Number sollte übereinstimmen",
                    )

            print("✅ Message Structure Comparison: OK")
        except Exception as e:
            self.fail(f"❌ Message Structure Comparison failed: {e}")

    def test_custom_order_id_generation(self):
        """Test: Benutzerdefinierte Order-ID wird korrekt verwendet"""
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

                    # Test mit benutzerdefinierter Order-ID
                    custom_order_id = "test-navigation-dps-to-hbw-wareneingang-001"
                    fts_message = self.generator.generate_fts_message("DPS_HBW", order_id=custom_order_id)

                    self.assertEqual(fts_message["orderId"], custom_order_id, "Order-ID sollte korrekt sein")

                    # Test mit benutzerdefiniertem OrderUpdateId
                    custom_update_id = 5
                    fts_message = self.generator.generate_fts_message("DPS_HBW", order_update_id=custom_update_id)

                    self.assertEqual(
                        fts_message["orderUpdateId"], custom_update_id, "OrderUpdateId sollte korrekt sein"
                    )

            print("✅ Custom Order ID Generation: OK")
        except Exception as e:
            self.fail(f"❌ Custom Order ID Generation failed: {e}")

    def test_json_serialization(self):
        """Test: FTS-Message kann zu JSON serialisiert werden"""
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

                    # Test JSON-Serialisierung
                    import json

                    json_string = json.dumps(fts_message, indent=2)
                    self.assertIsInstance(json_string, str, "JSON-String sollte generiert werden")

                    # Test JSON-Deserialisierung
                    parsed_message = json.loads(json_string)
                    self.assertEqual(
                        parsed_message["serialNumber"],
                        "5iO4",
                        "Serial Number sollte nach JSON-Serialisierung korrekt sein",
                    )
                    self.assertIn("nodes", parsed_message, "Nodes sollten nach JSON-Serialisierung vorhanden sein")
                    self.assertIn("edges", parsed_message, "Edges sollten nach JSON-Serialisierung vorhanden sein")

            print("✅ JSON Serialization: OK")
        except Exception as e:
            self.fail(f"❌ JSON Serialization failed: {e}")


if __name__ == "__main__":
    print("🧪 Running FTS Message Generation Tests...")
    print("=" * 60)

    # Test-Klasse ausführen
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFTSMessageGeneration)
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)

    if result.wasSuccessful():
        print("✅ TestFTSMessageGeneration: ALL TESTS PASSED")
    else:
        print(f"❌ TestFTSMessageGeneration: {len(result.failures)} FAILURES, {len(result.errors)} ERRORS")

    print("\n" + "=" * 60)
    print("🎉 FTS Message Generation Tests completed!")
