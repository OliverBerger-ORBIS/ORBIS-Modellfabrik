# Shopfloor Layout & AGV Routing Guide

## Overview

This guide documents the shopfloor layout visualization improvements and the new AGV routing system implemented for the ORBIS Modellfabrik project.

## Table of Contents

1. [Asset Manager Updates](#asset-manager-updates)
2. [Shopfloor Layout Enhancements](#shopfloor-layout-enhancements)
3. [AGV Routing System](#agv-routing-system)
4. [Factory Configuration](#factory-configuration)
5. [Integration Guide](#integration-guide)
6. [Testing](#testing)
7. [Migration Notes](#migration-notes)

---

## Asset Manager Updates

### New Asset Keys (v1.1)

The asset manager now uses domain-specific naming for empty positions:

**New Keys (Preferred):**
```python
# Company assets (ORBIS)
"company_rectangle" -> "ORBIS_logo_RGB.svg"
"company_square1" -> "shelves.svg"
"company_square2" -> "conveyor_belt.svg"

# Software assets (DSP)
"software_rectangle" -> "factory.svg"
"software_square1" -> "warehouse.svg"
"software_square2" -> "delivery_truck_speed.svg"
```

**Legacy Keys (Backward Compatible):**
```python
# These still work for backward compatibility
"EMPTY1" -> maps to "COMPANY_rectangle"
"EMPTY2" -> maps to "SOFTWARE_rectangle"

# Uppercase variants also supported
"COMPANY_rectangle", "SOFTWARE_rectangle", etc.
```

### Fallback Handling

A new `empty.svg` file provides graceful fallback for missing assets:

```python
from omf2.assets import get_asset_manager

asset_manager = get_asset_manager()
icon_path = asset_manager.get_module_icon_path("UNKNOWN")
# Returns path to empty.svg if icon not found
```

### Asset Locations

All SVG assets are located in:
```
/omf2/assets/svgs/
```

---

## Shopfloor Layout Enhancements

### Square Cell Grid

The shopfloor layout now uses consistent 200×200px square cells:

```python
from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_layout

show_shopfloor_layout(
    active_module_id="MILL",
    active_intersections=["1", "2"],
    title="Shopfloor Layout",
    mode="view_mode",
)
```

**Key Features:**
- ✅ Fixed cell size: 200×200px
- ✅ Aspect ratio: 1:1 enforced via CSS
- ✅ Labels separated from icon container (no cell distortion)
- ✅ Bottom border always visible (border-bottom: 2px)
- ✅ Icon sizing: max-width/height 80%, object-fit: contain

### CSS Improvements

```css
.cell {
    width: 200px;
    height: 200px;
    aspect-ratio: 1 / 1;  /* Enforce square */
    border-bottom: 2px solid #ddd;  /* Visible bottom border */
}

.icon-container img {
    object-fit: contain;
    max-width: 80%;
    max-height: 80%;
}
```

### Highlighting

Active modules and intersections are highlighted:

```python
# Orange border for active modules
.cell-active {
    border: 4px solid #FF9800 !important;
}

# Dashed orange border for active intersections
.cell-intersection-active {
    border: 3px dashed #FF9800 !important;
}
```

---

## AGV Routing System

### Architecture

The routing system consists of four main components:

1. **Graph Building** - Parse shopfloor layout into graph structure
2. **Route Computation** - BFS pathfinding algorithm
3. **Coordinate Conversion** - Convert route to pixel coordinates
4. **Visualization** - SVG overlay with polyline and marker

### Building a Graph

```python
from omf2.ui.ccu.common.route_utils import build_graph

# Load shopfloor layout config
layout_config = config_loader.load_shopfloor_layout()

# Build graph
graph = build_graph(layout_config)
# Returns: {
#   'nodes': {'SVR3QA2098': {...}, '1': {...}, ...},
#   'adjacency': {'SVR3QA2098': ['1'], '1': ['SVR3QA2098', '2'], ...}
# }
```

### Computing a Route

```python
from omf2.ui.ccu.common.route_utils import compute_route

# Compute route from MILL to AIQS
route = compute_route(graph, "SVR3QA2098", "SVR4H76530")
# Returns: ["SVR3QA2098", "1", "2", "SVR4H76530"]
```

**Algorithm:** Breadth-First Search (BFS)
- Guarantees shortest path (by number of edges)
- O(V + E) time complexity
- Returns None if no path exists

### Converting to Pixel Coordinates

```python
from omf2.ui.ccu.common.route_utils import route_segments_to_points

# Convert route to pixel coordinates
points = route_segments_to_points(route, graph, cell_size=200)
# Returns: [(300.0, 100.0), (300.0, 300.0), (500.0, 300.0), (600.0, 300.0)]
```

**Edge Handling:**
- Start: Center of edge adjacent to first waypoint
- Waypoints: Center of intersection cells
- End: Center of edge adjacent to last waypoint

### AGV Marker Positioning

```python
from omf2.ui.ccu.common.route_utils import point_on_polyline

# Calculate AGV position at 50% progress
agv_position = point_on_polyline(points, 0.5)
# Returns: (400.0, 300.0)
```

**Progress Values:**
- `0.0` - Start of route
- `0.5` - Midpoint of route
- `1.0` - End of route

### Complete Example

```python
from omf2.ui.ccu.common.route_utils import get_route_for_navigation_step
from omf2.ccu.config_loader import get_ccu_config_loader

# Load layout
config_loader = get_ccu_config_loader()
layout_config = config_loader.load_shopfloor_layout()

# Compute route in one call
route_points = get_route_for_navigation_step(
    layout_config, 
    source_id="SVR3QA2098",  # MILL
    target_id="SVR4H76530",  # AIQS
    cell_size=200
)

# Use in shopfloor layout
show_shopfloor_layout(
    route_points=route_points,
    agv_progress=0.5,  # 50% along route
)
```

---

## Factory Configuration

### Position Details Display

The factory configuration page now shows detailed information for each grid position:

**Format:**
```
📍 Details zu shopfloor-position-{row}-{col}
```

**For Modules:**
- ID, Name, Type
- Serial Number
- Position coordinates
- Asset Keys

**For Empty Positions:**
- ID, Name (COMPANY/SOFTWARE)
- Position coordinates
- Asset Keys (rectangle, square1, square2)

**For Intersections:**
- ID, Name
- Connected modules
- Position coordinates
- Asset Key (point_scan_3sections)

### Usage

```python
from omf2.ui.ccu.ccu_configuration.ccu_factory_configuration_subtab import (
    render_ccu_factory_configuration_subtab
)

# Renders complete factory configuration UI
render_ccu_factory_configuration_subtab()
```

---

## Integration Guide

### Production Orders

```python
from omf2.ui.ccu.ccu_orders.production_orders_subtab import show_production_orders_subtab

# Automatically computes and displays routes for FTS navigation steps
show_production_orders_subtab(i18n)
```

**Features:**
- Detects FTS/AGV navigation steps automatically
- Computes route from source to target
- Shows orange polyline overlay
- Displays AGV marker at current progress

### Storage Orders

```python
from omf2.ui.ccu.ccu_orders.storage_orders_subtab import show_storage_orders_subtab

# Same functionality as production orders
show_storage_orders_subtab(i18n)
```

### Custom Integration

```python
from omf2.ui.ccu.common.shopfloor_layout import show_shopfloor_layout
from omf2.ui.ccu.common.route_utils import get_route_for_navigation_step

# Get current navigation step
current_nav_step = get_current_navigation_step()  # Your logic

if current_nav_step:
    # Compute route
    route_points = get_route_for_navigation_step(
        layout_config,
        source=current_nav_step["source"],
        target=current_nav_step["target"],
        cell_size=200
    )
    
    # Calculate progress (example: 50% if IN_PROGRESS)
    agv_progress = 0.5 if current_nav_step["state"] == "IN_PROGRESS" else 0.0
else:
    route_points = None
    agv_progress = 0.0

# Display with routing
show_shopfloor_layout(
    active_module_id=active_module,
    active_intersections=active_intersections,
    route_points=route_points,
    agv_progress=agv_progress,
)
```

---

## Testing

### Running Tests

```bash
# Run all shopfloor and routing tests
pytest tests/test_omf2/test_shopfloor_layout_events.py tests/test_omf2/test_route_utils.py -v

# Run with coverage
pytest tests/test_omf2/test_route_utils.py --cov=omf2.ui.ccu.common.route_utils
```

### Test Coverage

- ✅ **Graph Building:** 2 tests
- ✅ **Route Computation:** 3 tests
- ✅ **Coordinate Conversion:** 2 tests
- ✅ **Polyline Utilities:** 6 tests
- ✅ **Shopfloor Layout:** 7 tests
- ✅ **Asset Manager:** 20 tests

**Total: 40 tests, 100% passing**

### Manual Testing

1. **Asset Display:**
   ```bash
   streamlit run tests/test_omf2/test_helper_apps/shopfloor_layout_test.py
   ```
   - Verify COMPANY/SOFTWARE assets display correctly
   - Check backward compatibility with EMPTY1/EMPTY2

2. **Route Visualization:**
   - Start a production order with FTS navigation
   - Verify orange route polyline appears
   - Check AGV marker position updates

3. **Factory Configuration:**
   - Open Factory Configuration tab
   - Select different grid positions from dropdown
   - Verify position details display correctly

---

## Migration Notes

### From v1.0 to v1.1

**shopfloor_layout.json Changes:**

```json
{
  "_meta": {
    "_version": "1.1",
    "_changelog": {
      "v1.1": "Renamed EMPTY1/EMPTY2 to COMPANY/SOFTWARE",
      "v1.0": "Initial configuration with EMPTY1/EMPTY2 naming"
    }
  },
  "empty_positions": [
    {
      "id": "COMPANY",  // Was: "EMPTY1"
      "position": [0, 0],
      "rectangle": "ORBIS",
      "square1": "shelves",
      "square2": "conveyer_belt"
    },
    {
      "id": "SOFTWARE",  // Was: "EMPTY2"
      "position": [0, 3],
      "rectangle": "DSP",
      "square1": "warehouse",
      "square2": "delivery_truck_speed"
    }
  ]
}
```

**Code Changes Required:**

None! The asset manager maintains full backward compatibility:

```python
# Old code still works
icon_path = asset_manager.get_module_icon_path("EMPTY1")  # ✅ Still works

# New code preferred
icon_path = asset_manager.get_module_icon_path("company_rectangle")  # ✅ Preferred
```

### Breaking Changes

**None.** This is a backward-compatible update.

### Deprecated Features

**None.** All old APIs remain functional.

---

## Performance Considerations

### Graph Building
- **Time:** O(V + E) where V = nodes, E = edges
- **Space:** O(V + E) for adjacency list
- **Typical:** ~10 nodes, ~20 edges = < 1ms

### BFS Pathfinding
- **Time:** O(V + E) worst case
- **Space:** O(V) for visited set and queue
- **Typical:** 10-node graph = < 1ms

### Route Rendering
- **SVG Overlay:** Minimal overhead
- **Polyline:** Single path element
- **Marker:** Single circle element

**Recommendation:** Pre-compute routes when state changes, not on every render.

---

## Troubleshooting

### Issue: Route not displaying

**Check:**
1. Route points returned by `compute_route()` is not None
2. `route_points` passed to `show_shopfloor_layout()`
3. At least 2 points in route (start + end)

**Debug:**
```python
route = compute_route(graph, source, target)
print(f"Route: {route}")  # Should print node IDs

points = route_segments_to_points(route, graph)
print(f"Points: {points}")  # Should print (x, y) tuples
```

### Issue: Assets not loading

**Check:**
1. SVG files exist in `/omf2/assets/svgs/`
2. Asset Manager initialized correctly
3. Fallback to `empty.svg` working

**Debug:**
```python
from omf2.assets import get_asset_manager

am = get_asset_manager()
print(f"Icons loaded: {len(am.module_icons)}")  # Should be ~38

icon_path = am.get_module_icon_path("COMPANY_rectangle")
print(f"Path: {icon_path}")  # Should print full path
```

### Issue: Cells not square

**Check:**
1. CSS aspect-ratio applied
2. Cell size set to 200px
3. No parent container forcing different dimensions

**Debug:**
```html
<!-- Check browser inspector -->
<div class="cell" style="width: 200px; height: 200px; aspect-ratio: 1/1;">
```

---

## Future Enhancements

### A* Pathfinding
Replace BFS with A* for optimized routes in larger graphs:

```python
def compute_route_astar(graph, start_id, goal_id):
    """A* pathfinding with euclidean distance heuristic"""
    # TODO: Implement A* algorithm
    pass
```

### Dynamic Route Progress
Calculate actual AGV progress from MQTT state messages:

```python
def get_agv_progress(current_step):
    """Calculate AGV progress from step state"""
    if "progress_percent" in current_step:
        return current_step["progress_percent"] / 100.0
    return 0.5  # Fallback
```

### Interactive Cell Selection
Add click handlers (requires Streamlit components):

```python
# Would require custom Streamlit component with JavaScript
show_shopfloor_layout(
    on_cell_click=lambda row, col: handle_cell_click(row, col)
)
```

---

## References

- [Shopfloor Layout JSON Schema](../omf2/config/ccu/shopfloor_layout.json)
- [Asset Manager Source](../omf2/assets/asset_manager.py)
- [Route Utils Source](../omf2/ui/ccu/common/route_utils.py)
- [Shopfloor Layout Component](../omf2/ui/ccu/common/shopfloor_layout.py)

---

## Support

For questions or issues:
1. Check existing tests for usage examples
2. Review this documentation
3. Consult source code docstrings
4. Contact development team

**Last Updated:** 2025-10-22
**Version:** 1.1
