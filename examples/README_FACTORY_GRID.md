# Factory Grid Example - Interactive Shopfloor Layout

This example demonstrates an interactive factory/shopfloor grid with click and double-click event handling in Streamlit, using the `streamlit-bokeh-events` pattern for JavaScript event integration.

## Overview

The factory grid is a 3x4 layout representing a shopfloor with production modules. Users can:

- **Single-click** a module to select and highlight it
- **Double-click** a module to open a detail panel with navigation options
- View event history and current state in real-time

## Architecture

### Components

1. **factory_grid.html** - Self-contained HTML file with:
   - SVG-based 3x4 grid layout
   - Interactive JavaScript for hover, click, and double-click events
   - Event dispatching via `postMessage` and `CustomEvent`
   - Visual feedback (highlighting, selection state)

2. **streamlit_factory_app.py** - Streamlit application that:
   - Embeds the HTML grid using `st.components.v1.html`
   - Captures events using `streamlit-bokeh-events`
   - Manages UI state (selected module, detail panel)
   - Provides navigation and drill-down functionality

3. **requirements.txt** - Minimal dependencies:
   - `streamlit>=1.28.0` - Web framework
   - `bokeh>=3.3.0` - Required by streamlit-bokeh-events
   - `streamlit-bokeh-events>=0.1.2` - Event bridge

## Grid Layout

### Special Cells (0,0) and (0,3)

Positions (0,0) and (0,3) are split into:
- One rectangle (main area)
- Two squares (sub-areas)

This creates a total of 16 modules:
- **0-0-main**, **0-0-sub1**, **0-0-sub2** (position 0,0)
- **0-1**, **0-2** (positions 0,1 and 0,2)
- **0-3-main**, **0-3-sub1**, **0-3-sub2** (position 0,3)
- **1-0**, **1-1**, **1-2**, **1-3** (row 1)
- **2-0**, **2-1**, **2-2**, **2-3** (row 2)

### Visual Layout

```
┌───────────┬───────────┬───────────┬───────────┐
│ 0-0-main  │           │           │ 0-3-main  │
├─────┬─────┤   0-1     │   0-2     ├─────┬─────┤
│0-0  │0-0  │           │           │0-3  │0-3  │
│-sub1│-sub2│           │           │-sub1│-sub2│
├─────┴─────┼───────────┼───────────┼─────┴─────┤
│           │           │           │           │
│   1-0     │   1-1     │   1-2     │   1-3     │
│           │           │           │           │
├───────────┼───────────┼───────────┼───────────┤
│           │           │           │           │
│   2-0     │   2-1     │   2-2     │   2-3     │
│           │           │           │           │
└───────────┴───────────┴───────────┴───────────┘
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Navigate to the examples directory:
   ```bash
   cd examples
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

   Or install from the repository root:
   ```bash
   pip install -r examples/requirements.txt
   ```

## Usage

### Running the Application

```bash
streamlit run streamlit_factory_app.py
```

Or from the repository root:
```bash
streamlit run examples/streamlit_factory_app.py
```

The application will open in your default browser at `http://localhost:8501`.

### Standalone HTML Grid

You can also open `factory_grid.html` directly in a browser to see the interactive grid without Streamlit:

```bash
# On Linux/Mac
open factory_grid.html

# On Windows
start factory_grid.html
```

The standalone version includes a built-in event log at the bottom.

## Event Flow

### 1. User Interaction
User clicks or double-clicks on a module in the SVG grid.

### 2. JavaScript Event Handling
The HTML file's JavaScript:
```javascript
// Single-click creates event
{
    type: 'module-click',
    id: 'module-id',
    timestamp: '2025-10-16T...'
}

// Double-click creates event
{
    type: 'module-dblclick',
    id: 'module-id',
    timestamp: '2025-10-16T...'
}
```

### 3. Event Dispatch
Events are sent via two mechanisms:
- **postMessage**: For iframe communication
- **CustomEvent**: For direct DOM event handling

### 4. Bokeh Event Bridge
The Streamlit app uses `streamlit-bokeh-events` to capture custom events:
```python
event_result = streamlit_bokeh_events(
    bokeh_plot=plot,
    events="GET_FACTORY_EVENT",
    key="factory_events",
    refresh_on_update=True,
    debounce_time=100
)
```

### 5. Python Event Processing
The Streamlit app processes events and updates state:
```python
if event_type == 'module-click':
    st.session_state.selected_module = module_id
    # Update UI...

elif event_type == 'module-dblclick':
    st.session_state.show_detail = True
    st.session_state.detail_module = module_id
    # Show detail panel...
```

### 6. UI Update
Streamlit reruns to reflect the new state:
- Highlight selected module
- Show detail panel
- Update event history

## Features

### Interactive Grid
- **Hover Effect**: Modules show visual feedback on hover
- **Selection**: Single-click highlights the selected module (green)
- **Multi-select**: Only one module can be selected at a time

### Event Handling
- **Click Events**: Select a module and update the UI state
- **Double-click Events**: Open detailed information panel
- **Event History**: Track all interactions with timestamps

### Detail Panel
When a module is double-clicked:
- Shows module information (type, status, location)
- Provides navigation buttons (Performance, Maintenance, Inventory views)
- Includes expandable drill-down data
- Can be closed to return to grid view

### State Management
- **Session State**: Persistent across reruns
- **Selected Module**: Tracked and displayed in sidebar
- **Detail View**: Toggle between grid and detail views
- **Event Log**: Maintains history of all interactions

## Configuration Options

The sidebar provides several options:

- **Show Debug Info**: Display session state and debug information
- **Show Event Log**: Toggle event history display
- **Reset State**: Clear all selections and event history

## Customization

### Adding New Modules

To add or modify modules in `factory_grid.html`:

1. Add a new `<rect>` element with the `module-cell` class:
   ```html
   <rect class="module-cell" 
         id="module-X-Y" 
         x="..." y="..." 
         width="..." height="..." 
         fill="#COLOR" 
         data-module-id="X-Y"/>
   ```

2. Add a label:
   ```html
   <text class="module-label" 
         x="..." y="..." 
         text-anchor="middle">Module X-Y</text>
   ```

### Styling

Modify the CSS in `factory_grid.html` to change colors, borders, and hover effects:

```css
.module-cell {
    stroke: #333;
    stroke-width: 2;
    cursor: pointer;
}

.module-cell:hover {
    stroke: #0066cc;
    stroke-width: 3;
}

.module-cell.selected {
    fill: #4CAF50 !important;
    stroke: #2E7D32;
}
```

### Event Processing

Modify `streamlit_factory_app.py` to add custom event handling logic:

```python
if event_type == 'module-click':
    # Custom click handling
    st.session_state.selected_module = module_id
    # Add your logic here

elif event_type == 'module-dblclick':
    # Custom double-click handling
    st.session_state.show_detail = True
    # Add your logic here
```

## Troubleshooting

### Events Not Captured

If events are not being captured by Streamlit:

1. **Check dependencies**: Ensure `streamlit-bokeh-events` is installed:
   ```bash
   pip show streamlit-bokeh-events
   ```

2. **Verify bokeh version**: The bokeh version must be compatible:
   ```bash
   pip show bokeh
   ```

3. **Browser console**: Check for JavaScript errors in the browser console (F12)

4. **Fallback**: Use the manual buttons in the control panel as a fallback

### HTML File Not Found

If you see "factory_grid.html not found":

1. Ensure you're running the app from the correct directory
2. Check that `factory_grid.html` is in the same directory as `streamlit_factory_app.py`
3. Verify file permissions

### Display Issues

If the grid doesn't display properly:

1. **Browser compatibility**: Use a modern browser (Chrome, Firefox, Safari, Edge)
2. **Zoom level**: Reset browser zoom to 100%
3. **Window size**: Ensure the browser window is wide enough

## Integration with Existing Systems

### MQTT Integration

To integrate with an MQTT system:

```python
import paho.mqtt.client as mqtt

def on_module_click(module_id):
    client.publish(f"factory/module/{module_id}/selected", "true")

def on_module_dblclick(module_id):
    client.publish(f"factory/module/{module_id}/details", "request")
```

### Database Integration

To log events to a database:

```python
import sqlite3

def log_event_to_db(event_type, module_id, timestamp):
    conn = sqlite3.connect('factory_events.db')
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (type, module_id, timestamp) VALUES (?, ?, ?)",
        (event_type, module_id, timestamp)
    )
    conn.commit()
    conn.close()
```

### REST API Integration

To send events to a REST API:

```python
import requests

def send_event_to_api(event_type, module_id):
    response = requests.post(
        "https://api.example.com/factory/events",
        json={"type": event_type, "module_id": module_id}
    )
    return response.json()
```

## Advanced Usage

### Custom Views

Create navigation to custom views based on module selection:

```python
if st.session_state.selected_module:
    view_type = st.selectbox("View", ["Overview", "Performance", "Maintenance"])
    
    if view_type == "Performance":
        show_performance_metrics(st.session_state.selected_module)
    elif view_type == "Maintenance":
        show_maintenance_schedule(st.session_state.selected_module)
```

### Multi-page Applications

Integrate the grid into a multi-page Streamlit app:

```python
# pages/factory_grid.py
import streamlit as st
from streamlit_factory_app import render_factory_grid

st.title("Factory Grid")
render_factory_grid()

# pages/analytics.py
import streamlit as st

st.title("Analytics Dashboard")
# Analytics content...
```

## Performance Considerations

- **Event Debouncing**: The `debounce_time=100` parameter prevents event flooding
- **State Management**: Use session state efficiently to avoid unnecessary reruns
- **HTML Embedding**: The grid is loaded once; only events trigger updates

## License

This example is part of the ORBIS-Modellfabrik project. See the main repository LICENSE file for details.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the [streamlit-bokeh-events documentation](https://github.com/ash2shukla/streamlit-bokeh-events)
3. Open an issue in the ORBIS-Modellfabrik repository

## References

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Bokeh Documentation](https://docs.bokeh.org/)
- [streamlit-bokeh-events GitHub](https://github.com/ash2shukla/streamlit-bokeh-events)
- [MDN Web Docs - SVG](https://developer.mozilla.org/en-US/docs/Web/SVG)
- [MDN Web Docs - CustomEvent](https://developer.mozilla.org/en-US/docs/Web/API/CustomEvent)
