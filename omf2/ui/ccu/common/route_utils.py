#!/usr/bin/env python3
"""
Route Utilities for AGV/FTS Navigation
======================================

Provides graph building and pathfinding utilities for AGV routing visualization.

Functions:
- buildGraph(shopfloor_layout): Build graph from shopfloor_layout.json
- computeRoute(graph, startId, goalId): Compute route using BFS
- routeSegmentsToPoints(route_segments, cell_size): Convert route to pixel coordinates
- pointOnPolyline(polyline_points, progress): Get point on polyline based on progress
"""

from collections import deque
from typing import Dict, List, Optional, Tuple

from omf2.common.logger import get_logger

logger = get_logger(__name__)


def build_graph(shopfloor_layout: dict) -> Dict:
    """
    Build graph representation from shopfloor_layout.json

    Args:
        shopfloor_layout: Dictionary containing modules, intersections, and roads

    Returns:
        Dictionary with:
        - nodes: Dict mapping node IDs to node data {id, type, position}
        - adjacency: Dict mapping node IDs to list of connected node IDs
        - id_to_primary: Dict mapping both id and serialNumber to primary node key

    Example:
        graph = build_graph(layout_config)
        # graph['nodes'] = {'SVR3QA2098': {...}, '1': {...}, ...}
        # graph['id_to_primary'] = {'MILL': 'SVR3QA2098', 'SVR3QA2098': 'SVR3QA2098', ...}
        # graph['adjacency'] = {'SVR3QA2098': ['1'], '1': ['SVR3QA2098', '2'], ...}
    """
    nodes = {}
    adjacency = {}
    id_to_primary = {}  # Maps both id and serialNumber to primary node key

    # Add modules as nodes - index by both serialNumber and id
    for module in shopfloor_layout.get("modules", []):
        # Use serialNumber as primary key (used in roads)
        serial_number = module.get("serialNumber")
        module_id = module.get("id")

        # Primary key is serialNumber if available, otherwise id
        primary_key = serial_number or module_id

        if primary_key:
            nodes[primary_key] = {
                "id": primary_key,
                "type": "module",
                "position": module.get("position", [0, 0]),
                "moduleType": module.get("type"),
            }
            adjacency[primary_key] = []

            # Map both serialNumber and id to the primary key
            if serial_number:
                id_to_primary[serial_number] = primary_key
            if module_id and module_id != serial_number:
                id_to_primary[module_id] = primary_key

    # Add intersections as nodes
    for intersection in shopfloor_layout.get("intersections", []):
        node_id = intersection.get("id")
        if node_id:
            nodes[node_id] = {
                "id": node_id,
                "type": "intersection",
                "position": intersection.get("position", [0, 0]),
            }
            adjacency[node_id] = []
            id_to_primary[node_id] = node_id

    # Build adjacency list from roads
    for road in shopfloor_layout.get("roads", []):
        from_node = road.get("from")
        to_node = road.get("to")

        if from_node and to_node and from_node in nodes and to_node in nodes:
            # Add bidirectional edges (roads are traversable in both directions)
            if to_node not in adjacency[from_node]:
                adjacency[from_node].append(to_node)
            if from_node not in adjacency[to_node]:
                adjacency[to_node].append(from_node)

    logger.debug(f"Built graph with {len(nodes)} nodes and {sum(len(v) for v in adjacency.values()) // 2} edges")
    logger.debug(f"Graph supports {len(id_to_primary)} identifiers (id + serialNumber mappings)")

    return {
        "nodes": nodes,
        "adjacency": adjacency,
        "id_to_primary": id_to_primary,
    }


def _find_nearest_intersection_to_goal(graph: Dict, goal_id: str) -> Optional[str]:
    """
    Find the intersection closest to the goal node.

    Args:
        graph: Graph dictionary from build_graph()
        goal_id: Resolved goal node ID

    Returns:
        ID of the nearest intersection, or None if no intersections exist
    """
    nodes = graph.get("nodes", {})
    goal_node = nodes.get(goal_id)

    if not goal_node:
        return None

    goal_pos = goal_node.get("position", [0, 0])

    # Find all intersections
    intersections = [(node_id, node) for node_id, node in nodes.items() if node.get("type") == "intersection"]

    if not intersections:
        return None

    # Calculate distance to each intersection and find the nearest
    min_distance = float("inf")
    nearest_intersection = None

    for node_id, node in intersections:
        pos = node.get("position", [0, 0])
        # Euclidean distance
        distance = ((pos[0] - goal_pos[0]) ** 2 + (pos[1] - goal_pos[1]) ** 2) ** 0.5

        if distance < min_distance:
            min_distance = distance
            nearest_intersection = node_id

    return nearest_intersection


def compute_route(graph: Dict, start_id: str, goal_id: str) -> Optional[List[str]]:
    """
    Compute route from start to goal using BFS (Breadth-First Search)

    Supports flexible lookup: accepts both module id (e.g., "DPS") and serialNumber (e.g., "SVR4H73275")

    Args:
        graph: Graph dictionary from build_graph()
        start_id: Starting node ID (module id, serialNumber, or intersection ID)
        goal_id: Goal node ID (module id, serialNumber, or intersection ID)

    Returns:
        List of node IDs representing the route from start to goal, or None if no route found

    Example:
        route = compute_route(graph, "DPS", "HBW")  # Using module ids
        route = compute_route(graph, "SVR4H73275", "SVR3QA0022")  # Using serialNumbers
        # Both return route like: ["SVR4H73275", "2", "1", "SVR3QA0022"]
    """
    # Flexible lookup: resolve start_id and goal_id to primary keys
    id_to_primary = graph.get("id_to_primary", {})

    # Resolve goal node first (needed to find nearest intersection)
    resolved_goal = id_to_primary.get(goal_id, goal_id)
    if resolved_goal not in graph.get("nodes", {}):
        available_nodes = sorted(id_to_primary.keys())
        logger.warning(
            f"Goal node '{goal_id}' not found in graph. "
            f"Available identifiers ({len(available_nodes)}): {', '.join(available_nodes[:10])}"
            f"{'...' if len(available_nodes) > 10 else ''}"
        )
        return None

    # Resolve start node - if unknown, use nearest intersection to goal
    resolved_start = id_to_primary.get(start_id, start_id)
    if resolved_start not in graph.get("nodes", {}):
        # START node not specified or unknown - select nearest intersection to goal
        # This is normal when FTS location is unknown at order process start
        nearest_intersection = _find_nearest_intersection_to_goal(graph, resolved_goal)

        if nearest_intersection:
            resolved_start = nearest_intersection
            logger.debug(
                f"Start node '{start_id}' not in graph. " f"Using nearest intersection to goal: '{resolved_start}'"
            )
        else:
            # No intersections available - cannot proceed
            logger.warning(f"Cannot compute route: start node '{start_id}' not found and no intersections available.")
            return None

    if resolved_start == resolved_goal:
        return [resolved_start]

    # BFS implementation
    queue = deque([(resolved_start, [resolved_start])])
    visited = {resolved_start}

    while queue:
        current_id, path = queue.popleft()

        # Check all neighbors
        for neighbor_id in graph["adjacency"].get(current_id, []):
            if neighbor_id in visited:
                continue

            new_path = path + [neighbor_id]

            # Goal reached?
            if neighbor_id == resolved_goal:
                logger.debug(f"Route found: {' → '.join(new_path)}")
                return new_path

            visited.add(neighbor_id)
            queue.append((neighbor_id, new_path))

    logger.warning(
        f"No route found from {start_id} (resolved: {resolved_start}) to {goal_id} (resolved: {resolved_goal})"
    )
    return None


def route_segments_to_points(
    route: List[str], graph: Dict, cell_size: int = 200, grid_cols: int = 4, grid_rows: int = 3
) -> List[Tuple[float, float]]:
    """
    Convert route segments to pixel coordinates for SVG rendering

    Args:
        route: List of node IDs (from compute_route)
        graph: Graph dictionary from build_graph()
        cell_size: Size of each grid cell in pixels (default: 200)
        grid_cols: Number of grid columns (default: 4)
        grid_rows: Number of grid rows (default: 3)

    Returns:
        List of (x, y) tuples representing pixel coordinates for the route

    The route starts from the center of the adjacent edge of the start module,
    goes through intersection centers, and ends at the center of the target module's edge.
    """
    if not route or len(route) < 2:
        return []

    points = []

    for i in range(len(route)):
        node_id = route[i]
        node = graph["nodes"].get(node_id)

        if not node:
            logger.warning(f"Node {node_id} not found in graph")
            continue

        position = node.get("position", [0, 0])
        row, col = position[0], position[1]

        # Calculate center of cell
        center_x = col * cell_size + cell_size / 2
        center_y = row * cell_size + cell_size / 2

        if i == 0:
            # Start point: center of edge adjacent to next node
            if len(route) > 1:
                next_node = graph["nodes"].get(route[1])
                if next_node:
                    next_pos = next_node.get("position", [0, 0])
                    edge_point = _get_edge_center(row, col, next_pos[0], next_pos[1], cell_size)
                    points.append(edge_point)
                else:
                    points.append((center_x, center_y))
            else:
                points.append((center_x, center_y))

        elif i == len(route) - 1:
            # End point: center of edge adjacent to previous node
            prev_node = graph["nodes"].get(route[i - 1])
            if prev_node:
                prev_pos = prev_node.get("position", [0, 0])
                edge_point = _get_edge_center(row, col, prev_pos[0], prev_pos[1], cell_size)
                points.append(edge_point)
            else:
                points.append((center_x, center_y))

        else:
            # Intersection: use center
            points.append((center_x, center_y))

    logger.debug(f"Generated {len(points)} route points")
    return points


def _get_edge_center(row: int, col: int, neighbor_row: int, neighbor_col: int, cell_size: int) -> Tuple[float, float]:
    """
    Get the center point of the edge between a cell and its neighbor

    Args:
        row, col: Current cell position
        neighbor_row, neighbor_col: Neighbor cell position
        cell_size: Size of each grid cell in pixels

    Returns:
        (x, y) tuple of edge center coordinates
    """
    center_x = col * cell_size + cell_size / 2
    center_y = row * cell_size + cell_size / 2

    # Determine which edge to use based on neighbor position
    if neighbor_col < col:  # Neighbor to the left
        return (col * cell_size, center_y)
    elif neighbor_col > col:  # Neighbor to the right
        return ((col + 1) * cell_size, center_y)
    elif neighbor_row < row:  # Neighbor above
        return (center_x, row * cell_size)
    elif neighbor_row > row:  # Neighbor below
        return (center_x, (row + 1) * cell_size)
    else:
        # Same position (shouldn't happen)
        return (center_x, center_y)


def point_on_polyline(polyline_points: List[Tuple[float, float]], progress: float) -> Optional[Tuple[float, float]]:
    """
    Get a point on a polyline based on progress (0.0 to 1.0)

    Args:
        polyline_points: List of (x, y) points defining the polyline
        progress: Progress along the polyline (0.0 = start, 1.0 = end)

    Returns:
        (x, y) tuple of the point at the given progress, or None if invalid input

    Example:
        points = [(0, 0), (100, 0), (100, 100)]
        point = point_on_polyline(points, 0.5)  # Returns midpoint of polyline
    """
    if not polyline_points or len(polyline_points) < 2:
        return None

    # Clamp progress to [0, 1]
    progress = max(0.0, min(1.0, progress))

    # Calculate total length of polyline
    total_length = 0.0
    segment_lengths = []

    for i in range(len(polyline_points) - 1):
        x1, y1 = polyline_points[i]
        x2, y2 = polyline_points[i + 1]
        length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        segment_lengths.append(length)
        total_length += length

    if total_length == 0:
        return polyline_points[0]

    # Find target distance along polyline
    target_distance = progress * total_length

    # Find which segment contains the target point
    accumulated_distance = 0.0
    for i, segment_length in enumerate(segment_lengths):
        if accumulated_distance + segment_length >= target_distance:
            # Target is in this segment
            distance_in_segment = target_distance - accumulated_distance
            t = distance_in_segment / segment_length if segment_length > 0 else 0.0

            # Interpolate point in segment
            x1, y1 = polyline_points[i]
            x2, y2 = polyline_points[i + 1]
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)

            return (x, y)

        accumulated_distance += segment_length

    # Fallback: return last point
    return polyline_points[-1]


def get_route_for_navigation_step(
    shopfloor_layout: dict, source_id: str, target_id: str, cell_size: int = 200
) -> Optional[List[Tuple[float, float]]]:
    """
    Convenience function to get route points for a navigation step

    Args:
        shopfloor_layout: Dictionary containing modules, intersections, and roads
        source_id: Source module/intersection ID
        target_id: Target module/intersection ID
        cell_size: Size of each grid cell in pixels (default: 200)

    Returns:
        List of (x, y) pixel coordinates for the route, or None if no route found
    """
    # Build graph
    graph = build_graph(shopfloor_layout)

    # Compute route
    route = compute_route(graph, source_id, target_id)

    if not route:
        return None

    # Convert to points
    points = route_segments_to_points(route, graph, cell_size)

    return points


# Export all functions
__all__ = [
    "build_graph",
    "compute_route",
    "route_segments_to_points",
    "point_on_polyline",
    "get_route_for_navigation_step",
]
