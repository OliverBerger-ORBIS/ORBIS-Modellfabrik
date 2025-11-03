# Shopfloor Test App (examples/shopfloor_test_app)

This example adds a standalone Streamlit test app that renders the interactive, scalable SVG shopfloor layout used in the project.

## Contents

- `app.py`: Main Streamlit application with interactive shopfloor layout visualization
- `route_utils.py`: Route computation utilities (graph building, path finding, position mapping)
- `shopfloor_layout.json`: Shopfloor layout configuration (3x4 grid with modules, intersections, and roads)
- `README.md`: This file

## Features

- **Interactive SVG Rendering**: Scalable shopfloor layout with hover/click support
- **Route Visualization**: Visualize AGV/FTS routes between modules and intersections
- **Programmatic Highlighting**: Highlight specific cells programmatically
- **Asset Manager Integration**: Uses `omf2.assets.asset_manager` for SVG icons when available

## Usage

### Running the Test App

```bash
streamlit run examples/shopfloor_test_app/app.py
```

The app will start on the default Streamlit port (usually 8501).

### Comparing with Production Tabs

To manually compare the behavior with the production implementations:

1. **CCU Configuration Tab** (`omf2/ui/ccu/ccu_configuration/ccu_factory_configuration_subtab.py`):
   - Factory layout visualization
   - Module selection and highlighting
   - Intersection display

2. **CCU Orders Tab** (`omf2/ui/ccu/ccu_orders/production_orders_subtab.py`):
   - Production order visualization
   - Active module highlighting
   - Route display for AGV/FTS movements

## API

### `show_shopfloor_layout()`

Main function for embedding the shopfloor layout in other Streamlit apps:

```python
from examples.shopfloor_test_app.app import show_shopfloor_layout

show_shopfloor_layout(
    title="Shopfloor Layout",
    unique_key="shopfloor_demo",
    mode="view",
    enable_click=True,
    highlight_cells=[[2, 0]],  # Highlight DRILL module
    route_points=[(100, 100), (200, 200), (300, 300)],  # Route visualization
    agv_progress=0.5,  # AGV position along route (0.0-1.0)
    show_controls=True
)
```

### `render_shopfloor_svg()`

Pure renderer function (no Streamlit dependencies) for testing:

```python
from examples.shopfloor_test_app.app import render_shopfloor_svg
import json

layout = json.load(open("examples/shopfloor_test_app/shopfloor_layout.json"))
svg = render_shopfloor_svg(
    layout,
    highlight_cells=[(2, 0)],
    route_points=[(100, 100), (200, 200)],
    scale=1.0
)
```

## Route Utilities

### `build_graph(layout)`

Builds an undirected adjacency graph from the layout's roads configuration.

### `find_path(graph, start, goal)`

Finds the shortest path between two nodes using BFS.

### `id_to_position_map(layout, cell_size=200)`

Maps node IDs (intersection IDs, module IDs, serial numbers) to pixel coordinates.

## Testing

Run the pytest tests:

```bash
pytest tests/test_shopfloor_layout_render.py -v
```

## Notes

- The app uses `omf2.assets.asset_manager` when available, but gracefully degrades if not present
- SVG rendering is pure Python (no Streamlit dependencies in the renderer function)
- Route computation follows the rules specified in the conversation (intersections, roads, start/goal rules for HBW/DPS)

