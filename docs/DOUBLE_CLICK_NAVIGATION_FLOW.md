# Double-Click Navigation Flow Diagram

```
┌──────────────────────────────────────────────────────────────────────┐
│                         SHOPFLOOR LAYOUT                             │
│                     (shopfloor_layout.py)                            │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ User double-clicks module
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                    JavaScript Event Handler                          │
│  handleModuleDoubleClick(event)                                      │
│  - Gets moduleId, moduleType from data attributes                   │
│  - Creates FACTORY_GRID_EVENT custom event                          │
│  - Dispatches event to document                                     │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Event captured
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  streamlit-bokeh-events                              │
│  Captures custom event and sends to Python                          │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Event data
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                  _handle_grid_event()                                │
│  if event_type == "module-dblclick":                                 │
│    - st.session_state.preselected_module_id = module_id             │
│    - st.session_state.preselected_module_type = module_type         │
│    - st.session_state.show_module_details = True                    │
│    - st.rerun()                                                      │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Page reloads
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                     SHOPFLOOR LAYOUT                                 │
│  Detects preselected_module_id in session state                     │
│  Shows: "✅ Module MILL preselected! Navigate to CCU Modules tab"   │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ User manually navigates
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                      CCU MODULES TAB                                 │
│                   (ccu_modules_tab.py)                               │
│  render_ccu_modules_tab()                                            │
│  - Checks for preselected_module_id                                  │
│  - Shows: "🎯 Module MILL selected from shopfloor layout"           │
└──────────────────────────────────────────────────────────────────────┘
                                    │
                                    │ Renders tab content
                                    ▼
┌──────────────────────────────────────────────────────────────────────┐
│                   MODULE DETAILS SECTION                             │
│                (ccu_modules_details.py)                              │
│  show_module_details_section()                                       │
│  - Gets preselected_module_id from session state                    │
│  - Finds module in module_options                                    │
│  - Sets dropdown index = module index                                │
│  - Clears session state variables                                    │
│  - Displays module SVG and factsheet                                 │
└──────────────────────────────────────────────────────────────────────┘
```

## Session State Variables

| Variable | Type | Purpose | Lifecycle |
|----------|------|---------|-----------|
| `preselected_module_id` | str | Stores the ID of the double-clicked module | Set on double-click, cleared after dropdown selection |
| `preselected_module_type` | str | Stores the type of the double-clicked module | Set on double-click, cleared after dropdown selection |
| `show_module_details` | bool | Flag to indicate module details should be shown | Set on double-click, cleared after dropdown selection |

## Visual Feedback

### In Shopfloor Layout (after double-click):
- **ccu_configuration mode**: Blue border (`#2196F3`) with semi-transparent fill
- **interactive mode**: Pink border (`#E91E63`)
- Success message: "✅ Module **{module_id}** preselected! Navigate to **CCU Modules** tab to see details."

### In CCU Modules Tab:
- Info message at top: "🎯 **Module {module_id}** selected from shopfloor layout. Scroll down to Module Details section."

### In Module Details:
- Dropdown automatically shows the selected module
- Module SVG and factsheet data displayed below
