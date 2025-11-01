SVG Icons Usage Guide

This guide explains consistent SVG icon usage across the UI (modules, headings, and components), Streamlit limitations, and implementation patterns.

## Architecture Overview

### Centralized Icon Management

All module icon rendering is centralized in `omf2/ccu/module_manager.py`:

```
Module Manager
  ├─→ get_module_icon_html(id, size_px) → SVG HTML (for st.markdown)
  └─→ get_module_icon(id) → Emoji string (for selectbox/dataframe)
```

### Core Helper Function

The underlying icon system uses `get_icon_html()` in `omf2/ui/common/symbols.py`:

- Heading SVGs via `heading_icons.get_svg_inline()`
- Module SVGs via `asset_manager.get_module_icon_path()`
- Emoji fallback from registries (TAB_ICONS, STATUS_ICONS, FUNCTIONAL_ICONS)

Features:
- CSS scoping via `scope_svg_styles()` to prevent class name collisions
- Automatic width/height cleanup and proportional scaling
- Configurable size via `size_px` parameter (default: 24px)

## Streamlit Technical Limitations

Components that cannot render HTML/SVG directly:

| Component | Supports HTML? | Icon Type Required |
|-----------|----------------|-------------------|
| `st.selectbox()` | ❌ No | Emoji only |
| `st.dataframe()` | ❌ No | Emoji only |
| `st.markdown()` | ✅ Yes (with `unsafe_allow_html=True`) | SVG supported |
| `st.write()` | ❌ No (by default) | Emoji only |

When using `st.selectbox()` or `st.dataframe()`, attempting to pass HTML/SVG will show raw HTML. Solution: Use emoji via Module Manager, or switch to custom HTML rendering with `st.markdown(..., unsafe_allow_html=True)`.

## Module Manager Integration

### For HTML Rendering (SVG Icons)

```python
html = module_manager.get_module_icon_html(module_id, size_px=20)
st.markdown(html, unsafe_allow_html=True)
```

### For Plain Text Rendering (Emoji Icons)

```python
emoji = module_manager.get_module_icon(module_id)
# Use in selectbox/dataframe
```

### Automatic Serial → Type Mapping

`get_module_icon_html()` accepts the serial ID (e.g., `SVR3QA0022`), resolves module type internally, and returns SVG HTML. Fallback to emoji is automatic.

## Implementation Patterns

### Pattern A: SVG Icons in Custom HTML Tables

Use `st.markdown(..., unsafe_allow_html=True)` and embed SVG HTML in cells. Size typically 20px for tables.

### Pattern B: Emoji Icons in Selectbox

Use `get_module_icon(module_id)` and build plain text labels.

### Pattern C: Heading Icons

Use `omf2/assets/heading_icons.py`:

```python
from omf2.assets.heading_icons import get_svg_inline

icon = get_svg_inline("PRODUCTION_ORDERS", size_px=22)
st.markdown(f"{icon} <strong>PRODUCTION</strong>", unsafe_allow_html=True)
```

Registry keys (excerpt): `ORDERS`, `PRODUCTION_ORDERS`, `STORAGE_ORDERS`, `SHOPFLOOR_LAYOUT`.

Recommended sizes:
- Major headings (page/section titles): 32px (e.g., Orders/Production/Storage titles)
- Sub-headings in content blocks: 22–24px

## Component-Specific Guidelines

- Lists/rows: prefer a flex layout with fixed columns (status | icon(s) | text) and 10–12px vertical spacing.
- Navigation display: render both endpoint icons with labels (e.g., `SVG-FTS FTS → SVG-HBW HBW`).
- Avoid raw inline SVG strings from files; use `get_icon_html()` or `get_svg_inline()` for sizing and scoping.

## Migration Checklist

1. Identify UI where icons appear (table/list/heading).
2. For HTML-capable areas, switch to `get_icon_html(..., size_px)` or `get_svg_inline(...)`.
3. For selectbox/dataframe, switch to emoji via `get_module_icon()`.
4. Test sizes (20px for tables/lists, 22–24px for headings) and spacing.

## Common Pitfalls

- Using SVG/HTML in selectbox/dataframe → raw HTML shown.
- Missing `unsafe_allow_html=True` for `st.markdown`.
- Mixing raw SVG file contents instead of helper functions (leads to 512px artifacts).

## Examples

See `omf2/ui/ccu/ccu_orders/*_orders_subtab.py` for list-row rendering, and `omf2/ui/ccu/ccu_modules/ccu_modules_tab.py` for table rendering.

