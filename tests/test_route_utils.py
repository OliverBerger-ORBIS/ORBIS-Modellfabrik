#!/usr/bin/env python3
"""
Unit tests for Route Utils START node fallback handling

Tests cover:
- START node fallback when configured START node is missing
- Empty graph handling (returns None with warning)
- Normal routing when START node exists
"""


from omf2.ui.ccu.common.route_utils import build_graph, compute_route


class TestStartNodeFallback:
    """Test cases for START node fallback behavior"""

    def test_start_node_fallback_to_first_node(self):
        """Test fallback to first available node when START node is missing"""
        # Create a minimal graph with nodes but missing the requested START node
        shopfloor_layout = {
            "modules": [
                {"id": "MODULE_A", "serialNumber": "SN_A", "position": [0, 0], "type": "storage"},
                {"id": "MODULE_B", "serialNumber": "SN_B", "position": [0, 1], "type": "machine"},
            ],
            "intersections": [{"id": "1", "position": [0, 2]}],
            "roads": [
                {"from": "SN_A", "to": "SN_B"},
                {"from": "SN_B", "to": "1"},
            ],
        }

        graph = build_graph(shopfloor_layout)

        # Request a START node that doesn't exist - should fallback to first node
        missing_start = "NONEXISTENT_START"
        goal = "SN_B"

        route = compute_route(graph, missing_start, goal)

        # Should return a route (fallback occurred)
        assert route is not None, "Route should not be None when fallback is possible"
        # Route should start from a fallback node (first available node)
        assert len(route) > 0, "Route should have at least one node"
        # The route should end at the goal
        assert route[-1] == goal, f"Route should end at goal {goal}"

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

    def test_fallback_selects_reachable_node(self):
        """Test that fallback node can reach the goal"""
        # Create a connected graph
        shopfloor_layout = {
            "modules": [
                {"id": "A", "serialNumber": "SN_A", "position": [0, 0], "type": "storage"},
                {"id": "B", "serialNumber": "SN_B", "position": [0, 1], "type": "machine"},
                {"id": "C", "serialNumber": "SN_C", "position": [0, 2], "type": "machine"},
            ],
            "intersections": [{"id": "1", "position": [1, 0]}],
            "roads": [
                {"from": "SN_A", "to": "1"},
                {"from": "1", "to": "SN_B"},
                {"from": "SN_B", "to": "SN_C"},
            ],
        }

        graph = build_graph(shopfloor_layout)

        # Request a missing START node with valid GOAL
        route = compute_route(graph, "MISSING_START", "SN_C")

        # Should return a route (fallback occurred and route found)
        assert route is not None, "Route should not be None when fallback is possible"
        # Route should end at the goal
        assert route[-1] == "SN_C", "Route should end at goal SN_C"
