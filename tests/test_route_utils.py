#!/usr/bin/env python3
"""
Unit tests for Route Utils START node handling

Tests cover:
- START node selection when FTS location is unknown (uses nearest intersection to goal)
- Empty graph and no intersection handling
- Normal routing when START node exists
"""


from omf2.ui.ccu.common.route_utils import build_graph, compute_route


class TestStartNodeHandling:
    """Test cases for START node handling behavior"""

    def test_unknown_start_uses_nearest_intersection_to_goal(self):
        """Test using nearest intersection to goal when START node is unknown"""
        # Create a graph with multiple intersections at different distances from goal
        shopfloor_layout = {
            "modules": [
                {"id": "GOAL", "serialNumber": "SN_GOAL", "position": [0, 0], "type": "storage"},
                {"id": "MODULE_B", "serialNumber": "SN_B", "position": [2, 2], "type": "machine"},
            ],
            "intersections": [
                {"id": "1", "position": [0, 1]},  # Close to goal (distance 1)
                {"id": "2", "position": [3, 3]},  # Far from goal
                {"id": "3", "position": [1, 0]},  # Also close to goal (distance 1)
            ],
            "roads": [
                {"from": "1", "to": "SN_GOAL"},
                {"from": "2", "to": "SN_B"},
                {"from": "3", "to": "SN_GOAL"},
                {"from": "1", "to": "3"},
            ],
        }

        graph = build_graph(shopfloor_layout)

        # Request with unknown START node - should use nearest intersection to goal
        unknown_start = "UNKNOWN_FTS_LOCATION"
        goal = "GOAL"

        route = compute_route(graph, unknown_start, goal)

        # Should return a route (nearest intersection selected)
        assert route is not None, "Route should not be None when intersections exist"
        # Route should start from an intersection (either 1 or 3, both closest to goal)
        assert route[0] in ["1", "3"], f"Route should start from intersection closest to goal, got {route[0]}"
        # The route should end at the goal
        assert route[-1] == "SN_GOAL", "Route should end at goal"

    def test_no_intersections_returns_none(self):
        """Test that no intersections returns None with clear warning"""
        # Create a graph without intersections
        shopfloor_layout = {
            "modules": [
                {"id": "MODULE_A", "serialNumber": "SN_A", "position": [0, 0], "type": "storage"},
                {"id": "MODULE_B", "serialNumber": "SN_B", "position": [0, 1], "type": "machine"},
            ],
            "intersections": [],
            "roads": [
                {"from": "SN_A", "to": "SN_B"},
            ],
        }

        graph = build_graph(shopfloor_layout)

        # Request with unknown START - should return None (no intersections)
        route = compute_route(graph, "UNKNOWN_START", "SN_B")

        # Should return None since there are no intersections
        assert route is None, "Route should be None when no intersections available"

    def test_empty_graph_returns_none(self):
        """Test that empty graph returns None with clear warning"""
        # Create an empty graph
        shopfloor_layout = {
            "modules": [],
            "intersections": [],
            "roads": [],
        }

        graph = build_graph(shopfloor_layout)

        # Request routing with empty graph
        route = compute_route(graph, "START", "GOAL")

        # Should return None since there are no nodes
        assert route is None, "Route should be None when graph is empty"

    def test_normal_routing_with_valid_start_node(self):
        """Test normal routing when START node exists"""
        # Create a graph with valid START node
        shopfloor_layout = {
            "modules": [
                {"id": "START", "serialNumber": "SN_START", "position": [0, 0], "type": "storage"},
                {"id": "GOAL", "serialNumber": "SN_GOAL", "position": [0, 1], "type": "machine"},
            ],
            "intersections": [],
            "roads": [
                {"from": "SN_START", "to": "SN_GOAL"},
            ],
        }

        graph = build_graph(shopfloor_layout)

        # Request routing with valid START node
        route = compute_route(graph, "START", "GOAL")

        # Should return a valid route
        assert route is not None, "Route should not be None with valid nodes"
        assert len(route) == 2, "Route should have 2 nodes"
        assert route[0] == "SN_START", "Route should start at START node"
        assert route[-1] == "SN_GOAL", "Route should end at GOAL node"

    def test_nearest_intersection_reaches_goal(self):
        """Test that nearest intersection to goal can successfully reach the goal"""
        # Create a connected graph with intersections at different distances
        shopfloor_layout = {
            "modules": [
                {"id": "A", "serialNumber": "SN_A", "position": [0, 0], "type": "storage"},
                {"id": "C", "serialNumber": "SN_C", "position": [0, 3], "type": "machine"},
            ],
            "intersections": [
                {"id": "1", "position": [0, 1]},  # Closer to C
                {"id": "2", "position": [1, 0]},  # Farther from C
            ],
            "roads": [
                {"from": "SN_A", "to": "1"},
                {"from": "SN_A", "to": "2"},
                {"from": "1", "to": "SN_C"},
                {"from": "2", "to": "1"},
            ],
        }

        graph = build_graph(shopfloor_layout)

        # Request with unknown START location with valid GOAL
        route = compute_route(graph, "UNKNOWN_START", "SN_C")

        # Should return a route (nearest intersection selected and route found)
        assert route is not None, "Route should not be None when graph is connected"
        # Route should start from intersection 1 (closest to SN_C)
        assert route[0] == "1", f"Route should start from nearest intersection to goal, got {route[0]}"
        # Route should end at the goal
        assert route[-1] == "SN_C", "Route should end at goal SN_C"

    def test_production_order_uses_intersection_2(self):
        """Test that PRODUCTION orders start at intersection 2"""
        # Create a graph with intersections 1 and 2
        shopfloor_layout = {
            "modules": [
                {"id": "HBW", "serialNumber": "SN_HBW", "position": [0, 0], "type": "storage"},
                {"id": "DPS", "serialNumber": "SN_DPS", "position": [3, 3], "type": "storage"},
            ],
            "intersections": [
                {"id": "1", "position": [0, 1]},
                {"id": "2", "position": [1, 0]},
            ],
            "roads": [
                {"from": "1", "to": "SN_DPS"},
                {"from": "2", "to": "SN_HBW"},
                {"from": "1", "to": "2"},
            ],
        }

        graph = build_graph(shopfloor_layout)

        # Request with unknown START for PRODUCTION order
        route = compute_route(graph, "UNKNOWN_START", "HBW", order_type="PRODUCTION")

        # Should return a route starting at intersection 2
        assert route is not None, "Route should not be None for PRODUCTION order"
        assert route[0] == "2", f"PRODUCTION order should start at intersection 2, got {route[0]}"
        assert route[-1] == "SN_HBW", "Route should end at HBW"

    def test_storage_order_uses_intersection_1(self):
        """Test that STORAGE orders start at intersection 1"""
        # Create a graph with intersections 1 and 2
        shopfloor_layout = {
            "modules": [
                {"id": "HBW", "serialNumber": "SN_HBW", "position": [0, 0], "type": "storage"},
                {"id": "DPS", "serialNumber": "SN_DPS", "position": [3, 3], "type": "storage"},
            ],
            "intersections": [
                {"id": "1", "position": [0, 1]},
                {"id": "2", "position": [1, 0]},
            ],
            "roads": [
                {"from": "1", "to": "SN_DPS"},
                {"from": "2", "to": "SN_HBW"},
                {"from": "1", "to": "2"},
            ],
        }

        graph = build_graph(shopfloor_layout)

        # Request with unknown START for STORAGE order
        route = compute_route(graph, "UNKNOWN_START", "DPS", order_type="STORAGE")

        # Should return a route starting at intersection 1
        assert route is not None, "Route should not be None for STORAGE order"
        assert route[0] == "1", f"STORAGE order should start at intersection 1, got {route[0]}"
        assert route[-1] == "SN_DPS", "Route should end at DPS"
