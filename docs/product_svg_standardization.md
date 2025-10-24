# Product SVG Standardization Guide

## Overview

This document describes the standardized product SVG rendering system implemented in ORBIS Modellfabrik. All product SVGs are now rendered with a consistent base size of **200×200 pixels** across all views.

## Key Features

### 1. Standardized Base Size
- **PRODUCT_SVG_BASE_SIZE**: 200px (defined in `omf2/ui/common/ui_constants.py`)
- Square SVGs are rendered at exactly 200×200px
- Non-square SVGs maintain aspect ratio with 200px width

### 2. Optional Scaling
- Default scale: `1.0` (200×200px)
- Example: `scale=1.5` produces 300×300px
- Example: `scale=0.5` produces 100×100px

### 3. Warehouse Grid
- Fixed 3×3 grid layout
- Each cell: 200×200px
- Grid remains consistent regardless of SVG variations

## Usage

### Basic Product SVG Container

```python
from omf2.ui.common.product_rendering import render_product_svg_container

# Get SVG content from asset manager
svg_content = asset_manager.get_workpiece_svg("BLUE", "product")

# Render with default 200x200 size
html = render_product_svg_container(svg_content, scale=1.0)
st.markdown(html, unsafe_allow_html=True)
```

### Scaled Product Display

```python
# Render at 1.5x size (300x300)
html = render_product_svg_container(svg_content, scale=1.5)
st.markdown(html, unsafe_allow_html=True)
```

### Warehouse Cell

```python
from omf2.ui.common.product_rendering import render_warehouse_cell

# Empty position
palett_content = asset_manager.get_workpiece_palett()
html = render_warehouse_cell(palett_content, position_label="A1", workpiece_type=None)
st.markdown(html, unsafe_allow_html=True)

# Filled position
svg_content = asset_manager.get_workpiece_svg("BLUE", "instock_unprocessed")
html = render_warehouse_cell(svg_content, position_label="A1", workpiece_type="BLUE")
st.markdown(html, unsafe_allow_html=True)
```

### Complete Product Card

```python
from omf2.ui.common.product_rendering import render_product_card

svg_content = asset_manager.get_workpiece_svg("BLUE", "product")
additional_info = {
    "Material": "Plastic",
    "Color": "Blue"
}
html = render_product_card(
    svg_content, 
    "Blue Product", 
    scale=1.0,
    additional_info=additional_info
)
st.markdown(html, unsafe_allow_html=True)
```

## Implementation Details

### Files Modified

1. **UI Constants** (`omf2/ui/common/ui_constants.py`)
   - `PRODUCT_SVG_BASE_SIZE = 200`
   - `WAREHOUSE_CELL_SIZE = 200`
   - `WAREHOUSE_GRID_COLUMNS = 3`

2. **Rendering Utilities** (`omf2/ui/common/product_rendering.py`)
   - `render_product_svg_container()` - Standard SVG container
   - `render_warehouse_cell()` - Warehouse grid cell
   - `render_product_card()` - Complete product card

3. **Updated Views**
   - `product_catalog_subtab.py` - Product catalog display
   - `customer_order_subtab.py` - Customer orders
   - `purchase_order_subtab.py` - Purchase orders
   - `inventory_subtab.py` - Warehouse inventory (3×3 grid)

### Container Behavior

#### Default Mode (Square Container)
```css
width: 200px;
height: 200px;
display: flex;
align-items: center;
justify-content: center;
```

SVG inside uses:
```css
max-width: 100%;
max-height: 100%;
object-fit: contain;
```

#### Width-Only Mode (force_width_only=True)
```css
width: 200px;
height: auto;
```

Use this for non-square SVGs where you want width fixed and height proportional.

## Testing

Comprehensive test suite available at `tests/test_omf2/test_ui/test_product_svg_size.py`:

- **20 tests** covering:
  - Constants validation
  - Size calculations with different scales
  - Container HTML/CSS structure
  - Warehouse cell rendering
  - Product card rendering
  - Integration scenarios

Run tests:
```bash
python -m pytest tests/test_omf2/test_ui/test_product_svg_size.py -v
```

## Benefits

1. **Visual Consistency**: All products display at the same size across different views
2. **Predictable Layout**: No layout shifts from varying SVG dimensions
3. **Easy Scaling**: Single parameter to adjust display size
4. **Grid Stability**: Warehouse 3×3 grid maintains structure
5. **Better UX**: Users see consistent product representations

## Migration Guide

### Before
```python
st.markdown(
    f'<div style="border: 1px solid #ccc; padding: 10px;">{svg_content}</div>',
    unsafe_allow_html=True
)
```

### After
```python
from omf2.ui.common.product_rendering import render_product_svg_container

html = render_product_svg_container(svg_content, scale=1.0)
st.markdown(html, unsafe_allow_html=True)
```

## Configuration

To change the base size globally, edit `omf2/ui/common/ui_constants.py`:

```python
# Change from 200 to your desired size
PRODUCT_SVG_BASE_SIZE = 250  # px
```

Note: This will affect all views using the standardized rendering functions.

## Screenshots

Screenshots demonstrating the standardized sizes are available for:
- Product Catalog (showing BLUE, WHITE, RED products at 200×200)
- Customer Orders (product displays with order buttons)
- Purchase Orders (unprocessed workpieces with palett display)
- Inventory (3×3 warehouse grid with 200×200 cells)

## FAQ

**Q: Can I display products at different sizes in the same view?**  
A: Yes, use the `scale` parameter. Example: `scale=1.5` for larger products.

**Q: What happens to non-square SVGs?**  
A: They maintain aspect ratio within the 200×200 container using `object-fit: contain`.

**Q: Does this affect existing SVG files?**  
A: No, the original SVG files are unchanged. Only the display containers are standardized.

**Q: Can I use this for non-product SVGs?**  
A: Yes, `render_product_svg_container()` works with any SVG content.

## Version History

- **v1.0** (2025-10-24): Initial implementation
  - Base size: 200×200px
  - Scale parameter support
  - 3×3 warehouse grid
  - Comprehensive test suite
