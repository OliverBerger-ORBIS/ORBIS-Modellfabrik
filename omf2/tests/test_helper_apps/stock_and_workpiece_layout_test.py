"""
Test-App für Stock und Workpiece Layout
=======================================

Testet die Workpiece-Management Lösung mit:
- SVG-basierte Workpiece-Darstellung
- OMF2 Asset Manager Integration
- Verschiedene Workpiece-Zustände (unprocessed, instock_reserved, etc.)
- Professionelle UI-Komponenten statt HTML-Templates
- Vorbereitung für OMF2-Integration
"""

import sys
from pathlib import Path

import streamlit as st

# OMF2 Imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Force reload to avoid cache issues
import importlib
import importlib.util

# Lade Asset Manager direkt aus der Datei (umgeht Python Cache)
spec = importlib.util.spec_from_file_location("asset_manager", str(Path(__file__).parent.parent.parent / "assets" / "asset_manager.py"))
asset_manager_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(asset_manager_module)
get_asset_manager = asset_manager_module.get_asset_manager

# Page configuration
st.set_page_config(page_title="Stock & Workpiece Layout Test", page_icon="📦", layout="wide", initial_sidebar_state="expanded")


def main():
    st.title("📦 Stock & Workpiece Layout Test")
    st.markdown("**SVG-basierte Workpiece-Management über Asset-Manager - Vorbereitung für OMF2-Integration**")

    # Asset Manager initialisieren
    asset_manager = get_asset_manager()

    # Tab-Navigation
    tab1, tab2, tab3 = st.tabs(["🎨 Dummy-Tab: Asset-Übersicht", "📋 Purchase Order", "👤 Customer Order"])
    
    with tab1:
        _show_dummy_asset_overview(asset_manager)
    
    with tab2:
        _show_purchase_order_dummy(asset_manager)
    
    with tab3:
        _show_customer_order_dummy(asset_manager)

    # Sidebar Controls
    st.sidebar.header("🎛️ Controls")

    # Workpiece Type Selection
    workpiece_type = st.sidebar.selectbox(
        "Workpiece Type:",
        ["BLUE", "RED", "WHITE"],
        index=0,
    )

    # Workpiece State Selection
    workpiece_state = st.sidebar.selectbox(
        "Workpiece State:",
        ["unprocessed", "instock_unprocessed", "instock_reserved", "drilled", "milled", "drilled_and_milled", "3dim"],
        index=0,
    )

    # Count Selection
    count = st.sidebar.slider(
        "Count:",
        min_value=0,
        max_value=20,
        value=5,
        help="Anzahl der Werkstücke",
    )

    # Available Status
    available = st.sidebar.checkbox(
        "Available",
        value=True,
        help="Ob Werkstücke verfügbar sind",
    )

    # Debug Info
    show_debug = st.sidebar.checkbox("Show Debug Info", value=False)

    # Debug Information
    if show_debug:
        st.subheader("🔍 Debug Information")
        _show_debug_info(asset_manager, workpiece_type, workpiece_state)


def _show_dummy_asset_overview(asset_manager):
    """Dummy-Tab: Zeigt alle verfügbaren Workpiece-Assets über Asset-Manager"""
    st.subheader("🎨 Asset-Übersicht: Verfügbare Workpiece-SVGs")
    st.markdown("**Übersicht aller verfügbaren Workpiece-SVG-Assets - Sortiert nach Farben**")
    st.markdown("**Verwendete Asset-Manager-Methode:** `asset_manager.get_workpiece_svg_content()`")
    
    # Asset-Manager Debug-Info
    workpiece_dir = asset_manager.assets_dir / "workpiece"
    
    if workpiece_dir.exists():
        svg_files = list(workpiece_dir.glob("*.svg"))
        st.success(f"✅ {len(svg_files)} Workpiece-SVG-Assets gefunden")
        
        # NEUE VEREINHEITLICHTE PRODUCT-SVGs (Registry/CCU-Alignment)
        st.markdown("### 🎯 **VEREINHEITLICHTE PRODUCT-SVGs**")
        st.markdown("**Registry & CCU-Domain Alignment:** `blue_product.svg`, `white_product.svg`, `red_product.svg`")
        
        # BLUE-Sektion
        st.markdown("#### 🔵 BLUE Workpieces")
        blue_methods = [
            ("get_product", "BLUE", "blue_product.svg"),
            ("get_3dim", "BLUE", "blue_3dim.svg"),
            ("get_unprocessed", "BLUE", "blue_unprocessed.svg"),
            ("get_instock_unprocessed", "BLUE", "blue_instock_unprocessed.svg"),
            ("get_instock_reserved", "BLUE", "blue_instock_reserved.svg"),
            ("get_drilled", "BLUE", "blue_drilled.svg"),
            ("get_milled", "BLUE", "blue_milled.svg"),
            ("get_drilled_and_milled", "BLUE", "blue_drilled_and_milled.svg")
        ]
        
        for method_name, color, filename in blue_methods:
            method = getattr(asset_manager.workpiece, method_name)
            svg_content = method(color)
            if svg_content:
                _display_svg_content(svg_content, "🔵", filename, highlight=(method_name == "get_product"))
                st.markdown(f"**Call:** `asset_manager.workpiece.{method_name}('{color}')`")
            else:
                st.error(f"❌ {filename} nicht gefunden!")
        
        # WHITE-Sektion
        st.markdown("#### ⚪ WHITE Workpieces")
        white_methods = [
            ("get_product", "WHITE", "white_product.svg"),
            ("get_3dim", "WHITE", "white_3dim.svg"),
            ("get_unprocessed", "WHITE", "white_unprocessed.svg"),
            ("get_instock_unprocessed", "WHITE", "white_instock_unprocessed.svg"),
            ("get_instock_reserved", "WHITE", "white_instock_reserved.svg"),
            ("get_drilled", "WHITE", "white_drilled.svg"),
            ("get_milled", "WHITE", "white_milled.svg"),
            ("get_drilled_and_milled", "WHITE", "white_drilled_and_milled.svg")
        ]
        
        for method_name, color, filename in white_methods:
            method = getattr(asset_manager.workpiece, method_name)
            svg_content = method(color)
            if svg_content:
                _display_svg_content(svg_content, "⚪", filename, highlight=(method_name == "get_product"))
                st.markdown(f"**Call:** `asset_manager.workpiece.{method_name}('{color}')`")
            else:
                st.error(f"❌ {filename} nicht gefunden!")
        
        # RED-Sektion
        st.markdown("#### 🔴 RED Workpieces")
        red_methods = [
            ("get_product", "RED", "red_product.svg"),
            ("get_3dim", "RED", "red_3dim.svg"),
            ("get_unprocessed", "RED", "red_unprocessed.svg"),
            ("get_instock_unprocessed", "RED", "red_instock_unprocessed.svg"),
            ("get_instock_reserved", "RED", "red_instock_reserved.svg"),
            ("get_drilled", "RED", "red_drilled.svg"),
            ("get_milled", "RED", "red_milled.svg"),
            ("get_drilled_and_milled", "RED", "red_drilled_and_milled.svg")
        ]
        
        for method_name, color, filename in red_methods:
            method = getattr(asset_manager.workpiece, method_name)
            svg_content = method(color)
            if svg_content:
                _display_svg_content(svg_content, "🔴", filename, highlight=(method_name == "get_product"))
                st.markdown(f"**Call:** `asset_manager.workpiece.{method_name}('{color}')`")
            else:
                st.error(f"❌ {filename} nicht gefunden!")
        
        # SONDERMETHODE: getPalett()
        st.markdown("---")
        st.markdown("#### 🎨 **SONDERMETHODE: getPalett()**")
        st.markdown("**Spezielle Palett-SVG für alle Workpieces**")
        
        # Palett-SVG über Asset-Manager laden
        palett_content = asset_manager.workpiece.get_palett()
        if palett_content:
            _display_svg_content(palett_content, "🎨", "palett.svg")
            st.markdown("**Call:** `asset_manager.workpiece.get_palett()`")
        else:
            st.error("❌ palett.svg nicht gefunden!")
        
        # Test der Asset-Manager-Methode
        st.markdown("---")
        st.markdown("### 🧪 **Asset-Manager Test**")
        st.markdown("**Test der neuen vereinheitlichten Namenskonvention:**")
        
        test_col1, test_col2, test_col3 = st.columns(3)
        
        with test_col1:
            st.markdown("**BLUE Test:**")
            try:
                blue_svg_content = asset_manager.workpiece.get_product("BLUE")
                if blue_svg_content:
                    st.success("✅ BLUE SVG geladen")
                    st.code(f"asset_manager.workpiece.get_product('BLUE')", language="python")
                else:
                    st.error("❌ BLUE SVG nicht geladen")
            except Exception as e:
                st.error(f"❌ Fehler: {e}")
        
        with test_col2:
            st.markdown("**WHITE Test:**")
            try:
                white_svg_content = asset_manager.workpiece.get_product("WHITE")
                if white_svg_content:
                    st.success("✅ WHITE SVG geladen")
                    st.code(f"asset_manager.workpiece.get_product('WHITE')", language="python")
                else:
                    st.error("❌ WHITE SVG nicht geladen")
            except Exception as e:
                st.error(f"❌ Fehler: {e}")
        
        with test_col3:
            st.markdown("**RED Test:**")
            try:
                red_svg_content = asset_manager.workpiece.get_product("RED")
                if red_svg_content:
                    st.success("✅ RED SVG geladen")
                    st.code(f"asset_manager.workpiece.get_product('RED')", language="python")
                else:
                    st.error("❌ RED SVG nicht geladen")
            except Exception as e:
                st.error(f"❌ Fehler: {e}")
                    
    else:
        st.error("❌ Workpiece-Verzeichnis nicht gefunden!")
        st.markdown(f"**Erwarteter Pfad:** `{workpiece_dir}`")


def _display_svg_content(svg_content: str, emoji: str, filename: str, highlight=False):
    """Zeigt SVG-Inhalt direkt mit Debug-Info"""
    st.markdown(f"**{emoji} {filename.replace('.svg', '')}**")
    
    # SVG-Inhalt analysieren
    svg_id = "N/A"
    svg_g_id = "N/A"
    if 'id=' in svg_content:
        import re
        id_match = re.search(r'id="([^"]*)"', svg_content)
        if id_match:
            svg_id = id_match.group(1)
    
    if '<g id=' in svg_content:
        import re
        g_match = re.search(r'<g id="([^"]*)"', svg_content)
        if g_match:
            svg_g_id = g_match.group(1)
    
    # Container-Styling basierend auf Highlight-Status
    if highlight:
        border_style = "3px solid #4ecdc4"
        background_style = "linear-gradient(135deg, rgba(78,205,196,0.1), rgba(78,205,196,0.05))"
        box_shadow = "0 6px 12px rgba(78,205,196,0.3)"
    else:
        border_style = "2px solid #ddd"
        background_style = "#f9f9f9"
        box_shadow = "0 2px 4px rgba(0,0,0,0.1)"
    
    # SVG in Container einbetten - 50% größer als bisher (120px statt 80px)
    st.markdown(f"""
    <div style="display: flex; justify-content: center; padding: 10px; border: {border_style}; border-radius: 8px; background: {background_style}; box-shadow: {box_shadow};">
        <div style="width: 120px; height: 120px; display: flex; align-items: center; justify-content: center; overflow: hidden;">
            <div style="transform: scale(0.45); transform-origin: center;">
                {svg_content}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Debug-Info anzeigen
    st.caption(f"📄 {filename}")
    st.caption(f"🆔 SVG ID: {svg_id}")
    st.caption(f"🏷️ G ID: {svg_g_id}")
    
    # Spezielle Info für product-SVGs
    if highlight and filename.endswith('_product.svg'):
        st.caption("🎯 **NEUE VEREINHEITLICHTE NAMENSKONVENTION**")


def _display_single_svg(svg_file, emoji, highlight=False):
    """Zeigt eine einzelne SVG-Datei mit Debug-Info"""
    st.markdown(f"**{emoji} {svg_file.stem}**")
    
    # SVG-Inhalt laden und anzeigen
    try:
        with open(svg_file, 'r', encoding='utf-8') as f:
            svg_content = f.read()
        
        # SVG-Inhalt analysieren
        svg_id = "N/A"
        svg_g_id = "N/A"
        if 'id=' in svg_content:
            import re
            id_match = re.search(r'id="([^"]*)"', svg_content)
            if id_match:
                svg_id = id_match.group(1)
        
        if '<g id=' in svg_content:
            import re
            g_match = re.search(r'<g id="([^"]*)"', svg_content)
            if g_match:
                svg_g_id = g_match.group(1)
        
        # Container-Styling basierend auf Highlight-Status
        if highlight:
            border_style = "3px solid #4ecdc4"
            background_style = "linear-gradient(135deg, rgba(78,205,196,0.1), rgba(78,205,196,0.05))"
            box_shadow = "0 6px 12px rgba(78,205,196,0.3)"
        else:
            border_style = "2px solid #ddd"
            background_style = "#f9f9f9"
            box_shadow = "0 2px 4px rgba(0,0,0,0.1)"
        
        # SVG in Container einbetten mit besserer Größenanpassung
        st.markdown(f"""
        <div style="display: flex; justify-content: center; padding: 10px; border: {border_style}; border-radius: 8px; background: {background_style}; box-shadow: {box_shadow};">
            <div style="width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; overflow: hidden;">
                <div style="transform: scale(0.3); transform-origin: center;">
                    {svg_content}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Debug-Info anzeigen
        st.caption(f"📄 {svg_file.name}")
        st.caption(f"🆔 SVG ID: {svg_id}")
        st.caption(f"🏷️ G ID: {svg_g_id}")
        
        # Spezielle Info für product-SVGs
        if highlight and svg_file.name.endswith('_product.svg'):
            st.caption("🎯 **NEUE VEREINHEITLICHTE NAMENSKONVENTION**")
        
    except Exception as e:
        st.error(f"Fehler beim Laden von {svg_file.name}: {e}")


def _show_purchase_order_dummy(asset_manager):
    """Dummy-Tab: Purchase Order Darstellung mit Asset-Manager"""
    st.subheader("📋 Purchase Order Dummy")
    st.markdown("**Simulation der Purchase Order View mit SVG-Komponenten**")
    
    # Beispiel-Daten
    purchase_orders = [
        {"type": "BLUE", "count": 10, "available": True},
        {"type": "WHITE", "count": 5, "available": True},
        {"type": "RED", "count": 3, "available": False},
    ]
    
    cols = st.columns(len(purchase_orders))
    
    for i, order in enumerate(purchase_orders):
        with cols[i]:
            st.markdown(f"**{order['type']} Purchase Order**")
            
            # SVG-basierte Darstellung
            svg_content = _get_workpiece_svg(order['type'], order['count'], order['available'], asset_manager)
            st.markdown(svg_content, unsafe_allow_html=True)
            
            # Zusätzliche Infos
            st.markdown(f"**Anzahl:** {order['count']}")
            st.markdown(f"**Status:** {'✅ Verfügbar' if order['available'] else '❌ Nicht verfügbar'}")


def _show_customer_order_dummy(asset_manager):
    """Dummy-Tab: Customer Order Darstellung mit Asset-Manager"""
    st.subheader("👤 Customer Order Dummy")
    st.markdown("**Simulation der Customer Order View mit SVG-Komponenten**")
    
    # Beispiel-Daten
    customer_orders = [
        {"type": "BLUE", "count": 2, "available": True},
        {"type": "WHITE", "count": 1, "available": True},
        {"type": "RED", "count": 4, "available": False},
    ]
    
    cols = st.columns(len(customer_orders))
    
    for i, order in enumerate(customer_orders):
        with cols[i]:
            st.markdown(f"**{order['type']} Customer Order**")
            
            # SVG-basierte Darstellung
            svg_content = _get_workpiece_svg(order['type'], order['count'], order['available'], asset_manager)
            st.markdown(svg_content, unsafe_allow_html=True)
            
            # Zusätzliche Infos
            st.markdown(f"**Bestellt:** {order['count']}")
            st.markdown(f"**Status:** {'✅ Verfügbar' if order['available'] else '❌ Nicht verfügbar'}")


def _show_purchase_order_view(workpiece_type: str, count: int, available: bool, asset_manager):
    """Zeigt Purchase Order View mit SVG-basierter Workpiece-Darstellung"""
    st.markdown(f"**{workpiece_type} Purchase Order**")
    
    # SVG-basierte Workpiece-Darstellung
    svg_content = _get_workpiece_svg(workpiece_type, count, available, asset_manager)
    st.markdown(svg_content, unsafe_allow_html=True)
    
    # Zusätzliche Informationen
    st.markdown(f"**Bestand:** {count}")
    st.markdown(f"**Verfügbar:** {'✅ Ja' if available else '❌ Nein'}")


def _show_customer_order_view(workpiece_type: str, count: int, available: bool, asset_manager):
    """Zeigt Customer Order View mit SVG-basierter Workpiece-Darstellung"""
    st.markdown(f"**{workpiece_type} Customer Order**")
    
    # SVG-basierte Workpiece-Darstellung
    svg_content = _get_workpiece_svg(workpiece_type, count, available, asset_manager)
    st.markdown(svg_content, unsafe_allow_html=True)
    
    # Zusätzliche Informationen
    st.markdown(f"**Anzahl:** {count}")
    st.markdown(f"**Verfügbar:** {'✅ Ja' if available else '❌ Nein'}")


def _show_inventory_view(workpiece_type: str, count: int, available: bool, asset_manager):
    """Zeigt Inventory View mit SVG-basierter Workpiece-Darstellung"""
    st.markdown(f"**{workpiece_type} Inventory**")
    
    # SVG-basierte Workpiece-Darstellung
    svg_content = _get_workpiece_svg(workpiece_type, count, available, asset_manager)
    st.markdown(svg_content, unsafe_allow_html=True)
    
    # Zusätzliche Informationen
    st.markdown(f"**Lagerbestand:** {count}")
    st.markdown(f"**Status:** {'Verfügbar' if available else 'Nicht verfügbar'}")


def _show_product_catalog_view(asset_manager):
    """Zeigt Product Catalog View mit allen Workpiece-Typen"""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**BLUE Products**")
        svg_content = _get_workpiece_svg("BLUE", 1, True, asset_manager)
        st.markdown(svg_content, unsafe_allow_html=True)
    
    with col2:
        st.markdown("**WHITE Products**")
        svg_content = _get_workpiece_svg("WHITE", 1, True, asset_manager)
        st.markdown(svg_content, unsafe_allow_html=True)
    
    with col3:
        st.markdown("**RED Products**")
        svg_content = _get_workpiece_svg("RED", 1, True, asset_manager)
        st.markdown(svg_content, unsafe_allow_html=True)


def _get_workpiece_svg(workpiece_type: str, count: int, available: bool, asset_manager) -> str:
    """Generiert SVG-basierte Workpiece-Darstellung über Asset Manager"""
    try:
        # Verwende Asset Manager Funktion - aber mit direktem SVG-Loading für bessere Kontrolle
        workpiece_dir = asset_manager.assets_dir / "workpiece"
        
        # Versuche verschiedene SVG-Zustände zu finden
        possible_states = ["unprocessed", "instock_unprocessed", "instock_reserved", "drilled", "milled", "drilled_and_milled", "3dim"]
        svg_content = None
        used_state = "unprocessed"
        
        # Versuche zuerst den gewünschten Zustand
        for state in possible_states:
            svg_filename = f"{workpiece_type.lower()}_{state}.svg"
            svg_path = workpiece_dir / svg_filename
            
            if svg_path.exists():
                with open(svg_path, 'r', encoding='utf-8') as f:
                    svg_content = f.read()
                    used_state = state
                    break
        
        # Fallback: Verwende Asset Manager
        if not svg_content:
            svg_content = asset_manager.get_workpiece_svg_content(workpiece_type, "unprocessed")
        
        if svg_content:
            # SVG anpassen (Größe, Farbe basierend auf Verfügbarkeit)
            opacity = "0.7" if not available else "1.0"
            border_color = "#ff6b6b" if not available else "#4ecdc4"
            
            # SVG in Container einbetten mit besserer Darstellung
            return f"""
            <div style="display: flex; flex-direction: column; align-items: center; padding: 15px; border: 3px solid {border_color}; border-radius: 12px; background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05)); box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <div style="opacity: {opacity}; width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; overflow: hidden;">
                    <div style="transform: scale(0.4); transform-origin: center;">
                        {svg_content}
                    </div>
                </div>
                <div style="margin-top: 10px; font-weight: bold; color: {border_color}; font-size: 16px;">
                    {workpiece_type}
                </div>
                <div style="margin-top: 5px; font-weight: bold; color: {border_color}; font-size: 20px;">
                    {count}
                </div>
                <div style="margin-top: 5px; font-size: 14px;">
                    {'✅ Verfügbar' if available else '❌ Nicht verfügbar'}
                </div>
                <div style="margin-top: 2px; font-size: 10px; color: #666;">
                    State: {used_state}
                </div>
            </div>
            """
        else:
            # Fallback: Einfache Darstellung
            return f"""
            <div style="display: flex; flex-direction: column; align-items: center; padding: 20px; border: 2px solid #ccc; border-radius: 8px; background-color: #f9f9f9;">
                <div style="font-size: 48px; margin-bottom: 10px;">📦</div>
                <div style="font-weight: bold; font-size: 18px;">{workpiece_type}</div>
                <div style="font-size: 16px; margin-top: 5px;">Count: {count}</div>
                <div style="font-size: 14px; margin-top: 5px;">{'✅' if available else '❌'}</div>
            </div>
            """
    
    except Exception as e:
        st.error(f"Fehler beim Laden der Workpiece-SVG: {e}")
        return f"""
        <div style="display: flex; flex-direction: column; align-items: center; padding: 20px; border: 2px solid #ff6b6b; border-radius: 8px; background-color: #ffe6e6;">
            <div style="font-size: 48px; margin-bottom: 10px;">❌</div>
            <div style="font-weight: bold; color: #ff6b6b; font-size: 16px;">Fehler</div>
            <div style="color: #ff6b6b;">{workpiece_type}</div>
            <div style="color: #ff6b6b; font-size: 12px; margin-top: 5px;">{str(e)}</div>
        </div>
        """


def _show_debug_info(asset_manager, workpiece_type: str, workpiece_state: str):
    """Zeigt Debug-Informationen für Entwicklung"""
    st.markdown("**Asset Manager Debug Info:**")
    
    # Verfügbare Workpiece-SVGs
    workpiece_dir = asset_manager.assets_dir / "workpiece"
    if workpiece_dir.exists():
        svg_files = list(workpiece_dir.glob("*.svg"))
        st.markdown(f"**Verfügbare Workpiece-SVGs:** {len(svg_files)}")
        for svg_file in sorted(svg_files):
            st.markdown(f"- {svg_file.name}")
    else:
        st.error("Workpiece-Verzeichnis nicht gefunden!")
    
    # Aktuelle Konfiguration
    st.markdown(f"**Aktuelle Konfiguration:**")
    st.markdown(f"- Workpiece Type: {workpiece_type}")
    st.markdown(f"- Workpiece State: {workpiece_state}")
    st.markdown(f"- Asset Manager: {type(asset_manager).__name__}")
    st.markdown(f"- Assets Dir: {asset_manager.assets_dir}")


if __name__ == "__main__":
    main()
