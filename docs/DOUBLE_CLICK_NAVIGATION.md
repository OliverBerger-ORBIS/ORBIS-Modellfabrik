# Double-Click Navigation Implementation

## Overview

This document describes the implementation of double-click navigation from the Shopfloor Layout to the CCU Modules Details section.

## Architecture

The implementation uses a session state-based approach to enable navigation between the Shopfloor Layout view and the CCU Modules tab.

### Components Involved

1. **shopfloor_layout.py** - Handles the double-click events from the SVG grid
2. **ccu_modules_tab.py** - Shows navigation hints when a module is preselected
3. **ccu_modules_details.py** - Automatically selects the preselected module in the dropdown

## How It Works

### 1. Event Capture (shopfloor_layout.py)

When a user double-clicks on a module in the shopfloor layout:

```javascript
// JavaScript in the SVG HTML
function handleModuleDoubleClick(event) {
    const moduleId = event.target.getAttribute('data-module-id');
    const moduleType = event.target.getAttribute('data-module-type');
    
    // Dispatch custom event
    const eventData = {
        type: 'module-dblclick',
        id: moduleId,
        moduleType: moduleType,
        timestamp: new Date().toISOString()
    };
    
    const customEvent = new CustomEvent('FACTORY_GRID_EVENT', {
        detail: eventData
    });
    document.dispatchEvent(customEvent);
}
```

### 2. Event Processing (shopfloor_layout.py)

The event is captured by `streamlit-bokeh-events` and processed:

```python
def _handle_grid_event(event_data: Dict[str, Any]):
    event_type = event_data.get("type")
    module_id = event_data.get("id")
    module_type = event_data.get("moduleType")

    if event_type == "module-dblclick":
        # Set session state for navigation
        st.session_state.preselected_module_id = module_id
        st.session_state.preselected_module_type = module_type
        st.session_state.show_module_details = True
        
        # Trigger rerun
        st.rerun()
```

### 3. Navigation Hint (ccu_modules_tab.py)

When the CCU Modules tab is rendered, it checks for a preselected module:

```python
def render_ccu_modules_tab(ccu_gateway=None, registry_manager=None):
    # Check if we have a preselected module
    if st.session_state.get("preselected_module_id"):
        module_id = st.session_state.get("preselected_module_id")
        st.info(f"🎯 Module {module_id} selected from shopfloor layout. Scroll down to Module Details section.")
```

### 4. Module Selection (ccu_modules_details.py)

The module details section automatically selects the preselected module:

```python
def show_module_details_section(ccu_gateway, i18n):
    # Check if we have a preselected module
    preselected_module_id = st.session_state.get("preselected_module_id")
    
    # Find the index of preselected module
    default_index = 0
    if preselected_module_id:
        for i, (display_name, module_id) in enumerate(module_options.items()):
            if module_id == preselected_module_id:
                default_index = i
                break
    
    # Show dropdown with preselected module
    selected_module_display = st.selectbox(
        "Select Module for Details:", 
        options=list(module_options.keys()), 
        index=default_index,
        key="module_details_selector"
    )
    
    # Clear session state after use
    if preselected_module_id:
        st.session_state.pop("preselected_module_id", None)
        st.session_state.pop("preselected_module_type", None)
```

## Limitations

Due to Streamlit's architecture, programmatic tab switching is not supported with `st.tabs()`. Therefore:

1. The user must manually navigate to the **CCU Modules** tab after double-clicking
2. A success message is shown in the shopfloor layout to guide the user
3. An info message is shown at the top of the CCU Modules tab to indicate the preselected module

## User Experience

### From Shopfloor Layout:
1. User double-clicks on a module (e.g., "MILL")
2. Visual feedback: Module border changes to blue (in ccu_configuration mode) or pink (in interactive mode)
3. Success message appears: "✅ Module MILL preselected! Navigate to CCU Modules tab to see details."

### In CCU Modules Tab:
1. Info message appears: "🎯 Module MILL selected from shopfloor layout. Scroll down to Module Details section."
2. The Module Details dropdown is automatically set to the selected module
3. Module SVG and factsheet data are displayed

## Dependencies

- **streamlit-bokeh-events**: Used to capture custom events from the Bokeh plot
- **bokeh**: Used to create the event capture mechanism

Both dependencies are added to `requirements.txt`.

## Testing

To test the implementation manually:

1. Run the Streamlit application
2. Navigate to a page with the Shopfloor Layout (e.g., CCU Configuration tab)
3. Double-click on any module in the grid
4. Observe the success message
5. Navigate to the CCU Modules tab
6. Verify the info message appears
7. Scroll to Module Details section
8. Verify the correct module is selected in the dropdown

## Future Improvements

- Investigate using Streamlit's experimental features for programmatic tab navigation
- Add animation/scrolling to automatically focus on the Module Details section
- Implement a "back to shopfloor" button in the Module Details section
