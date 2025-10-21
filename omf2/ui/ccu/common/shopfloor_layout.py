#!/usr/bin/env python3
"""
Shopfloor Layout - Streamlit-native Implementation
Ersetzt die fragile Bokeh/iframe-basierte Implementation mit einer sauberen Streamlit-Lösung
"""

from pathlib import Path
from typing import Dict, List, Optional

import streamlit as st

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
    Zeigt das interaktive Shopfloor Layout mit OMF2-Integration (Streamlit-native)

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

    # Asset Manager initialisieren
    asset_manager = get_asset_manager()

    # Layout-Konfiguration laden
    config_loader = get_ccu_config_loader()
    layout_config = config_loader.load_shopfloor_layout()

    # Module aus Konfiguration laden
    modules = layout_config.get("modules", [])
    empty_positions = layout_config.get("empty_positions", [])
    intersections = layout_config.get("intersections", [])

    # CSS für fixed-aspect grid
    st.markdown(
        """
    <style>
    .shopfloor-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        grid-template-rows: repeat(3, 1fr);
        gap: 8px;
        aspect-ratio: 4/3;
        max-width: 800px;
        margin: 0 auto;
    }

    .grid-cell {
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 8px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background: #f8f9fa;
        transition: all 0.2s ease;
        min-height: 120px;
    }

    .grid-cell:hover {
        border-color: #007bff;
        box-shadow: 0 2px 8px rgba(0,123,255,0.2);
    }

    .grid-cell.active {
        border-color: #ff6b35;
        background: #fff3e0;
        box-shadow: 0 4px 12px rgba(255,107,53,0.3);
    }

    .grid-cell.selected {
        border-color: #28a745;
        background: #e8f5e8;
        box-shadow: 0 4px 12px rgba(40,167,69,0.3);
    }

    .module-icon {
        width: 48px;
        height: 48px;
        margin-bottom: 4px;
    }

    .module-id {
        font-size: 12px;
        font-weight: bold;
        color: #495057;
        text-align: center;
    }

    .details-btn {
        margin-top: 4px;
        font-size: 10px;
        padding: 2px 6px;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    # Grid Container
    grid_html = '<div class="shopfloor-grid">'

    # 3x4 Grid generieren
    for row in range(3):
        for col in range(4):
            # Zellendaten finden
            cell_data = _find_cell_data(row, col, modules, empty_positions, intersections)

            # CSS-Klassen bestimmen
            cell_classes = ["grid-cell"]
            if cell_data and cell_data.get("id") == active_module_id:
                cell_classes.append("active")
            if st.session_state.get("selected_module_id") == cell_data.get("id"):
                cell_classes.append("selected")

            # Zelle HTML generieren
            cell_html = f'<div class="{" ".join(cell_classes)}">'

            if cell_data:
                # Module-Icon laden
                icon_svg = _get_module_icon_svg(asset_manager, cell_data.get("name", ""))
                if icon_svg:
                    cell_html += f'<div class="module-icon">{icon_svg}</div>'

                # Module-ID anzeigen
                cell_html += f'<div class="module-id">{cell_data.get("id", "")}</div>'

                # Details Button (nur in interaktiven Modi)
                if mode != "view_mode" and show_controls:
                    btn_key = f"details-{cell_data.get('id')}-{row}-{col}"
                    if unique_key:
                        btn_key = f"{unique_key}-{btn_key}"

                    cell_html += f"""
                    <button class="details-btn" onclick="
                        window.parent.postMessage({{
                            type: 'MODULE_DETAILS',
                            module_id: '{cell_data.get("id")}',
                            module_name: '{cell_data.get("name", "")}',
                            position: [{row}, {col}]
                        }}, '*');
                    ">📋 Details</button>
                    """
            else:
                # Leere Zelle
                cell_html += '<div class="module-id">Empty</div>'

            cell_html += "</div>"
            grid_html += cell_html

    grid_html += "</div>"

    # Grid rendern
    st.components.v1.html(grid_html, height=400)

    # JavaScript für Event-Handling
    st.markdown(
        """
    <script>
    window.addEventListener('message', function(event) {
        if (event.data.type === 'MODULE_DETAILS') {
            // Session State setzen
            const data = event.data;
            window.parent.postMessage({
                type: 'STREAMLIT_SESSION_STATE',
                key: 'selected_module_id',
                value: data.module_id
            }, '*');
            window.parent.postMessage({
                type: 'STREAMLIT_SESSION_STATE',
                key: 'show_module_details',
                value: true
            }, '*');
        }
    });
    </script>
    """,
        unsafe_allow_html=True,
    )


def _find_cell_data(
    row: int, col: int, modules: List[Dict], empty_positions: List, intersections: List
) -> Optional[Dict]:
    """Findet Zellendaten für gegebene Position"""
    position = [row, col]

    # Module suchen
    for module in modules:
        if module.get("position") == position:
            return module

    # Empty position prüfen
    if position in empty_positions:
        return None

    # Intersection prüfen
    for intersection in intersections:
        if intersection.get("position") == position:
            result = intersection.copy()
            result["type"] = "intersection"
            return result

    return None


def _get_module_icon_svg(
    asset_manager, module_name: str, width: int = 48, height: int = 48, fallback_text: str = None
) -> str:
    """Lädt SVG-Icon für Modul"""
    try:
        if not module_name:
            return ""

        icon_path = asset_manager.get_module_icon_path(module_name)
        if icon_path and Path(icon_path).exists():
            with open(icon_path, encoding="utf-8") as f:
                svg_content = f.read()
                # SVG skalieren
                scaled_svg = svg_content.replace("<svg", f'<svg width="{width}" height="{height}"')
                return scaled_svg
        else:
            # Fallback text element
            return f'<text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" font-size="12">{module_name}</text>'
        return ""
    except Exception as e:
        logger.error(f"Failed to load module icon for {module_name}: {e}")
        if fallback_text:
            return f'<text x="50%" y="50%" text-anchor="middle" dominant-baseline="middle" font-size="12">{fallback_text}</text>'
        return ""


# Deprecated functions - kept for compatibility
def _generate_omf2_svg_grid_with_roads(*args, **kwargs):
    """DEPRECATED: Returns empty string, logs warning"""
    logger.warning("_generate_omf2_svg_grid_with_roads is deprecated and returns empty string")
    return ""


def _process_grid_events(*args, **kwargs):
    """DEPRECATED: No-op, logs warning"""
    logger.warning("_process_grid_events is deprecated and does nothing")


def _handle_grid_event(*args, **kwargs):
    """DEPRECATED: No-op, logs warning"""
    logger.warning("_handle_grid_event is deprecated and does nothing")
