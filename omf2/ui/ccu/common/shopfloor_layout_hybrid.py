"""
Hybrid Shopfloor Layout - OMF2 Integration mit Copilot's SVG-Struktur
====================================================================

Kombiniert:
- Copilot's robuste SVG-basierte Grid-Struktur
- OMF2 Asset Manager für echte SVG-Icons
- Clickable Module mit Navigation zu Detail-Seiten
- Interaktive Events (Click/Double-click)

Features:
- 3x4 Grid mit speziellen Zellen (0,0) und (0,3)
- Echte OMF2 SVG-Icons (ORBIS-Logo, shelves, conveyor_belt, etc.)
- Event-Handling für Module-Navigation
- Integration in bestehende OMF2-Architektur
"""

import re
from pathlib import Path
from typing import Any, Dict, Optional

import streamlit as st
from bokeh.models import CustomJS
from bokeh.plotting import figure
from streamlit_bokeh_events import streamlit_bokeh_events

# OMF2 Imports
from omf2.assets import get_asset_manager
from omf2.ccu.config_loader import get_ccu_config_loader
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def show_shopfloor_layout_hybrid(
    active_module_id: Optional[str] = None,
    active_intersections: Optional[list] = None,
    title: str = "Shopfloor Layout",
    show_controls: bool = True,
    unique_key: Optional[str] = None,
) -> None:
    """
    Zeigt das interaktive Shopfloor Layout mit OMF2-Integration

    Args:
        active_module_id: ID des aktiven Moduls (für Hervorhebung)
        active_intersections: Liste aktiver Intersections
        title: Titel der Komponente
        show_controls: Ob Steuerungselemente angezeigt werden sollen
        unique_key: Eindeutiger Key für Streamlit-Komponenten (verhindert Key-Konflikte)
    """
    st.subheader(f"🏭 {title}")

    # Asset Manager initialisieren
    asset_manager = get_asset_manager()

    # Layout-Konfiguration laden
    config_loader = get_ccu_config_loader()
    layout_config = config_loader.load_shopfloor_layout()

    # HTML-Grid generieren
    grid_html = _generate_omf2_svg_grid(layout_config, asset_manager, active_module_id, active_intersections)

    # Event-Handling Setup
    _setup_event_handling()

    # Grid anzeigen
    st.components.v1.html(grid_html, height=500, scrolling=False)

    # Event-Verarbeitung
    _process_grid_events(unique_key)


def _generate_omf2_svg_grid(
    layout_config: Dict[str, Any],
    asset_manager,
    active_module_id: Optional[str] = None,
    active_intersections: Optional[list] = None,
) -> str:
    """Generiert das SVG-Grid mit OMF2-Integration"""

    # Grid-Dimensionen - kompakter
    grid_width = 600
    grid_height = 450
    cell_width = 150
    cell_height = 150

    # SVG-Header
    svg_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ margin: 0; padding: 4px; font-family: Arial, sans-serif; }}
            svg {{ display: block; margin: 0 auto; }}
            .module-cell {{
                stroke: #e0e0e0;
                stroke-width: 0.5;
                cursor: pointer;
                transition: all 0.2s ease;
            }}
            .module-cell:hover {{
                stroke: #0066cc;
                stroke-width: 2;
            }}
            .module-cell.selected {{
                fill: #FF9800 !important;    /* Orange Füllung */
                stroke: #FF9800 !important;
                stroke-width: 0;             /* Keine Umrandung */
            }}
            .module-label {{
                font-family: Arial, sans-serif;
                font-size: 12px;
                font-weight: bold;
                fill: #333;
                pointer-events: none;
                text-anchor: middle;
            }}
            .orbis-logo {{
                font-size: 10px;
                fill: #164194;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <svg width="{grid_width}" height="{grid_height}" viewBox="0 0 {grid_width} {grid_height}">
            <!-- Grid Background -->
            <rect x="0" y="0" width="{grid_width}" height="{grid_height}" fill="#fafafa"/>
    """

    # Module aus Konfiguration laden
    modules = layout_config.get("modules", [])
    empty_positions = layout_config.get("empty_positions", [])
    intersections = layout_config.get("intersections", [])

    # Grid-Positionen generieren
    for row in range(3):
        for col in range(4):
            x_pos = col * cell_width
            y_pos = row * cell_height

            # Spezielle Behandlung für Positionen (0,0) und (0,3)
            if (row == 0 and col == 0) or (row == 0 and col == 3):
                svg_content += _generate_split_cell_svg(
                    row, col, x_pos, y_pos, cell_width, cell_height, asset_manager, active_module_id
                )
            else:
                # Normale Zelle
                cell_data = _find_cell_data(row, col, modules, empty_positions, intersections)
                svg_content += _generate_normal_cell_svg(
                    row, col, x_pos, y_pos, cell_width, cell_height, cell_data, asset_manager, active_module_id
                )

    # JavaScript für Event-Handling
    svg_content += """
        </svg>

        <script>
            let selectedModule = null;

            // Event-Handler für Module-Clicks
            function handleModuleClick(event) {
                const moduleId = event.target.getAttribute('data-module-id');
                const moduleType = event.target.getAttribute('data-module-type');

                // Vorherige Auswahl entfernen
                if (selectedModule) {
                    selectedModule.classList.remove('selected');
                }

                // Neue Auswahl
                event.target.classList.add('selected');
                selectedModule = event.target;

                // Event an Streamlit senden
                const eventData = {
                    type: 'module-click',
                    id: moduleId,
                    moduleType: moduleType,
                    timestamp: new Date().toISOString()
                };

                // PostMessage für iframe communication
                if (window.parent !== window) {
                    window.parent.postMessage({
                        type: 'FACTORY_GRID_EVENT',
                        data: eventData
                    }, '*');
                }

                // CustomEvent für direkte DOM communication
                const customEvent = new CustomEvent('FACTORY_GRID_EVENT', {
                    detail: eventData
                });
                document.dispatchEvent(customEvent);
            }

            // Event-Handler für Module-Double-Clicks
            function handleModuleDoubleClick(event) {
                const moduleId = event.target.getAttribute('data-module-id');
                const moduleType = event.target.getAttribute('data-module-type');
                const position = event.target.getAttribute('data-position');

                // Debug-Logging für Doppelklicks
                console.log('🖱️ DOUBLE CLICK:', { moduleId, moduleType, position });
                console.log('🔍 DEBUG: Double-click on', moduleId, 'at position', position);

                const eventData = {
                    type: 'module-dblclick',
                    id: moduleId,
                    moduleType: moduleType,
                    position: position,
                    timestamp: new Date().toISOString()
                };

                // Event an Streamlit senden
                if (window.parent !== window) {
                    window.parent.postMessage({
                        type: 'FACTORY_GRID_EVENT',
                        data: eventData
                    }, '*');
                }

                const customEvent = new CustomEvent('FACTORY_GRID_EVENT', {
                    detail: eventData
                });
                document.dispatchEvent(customEvent);
            }

            // Event-Listener hinzufügen
            document.addEventListener('DOMContentLoaded', function() {
                const moduleCells = document.querySelectorAll('.module-cell');
                moduleCells.forEach(cell => {
                    cell.addEventListener('click', handleModuleClick);
                    cell.addEventListener('dblclick', handleModuleDoubleClick);
                });
            });
        </script>
    </body>
    </html>
    """

    return svg_content


def _generate_split_cell_svg(
    row: int,
    col: int,
    x_pos: int,
    y_pos: int,
    cell_width: int,
    cell_height: int,
    asset_manager,
    active_module_id: Optional[str],
) -> str:
    """Generiert SVG für aufgeteilte Zellen (0,0) und (0,3)"""

    # Position-ID basierend auf Koordinaten
    position_id = "EMPTY1" if (row == 0 and col == 0) else "EMPTY2"

    # Icons dynamisch über Asset Manager laden - FLEXIBEL!
    # Asset Manager entscheidet automatisch über die richtigen SVGs
    # Normale Größen ohne 20% Vergrößerung
    rectangle_icon = _get_module_icon_svg(
        asset_manager, f"{position_id}_rectangle", cell_width - 40, cell_width // 2 - 20, None
    )
    square1_icon = _get_module_icon_svg(
        asset_manager, f"{position_id}_square1", cell_width // 2 - 20, cell_width // 2 - 20, None
    )
    square2_icon = _get_module_icon_svg(
        asset_manager, f"{position_id}_square2", cell_width // 2 - 20, cell_width // 2 - 20, None
    )

    # SVG für aufgeteilte Zelle
    svg_content = f"""
        <!-- Split Cell ({row},{col}) -->
        <!-- ORBIS-Logo Rechteck oben (1:2 Seitenverhältnis) -->
        <rect class="module-cell"
              id="module-{row}-{col}-main"
              x="{x_pos}" y="{y_pos}"
              width="{cell_width}" height="{cell_width // 2}"
              fill="#e3f2fd"
              data-module-id="{position_id}-main"
              data-module-type="ORBIS-Logo"
              data-position="[{row},{col}]"/>

        <!-- Rectangle Icon SVG (dynamisch zentriert) -->
        <g transform="translate({x_pos + cell_width//2 - (cell_width - 40)//2}, {y_pos + cell_width // 4 - (cell_width // 2 - 20)//2})">
            {rectangle_icon}
        </g>

        <!-- Quadrat 1: Links unten -->
        <rect class="module-cell"
              id="module-{row}-{col}-sub1"
              x="{x_pos}" y="{y_pos + cell_width // 2}"
              width="{cell_width // 2}" height="{cell_width // 2}"
              fill="#FFFFFF"
              data-module-id="{position_id}-sub1"
              data-module-type="{position_id}_square1"
              data-position="[{row},{col}]"/>

        <!-- Quadrat 1 SVG Icon (dynamisch zentriert) -->
        <g transform="translate({x_pos + cell_width // 4 - (cell_width // 2 - 20)//2}, {y_pos + cell_width // 2 + cell_width // 4 - (cell_width // 2 - 20)//2})">
            {square1_icon}
        </g>

        <!-- Quadrat 2: Rechts unten -->
        <rect class="module-cell"
              id="module-{row}-{col}-sub2"
              x="{x_pos + cell_width // 2}" y="{y_pos + cell_width // 2}"
              width="{cell_width // 2}" height="{cell_width // 2}"
              fill="#FFFFFF"
              data-module-id="{position_id}-sub2"
              data-module-type="{position_id}_square2"
              data-position="[{row},{col}]"/>

        <!-- Quadrat 2 SVG Icon (dynamisch zentriert) -->
        <g transform="translate({x_pos + cell_width // 2 + cell_width // 4 - (cell_width // 2 - 20)//2}, {y_pos + cell_width // 2 + cell_width // 4 - (cell_width // 2 - 20)//2})">
            {square2_icon}
        </g>
    """

    return svg_content


def _generate_normal_cell_svg(
    row: int,
    col: int,
    x_pos: int,
    y_pos: int,
    cell_width: int,
    cell_height: int,
    cell_data: Dict[str, Any],
    asset_manager,
    active_module_id: Optional[str],
) -> str:
    """Generiert SVG für normale Zellen"""

    if not cell_data:
        return f"""
        <!-- Empty Cell ({row},{col}) -->
        <rect class="module-cell"
              id="module-{row}-{col}"
              x="{x_pos}" y="{y_pos}"
              width="{cell_width}" height="{cell_height}"
              fill="#FFFFFF"
              data-module-id="EMPTY-{row}-{col}"
              data-module-type="EMPTY"
              data-position="[{row},{col}]"/>
        <text class="module-label"
              x="{x_pos + cell_width//2}" y="{y_pos + cell_height//2}"
              text-anchor="middle" font-size="10">Empty</text>
        """

    cell_type = cell_data.get("type", "unknown")
    cell_id = cell_data.get("id", f"{row}-{col}")

    # Icon-SVG laden
    icon_svg = _get_module_icon_svg(asset_manager, cell_type, 120, 120, None)

    # Vereinfachte Farben - nur Standard + Active
    fill_color = "#FFFFFF"  # Weiß für bessere Umrandung-Sichtbarkeit
    stroke_color = "#1E90FF"  # Default dodger blue

    # Aktive Hervorhebung - komplette Zelle wird orange
    if active_module_id and cell_id == active_module_id:
        # Komplette Zelle wird orange (wie es funktioniert hat)
        fill_color = "#FF9800"  # Orange Füllung
        stroke_color = "#FF9800"  # Orange Umrandung
        stroke_width = "0"  # Keine Umrandung für aktive Module (nur Füllung)
    else:
        # Inaktive Module - dünne Umrandung
        stroke_width = "0.5"

    # Icon-SVG laden - Intersections maximal groß, andere 20% größer
    if cell_type == "intersection":
        # Intersections maximal groß (fast die ganze Zelle)
        icon_size = min(cell_width, cell_height) - 10  # 10px Rand
        icon_svg = _get_module_icon_svg(asset_manager, cell_type, icon_size, icon_size, cell_data)
    else:
        # Andere Module 20% größer (72 * 1.2 = 86.4)
        icon_size = 86
        icon_svg = _get_module_icon_svg(asset_manager, cell_type, icon_size, icon_size, cell_data)

    svg_content = f"""
        <!-- Module Cell ({row},{col}) -->
        <rect class="module-cell"
              id="module-{row}-{col}"
              x="{x_pos}" y="{y_pos}"
              width="{cell_width}" height="{cell_height}"
              fill="{fill_color}"
              stroke="{stroke_color}"
              stroke-width="{stroke_width}"
              data-module-id="{cell_id}"
              data-module-type="{cell_type}"
              data-position="[{row},{col}]"/>

        <!-- Module Icon SVG -->
        <g transform="translate({x_pos + cell_width//2 - icon_size//2}, {y_pos + cell_height//2 - icon_size//2})">
            {icon_svg}
        </g>

        <!-- Module Label -->
        <text class="module-label"
              x="{x_pos + cell_width//2}" y="{y_pos + cell_height - 4}"
              text-anchor="middle" font-size="9">{cell_data["data"].get("id", cell_id) if cell_type == "intersection" and cell_data and "data" in cell_data else cell_id}</text>
    """

    return svg_content


def _find_cell_data(
    row: int, col: int, modules: list, empty_positions: list, intersections: list
) -> Optional[Dict[str, Any]]:
    """Findet die Daten für eine Grid-Position"""

    logger.debug(f"🔍 DEBUG: Suche Position [{row},{col}]")

    # Module suchen - JSON: [row, column] -> UI: [row, col] (Matrix-Konvention)
    for module in modules:
        position = module.get("position", [])
        if len(position) == 2 and position[0] == row and position[1] == col:
            logger.debug(f"✅ Modul gefunden - Position: {position}, ID: {module.get('id')}")
            return {"type": module.get("type", "unknown"), "id": module.get("id", "unknown"), "data": module}

    # Intersections suchen - JSON: [row, column] -> UI: [row, col] (Matrix-Konvention)
    for intersection in intersections:
        position = intersection.get("position", [])
        if len(position) == 2 and position[0] == row and position[1] == col:
            logger.debug(f"✅ Intersection gefunden - Position: {position}, ID: {intersection.get('id')}")
            return {"type": "intersection", "id": intersection.get("id", "unknown"), "data": intersection}

    # Empty positions suchen - JSON: [row, column] -> UI: [row, col] (Matrix-Konvention)
    for empty in empty_positions:
        position = empty.get("position", [])
        if len(position) == 2 and position[0] == row and position[1] == col:
            print(f"✅ DEBUG: Empty Position gefunden - Position: {position}")
            return {"type": "empty", "id": empty.get("id", "unknown"), "data": empty}

    logger.warning(f"❌ DEBUG: Keine Daten gefunden für Position [{row},{col}]")
    return None


def _get_single_intersection_icon(
    module_type: str, width: int, height: int, cell_data: dict = None, asset_manager=None
) -> str:
    """Lädt ein einzelnes Icon für eine Intersection basierend auf der Position"""
    try:
        # Asset Manager hat bereits alle Intersection-Icon-Mappings!

        # Intersection-ID aus cell_data ermitteln
        intersection_id = "1"  # Default
        if cell_data and "data" in cell_data:
            intersection_id = cell_data["data"].get("id", "1")
            logger.debug(f"Intersection cell_data: {cell_data}, extracted id: {intersection_id}")
        elif cell_data:
            intersection_id = cell_data.get("id", "1")
            logger.debug(f"Intersection cell_data (direct): {cell_data}, extracted id: {intersection_id}")

        # Debug: Log the intersection ID being used
        logger.debug(f"Using intersection_id: {intersection_id} for position")

        # Asset Manager verwenden für Icon-Pfad
        if asset_manager:
            icon_path = asset_manager.get_module_icon_path(intersection_id)
        else:
            # Fallback falls kein Asset Manager übergeben wurde
            assets_dir = Path(__file__).parent.parent.parent.parent / "assets"
            intersection_icons = {"1": "add_2.svg", "2": "add.svg", "3": "point_scan.svg", "4": "grid_goldenratio.svg"}
            icon_file = intersection_icons.get(intersection_id, "add_2.svg")
            icon_path = assets_dir / "svgs" / icon_file

        if icon_path and Path(icon_path).exists():
            with open(icon_path, encoding="utf-8") as f:
                svg_content = f.read()
                # Skaliere das SVG
                svg_content = svg_content.replace('width="', f'width="{width}"').replace(
                    'height="', f'height="{height}"', 1
                )
                return svg_content
        else:
            return f'<text x="0" y="{height//2}" font-size="10" fill="red">Missing</text>'
    except Exception as e:
        logger.error(f"Error loading single intersection icon: {e}")
        return f'<text x="0" y="{height//2}" font-size="10" fill="red">Error</text>'


def _get_orbis_logo_svg(asset_manager, width: int, height: int) -> str:
    """Lädt das ORBIS-Logo SVG - VEREINFACHT mit Asset Manager"""
    try:
        # Asset Manager hat bereits ORBIS-Logo-Mapping
        orbis_logo_path = asset_manager.get_empty_position_asset_by_name("ORBIS")
        if orbis_logo_path and Path(orbis_logo_path).exists():
            with open(orbis_logo_path, encoding="utf-8") as svg_file:
                svg_content = svg_file.read()
                # SVG-Größe anpassen
                svg_content = re.sub(r'<svg([^>]*)width="[^"]*"', r"<svg\1", svg_content, count=1)
                svg_content = re.sub(r'<svg([^>]*)height="[^"]*"', r"<svg\1", svg_content, count=1)
                svg_content = svg_content.replace("<svg", f'<svg width="{width}" height="{height}"', 1)
                return svg_content
    except Exception as e:
        logger.warning(f"Could not load ORBIS logo: {e}")

    return f'<text x="{width//2}" y="{height//2}" text-anchor="middle" font-size="12" fill="#164194">ORBIS</text>'


def _get_module_icon_svg(asset_manager, module_type: str, width: int, height: int, cell_data: dict = None) -> str:
    """Lädt das SVG-Icon für ein Modul"""
    try:
        # Spezielle Behandlung für Intersections - ein Icon pro Intersection
        if module_type == "intersection":
            # Ein Icon pro Intersection basierend auf der ID
            return _get_single_intersection_icon(module_type, width, height, cell_data, asset_manager)

        # Für alle anderen Module: Asset Manager verwenden (VEREINFACHT!)
        icon_path = asset_manager.get_module_icon_path(module_type)

        if icon_path and Path(icon_path).exists():
            with open(icon_path, encoding="utf-8") as svg_file:
                svg_content = svg_file.read()
                # SVG-Größe anpassen
                svg_content = re.sub(r'<svg([^>]*)width="[^"]*"', r"<svg\1", svg_content, count=1)
                svg_content = re.sub(r'<svg([^>]*)height="[^"]*"', r"<svg\1", svg_content, count=1)
                svg_content = svg_content.replace("<svg", f'<svg width="{width}" height="{height}"', 1)
                return svg_content
    except Exception as e:
        logger.warning(f"Could not load icon for {module_type}: {e}")

    return f'<text x="{width//2}" y="{height//2}" text-anchor="middle" font-size="10" fill="#666">{module_type}</text>'


def _setup_event_handling():
    """Setup für Event-Handling mit streamlit-bokeh-events"""

    # Bokeh Plot für Event-Capture
    plot = figure(width=1, height=1, x_range=(0, 1), y_range=(0, 1))
    plot.axis.visible = False
    plot.grid.visible = False
    plot.outline_line_color = None

    # CustomJS für Event-Capture
    custom_js = CustomJS(
        code="""
        document.addEventListener('FACTORY_GRID_EVENT', function(event) {
            const eventData = event.detail;
            console.log('Factory Grid Event:', eventData);

            // Event an Streamlit weiterleiten
            const streamlitEvent = new CustomEvent('GET_FACTORY_EVENT', {
                detail: eventData
            });
            document.dispatchEvent(streamlitEvent);
        });
    """
    )

    plot.js_on_event("tap", custom_js)


def _process_grid_events(unique_key: Optional[str] = None):
    """Verarbeitet Events vom Grid"""

    # Eindeutigen Key generieren falls nicht angegeben
    if unique_key is None:
        import time

        unique_key = f"factory_events_{int(time.time() * 1000)}"

    # Event-Capture mit streamlit-bokeh-events
    # Erstelle eine minimale Bokeh-Figur mit einem unsichtbaren Renderer
    plot = figure(
        width=1,
        height=1,
        toolbar_location=None,
        x_axis_type=None,
        y_axis_type=None,
        outline_line_color=None,
        background_fill_color=None,
    )
    # Füge einen unsichtbaren Punkt hinzu, um den Renderer-Warning zu vermeiden
    plot.scatter([0], [0], size=0, alpha=0, color=None)

    event_result = streamlit_bokeh_events(
        bokeh_plot=plot, events="GET_FACTORY_EVENT", key=unique_key, refresh_on_update=True, debounce_time=100
    )

    if event_result:
        event_data = event_result.get("GET_FACTORY_EVENT")
        if event_data:
            _handle_grid_event(event_data)


def _handle_grid_event(event_data: Dict[str, Any]):
    """Behandelt ein Grid-Event"""

    event_type = event_data.get("type")
    module_id = event_data.get("id")
    module_type = event_data.get("moduleType")

    if event_type == "module-click":
        # Module auswählen
        st.session_state.selected_module = module_id
        st.session_state.selected_module_type = module_type
        st.success(f"Module {module_id} ({module_type}) selected")

    elif event_type == "module-dblclick":
        # Detail-Seite öffnen
        st.session_state.show_module_detail = True
        st.session_state.detail_module_id = module_id
        st.session_state.detail_module_type = module_type
        st.info(f"Opening detail view for {module_id} ({module_type})")

        # Navigation zu Detail-Seite
        _navigate_to_module_detail(module_id, module_type)


def _navigate_to_module_detail(module_id: str, module_type: str):
    """Navigiert zu einer Modul-Detail-Seite"""

    # Navigation basierend auf Modul-Typ
    navigation_map = {
        "MILL": "ccu_production_monitoring",
        "DRILL": "ccu_production_monitoring",
        "AIQS": "ccu_quality_control",
        "HBW": "ccu_storage_management",
        "DPS": "ccu_input_output",
        "CHRG": "ccu_charging_station",
        "ORBIS-Logo": "ccu_system_overview",
        "shelves": "ccu_storage_details",
        "conveyor_belt": "ccu_transport_system",
        "warehouse": "ccu_warehouse_management",
        "delivery_truck_speed": "ccu_delivery_tracking",
    }

    target_page = navigation_map.get(module_type, "ccu_module_details")

    # Navigation setzen
    st.session_state.current_page = target_page
    st.session_state.navigation_source = "shopfloor_grid"

    logger.info(f"Navigating to {target_page} for module {module_id} ({module_type})")


# Export für OMF2-Integration
__all__ = ["show_shopfloor_layout_hybrid"]
