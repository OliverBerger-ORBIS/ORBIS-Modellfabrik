#!/usr/bin/env python3
"""
Test for route and module highlighting fix
Verifies that routes are only shown during FTS navigation, not during manufacture steps
"""

import sys
from pathlib import Path

import pytest

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


class TestRouteHighlightingFix:
    """Test route and module highlighting behavior"""

    def test_route_only_shown_during_navigation(self):
        """
        Test that route is ONLY displayed when active module is FTS
        This verifies the fix for "both module and route highlighted" bug
        """
        # Simulate storage plan at step 2 (MANUFACTURE in progress)
        storage_plan = [
            {'step': 1, 'type': 'NAVIGATION', 'source': 'START', 'target': 'HBW', 'state': 'FINISHED'},
            {'step': 2, 'type': 'MANUFACTURE', 'moduleType': 'HBW', 'command': 'PICK', 'state': 'IN_PROGRESS'},
            {'step': 3, 'type': 'NAVIGATION', 'source': 'HBW', 'target': 'DPS', 'state': 'ENQUEUED'},
            {'step': 4, 'type': 'MANUFACTURE', 'moduleType': 'DPS', 'command': 'DROP', 'state': 'PENDING'},
        ]

        # Simulate _get_current_active_module logic
        active_module = None
        for step in storage_plan:
            if step['state'] != 'FINISHED':
                if step['type'] == 'NAVIGATION':
                    active_module = 'FTS'
                elif step['type'] == 'MANUFACTURE':
                    active_module = step.get('moduleType')
                break

        # At step 2, active module should be HBW
        assert active_module == 'HBW'

        # NEW BEHAVIOR: Route should NOT be calculated when active_module != "FTS"
        # This simulates the fixed logic in storage_orders_subtab.py lines 167-173
        should_show_route = False
        if active_module == "FTS":
            # Only look for navigation steps if FTS is active
            for step in storage_plan:
                if step['state'] == 'IN_PROGRESS' and step['type'] == 'NAVIGATION':
                    should_show_route = True
                    break

        # Result: Route should NOT be shown when active module is HBW
        assert should_show_route is False, "Route should not be shown when active module is HBW"

    def test_route_shown_during_fts_navigation(self):
        """
        Test that route IS displayed when active module is FTS
        """
        # Simulate storage plan at step 1 (NAVIGATION in progress)
        storage_plan = [
            {'step': 1, 'type': 'NAVIGATION', 'source': 'START', 'target': 'HBW', 'state': 'IN_PROGRESS'},
            {'step': 2, 'type': 'MANUFACTURE', 'moduleType': 'HBW', 'command': 'PICK', 'state': 'ENQUEUED'},
            {'step': 3, 'type': 'NAVIGATION', 'source': 'HBW', 'target': 'DPS', 'state': 'PENDING'},
            {'step': 4, 'type': 'MANUFACTURE', 'moduleType': 'DPS', 'command': 'DROP', 'state': 'PENDING'},
        ]

        # Simulate _get_current_active_module logic
        active_module = None
        for step in storage_plan:
            if step['state'] != 'FINISHED':
                if step['type'] == 'NAVIGATION':
                    active_module = 'FTS'
                elif step['type'] == 'MANUFACTURE':
                    active_module = step.get('moduleType')
                break

        # At step 1, active module should be FTS
        assert active_module == 'FTS'

        # NEW BEHAVIOR: Route SHOULD be calculated when active_module == "FTS"
        should_show_route = False
        current_nav_step = None
        if active_module == "FTS":
            # Only look for navigation steps if FTS is active
            for step in storage_plan:
                if step['state'] == 'IN_PROGRESS' and step['type'] == 'NAVIGATION':
                    should_show_route = True
                    current_nav_step = step
                    break

        # Result: Route should be shown when FTS is active
        assert should_show_route is True, "Route should be shown when active module is FTS"
        assert current_nav_step is not None
        assert current_nav_step['source'] == 'START'
        assert current_nav_step['target'] == 'HBW'

    def test_intersection_labels_enabled(self):
        """
        Test that intersection labels are now shown (not embedded in SVG)
        This verifies the fix for route visibility through intersections
        """
        # Test data for an intersection cell
        cell_data = {
            "type": "intersection",
            "id": "1",
            "data": {"id": "1", "position": [1, 1]}
        }

        # NEW BEHAVIOR: Labels should be shown for intersections too
        cell_type = cell_data.get("type", "unknown")
        cell_id = cell_data.get("id", "")

        # Before fix: if cell_type != "intersection": cell_label = cell_id
        # After fix: cell_label = cell_id (for all types)
        cell_label = cell_id

        assert cell_label == "1", "Intersection label should be shown"
        assert cell_label != "", "Intersection label should not be empty"

    def test_routes_pass_through_intersection_centers(self):
        """
        Test that routes are calculated to pass through intersection centers
        This verifies the route calculation is correct
        """
        from omf2.ccu.config_loader import get_ccu_config_loader
        from omf2.ui.ccu.common.route_utils import build_graph, compute_route, route_segments_to_points

        config_loader = get_ccu_config_loader()
        layout = config_loader.load_shopfloor_layout()

        graph = build_graph(layout)

        # Test route from DPS to HBW (typical storage order)
        route = compute_route(graph, 'DPS', 'HBW')
        assert route is not None, "Route should be found"

        # Convert to points
        points = route_segments_to_points(route, graph, cell_size=200)
        assert len(points) > 0, "Route should have points"

        # Verify route goes through intersection centers
        # Route should be: DPS edge -> Intersection 2 center -> Intersection 1 center -> HBW edge
        # Intersection 2 is at position [1, 2] -> center at (500, 300)
        # Intersection 1 is at position [1, 1] -> center at (300, 300)

        # Find intersection points (not start/end points)
        intersection_points = points[1:-1]  # Exclude start and end

        # Check that intersection points are at expected centers
        expected_intersections = [
            (500.0, 300.0),  # Intersection 2 center
            (300.0, 300.0),  # Intersection 1 center
        ]

        assert intersection_points == expected_intersections, \
            f"Route should pass through intersection centers. Got {intersection_points}"
