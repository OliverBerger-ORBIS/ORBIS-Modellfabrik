# SVG Icons Usage Guide

## Overview

This guide provides comprehensive instructions for consistently using SVG icons across UI components in the ORBIS-Modellfabrik application. It documents technical constraints, best practices, and implementation patterns.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Streamlit Technical Limitations](#streamlit-technical-limitations)
3. [Module Manager Integration](#module-manager-integration)
4. [Implementation Patterns](#implementation-patterns)
5. [Component-Specific Guidelines](#component-specific-guidelines)
6. [Migration Checklist](#migration-checklist)
7. [Common Pitfalls](#common-pitfalls)
8. [Examples](#examples)

---

## Architecture Overview

### Centralized Icon Management

All module icon rendering is centralized in **Module Manager** (`omf2/ccu/module_manager.py`):

```
Module Manager
  ├─→ get_module_icon_html(id, size_px) → SVG HTML (for st.markdown)
  └─→ get_module_icon(id) → Emoji string (for selectbox/dataframe)
```

### Core Helper Function

The underlying icon system uses `get_icon_html()` in `omf2/ui/common/symbols.py`:

**3-Tier Cascading Lookup:**
1. **Heading SVGs** via `heading_icons.get_svg_inline()`
2. **Module SVGs** via `asset_manager.get_module_icon_path()`
3. **Emoji Fallback** from registries (TAB_ICONS, STATUS_ICONS, FUNCTIONAL_ICONS)

**Features:**
- CSS scoping via `scope_svg_styles()` to prevent class name collisions
- Automatic width/height cleanup and proportional scaling
- Configurable size via `size_px` parameter (default: 24px)

---

## Streamlit Technical Limitations

### Components That CANNOT Render HTML

Streamlit has specific components that only accept **plain text** and cannot render HTML/SVG:

| Component | Supports HTML? | Icon Type Required |
|-----------|----------------|-------------------|
| `st.selectbox()` | ❌ No | Emoji only |
| `st.dataframe()` | ❌ No | Emoji only |
| `st.markdown()` | ✅ Yes (with `unsafe_allow_html=True`) | SVG supported |
| `st.write()` | ❌ No (by default) | Emoji only |

### Why This Matters

When using `st.selectbox()` or `st.dataframe()`, attempting to pass HTML/SVG will result in:
- HTML code displayed as plain text in the UI
- Example: `<span style="font-size: 24px;">⚙️</span> HBW` instead of the rendered emoji

**Solution:** Use emoji icons for these components, but ensure consistent sourcing via Module Manager.

---

## Module Manager Integration

### Key Methods

#### For HTML Rendering (SVG Icons)

```python
def get_module_icon_html(self, module_id: str, size_px: int = 24) -> str:
    """
    Get module icon as SVG HTML from module ID.
    
    Maps: serial ID (SVR3QA0022) → type (HBW) → SVG icon
    Falls back to emoji if SVG not available.
    
    Use with: st.markdown(..., unsafe_allow_html=True)
    """
```

#### For Plain Text Rendering (Emoji Icons)

```python
def get_module_icon(self, module_id: str) -> str:
    """
    Get module emoji icon from module ID.
    
    Maps: serial ID (SVR3QA0022) → type (HBW) → emoji (🏬)
    
    Use with: st.selectbox(), st.dataframe()
    """
```

### Automatic Serial ID → Type Mapping

Module Manager handles the mapping automatically:
- Input: Serial ID (e.g., `SVR3QA0022`)
- Lookup: Module registry to find type (e.g., `HBW`)
- Output: SVG or emoji icon for that type

**No manual type lookup needed in UI code!**

---

## Implementation Patterns

### Pattern 1: SVG Icons in Custom HTML Tables

**When to use:** Displaying data in a table format with visual icons

**Implementation:**

```python
from omf2.ccu.module_manager import get_ccu_module_manager

def _render_module_table_with_svg_icons(modules):
    """Render module table with SVG icons using st.markdown."""
    
    module_manager = get_ccu_module_manager()
    
    # Build HTML table
    table_html = '''
    <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="background-color: #f0f2f6;">
                <th style="padding: 8px; border: 1px solid #ddd;">Name</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Status</th>
            </tr>
        </thead>
        <tbody>
    '''
    
    for module_id, module_data in modules.items():
        # Get SVG icon (20px for table cells)
        icon_html = module_manager.get_module_icon_html(module_id, size_px=20)
        name = module_data.get('name', module_id)
        status = module_data.get('status', 'Unknown')
        
        table_html += f'''
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">
                {icon_html} {name}
            </td>
            <td style="padding: 8px; border: 1px solid #ddd;">
                {status}
            </td>
        </tr>
        '''
    
    table_html += '</tbody></table>'
    
    # Render with HTML support
    st.markdown(table_html, unsafe_allow_html=True)
```

**Key Points:**
- Use `st.markdown(..., unsafe_allow_html=True)` for HTML rendering
- Embed SVG icons directly in table cells
- Choose appropriate size (typically 20px for tables)
- Include proper CSS styling for borders, padding, headers

---

### Pattern 2: Emoji Icons in Selectbox

**When to use:** Module selection dropdowns

**Implementation:**

```python
from omf2.ccu.module_manager import get_ccu_module_manager

def _show_module_selector():
    """Show module selector with emoji icons."""
    
    module_manager = get_ccu_module_manager()
    modules = module_manager.get_all_modules()
    
    # Build options with emoji icons
    options = []
    for module_id, module_data in modules.items():
        emoji_icon = module_manager.get_module_icon(module_id)
        name = module_data.get('name', module_id)
        display_name = f"{emoji_icon} {name} ({module_id})"
        options.append(display_name)
    
    # Use selectbox with plain text options
    selected = st.selectbox(
        "Select Module:",
        options,
        key="module_selector"
    )
    
    return selected
```

**Key Points:**
- Use `get_module_icon()` NOT `get_module_icon_html()`
- Selectbox only accepts plain text strings
- Include module ID in display name for identification
- Emoji icons provide visual consistency

---

### Pattern 3: Emoji Icons in Dataframe

**When to use:** Displaying tabular data with Streamlit's native dataframe

**Implementation:**

```python
from omf2.ccu.module_manager import get_ccu_module_manager
import pandas as pd

def _show_messages_dataframe(messages):
    """Show messages table with emoji icons."""
    
    module_manager = get_ccu_module_manager()
    
    # Build dataframe with emoji icons
    data = []
    for msg in messages:
        module_id = msg.get('module_id')
        emoji_icon = module_manager.get_module_icon(module_id)
        
        data.append({
            'Module': f"{emoji_icon} {msg.get('module_name')}",
            'Topic': msg.get('topic'),
            'Timestamp': msg.get('timestamp')
        })
    
    df = pd.DataFrame(data)
    
    # Display with native dataframe
    st.dataframe(df, use_container_width=True)
```

**Key Points:**
- Use `get_module_icon()` NOT `get_module_icon_html()`
- Build emoji icons into dataframe column values
- st.dataframe displays plain text only
- Emoji icons provide consistent visual representation

---

### Pattern 4: SVG Icons in Headers and Large Displays

**When to use:** Page headers, detail views, icon galleries

**Implementation:**

```python
from omf2.ccu.module_manager import get_ccu_module_manager

def _show_module_details(module_id):
    """Show module details with SVG icons."""
    
    module_manager = get_ccu_module_manager()
    modules = module_manager.get_all_modules()
    module_data = modules.get(module_id, {})
    name = module_data.get('name', module_id)
    
    # Header with 32px SVG icon
    header_icon = module_manager.get_module_icon_html(module_id, size_px=32)
    st.markdown(
        f"<h2>{header_icon} {name} Module Details</h2>",
        unsafe_allow_html=True
    )
    
    # Large icon display (200px)
    st.subheader("📊 Module Icon")
    large_icon = module_manager.get_module_icon_html(module_id, size_px=200)
    st.markdown(
        f'<div style="text-align: center;">{large_icon}</div>',
        unsafe_allow_html=True
    )
    st.caption("✨ High-quality SVG icon with CSS scoping")
```

**Key Points:**
- Use different sizes for different contexts:
  - Headers: 32px
  - Lists: 20px
  - Gallery: 48px
  - Large display: 200px
- Always use `st.markdown(..., unsafe_allow_html=True)`
- Center large icons with CSS styling
- Add helpful captions

---

## Component-Specific Guidelines

### CCU Modules Tab

**Components:**
- Tab header (32px SVG)
- Module table (20px SVG in custom HTML table)
- Module gallery (48px SVG)

**Implementation:**
```python
# Header
header_icon = module_manager.get_module_icon_html('MODULES_TAB', size_px=32)
st.markdown(f"{header_icon} <h1>CCU Modules</h1>", unsafe_allow_html=True)

# Table - use custom HTML table with _render_module_table_with_svg_icons()
_render_module_table_with_svg_icons(modules)

# Gallery
for module_id in module_ids:
    icon = module_manager.get_module_icon_html(module_id, size_px=48)
    st.markdown(icon, unsafe_allow_html=True)
```

---

### Module Details Section

**Components:**
- Visual module list (20px SVG)
- Selectbox dropdown (emoji only - Streamlit limitation)
- Module header (32px SVG)
- Large icon display (200px SVG)

**Implementation:**
```python
# Visual list with SVG icons (20px)
st.subheader("Available Modules (with SVG icons):")
for module_id in module_ids:
    icon = module_manager.get_module_icon_html(module_id, size_px=20)
    st.markdown(f"{icon} {module_name}", unsafe_allow_html=True)

# Selectbox with emoji icons (Streamlit limitation)
options = []
for module_id in module_ids:
    emoji = module_manager.get_module_icon(module_id)
    options.append(f"{emoji} {module_name} ({module_id})")
selected = st.selectbox("Select Module for Details:", options)

# Details header with SVG icon (32px)
header_icon = module_manager.get_module_icon_html(module_id, size_px=32)
st.markdown(f"<h3>{header_icon} {module_name} Details</h3>", unsafe_allow_html=True)

# Large icon display (200px)
large_icon = module_manager.get_module_icon_html(module_id, size_px=200)
st.markdown(f'<div style="text-align: center;">{large_icon}</div>', unsafe_allow_html=True)
```

---

### Message Monitor Component

**Components:**
- Module filter selectbox (emoji only - Streamlit limitation)
- Messages dataframe (emoji only - Streamlit limitation)

**Implementation:**
```python
# Selectbox filter with emoji icons
module_options = []
for module_id in module_ids:
    emoji = module_manager.get_module_icon(module_id)
    module_options.append(f"{emoji} {module_name}")
selected_filter = st.selectbox("Filter by Module:", ["All"] + module_options)

# Messages dataframe with emoji icons
data = []
for msg in messages:
    emoji = module_manager.get_module_icon(msg['module_id'])
    data.append({
        'Module': f"{emoji} {msg['module_name']}",
        'Topic': msg['topic'],
        'Timestamp': msg['timestamp']
    })
df = pd.DataFrame(data)
st.dataframe(df, use_container_width=True)
```

---

## Migration Checklist

When migrating a component to use consistent SVG/emoji icons:

### 1. Identify Icon Usage
- [ ] List all places where module icons are displayed
- [ ] Determine which Streamlit components are used
- [ ] Check if HTML rendering is supported

### 2. Import Module Manager
```python
from omf2.ccu.module_manager import get_ccu_module_manager
```

### 3. Replace Icon Lookups

**For HTML-supported components (st.markdown):**
- [ ] Replace direct icon access with `module_manager.get_module_icon_html()`
- [ ] Add `unsafe_allow_html=True` to st.markdown calls
- [ ] Choose appropriate size_px (20px, 32px, 48px, 200px)

**For plain text components (selectbox, dataframe):**
- [ ] Replace direct icon access with `module_manager.get_module_icon()`
- [ ] Ensure icons are embedded in string values
- [ ] Remove any HTML tags or st.markdown wrapping

### 4. Convert Dataframes to Custom HTML Tables (Optional)

If you need SVG icons in table format:
- [ ] Replace `st.dataframe()` with custom HTML table
- [ ] Create `_render_[component]_table_with_svg_icons()` function
- [ ] Build HTML table with `<table>`, `<thead>`, `<tbody>` structure
- [ ] Embed SVG icons in table cells
- [ ] Use `st.markdown(table_html, unsafe_allow_html=True)`

### 5. Test and Verify
- [ ] Restart Streamlit application
- [ ] Clear Python cache: `find . -type d -name __pycache__ -exec rm -rf {} +`
- [ ] Clear Streamlit cache: `streamlit cache clear`
- [ ] Verify SVG icons display correctly in HTML components
- [ ] Verify emoji icons display correctly in selectbox/dataframe
- [ ] Check console for WARNING/ERROR messages
- [ ] Verify all module serial IDs map to correct icons

### 6. Remove Old Code
- [ ] Remove hardcoded emoji icons
- [ ] Remove direct registry access
- [ ] Remove redundant SVG loading functions
- [ ] Remove duplicate icon lookup logic

---

## Common Pitfalls

### ❌ Pitfall 1: Using HTML in Selectbox

**Wrong:**
```python
# This will display HTML as plain text!
icon_html = module_manager.get_module_icon_html(module_id, size_px=24)
options = [f"{icon_html} {name}"]
st.selectbox("Select:", options)
```

**Correct:**
```python
# Use emoji icons for selectbox
emoji = module_manager.get_module_icon(module_id)
options = [f"{emoji} {name}"]
st.selectbox("Select:", options)
```

---

### ❌ Pitfall 2: Using HTML in Dataframe

**Wrong:**
```python
# This will display HTML as plain text!
df = pd.DataFrame({
    'Module': [module_manager.get_module_icon_html(id, size_px=20) + " " + name]
})
st.dataframe(df)
```

**Correct:**
```python
# Use emoji icons for dataframe
emoji = module_manager.get_module_icon(module_id)
df = pd.DataFrame({
    'Module': [f"{emoji} {name}"]
})
st.dataframe(df)
```

---

### ❌ Pitfall 3: Forgetting unsafe_allow_html

**Wrong:**
```python
# SVG will not render!
icon_html = module_manager.get_module_icon_html(module_id, size_px=32)
st.markdown(f"{icon_html} Title")
```

**Correct:**
```python
# Always include unsafe_allow_html=True for HTML/SVG
icon_html = module_manager.get_module_icon_html(module_id, size_px=32)
st.markdown(f"{icon_html} Title", unsafe_allow_html=True)
```

---

### ❌ Pitfall 4: Using Module Type Instead of Serial ID

**Wrong:**
```python
# Module Manager expects serial IDs, not types!
icon = module_manager.get_module_icon_html("HBW", size_px=24)
```

**Correct:**
```python
# Pass the module serial ID
icon = module_manager.get_module_icon_html("SVR3QA0022", size_px=24)
```

Module Manager automatically maps serial ID → module type internally.

---

### ❌ Pitfall 5: Not Restarting Streamlit After Changes

**Problem:** Changes to icon rendering code may not take effect due to caching.

**Solution:**
```bash
# Stop Streamlit (Ctrl+C)
find . -type d -name __pycache__ -exec rm -rf {} +
streamlit cache clear
python -m streamlit run omf2/omf.py
```

---

## Examples

### Example 1: Complete Module Table with SVG Icons

```python
from omf2.ccu.module_manager import get_ccu_module_manager
import streamlit as st

def show_modules_tab():
    """Complete example: Modules tab with SVG icons."""
    
    module_manager = get_ccu_module_manager()
    
    # Header with SVG icon (32px)
    header_icon = module_manager.get_module_icon_html('MODULES_TAB', size_px=32)
    st.markdown(
        f"<h1>{header_icon} CCU Modules</h1>",
        unsafe_allow_html=True
    )
    
    # Get modules
    modules = module_manager.get_all_modules()
    
    # Build custom HTML table with SVG icons
    table_html = '''
    <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="background-color: #f0f2f6;">
                <th style="padding: 8px; border: 1px solid #ddd;">ID</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Name</th>
                <th style="padding: 8px; border: 1px solid #ddd;">Status</th>
            </tr>
        </thead>
        <tbody>
    '''
    
    for module_id, module_data in modules.items():
        # Get SVG icon (20px for table)
        icon_html = module_manager.get_module_icon_html(module_id, size_px=20)
        name = module_data.get('name', module_id)
        status = module_data.get('status', 'Unknown')
        
        table_html += f'''
        <tr>
            <td style="padding: 8px; border: 1px solid #ddd;">{module_id}</td>
            <td style="padding: 8px; border: 1px solid #ddd;">
                {icon_html} {name}
            </td>
            <td style="padding: 8px; border: 1px solid #ddd;">{status}</td>
        </tr>
        '''
    
    table_html += '</tbody></table>'
    
    # Render table
    st.markdown(table_html, unsafe_allow_html=True)
    st.caption("✨ Module icons rendered as SVG graphics")
```

---

### Example 2: Module Details with Mixed Icon Types

```python
from omf2.ccu.module_manager import get_ccu_module_manager
import streamlit as st

def show_module_details():
    """Complete example: Module details with SVG and emoji icons."""
    
    module_manager = get_ccu_module_manager()
    modules = module_manager.get_all_modules()
    module_ids = list(modules.keys())
    
    # Visual list with SVG icons (20px)
    st.subheader("Available Modules (with SVG icons):")
    for module_id in module_ids:
        icon_html = module_manager.get_module_icon_html(module_id, size_px=20)
        name = modules[module_id].get('name', module_id)
        st.markdown(
            f"{icon_html} **{name}** ({module_id})",
            unsafe_allow_html=True
        )
    
    st.caption("💡 Select a module to view detailed information with SVG icons")
    
    # Selectbox with emoji icons (Streamlit limitation)
    st.subheader("Select Module for Details:")
    options = []
    for module_id in module_ids:
        emoji_icon = module_manager.get_module_icon(module_id)
        name = modules[module_id].get('name', module_id)
        options.append(f"{emoji_icon} {name} ({module_id})")
    
    selected_option = st.selectbox(
        "Module:",
        options,
        label_visibility="collapsed"
    )
    
    # Extract module ID from selection
    selected_id = selected_option.split('(')[-1].rstrip(')')
    
    # Module details header with SVG icon (32px)
    name = modules[selected_id].get('name', selected_id)
    header_icon = module_manager.get_module_icon_html(selected_id, size_px=32)
    st.markdown(
        f"<h3>{header_icon} {name} Module Details</h3>",
        unsafe_allow_html=True
    )
    
    # Large SVG icon display (200px)
    st.subheader("📊 Module Icon")
    large_icon = module_manager.get_module_icon_html(selected_id, size_px=200)
    st.markdown(
        f'<div style="text-align: center; padding: 20px;">{large_icon}</div>',
        unsafe_allow_html=True
    )
    st.caption("✨ High-quality SVG icon with CSS scoping")
```

---

### Example 3: Message Monitor with Emoji Icons

```python
from omf2.ccu.module_manager import get_ccu_module_manager
import streamlit as st
import pandas as pd

def show_message_monitor():
    """Complete example: Message monitor with emoji icons."""
    
    module_manager = get_ccu_module_manager()
    modules = module_manager.get_all_modules()
    
    # Module filter selectbox with emoji icons
    st.subheader("Filter Messages by Module")
    
    filter_options = ["All Modules"]
    for module_id, module_data in modules.items():
        emoji_icon = module_manager.get_module_icon(module_id)
        name = module_data.get('name', module_id)
        filter_options.append(f"{emoji_icon} {name}")
    
    selected_filter = st.selectbox(
        "Module Filter:",
        filter_options
    )
    
    # Sample messages data
    messages = [
        {'module_id': 'SVR3QA0022', 'topic': 'status', 'timestamp': '10:30:15'},
        {'module_id': 'SVR4H76449', 'topic': 'position', 'timestamp': '10:30:20'},
        {'module_id': 'SVR3QA2098', 'topic': 'error', 'timestamp': '10:30:25'},
    ]
    
    # Build dataframe with emoji icons
    data = []
    for msg in messages:
        module_id = msg['module_id']
        emoji_icon = module_manager.get_module_icon(module_id)
        name = modules.get(module_id, {}).get('name', module_id)
        
        data.append({
            'Module': f"{emoji_icon} {name}",
            'Topic': msg['topic'],
            'Timestamp': msg['timestamp']
        })
    
    df = pd.DataFrame(data)
    
    # Display dataframe
    st.subheader("Received Messages")
    st.dataframe(df, use_container_width=True)
    st.caption("Note: Emoji icons used due to Streamlit dataframe limitations")
```

---

## Summary

### Key Takeaways

1. **Always use Module Manager** for consistent icon rendering
   - `get_module_icon_html()` for HTML components
   - `get_module_icon()` for plain text components

2. **Know Streamlit's limitations**
   - `st.selectbox()` and `st.dataframe()` don't support HTML
   - Use emoji icons for these components
   - Use SVG icons everywhere else via `st.markdown(..., unsafe_allow_html=True)`

3. **For tables with SVG icons**
   - Replace `st.dataframe()` with custom HTML table
   - Build table with proper HTML structure
   - Render with `st.markdown(table_html, unsafe_allow_html=True)`

4. **Choose appropriate icon sizes**
   - Table cells: 20px
   - Headers: 32px
   - Gallery: 48px
   - Large display: 200px

5. **Always restart Streamlit** after making icon-related code changes

---

## Support

For questions or issues:
- Review this guide
- Check Module Manager implementation (`omf2/ccu/module_manager.py`)
- Check symbols helper (`omf2/ui/common/symbols.py`)
- Review test cases (`tests/test_omf2/test_symbols.py`)

---

**Document Version:** 1.0  
**Last Updated:** 2025-10-30  
**Author:** ORBIS Development Team
