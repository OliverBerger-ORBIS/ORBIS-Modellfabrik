"""
OMF Dashboard Shopfloor Layout - 4x3 Grid Layout Anzeige
Visualisierung des Shopfloor-Layouts mit Modul-Positionen
"""

# Direkter Icon-Pfad (wie ORBIS-Logo)
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st
import yaml


def get_module_icon_path(module_id):
    """Gibt den Pfad zum Modul-Icon zurück (wie ORBIS-Logo)"""
    # Assets-Verzeichnis
    assets_dir = str(Path(__file__).parent / ".." / "assets")

    # Icon-Mapping
    icon_mapping = {
        "HBW": "hbw_icon.png",
        "DRILL": "drill_icon.png",
        "MILL": "mill_icon.png",
        "AIQS": "aiqs_icon.png",
        "DPS": "dps_icon.png",
        "CHRG": "chrg_icon.png",
        "CHRG0": "chrg_icon.png",  # CHRG0 -> CHRG mapping
        "FTS": "fts_icon.jpeg",
        "TXT": "txt_icon.png",
        "RPI": "rpi_icon.png",
    }

    icon_file = icon_mapping.get(module_id, "machine_icon.png")
    return os.path.join(assets_dir, icon_file)


def display_module_icon(module_id, width=60, caption=""):
    """Zeigt ein Modul-Icon an (wie ORBIS-Logo)"""
    icon_path = get_module_icon_path(module_id)
    if os.path.exists(icon_path):
        st.image(icon_path, width=width, caption=caption or module_id)
    else:
        # Fallback zu Emoji
        st.markdown(f"🔧 {module_id}")
        if caption:
            st.caption(caption)


def show_shopfloor_layout():
    """Zeigt das 4x3 Grid Layout des Shopfloors"""
    st.subheader("🗺️ Shopfloor-Layout (4x3 Grid)")

    # Shopfloor Grid anzeigen
    show_shopfloor_grid()


def show_shopfloor_grid():
    """Zeigt das 4x3 Grid mit Modulen aus layout.yml"""

    # Layout aus YAML laden
    layout_data = load_shopfloor_layout()
    if not layout_data:
        st.error("❌ Fehler beim Laden des Shopfloor-Layouts")
        return

    # Grid basierend auf layout.yml generieren
    positions = layout_data.get("positions", [])

    # Grid-Array erstellen (3 Zeilen x 4 Spalten)
    grid = [[None for _ in range(4)] for _ in range(3)]

    # Positionen in Grid eintragen
    for pos in positions:
        row, col = pos["position"]
        if 0 <= row < 3 and 0 <= col < 4:
            grid[row][col] = pos

    # Streamlit Grid anzeigen
    for row in range(3):
        cols = st.columns(4)
        for col in range(4):
            with cols[col]:
                cell_data = grid[row][col]

                if cell_data and cell_data.get("type") == "MODULE":
                    module_id = cell_data.get("id", "")
                    module_name = cell_data.get("name_lang_de", cell_data.get("name", ""))
                    module_serial = cell_data.get("module_serial", "")

                    # Icon direkt anzeigen (wie ORBIS-Logo)
                    display_module_icon(module_id, width=60, caption=module_name)

                    st.write(f"**{module_name}**")
                    st.caption(f"ID: {module_serial}")
                else:
                    st.info("Leer")


def load_shopfloor_layout():
    """Lädt das Shopfloor-Layout aus der YAML-Datei"""
    try:
        config_path = Path(__file__).parent.parent.parent.parent / "omf" / "config" / "shopfloor" / "layout.yml"
        with open(config_path, encoding="utf-8") as file:
            return yaml.safe_load(file)
    except Exception as e:
        st.error(f"❌ Fehler beim Laden des Shopfloor-Layouts: {e}")
        return None


def show_grid_visualization():
    """Visualisiert das 4x3 Grid mit Modulen"""
    st.subheader("📊 Grid-Visualisierung")

    positions = get_module_positions()

    # Zeige Grid mit Icons
    st.subheader("🎨 Grid mit Modul-Icons")
    show_grid_with_icons(positions)

    # Erstelle Grid-Matrix
    grid_matrix = create_grid_matrix(positions)

    # Zeige Grid als Tabelle
    st.subheader("📋 Grid-Tabelle")
    df = pd.DataFrame(grid_matrix)
    df.index = [f"Zeile {i}" for i in range(3)]
    df.columns = [f"Spalte {i}" for i in range(4)]

    st.dataframe(df, use_container_width=True)

    # ASCII-Darstellung
    st.subheader("📋 ASCII-Layout")
    show_ascii_layout()


def create_grid_matrix(positions: List[Dict[str, Any]]) -> List[List[str]]:
    """Erstellt eine 3x4 Matrix für die Grid-Darstellung"""
    matrix = [["" for _ in range(4)] for _ in range(3)]

    for position in positions:
        pos = position.get("position", [])
        if len(pos) >= 2:
            row, col = pos[0], pos[1]
            if 0 <= row < 3 and 0 <= col < 4:
                # Bestimme Anzeige-Text basierend auf Typ
                if position.get("type") == "MODULE":
                    name = position.get("name", "UNKNOWN")
                    icon = position.get("icon", "❓")
                    matrix[row][col] = f"{icon} {name}"
                elif position.get("type") == "INTERSECTION":
                    name = position.get("name", "UNKNOWN")
                    icon = position.get("icon", "➕")
                    matrix[row][col] = f"{icon} {name}"
                elif position.get("type") == "EMPTY":
                    matrix[row][col] = "⬜ Leer"

    return matrix


def show_grid_with_icons(positions: List[Dict[str, Any]]):
    """Zeigt das Grid mit Modul-Icons"""
    # Erstelle 3x4 Grid
    for row in range(3):
        cols = st.columns(4)
        for col in range(4):
            with cols[col]:
                # Finde Modul an dieser Position
                module = next((p for p in positions if p.get("position") == [row, col]), None)

                if module:
                    module_type = module.get("type", "UNKNOWN")
                    module_id = module.get("id", "UNKNOWN")
                    module_name = module.get("name", module_id)

                    if module_type == "MODULE":
                        display_module_icon(module_id, width=60, caption=module_name)
                    elif module_type == "INTERSECTION":
                        st.markdown(f"➕ {module_name}")
                    else:
                        st.markdown("⬜")
                else:
                    st.markdown("⬜")


def show_ascii_layout():
    """Zeigt das ASCII-Layout basierend auf der Dokumentation"""
    ascii_layout = """
```
[EMPTY]    [MILL]    [AIQS]    [EMPTY]
              |         |
[HBW] ------[I1]------[I2]-------[DPS]
              |         |
[DRILL] -----[I3]------[I4]-------[CHRG]
```

**Legende:**
- **Module:** HBW, DRILL, MILL, AIQS, DPS, CHRG
- **Kreuzungen:** I1, I2, I3, I4
- **Leere Positionen:** EMPTY
    """
    st.code(ascii_layout, language="text")


def show_module_details():
    """Zeigt detaillierte Informationen zu allen Modulen"""
    st.subheader("🏭 Modul-Details")

    positions = get_module_positions()
    modules = [p for p in positions if p.get("type") == "MODULE"]

    if not modules:
        st.warning("⚠️ Keine Module gefunden")
        return

    # Erstelle DataFrame für Module
    module_data = []
    for module in modules:
        module_data.append(
            {
                "Position": f"[{module.get('position', [0, 0])[0]}, {module.get('position', [0, 0])[1]}]",
                "ID": module.get("id", "UNKNOWN"),
                "Name": module.get("name", "UNKNOWN"),
                "Typ": module.get("type", "UNKNOWN"),
                "Serial": module.get("module_serial", "N/A"),
                "Status": "✅ Aktiv" if module.get("enabled", False) else "❌ Inaktiv",
                "Icon": module.get("icon", "❓"),
                "Beschreibung": module.get("description", "Keine Beschreibung"),
            }
        )

    df = pd.DataFrame(module_data)
    st.dataframe(df, use_container_width=True)

    # Modul-spezifische Details
    show_module_specific_details(modules)


def show_module_specific_details(modules: List[Dict[str, Any]]):
    """Zeigt spezifische Details für jedes Modul"""
    st.subheader("🔧 Modul-spezifische Details")

    for module in modules:
        module_id = module.get("id", "UNKNOWN")
        module_name = module.get("name", "UNKNOWN")

        with st.expander(f"{module.get('icon', '❓')} {module_name} - {module_id}"):
            col1, col2, col3 = st.columns([1, 2, 2])

            with col1:
                # Zeige Modul-Icon
                display_module_icon(module_id, width=80, caption=module_name)

            with col2:
                st.write(f"**Position:** [{module.get('position', [0, 0])[0]}, {module.get('position', [0, 0])[1]}]")
                st.write(f"**Serial Number:** {module.get('module_serial', 'N/A')}")
                st.write(f"**Typ:** {module.get('type', 'UNKNOWN')}")
                st.write(f"**Status:** {'✅ Aktiv' if module.get('enabled', False) else '❌ Inaktiv'}")

            with col3:
                commands = module.get("commands", [])
                if commands:
                    st.write("**Verfügbare Befehle:**")
                    for cmd in commands:
                        st.write(f"- {cmd}")
                else:
                    st.write("**Keine Befehle definiert**")

            st.write(f"**Beschreibung:** {module.get('description', 'Keine Beschreibung')}")


def show_shopfloor_statistics():
    """Zeigt Shopfloor-Statistiken"""
    st.subheader("📊 Shopfloor-Statistiken")

    stats = get_shopfloor_statistics()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Gesamtpositionen", stats.get("total_positions", 0))
        st.metric("Module", stats.get("modules", 0))

    with col2:
        st.metric("Kreuzungen", stats.get("intersections", 0))
        st.metric("Leere Positionen", stats.get("empty_positions", 0))

    with col3:
        st.metric("Aktive Module", stats.get("active_modules", 0))
        st.metric("Gesamtrouten", stats.get("total_routes", 0))

    with col4:
        st.metric("Produkt-Routen", stats.get("product_routes", 0))
        st.metric("Grid-Größe", stats.get("grid_size", "4x3"))


def get_module_by_serial(serial_number: str) -> Optional[Dict[str, Any]]:
    """Findet ein Modul anhand der Serial Number"""
    positions = get_module_positions()

    for position in positions:
        if position.get("module_serial") == serial_number:
            return position
    return None


def get_modules_by_type(module_type: str) -> List[Dict[str, Any]]:
    """Gibt alle Module eines bestimmten Typs zurück"""
    positions = get_module_positions()

    return [p for p in positions if p.get("type") == "MODULE" and p.get("name") == module_type]


def get_intersections() -> List[Dict[str, Any]]:
    """Gibt alle Kreuzungspunkte zurück"""
    positions = get_module_positions()

    return [p for p in positions if p.get("type") == "INTERSECTION"]


def get_enabled_modules() -> List[Dict[str, Any]]:
    """Gibt alle aktiven Module zurück"""
    positions = get_module_positions()

    return [p for p in positions if p.get("type") == "MODULE" and p.get("enabled", False)]


def get_shopfloor_metadata() -> Dict[str, Any]:
    """Lädt Shopfloor-Metadaten aus der Konfiguration"""
    try:
        from pathlib import Path

        import yaml

        config_file = Path(__file__).parent.parent.parent.parent / "config" / "shopfloor" / "layout.yml"
        if config_file.exists():
            with open(config_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                metadata = config.get("metadata", {})
                return {
                    "version": metadata.get("version", "3.3.0"),
                    "grid_size": metadata.get("grid_size", "4x3"),
                    "total_positions": metadata.get("total_positions", 12),
                    "fts_serial": "5iO4",
                }
    except Exception:
        pass

    return {"version": "3.3.0", "grid_size": "4x3", "total_positions": 12, "fts_serial": "5iO4"}


def get_module_positions() -> List[Dict[str, Any]]:
    """Lädt Modul-Positionen aus der Konfiguration"""
    try:
        from pathlib import Path

        import yaml

        config_file = Path(__file__).parent.parent.parent.parent / "config" / "shopfloor" / "layout.yml"
        # Fallback für absoluten Pfad
        if not config_file.exists():
            config_file = Path("omf/config/shopfloor/layout.yml")
        if config_file.exists():
            with open(config_file, encoding="utf-8") as f:
                config = yaml.safe_load(f)
                positions = config.get("positions", [])

                # Icons aus module_config.yml hinzufügen
                module_config_file = Path(__file__).parent.parent.parent.parent / "config" / "module_config.yml"
                # Fallback für absoluten Pfad
                if not module_config_file.exists():
                    module_config_file = Path("omf/config/module_config.yml")
                if module_config_file.exists():
                    with open(module_config_file, encoding="utf-8") as f:
                        module_config = yaml.safe_load(f)
                        modules = module_config.get("modules", {})

                        # Icons zu Positionen hinzufügen
                        for position in positions:
                            if position.get("type") == "MODULE":
                                module_serial = position.get("module_serial")
                                if module_serial in modules:
                                    position["icon"] = modules[module_serial].get("icon", "❓")
                                else:
                                    # Fallback: Suche nach Modul-Name
                                    module_name = position.get("id")
                                    for _serial, module_data in modules.items():
                                        if module_data.get("name") == module_name:
                                            position["icon"] = module_data.get("icon", "❓")
                                            break
                                    else:
                                        position["icon"] = "❓"
                            elif position.get("type") == "INTERSECTION":
                                position["icon"] = "➕"
                            elif position.get("type") == "EMPTY":
                                position["icon"] = "⬜"

                return positions
    except Exception:
        pass

    return []


def get_shopfloor_statistics() -> Dict[str, Any]:
    """Berechnet Shopfloor-Statistiken"""
    positions = get_module_positions()

    total_positions = len(positions)
    modules = len([p for p in positions if p.get("type") == "MODULE"])
    intersections = len([p for p in positions if p.get("type") == "INTERSECTION"])
    empty_positions = len([p for p in positions if p.get("type") == "EMPTY"])
    active_modules = len([p for p in positions if p.get("type") == "MODULE" and p.get("enabled", False)])

    return {
        "total_positions": total_positions,
        "modules": modules,
        "intersections": intersections,
        "empty_positions": empty_positions,
        "active_modules": active_modules,
        "total_routes": 11,  # Aus routes.yml
        "product_routes": 3,  # Aus routes.yml
        "grid_size": "4x3",
    }
