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


def show_shopfloor_layout(
    active_module_id: Optional[str] = None,
    active_intersections: Optional[list] = None,
    title: str = "Shopfloor Layout",
    show_controls: bool = True,
    unique_key: Optional[str] = None,
    mode: str = "interactive",  # "view_mode", "ccu_configuration", "interactive"
) -> None:
    """
    Zeigt das interaktive Shopfloor Layout mit OMF2-Integration

    Args:
        active_module_id: ID des aktiven Moduls (für Hervorhebung)
        active_intersections: Liste aktiver Intersections
        title: Titel der Komponente
        show_controls: Ob Steuerungselemente angezeigt werden sollen
        unique_key: Eindeutiger Key für Streamlit-Komponenten (verhindert Key-Konflikte)
        mode: Verwendungsmodus
            - "view_mode": Nur aktive Module anzeigen, keine Klicks
            - "ccu_configuration": Single/Double Click für Auswahl/Navigation
            - "interactive": Standard-Interaktivität
    """
    st.subheader(f"🏭 {title}")

    # Show navigation hint if there's a preselected module (from double-click)
    if st.session_state.get("preselected_module_id"):
        module_id = st.session_state.get("preselected_module_id")
        st.success(f"✅ Module **{module_id}** preselected! Navigate to **CCU Modules** tab to see details.")

    # Asset Manager initialisieren
    asset_manager = get_asset_manager()

    # Layout-Konfiguration laden
    config_loader = get_ccu_config_loader()
    layout_config = config_loader.load_shopfloor_layout()

    # HTML-Grid generieren mit Roads-Layer und Mode
    grid_html = _generate_omf2_svg_grid_with_roads(
        layout_config, asset_manager, active_module_id, active_intersections, mode
    )

    # Event-Handling Setup
    _setup_event_handling()

    # Grid anzeigen
    st.components.v1.html(grid_html, height=500, scrolling=False)

    # Event-Verarbeitung
    _process_grid_events(unique_key)


def _generate_omf2_svg_grid_with_roads(
    layout_config: Dict[str, Any],
    asset_manager,
    active_module_id: Optional[str] = None,
    active_intersections: Optional[list] = None,
    mode: str = "interactive",
) -> str:
    """Generiert das SVG-Grid mit OMF2-Integration und Roads-Layer"""

    # Grid-Dimensionen - kompakter
    grid_width = 600
    grid_height = 450
    cell_width = 150
    cell_height = 150

    # Roads-Layer generieren (untere Ebene)
    roads_layer = _generate_roads_layer(
        layout_config, grid_width, grid_height, cell_width, cell_height, active_intersections
    )

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
                transition: all 0.2s ease;
                fill: rgba(255, 255, 255, 0.6);  /* Mehr Transparenz für Roads-Sichtbarkeit */
            }}
            .module-cell.active-module {{
                stroke: #FF9800;
                stroke-width: 10;
                fill: rgba(255, 255, 255, 0.9);  /* Weniger transparent für aktive Module */
            }}
            .module-cell.selected {{
                fill: #FF9800 !important;    /* Orange Füllung */
                stroke: #FF9800 !important;
                stroke-width: 0;             /* Keine Umrandung */
            }}
            .module-cell.rectangle {{
                fill: rgba(135, 206, 250, 0.3);  /* Helles Blau für Rectangles */
                stroke: #87CEEB;
                stroke-width: 1;
            }}
            .module-cell.rectangle:hover {{
                fill: rgba(135, 206, 250, 0.5);  /* Helleres Blau beim Hover */
                stroke: #87CEEB;
                stroke-width: 2;
            }}

            /* Mode-spezifische Styles */
            .mode-interactive .module-cell {{
                cursor: pointer;
            }}
            .mode-interactive .module-cell:hover {{
                stroke: #0066cc;
                stroke-width: 2;
            }}
            .mode-interactive .module-cell.clicked {{
                stroke: #FF5722;
                stroke-width: 3;
            }}
            .mode-interactive .module-cell.double-clicked {{
                stroke: #E91E63;
                stroke-width: 5;
            }}

            .mode-ccu-configuration .module-cell {{
                cursor: pointer;
            }}
            .mode-ccu-configuration .module-cell:hover {{
                stroke: #0066cc;
                stroke-width: 2;
            }}
            .mode-ccu-configuration .module-cell.clicked {{
                stroke: #FF9800;
                stroke-width: 3;
            }}
            .mode-ccu-configuration .module-cell.double-clicked {{
                stroke: #2196F3;
                stroke-width: 5;
                fill: rgba(33, 150, 243, 0.1);  /* Helles Blau für Double-Click */
            }}

            .mode-view-mode .module-cell {{
                cursor: default;  /* Keine Klicks möglich */
            }}
            .mode-view-mode .module-cell:hover {{
                /* Keine Hover-Effekte in View Mode */
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
            .road-line {{
                stroke: #000;
                stroke-width: 5;
                opacity: 1;
                stroke-linecap: square;
                filter: drop-shadow(1px 1px 2px rgba(0,0,0,0.3));
            }}
            .road-line.active {{
                stroke: #FF9800;
                stroke-width: 7;
                opacity: 1;
                stroke-linecap: square;
                filter: drop-shadow(2px 2px 4px rgba(255,152,0,0.5));
            }}
        </style>
    </head>
    <body class="mode-{mode}">
        <svg width="{grid_width}" height="{grid_height}" viewBox="-50 -50 {grid_width + 100} {grid_height + 100}">
            <!-- Grid Background -->
            <rect x="0" y="0" width="{grid_width}" height="{grid_height}" fill="#fafafa"/>

            <!-- Roads Layer (untere Ebene) -->
            {roads_layer}
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

            // Double-Click Detection mit Timer
            let clickTimer = null;
            let clickCount = 0;

            // Event-Handler für Module-Clicks
            function handleModuleClick(event) {
                const moduleId = event.target.getAttribute('data-module-id');
                const moduleType = event.target.getAttribute('data-module-type');
                const position = event.target.getAttribute('data-position');

                // Debug-Logging für Klicks
                console.log('🖱️ CLICK DEBUG:', {
                    moduleId,
                    moduleType,
                    position,
                    targetId: event.target.id,
                    classes: event.target.className
                });

                // Double-Click Detection
                clickCount++;
                if (clickCount === 1) {
                    clickTimer = setTimeout(() => {
                        // Single Click nach 300ms
                        console.log('🖱️ SINGLE CLICK detected');
                        clickCount = 0;
                    }, 300);
                } else if (clickCount === 2) {
                    // Double Click erkannt
                    clearTimeout(clickTimer);
                    console.log('🖱️ DOUBLE CLICK detected');
                    clickCount = 0;

                    // Rufe Double-Click Handler auf
                    handleModuleDoubleClick(event);
                    return;
                }

                // Vorherige Auswahl entfernen
                if (selectedModule) {
                    selectedModule.classList.remove('selected', 'clicked');
                    // Reset vorherige Styles
                    selectedModule.style.fill = '';
                    selectedModule.style.stroke = '';
                    selectedModule.style.strokeWidth = '';
                }

                // Neue Auswahl mit Click-Highlighting
                event.target.classList.add('selected', 'clicked');
                selectedModule = event.target;

                // Mode-spezifisches Click-Highlighting - Orange Füllung
                const body = document.body;
                if (body.classList.contains('mode-ccu-configuration')) {
                    // CCU Configuration: Orange Füllung
                    event.target.style.fill = '#FF9800';
                    event.target.style.stroke = '#FF9800';
                    event.target.style.strokeWidth = '0';
                } else {
                    // Interactive: Orange Füllung
                    event.target.style.fill = '#FF9800';
                    event.target.style.stroke = '#FF9800';
                    event.target.style.strokeWidth = '0';
                }

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
                console.log('🔧 DEBUG: handleModuleDoubleClick called');
                const moduleId = event.target.getAttribute('data-module-id');
                const moduleType = event.target.getAttribute('data-module-type');
                const position = event.target.getAttribute('data-position');

                // Debug-Logging für Doppelklicks
                console.log('🖱️ DOUBLE CLICK DEBUG:', {
                    moduleId,
                    moduleType,
                    position,
                    targetId: event.target.id,
                    classes: event.target.className
                });
                console.log('🔍 DEBUG: Double-click on', moduleId, 'at position', position);

                    // Mode-spezifisches Double-Click-Highlighting
                    const body = document.body;
                    console.log('🔧 DEBUG: Double-click body classes:', body.className);
                    console.log('🔧 DEBUG: Contains mode-ccu_configuration:', body.classList.contains('mode-ccu_configuration'));

                    if (body.classList.contains('mode-ccu_configuration')) {
                    // CCU Configuration: Blaue Umrandung und Füllung
                    event.target.classList.add('double-clicked');
                    event.target.style.stroke = '#2196F3';
                    event.target.style.strokeWidth = '5';
                    event.target.style.fill = 'rgba(33, 150, 243, 0.1)';

                    // Navigation-Simulation für CCU Configuration
                    console.log('🚀 NAVIGATION: Double-click on', moduleId, '- would navigate to module configuration');

                    // Simuliere Navigation durch Alert (für Demo)
                    alert(`🚀 Navigation: Würde zu ${moduleId} Detail-Seite weiterleiten\\n\\nIn der echten App würde hier die Modul-Konfiguration geöffnet werden.`);
                } else {
                    // Interactive: Pink Umrandung
                    event.target.classList.add('double-clicked');
                    event.target.style.stroke = '#E91E63';
                    event.target.style.strokeWidth = '5';
                }

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
                const body = document.body;
                const mode = body.classList.contains('mode-view-mode') ? 'view-mode' :
                             body.classList.contains('mode-ccu_configuration') ? 'ccu-configuration' : 'interactive';

                console.log('🔧 DEBUG: Mode detected:', mode);
                console.log('🔧 DEBUG: Body classes:', body.className);
                console.log('🔧 DEBUG: Found', moduleCells.length, 'module cells');

                moduleCells.forEach((cell, index) => {
                    console.log('🔧 DEBUG: Cell', index, ':', {
                        id: cell.id,
                        classes: cell.className,
                        moduleId: cell.getAttribute('data-module-id'),
                        moduleType: cell.getAttribute('data-module-type')
                    });

                    // Nur in interaktiven Modi Klicks erlauben
                    if (mode !== 'view-mode') {
                        cell.addEventListener('click', handleModuleClick);
                        cell.addEventListener('dblclick', handleModuleDoubleClick);
                        console.log('🔧 DEBUG: Added click listeners to cell', index);

                        // Debug: Teste ob Double-Click Event-Listener funktioniert
                        cell.addEventListener('dblclick', function(e) {
                            console.log('🔧 DEBUG: Double-click event fired on', e.target.id);
                        });
                    }

                    // Mouse-Over nur in interaktiven Modi
                    if (mode !== 'view-mode') {
                        cell.addEventListener('mouseenter', function() {
                            if (!cell.classList.contains('active-module')) {
                                cell.style.stroke = '#0066cc';
                                cell.style.strokeWidth = '2';
                            }
                        });

                        cell.addEventListener('mouseleave', function() {
                            if (!cell.classList.contains('active-module')) {
                                cell.style.stroke = '#e0e0e0';
                                cell.style.strokeWidth = '0.5';
                            }
                        });
                    }
                });
            });
        </script>
    </body>
    </html>
    """

    return svg_content


# API-Kompatibilität: Ursprüngliche Funktion als Alias
def _generate_omf2_svg_grid(
    layout_config: Dict[str, Any],
    asset_manager,
    active_module_id: Optional[str] = None,
    active_intersections: Optional[list] = None,
) -> str:
    """Generiert das SVG-Grid mit OMF2-Integration (ohne Roads-Layer für Kompatibilität)"""
    # Temporär ohne Roads-Layer für bestehende Verwendung
    return _generate_omf2_svg_grid_with_roads(layout_config, asset_manager, active_module_id, active_intersections)


def _generate_roads_layer(
    layout_config: Dict[str, Any],
    grid_width: int,
    grid_height: int,
    cell_width: int,
    cell_height: int,
    active_intersections: Optional[list] = None,
) -> str:
    """Generiert den Roads-Layer als untere Ebene mit aktiver Hervorhebung"""
    roads = layout_config.get("roads", [])
    modules = layout_config.get("modules", [])
    intersections = layout_config.get("intersections", [])

    # Position-Mapping für Module und Intersections
    position_map = {}

    # Module-Positionen
    for module in modules:
        position = module.get("position", [0, 0])
        serial_number = module.get("serialNumber", "")
        if serial_number:
            position_map[serial_number] = position

    # Intersection-Positionen
    for intersection in intersections:
        intersection_id = intersection.get("id", "")
        position = intersection.get("position", [0, 0])
        if intersection_id:
            position_map[intersection_id] = position

    roads_svg = ""

    for road in roads:
        from_id = road.get("from", "")
        to_id = road.get("to", "")
        direction = road.get("direction", "")

        if from_id in position_map and to_id in position_map:
            # Start- und End-Position berechnen
            from_pos = position_map[from_id]
            to_pos = position_map[to_id]

            # Koordinaten in Pixel umrechnen - Roads gehen bis an Zellränder
            from_x = from_pos[1] * cell_width + cell_width // 2  # [row, col] -> [col, row]
            from_y = from_pos[0] * cell_height + cell_height // 2
            to_x = to_pos[1] * cell_width + cell_width // 2
            to_y = to_pos[0] * cell_height + cell_height // 2

            # Roads-Linien: 50% länger, alle gleich lang
            if direction == "EAST":
                from_x = from_pos[1] * cell_width + cell_width - 22  # 50% länger (15 * 1.5 = 22.5 ≈ 22)
                to_x = to_pos[1] * cell_width + 22  # 50% länger
            elif direction == "WEST":
                from_x = from_pos[1] * cell_width + 22  # 50% länger
                to_x = to_pos[1] * cell_width + cell_width - 22  # 50% länger
            elif direction == "NORTH":
                from_y = from_pos[0] * cell_height + 22  # 50% länger
                to_y = to_pos[0] * cell_height + cell_height - 22  # 50% länger
            elif direction == "SOUTH":
                from_y = from_pos[0] * cell_height + cell_height - 22  # 50% länger
                to_y = to_pos[0] * cell_height + 22  # 50% länger

            # Prüfe ob Road aktiv ist (für FTS Navigation)
            is_active = False
            if active_intersections:
                is_active = from_id in active_intersections or to_id in active_intersections

            # CSS-Klasse basierend auf Aktivität
            css_class = "road-line active" if is_active else "road-line"

            # Road-Linie zeichnen
            roads_svg += f"""
            <line class="{css_class}"
                  x1="{from_x}" y1="{from_y}"
                  x2="{to_x}" y2="{to_y}"
                  data-from="{from_id}"
                  data-to="{to_id}"
                  data-direction="{direction}"/>"""

    return roads_svg


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
        <rect class="module-cell rectangle"
              id="module-{row}-{col}-main"
              x="{x_pos}" y="{y_pos}"
              width="{cell_width}" height="{cell_width // 2}"
              fill="rgba(135, 206, 250, 0.3)"
              stroke="#87CEEB"
              stroke-width="1"
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

    # Debug: Zeige cell_data für aktive Module
    if active_module_id:
        print(f"🔧 DEBUG: Checking cell {cell_id} (type: {cell_type}) against active_module_id: {active_module_id}")
        print(f"🔧 DEBUG: cell_data: {cell_data}")

    # Icon-SVG laden
    icon_svg = _get_module_icon_svg(asset_manager, cell_type, 120, 120, None)

    # Highlighting-System: Verschiedene Modi
    fill_color = "#FFFFFF"  # Weiß für bessere Umrandung-Sichtbarkeit
    stroke_color = "#1E90FF"  # Default dodger blue
    stroke_width = "0.5"  # Standard-Umrandung
    css_classes = "module-cell"  # CSS classes for the rect element

    # Aktive Module aus Production/Storage Orders - Orange Umrandung
    # Vergleiche mit Modul-Namen (z.B. "DPS") statt Grid-Position
    if active_module_id and cell_data.get("id") == active_module_id:
        fill_color = "#FFFFFF"  # Weiße Füllung
        stroke_color = "#FF9800"  # Orange Umrandung
        stroke_width = "10"  # Dicke orange Umrandung
        css_classes = "module-cell active-module"  # Add active-module class for CSS styling
        print(f"🔧 DEBUG: Active module {active_module_id} found at cell {cell_id} - applying orange border")

    # Icon-SVG laden - VEREINFACHT: Einheitliche Größe für alle Module
    icon_size = 86  # Einheitliche Größe für alle Module (ohne Spezial-Effekte)
    icon_svg = _get_module_icon_svg(asset_manager, cell_type, icon_size, icon_size, cell_data)

    svg_content = f"""
        <!-- Module Cell ({row},{col}) -->
        <rect class="{css_classes}"
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
        <g transform="translate({x_pos + cell_width//2 - icon_size//2}, {y_pos + cell_height//2 - icon_size//2})"
           style="opacity: 0.7;">
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
    """Lädt ein einzelnes Icon für eine Intersection - VEREINFACHT ohne Spezial-Effekte"""
    try:
        # Intersection-ID aus cell_data ermitteln
        intersection_id = "1"  # Default
        if cell_data and "data" in cell_data:
            intersection_id = cell_data["data"].get("id", "1")
        elif cell_data:
            intersection_id = cell_data.get("id", "1")

        # Asset Manager verwenden für Icon-Pfad (wie alle anderen Module)
        if asset_manager:
            icon_path = asset_manager.get_module_icon_path(intersection_id)
        else:
            # Fallback falls kein Asset Manager übergeben wurde
            assets_dir = Path(__file__).parent.parent.parent.parent / "assets"
            intersection_icons = {
                "1": "fiber_manual_record_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg",
                "2": "rotate_right_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg",
                "3": "rotate_left_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg",
                "4": "mode_standby_24dp_1F1F1F_FILL0_wght400_GRAD0_opsz24.svg",
            }
            icon_file = intersection_icons.get(intersection_id, "add_cross_10px_whitebg.svg")
            icon_path = assets_dir / "svgs" / icon_file

        if icon_path and Path(icon_path).exists():
            with open(icon_path, encoding="utf-8") as f:
                svg_content = f.read()
                # ViewBox-bewusste Skalierung - keine Verzerrung!
                svg_content = _scale_svg_properly(svg_content, width, height)
                return svg_content
        else:
            return f'<text x="{width//2}" y="{height//2}" text-anchor="middle" font-size="10" fill="#666">+</text>'
    except Exception as e:
        logger.error(f"Error loading intersection icon: {e}")
        return f'<text x="{width//2}" y="{height//2}" text-anchor="middle" font-size="10" fill="#666">+</text>'


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


def _scale_svg_properly(svg_content: str, width: int, height: int) -> str:
    """Skaliert SVG korrekt basierend auf ViewBox - keine Verzerrung!"""
    try:
        # ViewBox aus SVG extrahieren
        viewbox_match = re.search(r'viewBox="([^"]*)"', svg_content)
        if viewbox_match:
            viewbox = viewbox_match.group(1)
            # ViewBox-Parameter extrahieren: "x y width height"
            viewbox_parts = viewbox.split()
            if len(viewbox_parts) == 4:
                vb_x, vb_y, vb_width, vb_height = map(float, viewbox_parts)

                # Seitenverhältnis der ViewBox berechnen
                vb_aspect_ratio = vb_width / vb_height
                target_aspect_ratio = width / height

                # Skalierung basierend auf Seitenverhältnis
                if vb_aspect_ratio > target_aspect_ratio:
                    # ViewBox ist breiter - Höhe anpassen
                    scale = width / vb_width
                    new_height = int(vb_height * scale)
                    # SVG mit korrekter Skalierung
                    svg_content = re.sub(r'<svg([^>]*)width="[^"]*"', r"<svg\1", svg_content, count=1)
                    svg_content = re.sub(r'<svg([^>]*)height="[^"]*"', r"<svg\1", svg_content, count=1)
                    svg_content = svg_content.replace("<svg", f'<svg width="{width}" height="{new_height}"', 1)
                else:
                    # ViewBox ist höher - Breite anpassen
                    scale = height / vb_height
                    new_width = int(vb_width * scale)
                    # SVG mit korrekter Skalierung
                    svg_content = re.sub(r'<svg([^>]*)width="[^"]*"', r"<svg\1", svg_content, count=1)
                    svg_content = re.sub(r'<svg([^>]*)height="[^"]*"', r"<svg\1", svg_content, count=1)
                    svg_content = svg_content.replace("<svg", f'<svg width="{new_width}" height="{height}"', 1)
            else:
                # Fallback: Standard-Skalierung
                svg_content = re.sub(r'<svg([^>]*)width="[^"]*"', r"<svg\1", svg_content, count=1)
                svg_content = re.sub(r'<svg([^>]*)height="[^"]*"', r"<svg\1", svg_content, count=1)
                svg_content = svg_content.replace("<svg", f'<svg width="{width}" height="{height}"', 1)
        else:
            # Keine ViewBox gefunden - Standard-Skalierung
            svg_content = re.sub(r'<svg([^>]*)width="[^"]*"', r"<svg\1", svg_content, count=1)
            svg_content = re.sub(r'<svg([^>]*)height="[^"]*"', r"<svg\1", svg_content, count=1)
            svg_content = svg_content.replace("<svg", f'<svg width="{width}" height="{height}"', 1)

        return svg_content
    except Exception as e:
        logger.warning(f"Error scaling SVG: {e}")
        # Fallback: Standard-Skalierung
        svg_content = re.sub(r'<svg([^>]*)width="[^"]*"', r"<svg\1", svg_content, count=1)
        svg_content = re.sub(r'<svg([^>]*)height="[^"]*"', r"<svg\1", svg_content, count=1)
        return svg_content.replace("<svg", f'<svg width="{width}" height="{height}"', 1)


def _get_module_icon_svg(asset_manager, module_type: str, width: int, height: int, cell_data: dict = None) -> str:
    """Lädt das SVG-Icon für ein Modul - ViewBox-bewusste Skalierung"""
    try:
        # Spezielle Behandlung für Intersections - ein Icon pro Intersection
        if module_type == "intersection":
            # Ein Icon pro Intersection basierend auf der ID
            return _get_single_intersection_icon(module_type, width, height, cell_data, asset_manager)

        # Für alle anderen Module: Asset Manager verwenden
        icon_path = asset_manager.get_module_icon_path(module_type)

        if icon_path and Path(icon_path).exists():
            with open(icon_path, encoding="utf-8") as svg_file:
                svg_content = svg_file.read()
                # ViewBox-bewusste Skalierung - keine Verzerrung!
                svg_content = _scale_svg_properly(svg_content, width, height)
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

    logger.info(f"🔧 Grid event received: type={event_type}, module={module_id}, type={module_type}")

    if event_type == "module-click":
        # Module auswählen
        st.session_state.selected_module = module_id
        st.session_state.selected_module_type = module_type
        logger.info(f"✅ Module {module_id} selected")

    elif event_type == "module-dblclick":
        # Detail-Seite öffnen - Session State für Navigation setzen
        logger.info(f"🚀 Double-click detected on {module_id} - preparing navigation")
        
        # Session State für Navigation zu CCU Modules setzen
        st.session_state.navigate_to_ccu_modules = True
        st.session_state.preselected_module_id = module_id
        st.session_state.preselected_module_type = module_type
        st.session_state.show_module_details = True
        
        logger.info(f"✅ Navigation prepared: module={module_id}, type={module_type}")
        
        # Trigger rerun to navigate
        st.rerun()

# Export für OMF2-Integration
__all__ = ["show_shopfloor_layout"]
