"""
OMF Dashboard Shopfloor Positioning - Modul-Positionierung
Verwaltung und Anzeige der Modul-Positionen im 4x3 Grid
"""

from typing import Any, Dict, List, Optional

import pandas as pd
import streamlit as st

from .shopfloor_utils import get_intersections, get_module_positions


def show_shopfloor_positioning():
    """Zeigt die Modul-Positionierung"""
    st.subheader("📍 Modul-Positionierung")

    # Grid-Übersicht
    show_positioning_overview()

    st.divider()

    # Modul-Positionen
    show_module_positions()

    st.divider()

    # Kreuzungspunkte
    show_intersections()

    st.divider()

    # Positionierungs-Statistiken
    show_positioning_statistics()


def show_positioning_overview():
    """Zeigt eine Übersicht der Positionierung"""
    st.subheader("📊 Positionierungs-Übersicht")

    positions = get_module_positions()

    # Erstelle Grid-Matrix für Positionierung
    grid_matrix = create_positioning_matrix(positions)

    # Zeige Grid als Tabelle
    df = pd.DataFrame(grid_matrix)
    df.index = [f"Zeile {i}" for i in range(3)]
    df.columns = [f"Spalte {i}" for i in range(4)]

    st.dataframe(df, use_container_width=True)

    # Grid-Legende
    show_grid_legend()


def create_positioning_matrix(positions: List[Dict[str, Any]]) -> List[List[str]]:
    """Erstellt eine 3x4 Matrix für die Positionierungs-Darstellung"""
    matrix = [["" for _ in range(4)] for _ in range(3)]

    for position in positions:
        pos = position.get("position", [])
        if len(pos) >= 2:
            row, col = pos[0], pos[1]
            if 0 <= row < 3 and 0 <= col < 4:
                # Bestimme Anzeige-Text basierend auf Typ und Status
                if position.get("type") == "MODULE":
                    name = position.get("name", "UNKNOWN")
                    icon = position.get("icon", "❓")
                    status = "✅" if position.get("enabled", False) else "❌"
                    matrix[row][col] = f"{icon} {name} {status}"
                elif position.get("type") == "INTERSECTION":
                    name = position.get("name", "UNKNOWN")
                    icon = position.get("icon", "➕")
                    matrix[row][col] = f"{icon} {name}"
                elif position.get("type") == "EMPTY":
                    matrix[row][col] = "⬜ Leer"

    return matrix


def show_grid_legend():
    """Zeigt die Grid-Legende"""
    st.subheader("📋 Grid-Legende")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.write("**Module:**")
        st.write("🏬 HBW - Hochregallager")
        st.write("🔩 DRILL - Bohrer")
        st.write("⚙️ MILL - Fräse")
        st.write("🔍 AIQS - Qualitätssicherung")
        st.write("🔩 DPS - Bohr-Verarbeitungsstation")
        st.write("🔌 CHRG - FTS-Ladestation")

    with col2:
        st.write("**Kreuzungen:**")
        st.write("➕ I1 - HBW ↔ MILL")
        st.write("➕ I2 - MILL ↔ AIQS ↔ DPS")
        st.write("➕ I3 - DRILL ↔ HBW")
        st.write("➕ I4 - DRILL ↔ CHRG ↔ DPS")

    with col3:
        st.write("**Status:**")
        st.write("✅ Aktiv")
        st.write("❌ Inaktiv")
        st.write("⬜ Leer")


def show_module_positions():
    """Zeigt detaillierte Modul-Positionen"""
    st.subheader("🏭 Modul-Positionen")

    positions = get_module_positions()
    modules = [p for p in positions if p.get("type") == "MODULE"]

    if not modules:
        st.warning("⚠️ Keine Module gefunden")
        return

    # Erstelle DataFrame für Modul-Positionen
    position_data = []
    for module in modules:
        pos = module.get("position", [0, 0])
        position_data.append(
            {
                "Modul": module.get("name", "UNKNOWN"),
                "ID": module.get("id", "UNKNOWN"),
                "Position": f"[{pos[0]}, {pos[1]}]",
                "Zeile": pos[0] if len(pos) > 0 else 0,
                "Spalte": pos[1] if len(pos) > 1 else 0,
                "Serial": module.get("module_serial", "N/A"),
                "Status": "✅ Aktiv" if module.get("enabled", False) else "❌ Inaktiv",
                "Icon": module.get("icon", "❓"),
            }
        )

    df = pd.DataFrame(position_data)
    st.dataframe(df, use_container_width=True)

    # Modul-Position-Details
    show_module_position_details(modules)


def show_module_position_details(modules: List[Dict[str, Any]]):
    """Zeigt detaillierte Informationen zu den Modul-Positionen"""
    st.subheader("🔍 Modul-Position-Details")

    for module in modules:
        pos = module.get("position", [0, 0])
        with st.expander(f"{module.get('icon', '❓')} {module.get('name', 'UNKNOWN')} - Position [{pos[0]}, {pos[1]}]"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Modul-ID:** {module.get('id', 'UNKNOWN')}")
                st.write(f"**Position:** [{pos[0]}, {pos[1]}]")
                st.write(f"**Zeile:** {pos[0] if len(pos) > 0 else 0}")
                st.write(f"**Spalte:** {pos[1] if len(pos) > 1 else 0}")
                st.write(f"**Serial Number:** {module.get('module_serial', 'N/A')}")

            with col2:
                st.write(f"**Typ:** {module.get('type', 'UNKNOWN')}")
                st.write(f"**Status:** {'✅ Aktiv' if module.get('enabled', False) else '❌ Inaktiv'}")
                st.write(f"**Icon:** {module.get('icon', '❓')}")

                commands = module.get("commands", [])
                if commands:
                    st.write("**Verfügbare Befehle:**")
                    for cmd in commands:
                        st.write(f"- {cmd}")
                else:
                    st.write("**Keine Befehle definiert**")

            st.write(f"**Beschreibung:** {module.get('description', 'Keine Beschreibung')}")


def show_intersections():
    """Zeigt die Kreuzungspunkte"""
    st.subheader("➕ Kreuzungspunkte")

    intersections = get_intersections()

    if not intersections:
        st.warning("⚠️ Keine Kreuzungspunkte gefunden")
        return

    # Erstelle DataFrame für Kreuzungen
    intersection_data = []
    for intersection in intersections:
        pos = intersection.get("position", [0, 0])
        connected = intersection.get("connected_modules", [])
        intersection_data.append(
            {
                "ID": intersection.get("id", "UNKNOWN"),
                "Name": intersection.get("name", "UNKNOWN"),
                "Position": f"[{pos[0]}, {pos[1]}]",
                "Zeile": pos[0] if len(pos) > 0 else 0,
                "Spalte": pos[1] if len(pos) > 1 else 0,
                "Verbunden mit": ", ".join(connected),
                "Anzahl Verbindungen": len(connected),
                "Status": "✅ Aktiv" if intersection.get("enabled", False) else "❌ Inaktiv",
            }
        )

    df = pd.DataFrame(intersection_data)
    st.dataframe(df, use_container_width=True)

    # Kreuzungs-Details
    show_intersection_details(intersections)


def show_intersection_details(intersections: List[Dict[str, Any]]):
    """Zeigt detaillierte Informationen zu den Kreuzungspunkten"""
    st.subheader("🔍 Kreuzungs-Details")

    for intersection in intersections:
        pos = intersection.get("position", [0, 0])
        connected = intersection.get("connected_modules", [])

        with st.expander(f"➕ {intersection.get('name', 'UNKNOWN')} - Position [{pos[0]}, {pos[1]}]"):
            col1, col2 = st.columns(2)

            with col1:
                st.write(f"**Kreuzungs-ID:** {intersection.get('id', 'UNKNOWN')}")
                st.write(f"**Position:** [{pos[0]}, {pos[1]}]")
                st.write(f"**Zeile:** {pos[0] if len(pos) > 0 else 0}")
                st.write(f"**Spalte:** {pos[1] if len(pos) > 1 else 0}")
                st.write(f"**Status:** {'✅ Aktiv' if intersection.get('enabled', False) else '❌ Inaktiv'}")

            with col2:
                st.write(f"**Anzahl Verbindungen:** {len(connected)}")
                if connected:
                    st.write("**Verbunden mit:**")
                    for module in connected:
                        st.write(f"- {module}")
                else:
                    st.write("**Keine Verbindungen**")

            st.write(f"**Beschreibung:** {intersection.get('description', 'Keine Beschreibung')}")


def show_positioning_statistics():
    """Zeigt Positionierungs-Statistiken"""
    st.subheader("📊 Positionierungs-Statistiken")

    positions = get_module_positions()
    modules = [p for p in positions if p.get("type") == "MODULE"]
    intersections = [p for p in positions if p.get("type") == "INTERSECTION"]
    empty_positions = [p for p in positions if p.get("type") == "EMPTY"]
    enabled_modules = [p for p in modules if p.get("enabled", False)]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Gesamtpositionen", len(positions))
        st.metric("Module", len(modules))

    with col2:
        st.metric("Kreuzungen", len(intersections))
        st.metric("Leere Positionen", len(empty_positions))

    with col3:
        st.metric("Aktive Module", len(enabled_modules))
        st.metric("Inaktive Module", len(modules) - len(enabled_modules))

    with col4:
        st.metric("Auslastung", f"{(len(modules) / len(positions) * 100):.1f}%")
        st.metric("Aktivierungsrate", f"{(len(enabled_modules) / len(modules) * 100):.1f}%" if modules else "0%")


def get_position_by_coordinates(row: int, col: int) -> Optional[Dict[str, Any]]:
    """Gibt die Position an bestimmten Koordinaten zurück"""
    positions = get_module_positions()

    for position in positions:
        pos = position.get("position", [])
        if len(pos) >= 2 and pos[0] == row and pos[1] == col:
            return position
    return None


def get_modules_in_row(row: int) -> List[Dict[str, Any]]:
    """Gibt alle Module in einer bestimmten Zeile zurück"""
    positions = get_module_positions()

    return [p for p in positions if p.get("type") == "MODULE" and p.get("position", [0, 0])[0] == row]


def get_modules_in_column(col: int) -> List[Dict[str, Any]]:
    """Gibt alle Module in einer bestimmten Spalte zurück"""
    positions = get_module_positions()

    return [p for p in positions if p.get("type") == "MODULE" and p.get("position", [0, 0])[1] == col]


def get_neighboring_positions(row: int, col: int) -> List[Dict[str, Any]]:
    """Gibt alle benachbarten Positionen zurück"""
    _positions = get_module_positions()
    neighbors = []

    # Prüfe alle 8 Nachbarpositionen
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue  # Überspringe die Position selbst

            neighbor_row = row + dr
            neighbor_col = col + dc

            # Prüfe ob die Position im Grid liegt
            if 0 <= neighbor_row < 3 and 0 <= neighbor_col < 4:
                neighbor = get_position_by_coordinates(neighbor_row, neighbor_col)
                if neighbor:
                    neighbors.append(neighbor)

    return neighbors
