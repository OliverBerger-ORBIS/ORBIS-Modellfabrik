#!/usr/bin/env python3
"""
Tests for Route Utilities (AGV Routing)
"""

import json
from pathlib import Path

from omf2.ui.ccu.common.route_utils import (
    build_graph,
    compute_route,
    point_on_polyline,
    route_segments_to_points,
)


class TestGraphBuilding:
    """Test cases for graph building from shopfloor layout"""

    def test_build_graph_with_real_config(self):
        """Test that build_graph works with real shopfloor_layout.json"""
        # Load real config
        config_path = Path(__file__).parent.parent.parent / "omf2" / "config" / "ccu" / "shopfloor_layout.json"
        with open(config_path, "r") as f:
            layout = json.load(f)

        graph = build_graph(layout)

        # Check nodes
        assert "nodes" in graph
        assert "adjacency" in graph
        assert "id_to_primary" in graph
        assert len(graph["nodes"]) > 0

        # Check that modules are nodes
        assert "SVR3QA2098" in graph["nodes"]  # MILL
        assert "SVR4H76530" in graph["nodes"]  # AIQS

        # Check that intersections are nodes
        assert "1" in graph["nodes"]
        assert "2" in graph["nodes"]

    def test_build_graph_id_to_primary_mapping(self):
        """Test that build_graph creates id_to_primary mapping for both id and serialNumber"""
        # Load real config
        config_path = Path(__file__).parent.parent.parent / "omf2" / "config" / "ccu" / "shopfloor_layout.json"
        with open(config_path, "r") as f:
            layout = json.load(f)

        graph = build_graph(layout)

        # Check id_to_primary mapping exists
        assert "id_to_primary" in graph
        id_to_primary = graph["id_to_primary"]

        # Both module id and serialNumber should map to the same primary key
        assert "MILL" in id_to_primary
        assert "SVR3QA2098" in id_to_primary
        assert id_to_primary["MILL"] == "SVR3QA2098"
        assert id_to_primary["SVR3QA2098"] == "SVR3QA2098"

        # Check DPS
        assert "DPS" in id_to_primary
        assert "SVR4H73275" in id_to_primary
        assert id_to_primary["DPS"] == "SVR4H73275"

        # Check HBW
        assert "HBW" in id_to_primary
        assert "SVR3QA0022" in id_to_primary
        assert id_to_primary["HBW"] == "SVR3QA0022"

    def test_build_graph_creates_adjacency(self):
        """Test that build_graph creates proper adjacency list"""
        layout = {
            "modules": [
                {"id": "MOD1", "serialNumber": "SN1", "position": [0, 0]},
                {"id": "MOD2", "serialNumber": "SN2", "position": [0, 1]},
            ],
            "intersections": [{"id": "I1", "position": [1, 0]}],
            "roads": [
                {"from": "SN1", "to": "I1"},
                {"from": "I1", "to": "SN2"},
            ],
        }

        graph = build_graph(layout)

        # Check adjacency
        assert "SN1" in graph["adjacency"]["I1"]
        assert "I1" in graph["adjacency"]["SN1"]
        assert "SN2" in graph["adjacency"]["I1"]
        assert "I1" in graph["adjacency"]["SN2"]


class TestRouteComputation:
    """Test cases for route computation using BFS"""

    def test_compute_route_with_real_config(self):
        """Test route computation with real config"""
        # Load real config
        config_path = Path(__file__).parent.parent.parent / "omf2" / "config" / "ccu" / "shopfloor_layout.json"
        with open(config_path, "r") as f:
            layout = json.load(f)

        graph = build_graph(layout)

        # Test route from MILL to AIQS
        route = compute_route(graph, "SVR3QA2098", "SVR4H76530")

        assert route is not None
        assert len(route) >= 2
        assert route[0] == "SVR3QA2098"
        assert route[-1] == "SVR4H76530"

    def test_compute_route_with_module_ids(self):
        """Test route computation using module ids instead of serialNumbers"""
        # Load real config
        config_path = Path(__file__).parent.parent.parent / "omf2" / "config" / "ccu" / "shopfloor_layout.json"
        with open(config_path, "r") as f:
            layout = json.load(f)

        graph = build_graph(layout)

        # Test route using module ids (DPS to HBW)
        route = compute_route(graph, "DPS", "HBW")

        assert route is not None
        assert len(route) >= 2
        # Route should use primary keys (serialNumbers)
        assert route[0] == "SVR4H73275"  # DPS serialNumber
        assert route[-1] == "SVR3QA0022"  # HBW serialNumber

    def test_compute_route_mixed_id_and_serial(self):
        """Test route computation with mixed id and serialNumber"""
        # Load real config
        config_path = Path(__file__).parent.parent.parent / "omf2" / "config" / "ccu" / "shopfloor_layout.json"
        with open(config_path, "r") as f:
            layout = json.load(f)

        graph = build_graph(layout)

        # Test route using module id for start and serialNumber for goal
        route = compute_route(graph, "MILL", "SVR4H76530")

        assert route is not None
        assert len(route) >= 2
        assert route[0] == "SVR3QA2098"  # MILL serialNumber
        assert route[-1] == "SVR4H76530"  # AIQS serialNumber

    def test_compute_route_same_node(self):
        """Test that route from node to itself is trivial"""
        layout = {
            "modules": [{"id": "MOD1", "serialNumber": "SN1", "position": [0, 0]}],
            "intersections": [],
            "roads": [],
        }

        graph = build_graph(layout)
        route = compute_route(graph, "SN1", "SN1")

        assert route == ["SN1"]

    def test_compute_route_same_node_using_id(self):
        """Test that route from node to itself works with module id"""
        layout = {
            "modules": [{"id": "MOD1", "serialNumber": "SN1", "position": [0, 0]}],
            "intersections": [],
            "roads": [],
        }

        graph = build_graph(layout)
        route = compute_route(graph, "MOD1", "MOD1")

        assert route == ["SN1"]  # Returns primary key

    def test_compute_route_no_path(self):
        """Test that compute_route returns None when no path exists"""
        layout = {
            "modules": [
                {"id": "MOD1", "serialNumber": "SN1", "position": [0, 0]},
                {"id": "MOD2", "serialNumber": "SN2", "position": [0, 1]},
            ],
            "intersections": [],
            "roads": [],  # No roads = no path
        }

        graph = build_graph(layout)
        route = compute_route(graph, "SN1", "SN2")

        assert route is None

    def test_compute_route_invalid_start(self):
        """Test that compute_route handles invalid start node gracefully"""
        layout = {
            "modules": [{"id": "MOD1", "serialNumber": "SN1", "position": [0, 0]}],
            "intersections": [],
            "roads": [],
        }

        graph = build_graph(layout)
        route = compute_route(graph, "INVALID", "SN1")

        assert route is None

    def test_compute_route_invalid_goal(self):
        """Test that compute_route handles invalid goal node gracefully"""
        layout = {
            "modules": [{"id": "MOD1", "serialNumber": "SN1", "position": [0, 0]}],
            "intersections": [],
            "roads": [],
        }

        graph = build_graph(layout)
        route = compute_route(graph, "SN1", "INVALID")

        assert route is None


class TestRouteToPoints:
    """Test cases for converting routes to pixel coordinates"""

    def test_route_segments_to_points(self):
        """Test conversion of route to pixel points"""
        layout = {
            "modules": [
                {"id": "MOD1", "serialNumber": "SN1", "position": [0, 0]},
                {"id": "MOD2", "serialNumber": "SN2", "position": [0, 2]},
            ],
            "intersections": [{"id": "I1", "position": [0, 1]}],
            "roads": [
                {"from": "SN1", "to": "I1"},
                {"from": "I1", "to": "SN2"},
            ],
        }

        graph = build_graph(layout)
        route = compute_route(graph, "SN1", "SN2")

        points = route_segments_to_points(route, graph, cell_size=200)

        assert len(points) == 3  # Start edge, intersection center, end edge
        assert all(isinstance(p, tuple) and len(p) == 2 for p in points)

    def test_route_segments_to_points_empty_route(self):
        """Test that empty route returns empty points"""
        graph = {"nodes": {}, "adjacency": {}}
        points = route_segments_to_points([], graph, cell_size=200)

        assert points == []


class TestPointOnPolyline:
    """Test cases for calculating points on polylines"""

    def test_point_on_polyline_at_start(self):
        """Test point at start of polyline (progress=0)"""
        points = [(0, 0), (100, 0), (100, 100)]
        point = point_on_polyline(points, 0.0)

        assert point == (0, 0)

    def test_point_on_polyline_at_end(self):
        """Test point at end of polyline (progress=1)"""
        points = [(0, 0), (100, 0), (100, 100)]
        point = point_on_polyline(points, 1.0)

        assert point == (100, 100)

    def test_point_on_polyline_at_middle(self):
        """Test point at middle of polyline (progress=0.5)"""
        points = [(0, 0), (100, 0), (100, 100)]
        point = point_on_polyline(points, 0.5)

        # Should be at or near the midpoint of the polyline
        assert point is not None
        assert isinstance(point, tuple)
        assert len(point) == 2

    def test_point_on_polyline_empty_returns_none(self):
        """Test that empty polyline returns None"""
        points = []
        point = point_on_polyline(points, 0.5)

        assert point is None

    def test_point_on_polyline_single_point_returns_none(self):
        """Test that single point returns None"""
        points = [(0, 0)]
        point = point_on_polyline(points, 0.5)

        assert point is None

    def test_point_on_polyline_clamps_progress(self):
        """Test that progress values outside [0, 1] are clamped"""
        points = [(0, 0), (100, 0)]

        # Progress > 1 should be clamped to 1
        point = point_on_polyline(points, 1.5)
        assert point == (100, 0)

        # Progress < 0 should be clamped to 0
        point = point_on_polyline(points, -0.5)
        assert point == (0, 0)
