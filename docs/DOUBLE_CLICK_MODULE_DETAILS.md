# Double-Click Module Details Implementation

## Overview

This document describes the implementation of double-click functionality to show module details in the same tab (CCU Configuration) without tab switching.

## User Experience

When a user double-clicks on a module in the Shopfloor Layout:

1. **Visual Feedback**: Module border changes color (blue in ccu_configuration mode, pink in interactive mode)
2. **Same-Tab Display**: Module details appear immediately below the Shopfloor Layout
3. **No Tab Switching**: User stays in the CCU Configuration tab
4. **Close Button**: User can close the module details with an ✖️ button

## Architecture

### 1. Event Capture (shopfloor_layout.py)

Double-click events are captured via JavaScript in the SVG grid:

```javascript
function handleModuleDoubleClick(event) {
    const moduleId = event.target.getAttribute('data-module-id');
    const moduleType = event.target.getAttribute('data-module-type');
    
    // Dispatch custom event
    const eventData = {
        type: 'module-dblclick',
        id: moduleId,
        moduleType: moduleType
    };
    
    document.dispatchEvent(new CustomEvent('FACTORY_GRID_EVENT', {
        detail: eventData
    }));
}
```

### 2. Event Processing (shopfloor_layout.py)

Events are processed via `streamlit-bokeh-events`:

```python
def _handle_grid_event(event_data: Dict[str, Any]):
    event_type = event_data.get("type")
    module_id = event_data.get("id")
    module_type = event_data.get("moduleType")

    if event_type == "module-dblclick":
        # Show module details in same tab
        st.session_state.selected_module_id = module_id
        st.session_state.selected_module_type = module_type
        st.session_state.show_module_details = True
        st.rerun()
```

### 3. Module Details Display (ccu_factory_configuration_subtab.py)

Module details are shown conditionally after the Shopfloor Layout:

```python
def render_ccu_factory_configuration_subtab():
    # ... Shopfloor Layout ...
    
    # Module Details Section (shown after double-click)
    if st.session_state.get("show_module_details") and st.session_state.get("selected_module_id"):
        st.divider()
        _show_module_details_section()
```

### 4. Registry Integration

Module data is fetched from the Registry Manager:

```python
def _show_module_details_section():
    registry_manager = get_registry_manager()
    
    # Get registry data
    modules = registry_manager.get_modules()
    stations = registry_manager.get_stations()
    txt_controllers = registry_manager.get_txt_controllers()
    
    # Display module SVG + information
```

## UI Layout

```
┌─────────────────────────────────────┐
│ CCU Configuration Tab               │
├─────────────────────────────────────┤
│ Factory Configuration Subtab        │
│ ├── Factory Controls (expandable)    │
│ ├── Shopfloor Layout (3x4 Grid)     │
│ │   [User double-clicks MILL]        │
│ ├── ─────────────────────────────   │
│ └── Module Details Section          │
│     ┌─────────────────────────────┐ │
│     │ 🔧 Module Details: MILL  ✖️ │ │
│     ├─────────────────────────────┤ │
│     │ 📊 SVG │ 📋 Module Info     │ │
│     │  Icon  │ - ID: MILL         │ │
│     │        │ - Name: ...        │ │
│     │        │ - Type: ...        │ │
│     │        │                    │ │
│     │        │ Station Info:      │ │
│     │        │ - IP: ...          │ │
│     │        │                    │ │
│     │        │ TXT Controller:    │ │
│     │        │ - IP: ...          │ │
│     └─────────────────────────────┘ │
└─────────────────────────────────────┘
```

## Session State Variables

| Variable | Type | Purpose | Lifecycle |
|----------|------|---------|-----------|
| `selected_module_id` | str | ID of the selected module | Set on double-click, cleared on close |
| `selected_module_type` | str | Type of the selected module | Set on double-click, cleared on close |
| `show_module_details` | bool | Flag to show/hide module details | Set on double-click, cleared on close |

## Module Information Displayed

### From Registry Modules
- Module ID
- Module Name
- Module Type
- Enabled status
- Icon
- Serial Number

### From Registry Stations (if linked)
- Station ID
- IP Address
- OPC UA Port
- Description

### From Registry TXT Controllers (if linked)
- Controller ID
- IP Address
- MQTT Port
- Description
- Linked Module (via `zugeordnet_zu_modul` field)

## Files Modified

1. **omf2/ui/ccu/common/shopfloor_layout.py**
   - Changed `_handle_grid_event()` to set `selected_module_id` instead of `preselected_module_id`
   - Removed navigation hint message
   - Session state now shows module details in same tab

2. **omf2/ui/ccu/ccu_configuration/ccu_factory_configuration_subtab.py**
   - Added conditional rendering of module details section
   - Implemented `_show_module_details_section()` function
   - Implemented `_display_module_svg()` function
   - Implemented `_display_module_info()` function
   - Added Registry Manager integration

3. **requirements.txt**
   - streamlit-bokeh-events>=0.1.2 (already added)

## Benefits Over Tab Switching

1. **Better UX**: User stays in context, no tab switching needed
2. **Faster**: Immediate display of module details
3. **Simpler**: No need to guide user to another tab
4. **Clearer**: Module details appear right below the clicked module location
5. **More Intuitive**: Direct cause-and-effect relationship

## Testing

1. Navigate to CCU Configuration tab
2. Double-click any module in the Shopfloor Layout (e.g., MILL, DRILL)
3. Verify module details appear below the layout
4. Verify SVG icon is displayed
5. Verify module information is shown
6. Verify station and TXT controller information (if available)
7. Click the ✖️ Close button
8. Verify module details disappear

## Future Enhancements

- Add edit functionality for module configuration
- Add more detailed station/controller information
- Add link to edit module in Registry
- Add module status information from MQTT
- Add module history/logs
