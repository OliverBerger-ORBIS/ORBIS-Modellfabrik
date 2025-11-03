"""
Route utilities for examples/shopfloor_test_app

Functions:
- build_graph(layout): builds undirected adjacency graph from layout['roads']
- find_path(graph, start, goal): BFS path as list of node ids
- id_to_position_map(layout, cell_size): maps node ids (intersection ids and module ids/serials) to pixel centers
"""
from collections import deque


def build_graph(layout):
    graph = {}
    # add intersections
    for it in layout.get("intersections", []):
        node = str(it["id"])
        graph.setdefault(node, [])
    # add modules and fixed positions by id and serialNumber
    for mod in layout.get("modules", []):
        key_id = mod.get("id")
        key_sn = mod.get("serialNumber")
        if key_id:
            graph.setdefault(str(key_id), [])
        if key_sn:
            graph.setdefault(str(key_sn), [])
    for f in layout.get("fixed_positions", []):
        key_id = f.get("id")
        if key_id:
            graph.setdefault(str(key_id), [])

    # connect edges bidirectionally
    for r in layout.get("roads", []):
        a = str(r["from"])
        b = str(r["to"])
        graph.setdefault(a, [])
        graph.setdefault(b, [])
        if b not in graph[a]:
            graph[a].append(b)
        if a not in graph[b]:
            graph[b].append(a)
    return graph


def find_path(graph, start, goal):
    if start is None or goal is None:
        return []
    start = str(start)
    goal = str(goal)
    if start == goal:
        return [start]
    q = deque([start])
    prev = {start: None}
    while q:
        node = q.popleft()
        for nb in graph.get(node, []):
            if nb not in prev:
                prev[nb] = node
                if nb == goal:
                    path = [goal]
                    cur = goal
                    while prev[cur] is not None:
                        cur = prev[cur]
                        path.append(cur)
                    return list(reversed(path))
                q.append(nb)
    return []


def id_to_position_map(layout, cell_size=200):
    """
    Return mapping node_id -> center_x,center_y in pixel coordinates based on grid positions.
    node_id: intersections use their id as string, modules mapped by id and serialNumber, fixed_positions by id.
    """
    m = {}

    def center_of_cell(row, col):
        x = col * cell_size + cell_size // 2
        y = row * cell_size + cell_size // 2
        return (x, y)

    for inter in layout.get("intersections", []):
        r, c = inter["position"]
        m[str(inter["id"])] = center_of_cell(r, c)
    for mod in layout.get("modules", []):
        pos = mod.get("position")
        if pos:
            center = center_of_cell(pos[0], pos[1])
            if mod.get("id"):
                m[str(mod["id"])] = center
            if mod.get("serialNumber"):
                m[str(mod.get("serialNumber"))] = center
    for f in layout.get("fixed_positions", []):
        pos = f.get("position")
        if pos:
            center = center_of_cell(pos[0], pos[1])
            if f.get("id"):
                m[str(f.get("id"))] = center
    return m

