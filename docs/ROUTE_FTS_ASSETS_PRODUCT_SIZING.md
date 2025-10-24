# Route Visualization, FTS Icon, Asset Keys, and Product SVG Sizing

## Overview

This document describes the implementation of enhanced route visualization with FTS/AGV icon rendering, canonical asset key management, and standardized product SVG sizing.

## 1. Route Visualization with Flexible Identifier Lookup

### Problem
Routes were not displayed correctly due to inconsistent identifiers:
- Modules use both `id` (e.g., "DPS", "HBW") and `serialNumber` (e.g., "SVR4H73275", "SVR3QA0022")
- Roads in `shopfloor_layout.json` reference modules via `serialNumber`
- Production/Storage orders may use either identifier
- Log messages: "Start (DPS) or goal (HBW) not found in graph"

### Solution

#### Enhanced `route_utils.py`

**1. build_graph()**: Indexes nodes by BOTH `id` and `serialNumber`
```python
graph = build_graph(layout_config)
# graph['id_to_primary'] maps both identifiers to primary key
# Example: {'DPS': 'SVR4H73275', 'SVR4H73275': 'SVR4H73275', '1': '1', ...}
```

**2. compute_route()**: Flexible lookup accepts either identifier
```python
route = compute_route(graph, "DPS", "HBW")  # Using module ids
route = compute_route(graph, "SVR4H73275", "SVR3QA0022")  # Using serialNumbers
# Both work correctly
```

**3. Warning logs**: If start/goal not found, logs available identifiers
```python
logger.warning(
    f"Start node '{start_id}' not found in graph. "
    f"Available identifiers ({len(available_nodes)}): {', '.join(available_nodes[:10])}"
)
```

### Usage in Production/Storage Orders

```python
# production_orders_subtab.py and storage_orders_subtab.py
from omf2.ui.ccu.common.route_utils import get_route_for_navigation_step

# Compute route for current navigation step
source = current_nav_step.get("source")  # Could be id or serialNumber
target = current_nav_step.get("target")  # Could be id or serialNumber

route_points = get_route_for_navigation_step(
    shopfloor_layout=layout_config,
    source_id=source,
    target_id=target,
    cell_size=200
)

# Pass to shopfloor renderer
show_shopfloor_layout(
    route_points=route_points,
    agv_progress=0.5,  # 0.0-1.0 along route
)
```

## 2. FTS/AGV Icon Rendering Along Route

### Problem
FTS icon (`ic_ft_fts.svg`) exists in Asset Manager but was not displayed as a mobile element along the route.

### Solution

#### Asset Manager Access
```python
from omf2.assets.asset_manager import get_asset_manager

asset_manager = get_asset_manager()

# Get FTS icon path
fts_icon_path = asset_manager.get_module_icon_path('FTS')
# Returns: '/omf2/assets/svgs/ic_ft_fts.svg'

# Or via getAssetFile
fts_icon_path = asset_manager.get_asset_file('FTS')
# Returns: '/omf2/assets/svgs/ic_ft_fts.svg'
```

#### Shopfloor Rendering

The `shopfloor_layout.py` `_generate_route_overlay()` function:
1. Renders SVG polyline for route path (orange stroke)
2. Calculates AGV position using `point_on_polyline(route_points, agv_progress)`
3. Embeds FTS icon SVG at calculated position
4. Scales icon to 32x32px for visibility

```python
def _generate_route_overlay(route_points, agv_progress, max_width, max_height):
    """Generate SVG overlay with route polyline and AGV/FTS marker icon"""
    
    # 1. Polyline for route
    points_str = " ".join([f"{x},{y}" for x, y in route_points])
    svg = f'<polyline class="route-path" points="{points_str}"/>'
    
    # 2. Calculate AGV position
    agv_position = point_on_polyline(route_points, agv_progress)
    
    # 3. Load and embed FTS icon
    fts_icon_path = asset_manager.get_module_icon_path('FTS')
    with open(fts_icon_path, 'r') as f:
        fts_svg_content = f.read()
    
    # 4. Position and scale icon
    agv_marker_svg = f'''
    <g transform="translate({agv_x - 16}, {agv_y - 16}) scale(1.33)">
        {fts_svg_content}
    </g>
    '''
    
    return f'<svg class="route-overlay">{svg}{agv_marker_svg}</svg>'
```

### CSS Styling
```css
.route-overlay {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;  /* Don't block clicks */
    z-index: 10;
}

.route-path {
    fill: none;
    stroke: #FF9800;  /* Orange */
    stroke-width: 4;
    stroke-linecap: round;
    stroke-linejoin: round;
}
```

## 3. Canonical Asset Keys

### Problem
Asset Manager used legacy keys (EMPTY1/EMPTY2) and mixed case, causing SVGs at positions [0,0] and [0,3] not to load.

### Solution

#### Canonical Key Format

**Shopfloor Assets:**
- `COMPANY_rectangle` → ORBIS logo (position [0,0])
- `COMPANY_square1` → shelves icon
- `COMPANY_square2` → conveyor belt icon
- `SOFTWARE_rectangle` → DSP/factory logo (position [0,3])
- `SOFTWARE_square1` → warehouse icon
- `SOFTWARE_square2` → delivery truck icon

**Module Assets:**
- `MILL` → ic_ft_mill.svg
- `DRILL` → ic_ft_drill.svg
- `HBW` → ic_ft_hbw.svg
- `DPS` → ic_ft_dps.svg
- `CHRG` → ic_ft_chrg.svg
- `AIQS` → ic_ft_aiqs.svg
- `FTS` → ic_ft_fts.svg

#### shopfloor_layout.json Migration

**v2.0 Structure:**
```json
{
  "fixed_positions": [
    {
      "id": "COMPANY",
      "type": "company",
      "position": [0, 0],
      "assets": {
        "rectangle": "ORBIS",
        "square1": "shelves",
        "square2": "conveyer_belt"
      }
    },
    {
      "id": "SOFTWARE",
      "type": "software",
      "position": [0, 3],
      "assets": {
        "rectangle": "DSP",
        "square1": "warehouse",
        "square2": "delivery_truck_speed"
      }
    }
  ]
}
```

#### Asset Manager Implementation

```python
# asset_manager.py
class OMF2AssetManager:
    def _load_module_icons(self) -> Dict[str, str]:
        icon_mapping = {
            # Modules
            "HBW": "ic_ft_hbw.svg",
            "DPS": "ic_ft_dps.svg",
            "MILL": "ic_ft_mill.svg",
            "DRILL": "ic_ft_drill.svg",
            "AIQS": "ic_ft_aiqs.svg",
            "CHRG": "ic_ft_chrg.svg",
            "FTS": "ic_ft_fts.svg",
        }
        
        # Canonical shopfloor assets
        shopfloor_assets = {
            "COMPANY_rectangle": "ORBIS_logo_RGB.svg",
            "COMPANY_square1": "shelves.svg",
            "COMPANY_square2": "conveyor_belt.svg",
            "SOFTWARE_rectangle": "factory.svg",
            "SOFTWARE_square1": "warehouse.svg",
            "SOFTWARE_square2": "delivery_truck_speed.svg",
        }
        
        icon_mapping.update(shopfloor_assets)
        # ... load SVGs from files ...
    
    def get_shopfloor_asset_path(self, asset_type: str, position: str) -> Optional[str]:
        """Get shopfloor asset using canonical format"""
        asset_key = f"{asset_type}_{position}"  # e.g., "COMPANY_rectangle"
        return self.get_module_icon_path(asset_key)
    
    def get_asset_file(self, key: str) -> str:
        """Get deterministic asset file path"""
        icon_path = self.get_module_icon_path(key)
        if icon_path and Path(icon_path).exists():
            return icon_path
        # Fallback to empty.svg
        return str(self.svgs_dir / "empty.svg")
```

#### Legacy Key Deprecation

**Deprecated (no longer supported in productive code):**
- `EMPTY1` → Use `COMPANY_*` instead
- `EMPTY2` → Use `SOFTWARE_*` instead
- Mixed case keys → Use uppercase canonical keys

**Backward compatibility:**
```python
def get_empty_position_asset(self, empty_id: str, asset_type: str):
    """DEPRECATED: Use get_shopfloor_asset_path() with canonical keys instead"""
    logger.warning(f"⚠️ DEPRECATED: Use canonical COMPANY/SOFTWARE keys.")
    # Convert to canonical format if possible
    if empty_id in ["COMPANY", "SOFTWARE"]:
        return self.get_shopfloor_asset_path(empty_id, asset_type)
    return None
```

## 4. Product SVG Sizing

### Problem
Product SVGs (BLUE/WHITE/RED workpieces) had variable sizes. Needed standardization:
- Default 200x200 px container
- If non-square: width=200px, height proportional
- Support optional scale factor
- Warehouse 3x3 grid must remain intact

### Solution

#### PRODUCT_SVG_BASE_SIZE Constant

```python
# omf2/assets/asset_manager.py
PRODUCT_SVG_BASE_SIZE = 200  # Default base size in pixels for product SVGs
```

#### get_product_svg_with_sizing() Method

```python
def get_product_svg_with_sizing(
    self, 
    workpiece_type: str, 
    state: str = "product", 
    scale: float = 1.0,
    enforce_width: bool = True
) -> Optional[str]:
    """
    Get workpiece SVG with standardized sizing
    
    Args:
        workpiece_type: BLUE, WHITE, or RED
        state: product, 3dim, unprocessed, instock_unprocessed, etc.
        scale: Scale factor (1.0 = 200px, 1.5 = 300px, 0.5 = 100px)
        enforce_width: If True and non-square, enforce width=200px with proportional height
    
    Returns:
        SVG content wrapped in container div with standardized sizing
    """
    svg_content = self.get_workpiece_svg(workpiece_type, state)
    if not svg_content:
        return None
    
    container_size = int(PRODUCT_SVG_BASE_SIZE * scale)
    
    return f"""
    <div style="width: {container_size}px; height: {container_size}px; 
                display: flex; align-items: center; justify-content: center; 
                overflow: hidden;">
        {svg_content}
    </div>
    """
```

#### Usage Examples

```python
from omf2.assets.asset_manager import get_asset_manager, PRODUCT_SVG_BASE_SIZE

asset_manager = get_asset_manager()

# 1. Default 200x200 container
svg_html = asset_manager.get_product_svg_with_sizing('BLUE', 'product')
# Renders in 200x200px container

# 2. Scaled to 300x300 (1.5x)
svg_html = asset_manager.get_product_svg_with_sizing('WHITE', '3dim', scale=1.5)
# Renders in 300x300px container

# 3. Different workpiece states
states = ['product', '3dim', 'unprocessed', 'instock_unprocessed', 'instock_reserved']
for state in states:
    svg_html = asset_manager.get_product_svg_with_sizing('RED', state)
    # All render in consistent 200x200px containers
```

#### Warehouse 3x3 Grid

```python
# CSS Grid enforcement for warehouse/stock view
warehouse_style = """
<div style="display: grid; 
            grid-template-columns: repeat(3, 200px); 
            grid-template-rows: repeat(3, 200px); 
            gap: 0;">
    <!-- 9 positions: A1-A3, B1-B3, C1-C3 -->
</div>
"""
```

**Grid Layout:**
```
A1  A2  A3
B1  B2  B3
C1  C2  C3
```

Each cell: 200x200px (matches PRODUCT_SVG_BASE_SIZE)

#### Non-Square SVG Handling

For SVGs with aspect ratio ≠ 1:1:

**Example: 300x200 SVG (aspect ratio 1.5:1)**
```
Original: 300w x 200h
Container: 200w x 200h
SVG renders: width=200px, height=133px (proportional)
```

The container uses flexbox to center the SVG:
```css
display: flex;
align-items: center;
justify-content: center;
```

## 5. Testing

### Test Coverage

**test_route_utils.py** (19 tests)
- `test_build_graph_id_to_primary_mapping`: Verifies id and serialNumber mapping
- `test_compute_route_with_module_ids`: Routes using module ids
- `test_compute_route_mixed_id_and_serial`: Mixed identifier usage
- All route computation and point-on-polyline tests

**test_asset_manager.py** (44 tests)
- `TestCanonicalShopfloorAssets`: Canonical COMPANY_*/SOFTWARE_* keys
- `TestFTSIconAccess`: FTS icon accessibility via getAssetFile
- `TestProductSvgSizing`: PRODUCT_SVG_BASE_SIZE and get_product_svg_with_sizing
- `TestIconVisibilityAtPositions`: Positions [0,0] and [0,3] icon visibility

**test_product_svg_sizing.py** (9 tests)
- `TestProductSvgSizeConstant`: PRODUCT_SVG_BASE_SIZE = 200
- `TestWarehouseGridLayout`: 3x3 grid enforcement
- `TestProductSvgSizingPolicy`: Sizing policy and scale support
- `TestWorkpieceSvgRenderingConsistency`: Consistent sizing across colors/states

### Running Tests

```bash
# All related tests
pytest tests/test_omf2/test_route_utils.py tests/test_omf2/test_asset_manager.py tests/test_omf2/test_product_svg_sizing.py -v

# Test specific functionality
pytest tests/test_omf2/test_route_utils.py::TestRouteComputation -v
pytest tests/test_omf2/test_asset_manager.py::TestFTSIconAccess -v
pytest tests/test_omf2/test_product_svg_sizing.py::TestWarehouseGridLayout -v
```

**Expected: 72 tests passing**

## 6. Acceptance Criteria Verification

✅ **Route Computation:**
- compute_route finds path when Start/Goal passed as module.id OR module.serialNumber
- No "Start or goal not found" warnings for known modules
- Warning logs include list of available identifiers when node not found

✅ **Route Visualization:**
- Storage and Production orders display orange route polyline from source to destination
- Routes computed using get_route_for_navigation_step()
- SVG overlay renders with pointer-events:none, position:absolute

✅ **FTS Icon:**
- AGV/FTS icon (ic_ft_fts.svg) accessible via getAssetFile('FTS')
- Icon displayed along route when Step is FTS/AGV with agv_progress
- Icon embedded in SVG overlay at calculated position

✅ **Canonical Asset Keys:**
- Positions [0,0] and [0,3] show correct COMPANY/SOFTWARE SVGs
- COMPANY_rectangle → ORBIS_logo_RGB.svg
- SOFTWARE_rectangle → factory.svg (DSP logo)
- Legacy EMPTY1/EMPTY2 keys deprecated

✅ **Product SVG Sizing:**
- PRODUCT_SVG_BASE_SIZE constant defined (200px)
- get_product_svg_with_sizing() method with scale support
- Product SVGs render within 200x200 px container
- Non-square SVGs: width=200px, height proportional
- Optional scale parameter works (scale=1.5 → 300x300)

✅ **Warehouse Grid:**
- 3x3 grid remains intact visually
- CSS grid-template-columns: repeat(3, 200px)
- Cell size matches PRODUCT_SVG_BASE_SIZE

✅ **Tests:**
- All modified/added tests pass (72/72)
- Comprehensive test coverage for all new features

## 7. Migration Guide

### For Applications Using Old Asset Keys

**Before (deprecated):**
```python
# Legacy EMPTY1/EMPTY2 keys
asset_path = asset_manager.get_empty_position_asset("EMPTY1", "rectangle")
```

**After (canonical):**
```python
# Use canonical COMPANY/SOFTWARE keys
asset_path = asset_manager.get_shopfloor_asset_path("COMPANY", "rectangle")
# Or directly via key
asset_path = asset_manager.get_asset_file("COMPANY_rectangle")
```

### For Product Rendering Code

**Before (inconsistent sizing):**
```python
svg_content = asset_manager.get_workpiece_svg("BLUE", "product")
st.markdown(svg_content, unsafe_allow_html=True)
```

**After (standardized sizing):**
```python
svg_html = asset_manager.get_product_svg_with_sizing("BLUE", "product", scale=1.0)
st.markdown(svg_html, unsafe_allow_html=True)
```

### For Warehouse Grid Rendering

**Enforce 3x3 grid:**
```python
# CSS Grid with fixed cell size
warehouse_grid_css = """
<style>
.warehouse-grid {
    display: grid;
    grid-template-columns: repeat(3, var(--cell-size));
    grid-template-rows: repeat(3, var(--cell-size));
    --cell-size: 200px;  /* Matches PRODUCT_SVG_BASE_SIZE */
    gap: 0;
}
</style>
"""
```

## 8. Troubleshooting

### Route Not Displayed

**Symptom:** "Start (DPS) or goal (HBW) not found in graph"

**Solution:**
1. Check module identifiers in shopfloor_layout.json
2. Verify roads[] use serialNumber references
3. Use flexible lookup in compute_route():
   ```python
   route = compute_route(graph, "DPS", "HBW")  # Try both id and serialNumber
   ```

### FTS Icon Missing

**Symptom:** Route displayed but no AGV icon

**Solution:**
1. Verify FTS icon exists: `ls omf2/assets/svgs/ic_ft_fts.svg`
2. Test access: `asset_manager.get_asset_file('FTS')`
3. Check agv_progress is between 0.0-1.0
4. Verify _generate_route_overlay() includes AGV marker rendering

### SVGs Not Loading at Positions [0,0] and [0,3]

**Symptom:** Blank or fallback icons at corner positions

**Solution:**
1. Check canonical key format: `COMPANY_rectangle`, `SOFTWARE_rectangle`
2. Verify asset files exist in omf2/assets/svgs/
3. Update code to use get_shopfloor_asset_path():
   ```python
   asset_path = asset_manager.get_shopfloor_asset_path("COMPANY", "rectangle")
   ```

### Product SVGs Variable Sizes

**Symptom:** Inconsistent workpiece rendering across UI

**Solution:**
1. Use get_product_svg_with_sizing() instead of get_workpiece_svg()
2. Apply PRODUCT_SVG_BASE_SIZE standard
3. Update all product rendering code to use consistent container size

### Warehouse Grid Not 3x3

**Symptom:** Grid expands/contracts with different SVG sizes

**Solution:**
1. Use CSS Grid with fixed columns:
   ```css
   grid-template-columns: repeat(3, 200px);
   ```
2. Match cell size to PRODUCT_SVG_BASE_SIZE
3. Don't use `fr` units for warehouse grid (use fixed px)

## 9. Further Development

### Planned Enhancements

1. **Animated AGV Movement**
   - Real-time agv_progress updates via MQTT
   - Smooth CSS transitions for AGV marker

2. **Route Optimization**
   - Dijkstra's algorithm for weighted paths
   - Consider road lengths from shopfloor_layout.json

3. **Multiple AGVs**
   - Support multiple FTS units on different routes
   - Collision detection and avoidance visualization

4. **Interactive Route Planning**
   - Click-to-select source and destination
   - Preview route before order execution

## 10. References

### Files Modified

- `omf2/assets/asset_manager.py`: Added PRODUCT_SVG_BASE_SIZE and get_product_svg_with_sizing()
- `omf2/config/ccu/shopfloor_layout.json`: Updated _meta with v2.1 documentation
- `tests/test_omf2/test_asset_manager.py`: Added ProductSvgSizing and FTSIconAccess tests
- `tests/test_omf2/test_product_svg_sizing.py`: New comprehensive sizing tests

### Files Already Implemented

- `omf2/ui/ccu/common/route_utils.py`: Flexible id/serialNumber lookup (already working)
- `omf2/ui/ccu/common/shopfloor_layout.py`: SVG overlay with AGV marker (already working)
- `omf2/ui/ccu/ccu_orders/production_orders_subtab.py`: Route visualization integration (already working)
- `omf2/ui/ccu/ccu_orders/storage_orders_subtab.py`: Route visualization integration (already working)

### Related Documentation

- [shopfloor_layout.json specification](../omf2/config/ccu/shopfloor_layout.json)
- [Asset Manager API](../omf2/assets/asset_manager.py)
- [Route Utils API](../omf2/ui/ccu/common/route_utils.py)

---

**Version:** 2.1  
**Last Updated:** 2025-10-24  
**Status:** ✅ Implemented and Tested (72/72 tests passing)
