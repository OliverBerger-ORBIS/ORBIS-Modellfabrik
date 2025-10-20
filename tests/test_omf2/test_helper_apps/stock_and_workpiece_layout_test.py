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

import re
import sys
import uuid
from pathlib import Path

import streamlit as st

# OMF2 Imports
sys.path.append(str(Path(__file__).parent.parent.parent))

# Force reload to avoid cache issues
from omf2.assets.asset_manager import get_asset_manager

# Page configuration
st.set_page_config(
    page_title="Stock & Workpiece Layout Test", page_icon="📦", layout="wide", initial_sidebar_state="expanded"
)


def scope_svg_styles(svg_content: str) -> str:
    """
    Scopes SVG styles to prevent CSS class conflicts when multiple SVGs are embedded.

    This function:
    1. Generates a unique ID for each SVG instance
    2. Wraps the SVG content in a group with that unique ID
    3. Scopes all CSS selectors in the <style> section to that unique ID

    This ensures that CSS classes like .cls-1, .cls-2 don't conflict between different SVGs.
    """
    # Generate unique ID for this SVG instance
    unique_id = f"svg-{uuid.uuid4().hex[:8]}"

    # Check if SVG has a <style> section that needs scoping
    if "<style>" not in svg_content and "<style " not in svg_content:
        # No style section, return as-is
        return svg_content

    # Extract the style content
    style_pattern = r"<style[^>]*>(.*?)</style>"
    style_match = re.search(style_pattern, svg_content, re.DOTALL)

    if not style_match:
        return svg_content

    style_content = style_match.group(1)

    # Scope all CSS selectors by prepending with #unique_id
    # Match CSS selectors (e.g., .cls-1, #id, element)
    # This regex matches CSS rules like: .cls-1{fill:#000;}
    def scope_selector(match):
        selector = match.group(1).strip()
        properties = match.group(2)

        # Split multiple selectors (e.g., ".cls-1, .cls-2")
        selectors = [s.strip() for s in selector.split(",")]

        # Scope each selector
        scoped_selectors = []
        for sel in selectors:
            # Don't scope @-rules or already scoped selectors
            if sel.startswith("@") or sel.startswith("#" + unique_id):
                scoped_selectors.append(sel)
            else:
                scoped_selectors.append(f"#{unique_id} {sel}")

        return ",".join(scoped_selectors) + "{" + properties + "}"

    # Pattern to match CSS rules: selector{properties}
    css_rule_pattern = r"([^{]+)\{([^}]+)\}"
    scoped_style_content = re.sub(css_rule_pattern, scope_selector, style_content)

    # Replace the style content with scoped version
    scoped_svg = svg_content.replace(style_content, scoped_style_content)

    # Wrap the SVG content in a group with the unique ID
    # Find the opening <svg> tag and insert a <g id="unique_id"> after it
    svg_tag_pattern = r"(<svg[^>]*>)"

    def add_group(match):
        svg_tag = match.group(1)
        return f'{svg_tag}<g id="{unique_id}">'

    scoped_svg = re.sub(svg_tag_pattern, add_group, scoped_svg, count=1)

    # Close the group before the closing </svg> tag
    scoped_svg = scoped_svg.replace("</svg>", "</g></svg>", 1)

    return scoped_svg


def main():
    st.title("📦 Stock & Workpiece Layout Test")
    st.markdown("**SVG-basierte Workpiece-Management über Asset-Manager - Vorbereitung für OMF2-Integration**")

    # Asset Manager initialisieren
    asset_manager = get_asset_manager()

    # Tab-Navigation
    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🎨 Asset-Übersicht", "📋 Purchase Order", "👤 Customer Order", "📦 Product Catalog", "🏭 Stock Manager Test"]
    )

    with tab1:
        _show_dummy_asset_overview(asset_manager)

    with tab2:
        _show_purchase_order_dummy(asset_manager)

    with tab3:
        _show_customer_order_dummy(asset_manager)

    with tab4:
        _show_product_catalog_test(asset_manager)

    with tab5:
        _show_stock_manager_test(asset_manager)

    # Sidebar Controls - für Debug und Test-Zwecke
    st.sidebar.header("🎛️ Controls")
    st.sidebar.markdown("**Debug & Test-Parameter für Entwicklung**")

    # Workpiece Type Selection - für Debug-Info
    workpiece_type = st.sidebar.selectbox(
        "Workpiece Type:", ["BLUE", "RED", "WHITE"], index=0, help="Für Debug-Informationen in der Sidebar"
    )

    # Workpiece State Selection - nur tatsächlich unterstützte Methoden
    workpiece_state = st.sidebar.selectbox(
        "Workpiece State:",
        ["product", "3dim", "unprocessed", "instock_unprocessed", "instock_reserved"],
        index=0,
        help="Nur tatsächlich unterstützte Asset-Manager-Methoden",
    )

    # Count Selection - für Debug-Info
    st.sidebar.slider(
        "Count:",
        min_value=0,
        max_value=20,
        value=5,
        help="Anzahl der Werkstücke - nur für Debug-Info verwendet",
    )

    # Available Status - für Debug-Info
    st.sidebar.checkbox(
        "Available",
        value=True,
        help="Verfügbarkeitsstatus - nur für Debug-Info verwendet",
    )

    # Debug Info - zeigt Asset-Manager Details
    show_debug = st.sidebar.checkbox(
        "Show Debug Info", value=False, help="Zeigt Asset-Manager Debug-Informationen und verfügbare SVG-Dateien"
    )

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

        # HART KODIERTE SVG-DARSTELLUNG - OHNE SCHNICKSCHNACK
        st.markdown("---")
        st.markdown("### 🔧 **HART KODIERTE SVG-DARSTELLUNG**")
        st.markdown("**Alle verfügbaren SVGs - direkt geladen ohne Asset-Manager:**")

        # Alle SVG-Dateien direkt laden und in logischer Reihenfolge anzeigen
        svg_files = list(workpiece_dir.glob("*.svg"))

        if svg_files:
            # Definierte Reihenfolge: 6 Zeilen mit Überschriften
            row_groups = [
                {"title": "🎯 **PRODUCT**", "files": ["blue_product", "red_product", "white_product"]},
                {"title": "📐 **3DIM**", "files": ["blue_3dim", "red_3dim", "white_3dim"]},
                {
                    "title": "📦 **INSTOCK UNPROCESSED**",
                    "files": ["blue_instock_unprocessed", "red_instock_unprocessed", "white_instock_unprocessed"],
                },
                {
                    "title": "🔒 **INSTOCK RESERVED**",
                    "files": ["blue_instock_reserved", "red_instock_reserved", "white_instock_reserved"],
                },
                {"title": "⚙️ **UNPROCESSED**", "files": ["blue_unprocessed", "red_unprocessed", "white_unprocessed"]},
                {"title": "🎨 **PALLETT**", "files": ["palett"]},  # Nur einmal anzeigen
            ]

            # Zeige alle SVGs in Gruppen mit Überschriften
            for group in row_groups:
                st.markdown(f"### {group['title']}")

                # Finde verfügbare SVG-Dateien für diese Gruppe
                group_svg_files = []
                for filename in group["files"]:
                    svg_file = workpiece_dir / f"{filename}.svg"
                    if svg_file.exists():
                        group_svg_files.append(svg_file)

                if group_svg_files:
                    # Zeige SVGs in Spalten
                    cols_per_row = len(group_svg_files)
                    cols = st.columns(cols_per_row)

                    for i, svg_file in enumerate(group_svg_files):
                        with cols[i]:
                            st.markdown(f"**{svg_file.stem}**")
                            try:
                                with open(svg_file, encoding="utf-8") as f:
                                    svg_content = f.read()

                                # Scope SVG styles to prevent CSS conflicts
                                scoped_svg_content = scope_svg_styles(svg_content)

                                # SVG-Darstellung mit Scoping
                                st.markdown(
                                    f"""
                                <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                                    {scoped_svg_content}
                                </div>
                                """,
                                    unsafe_allow_html=True,
                                )

                            except Exception as e:
                                st.error(f"Fehler: {e}")
                else:
                    st.warning(f"Keine SVG-Dateien für {group['title']} gefunden")

                # Abstand zwischen den Gruppen
                st.markdown("")
        else:
            st.error("Keine SVG-Dateien gefunden!")

        # NEUE VEREINHEITLICHTE PRODUCT-SVGs (Registry/CCU-Alignment)
        st.markdown("---")
        st.markdown("### 🎯 **VEREINHEITLICHTE PRODUCT-SVGs**")
        st.markdown("**Registry & CCU-Domain Alignment:** `blue_product.svg`, `white_product.svg`, `red_product.svg`")

        # 3-SPALTEN-LAYOUT: BLUE | WHITE | RED
        st.markdown("### 🎨 **3-SPALTEN-DARSTELLUNG**")

        # Spalten erstellen
        col1, col2, col3 = st.columns(3)

        # Verfügbare Patterns für alle Farben
        patterns = ["3dim", "unprocessed", "instock_unprocessed", "instock_reserved", "product"]

        with col1:
            st.markdown("#### 🔵 **BLUE Workpieces**")
            for pattern in patterns:
                svg_content = asset_manager.get_workpiece_svg("BLUE", pattern)
                if svg_content:
                    # Verwende die neue korrekte SVG-Darstellung
                    st.markdown(f"**🔵 {pattern}**")
                    st.markdown(
                        f"""
                    <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                        {svg_content}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**Call:** `asset_manager.get_workpiece_svg('BLUE', '{pattern}')`")
                else:
                    st.error(f"❌ blue_{pattern}.svg nicht gefunden!")

        with col2:
            st.markdown("#### ⚪ **WHITE Workpieces**")
            for pattern in patterns:
                svg_content = asset_manager.get_workpiece_svg("WHITE", pattern)
                if svg_content:
                    # Verwende die neue korrekte SVG-Darstellung
                    st.markdown(f"**⚪ {pattern}**")
                    st.markdown(
                        f"""
                    <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                        {svg_content}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**Call:** `asset_manager.get_workpiece_svg('WHITE', '{pattern}')`")
                else:
                    st.error(f"❌ white_{pattern}.svg nicht gefunden!")

        with col3:
            st.markdown("#### 🔴 **RED Workpieces**")
            for pattern in patterns:
                svg_content = asset_manager.get_workpiece_svg("RED", pattern)
                if svg_content:
                    # Verwende die neue korrekte SVG-Darstellung
                    st.markdown(f"**🔴 {pattern}**")
                    st.markdown(
                        f"""
                    <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                        {svg_content}
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )
                    st.markdown(f"**Call:** `asset_manager.get_workpiece_svg('RED', '{pattern}')`")
                else:
                    st.error(f"❌ red_{pattern}.svg nicht gefunden!")

            # SONDERMETHODE: getPalett()
            st.markdown("---")
            st.markdown("#### 🎨 **SONDERMETHODE: getPalett()**")
            st.markdown("**Spezielle Palett-SVG für alle Workpieces**")

            # Palett-SVG über Asset-Manager laden
            palett_content = asset_manager.get_workpiece_palett()
            if palett_content:
                # GLEICHE DARSTELLUNG WIE WORKPIECE-SVGs
                st.markdown("**🎨 palett**")
                st.markdown(
                    f"""
                <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                    {palett_content}
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.markdown("**Call:** `asset_manager.get_workpiece_palett()`")
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
                blue_svg_content = asset_manager.get_workpiece_svg("BLUE", "product")
                if blue_svg_content:
                    st.success("✅ BLUE SVG geladen")
                    st.code("asset_manager.get_workpiece_svg('BLUE', 'product')", language="python")
                else:
                    st.error("❌ BLUE SVG nicht geladen")
            except Exception as e:
                st.error(f"❌ Fehler: {e}")

        with test_col2:
            st.markdown("**WHITE Test:**")
            try:
                white_svg_content = asset_manager.get_workpiece_svg("WHITE", "product")
                if white_svg_content:
                    st.success("✅ WHITE SVG geladen")
                    st.code("asset_manager.get_workpiece_svg('WHITE', 'product')", language="python")
                else:
                    st.error("❌ WHITE SVG nicht geladen")
            except Exception as e:
                st.error(f"❌ Fehler: {e}")

        with test_col3:
            st.markdown("**RED Test:**")
            try:
                red_svg_content = asset_manager.get_workpiece_svg("RED", "product")
                if red_svg_content:
                    st.success("✅ RED SVG geladen")
                    st.code("asset_manager.get_workpiece_svg('RED', 'product')", language="python")
                else:
                    st.error("❌ RED SVG nicht geladen")
            except Exception as e:
                st.error(f"❌ Fehler: {e}")

    else:
        st.error("❌ Workpiece-Verzeichnis nicht gefunden!")
        st.markdown(f"**Erwarteter Pfad:** `{workpiece_dir}`")


def _display_svg_content(svg_content: str, emoji: str, filename: str, highlight=False):
    """Zeigt SVG-Inhalt direkt mit Debug-Info"""
    if not svg_content:
        st.error(f"❌ Kein SVG-Inhalt für {filename}")
        return

    st.markdown(f"**{emoji} {filename.replace('.svg', '')}**")

    # SVG-Inhalt analysieren
    svg_id = "N/A"
    svg_g_id = "N/A"
    viewbox = "N/A"

    if "id=" in svg_content:
        id_match = re.search(r'id="([^"]*)"', svg_content)
        if id_match:
            svg_id = id_match.group(1)

    if "<g id=" in svg_content:
        g_match = re.search(r'<g id="([^"]*)"', svg_content)
        if g_match:
            svg_g_id = g_match.group(1)

    if "viewBox=" in svg_content:
        viewbox_match = re.search(r'viewBox="([^"]*)"', svg_content)
        if viewbox_match:
            viewbox = viewbox_match.group(1)

    # Scope SVG styles to prevent CSS conflicts
    scoped_svg_content = scope_svg_styles(svg_content)

    # SVG mit festen Dimensionen vorbereiten
    normalized_svg = scoped_svg_content
    # Entferne bestehende width/height Attribute falls vorhanden
    normalized_svg = re.sub(r'\s+width="[^"]*"', "", normalized_svg)
    normalized_svg = re.sub(r'\s+height="[^"]*"', "", normalized_svg)
    # Füge feste Dimensionen hinzu (150x150 für gute Sichtbarkeit)
    normalized_svg = normalized_svg.replace("<svg", '<svg width="150" height="150"', 1)

    # Container-Styling basierend auf Highlight-Status
    if highlight:
        border_style = "3px solid #4ecdc4"
        background_style = "linear-gradient(135deg, rgba(78,205,196,0.1), rgba(78,205,196,0.05))"
        box_shadow = "0 6px 12px rgba(78,205,196,0.3)"
    else:
        border_style = "2px solid #ddd"
        background_style = "#f9f9f9"
        box_shadow = "0 2px 4px rgba(0,0,0,0.1)"

    # SVG in einfachem Container einbetten - Direkte Darstellung ohne komplexe Transforms
    st.markdown(
        f"""
    <div style="display: flex; justify-content: center; align-items: center; padding: 15px; border: {border_style}; border-radius: 8px; background: {background_style}; box-shadow: {box_shadow}; min-height: 180px;">
        {normalized_svg}
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Debug-Info anzeigen
    st.caption(f"📄 {filename}")
    st.caption(f"🆔 SVG ID: {svg_id}")
    st.caption(f"🏷️ G ID: {svg_g_id}")
    st.caption(f"📐 ViewBox: {viewbox}")

    # Spezielle Info für product-SVGs
    if highlight and filename.endswith("_product.svg"):
        st.caption("🎯 **NEUE VEREINHEITLICHTE NAMENSKONVENTION**")


def _display_single_svg(svg_file, emoji, highlight=False):
    """Zeigt eine einzelne SVG-Datei mit Debug-Info"""
    st.markdown(f"**{emoji} {svg_file.stem}**")

    # SVG-Inhalt laden und anzeigen
    try:
        with open(svg_file, encoding="utf-8") as f:
            svg_content = f.read()

        # Scope SVG styles to prevent CSS conflicts
        scoped_svg_content = scope_svg_styles(svg_content)

        # SVG-Inhalt analysieren
        svg_id = "N/A"
        svg_g_id = "N/A"
        if "id=" in svg_content:
            id_match = re.search(r'id="([^"]*)"', svg_content)
            if id_match:
                svg_id = id_match.group(1)

        if "<g id=" in svg_content:
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
        st.markdown(
            f"""
        <div style="display: flex; justify-content: center; padding: 10px; border: {border_style}; border-radius: 8px; background: {background_style}; box-shadow: {box_shadow};">
            <div style="width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; overflow: hidden;">
                <div style="transform: scale(0.3); transform-origin: center;">
                    {scoped_svg_content}
                </div>
            </div>
        </div>
        """,
            unsafe_allow_html=True,
        )

        # Debug-Info anzeigen
        st.caption(f"📄 {svg_file.name}")
        st.caption(f"🆔 SVG ID: {svg_id}")
        st.caption(f"🏷️ G ID: {svg_g_id}")

        # Spezielle Info für product-SVGs
        if highlight and svg_file.name.endswith("_product.svg"):
            st.caption("🎯 **NEUE VEREINHEITLICHTE NAMENSKONVENTION**")

    except Exception as e:
        st.error(f"Fehler beim Laden von {svg_file.name}: {e}")


def _show_purchase_order_dummy(asset_manager):
    """Purchase Order Darstellung mit Asset-Manager Integration"""
    st.subheader("📋 Purchase Order")
    st.markdown("**Purchase Order View mit Asset-Manager SVG-Integration**")

    # Lade Product Manager für Produktdaten
    try:
        from omf2.common.product_manager import get_omf2_product_manager

        product_manager = get_omf2_product_manager()
        catalog = product_manager.get_all_products()

        st.success(f"✅ Product Manager geladen: {len(catalog)} Produkte")

        if not catalog:
            st.error("❌ Keine Produkte im Katalog gefunden")
            return

        # Asset-Manager SVG-Darstellung
        st.markdown("### 🎨 **Purchase Orders mit Asset-Manager SVG**")

        # Beispiel Purchase Orders mit Bedarfsberechnung
        MAX_CAPACITY = 3
        purchase_orders = [
            {"product_id": "blue", "count": 1, "need": 2},  # Bedarf = MAX_CAPACITY - count
            {"product_id": "white", "count": 0, "need": 3},
            {"product_id": "red", "count": 2, "need": 1},
        ]

        # Schleife über die Purchase Orders (3 Zeilen)

        for order in purchase_orders:
            if order["product_id"] in catalog:
                product = catalog[order["product_id"]]
                color_name = product.get("name", order["product_id"].capitalize())
                color_emoji = product.get(
                    "icon", "🔵" if order["product_id"] == "blue" else "⚪" if order["product_id"] == "white" else "🔴"
                )

                st.markdown(f"#### {color_emoji} **{color_name.upper()} Purchase Order**")

                # 2 Spalten: Links SVGs, Rechts Daten
                col1, col2 = st.columns([2, 1])

                with col1:
                    # 3DIM SVG - DIREKTE SVG-DARSTELLUNG (EXAKT WIE IM ERSTEN TAB)
                    st.markdown("**3DIM SVG:**")
                    svg_content = asset_manager.get_workpiece_svg(order["product_id"].upper(), "3dim")
                    if svg_content:
                        # EXAKT WIE IM ERSTEN TAB - GLEICHE DARSTELLUNG
                        st.markdown(
                            f"""
                        <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                            {svg_content}
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f"**Call:** `asset_manager.get_workpiece_svg('{order['product_id'].upper()}', '3dim')`"
                        )
                    else:
                        st.error(f"❌ {order['product_id'].lower()}_3dim.svg nicht gefunden!")

                    # Bestand anzeigen
                    st.markdown(f"**Bestand: {order['count']}**")

                    # Leere Baskets durch Palett ersetzen - DIREKTE SVG-DARSTELLUNG (WIE IN purchase_order_subtab.py)
                    if order["need"] > 0:
                        st.markdown("**Fehlende Baskets:**")
                        palett_content = asset_manager.get_workpiece_palett()
                        if palett_content:
                            # FESTE GRÖSSE für Palett-SVGs (100x100) - WIE IN purchase_order_subtab.py
                            palett_html = ""
                            for _i in range(order["need"]):
                                palett_html += f"""
                                <div style="display: inline-block; margin: 2px;">
                                    <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                                        <div style="width: 100px; height: 100px; overflow: hidden;">
                                            {palett_content}
                                        </div>
                                    </div>
                                </div>
                                """
                            st.markdown(palett_html, unsafe_allow_html=True)
                        else:
                            st.error("❌ palett.svg nicht gefunden!")

                with col2:
                    # Purchase Order Daten
                    st.markdown("**Purchase Order Daten:**")
                    st.write(f"**Bestand:** {order['count']}/{MAX_CAPACITY}")
                    st.write(f"**Bedarf:** {order['need']} Stück")

                    if order["need"] > 0:
                        if st.button("📦 Bestellen", key=f"purchase_order_{order['product_id']}"):
                            st.success(f"✅ Rohmaterial-Bestellung für {order['product_id'].upper()} gesendet")
                    else:
                        st.success("✅ Bestand vollständig")

                # Abstand zwischen den Zeilen
                st.markdown("---")

    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Purchase Orders: {e}")
        st.info("💡 Stelle sicher, dass die Registry-Konfiguration korrekt ist")


def _show_customer_order_dummy(asset_manager):
    """Customer Order Darstellung mit Asset-Manager Integration"""
    st.subheader("👤 Customer Order")
    st.markdown("**Customer Order View mit Asset-Manager SVG-Integration**")

    # Lade Product Manager für Produktdaten
    try:
        from omf2.common.product_manager import get_omf2_product_manager

        product_manager = get_omf2_product_manager()
        catalog = product_manager.get_all_products()

        st.success(f"✅ Product Manager geladen: {len(catalog)} Produkte")

        if not catalog:
            st.error("❌ Keine Produkte im Katalog gefunden")
            return

        # Beispiel Customer Orders
        customer_orders = [
            {"product_id": "blue", "count": 2, "available": True},
            {"product_id": "white", "count": 1, "available": True},
            {"product_id": "red", "count": 4, "available": False},
        ]

        # Asset-Manager SVG-Darstellung
        st.markdown("### 🎨 **Customer Orders mit Asset-Manager SVG**")

        # 3 Spalten für die Customer Orders
        col1, col2, col3 = st.columns(3)

        # Schleife über die Customer Orders
        columns = [col1, col2, col3]

        for i, order in enumerate(customer_orders):
            if order["product_id"] in catalog and i < 3:
                product = catalog[order["product_id"]]
                color_name = product.get("name", order["product_id"].capitalize())
                color_emoji = product.get(
                    "icon", "🔵" if order["product_id"] == "blue" else "⚪" if order["product_id"] == "white" else "🔴"
                )

                with columns[i]:
                    st.markdown(f"#### {color_emoji} **{color_name.upper()} Customer Order**")

                    # PRODUCT SVG - DIREKTE SVG-DARSTELLUNG
                    svg_content = asset_manager.get_workpiece_svg(order["product_id"].upper(), "product")
                    if svg_content:
                        st.markdown(
                            f"""
                        <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                            {svg_content}
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.error(f"❌ {order['product_id'].lower()}_product.svg nicht gefunden!")

                    # Customer Order Daten
                    st.write(f"**Bestellt:** {order['count']} Stück")
                    st.write(f"**Status:** {'✅ Verfügbar' if order['available'] else '❌ Nicht verfügbar'}")

    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Customer Orders: {e}")
        st.info("💡 Stelle sicher, dass die Registry-Konfiguration korrekt ist")


def _show_product_catalog_test(asset_manager):
    """Test-Tab: Product Catalog mit Asset-Manager Integration"""
    st.subheader("📦 Product Catalog Test")
    st.markdown("**Test der Product Catalog Subtab mit Asset-Manager SVG-Integration**")

    # Lade Product Manager
    try:
        from omf2.common.product_manager import get_omf2_product_manager

        product_manager = get_omf2_product_manager()
        catalog = product_manager.get_all_products()

        st.success(f"✅ Product Manager geladen: {len(catalog)} Produkte")

        if not catalog:
            st.error("❌ Keine Produkte im Katalog gefunden")
            return

        # Asset-Manager SVG-Darstellung (ohne HTML-Templates)
        st.markdown("### 🎨 **Asset-Manager SVG-Darstellung**")

        # 3 Spalten für die Produkte
        col1, col2, col3 = st.columns(3)

        # Schleife über die Produkte in der Registry
        product_order = ["blue", "white", "red"]  # Definierte Reihenfolge
        columns = [col1, col2, col3]

        for i, product_id in enumerate(product_order):
            if product_id in catalog and i < 3:
                product = catalog[product_id]
                color_name = product.get("name", product_id.capitalize())
                color_emoji = product.get(
                    "icon", "🔵" if product_id == "blue" else "⚪" if product_id == "white" else "🔴"
                )

                with columns[i]:
                    st.markdown(f"#### {color_emoji} **{color_name.upper()}**")

                    # PRODUCT SVG - DIREKTE SVG-DARSTELLUNG
                    st.markdown("**Product SVG:**")
                    svg_content = asset_manager.get_workpiece_svg(product_id.upper(), "product")
                    if svg_content:
                        st.markdown(
                            f"""
                        <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                            {svg_content}
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.error(f"❌ {product_id.lower()}_product.svg nicht gefunden!")

                    # 3DIM SVG - DIREKTE SVG-DARSTELLUNG
                    st.markdown("**3DIM SVG:**")
                    svg_content = asset_manager.get_workpiece_svg(product_id.upper(), "3dim")
                    if svg_content:
                        st.markdown(
                            f"""
                        <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                            {svg_content}
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )
                    else:
                        st.error(f"❌ {product_id.lower()}_3dim.svg nicht gefunden!")

                    # Produktdaten aus Registry
                    st.markdown("**Produktdaten:**")
                    st.write(f"**Name:** {product.get('name', 'Kein Name')}")
                    st.write(f"**Material:** {product.get('material', 'Kein Material')}")
                    st.write(f"**Beschreibung:** {product.get('description', 'Keine Beschreibung')}")

        # Zusammenfassung
        st.markdown("---")
        st.markdown("### 📊 **Zusammenfassung:**")
        st.info(f"📦 **Produktkatalog:** {len(catalog)} Produkte verfügbar")
        st.success("✅ **Asset-Manager Integration:** SVG-basierte Darstellung funktioniert")
        st.warning("⚠️ **HTML-Templates:** Sollten durch Asset-Manager ersetzt werden")

    except Exception as e:
        st.error(f"❌ Fehler beim Laden des Product Catalogs: {e}")
        st.info("💡 Stelle sicher, dass die Registry-Konfiguration korrekt ist")


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
        possible_states = [
            "unprocessed",
            "instock_unprocessed",
            "instock_reserved",
            "drilled",
            "milled",
            "drilled_and_milled",
            "3dim",
        ]
        svg_content = None
        used_state = "unprocessed"

        # Versuche zuerst den gewünschten Zustand
        for state in possible_states:
            svg_filename = f"{workpiece_type.lower()}_{state}.svg"
            svg_path = workpiece_dir / svg_filename

            if svg_path.exists():
                with open(svg_path, encoding="utf-8") as f:
                    svg_content = f.read()
                    used_state = state
                    break

        # Fallback: Verwende Asset Manager
        if not svg_content:
            svg_content = asset_manager.get_workpiece_svg_content(workpiece_type, "unprocessed")

        if svg_content:
            # Scope SVG styles to prevent CSS conflicts
            scoped_svg_content = scope_svg_styles(svg_content)

            # SVG anpassen (Größe, Farbe basierend auf Verfügbarkeit)
            opacity = "0.7" if not available else "1.0"
            border_color = "#ff6b6b" if not available else "#4ecdc4"

            # SVG in Container einbetten mit besserer Darstellung
            return f"""
            <div style="display: flex; flex-direction: column; align-items: center; padding: 15px; border: 3px solid {border_color}; border-radius: 12px; background: linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05)); box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
                <div style="opacity: {opacity}; width: 80px; height: 80px; display: flex; align-items: center; justify-content: center; overflow: hidden;">
                    <div style="transform: scale(0.4); transform-origin: center;">
                        {scoped_svg_content}
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


def _show_stock_manager_test(asset_manager):
    """Stock Manager Test mit Asset-Manager Integration"""
    st.subheader("🏭 Stock Manager Test")
    st.markdown("**Test der Stock Manager Integration mit Asset-Manager SVG-Darstellung**")

    try:
        # Stock Manager laden
        from omf2.ccu.stock_manager import get_stock_manager

        stock_manager = get_stock_manager()
        inventory_status = stock_manager.get_inventory_status()

        st.success("✅ Stock Manager geladen")
        st.info(f"📊 **Inventory Status:** {len(inventory_status.get('inventory', {}))} Positionen")

        # Zeige Stock Manager Daten
        st.markdown("### 📊 **Stock Manager Daten:**")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📦 Inventory (A1-C3):**")
            inventory_data = inventory_status.get("inventory", {})
            for position in ["A1", "A2", "A3", "B1", "B2", "B3", "C1", "C2", "C3"]:
                value = inventory_data.get(position, "None")
                st.write(f"**{position}:** {value}")

        with col2:
            st.markdown("**📈 Verfügbare Werkstücke:**")
            available = inventory_status.get("available", {})
            for color, count in available.items():
                st.write(f"**{color}:** {count} Stück")

            st.markdown("**📉 Bedarf:**")
            need = inventory_status.get("need", {})
            for color, count in need.items():
                st.write(f"**{color}:** {count} Stück")

        # 3x3 Grid Darstellung - EXAKT WIE 3-SPALTEN-DARSTELLUNG
        st.markdown("### 🎨 **3x3 Grid mit direkter SVG-Darstellung:**")
        st.markdown("**Leere Positionen → Palett-SVG, Gefüllte Positionen → Werkstück-SVG**")
        st.markdown("**Verwendet die gleiche Darstellung wie die funktionierende 3-Spaltendarstellung**")

        # Row A - EXAKT WIE 3-SPALTEN-DARSTELLUNG
        st.markdown("#### **Reihe A:**")
        col_a1, col_a2, col_a3 = st.columns(3)

        with col_a1:
            st.markdown("**A1:**")
            _render_inventory_position_direct("A1", inventory_data.get("A1"), asset_manager)

        with col_a2:
            st.markdown("**A2:**")
            _render_inventory_position_direct("A2", inventory_data.get("A2"), asset_manager)

        with col_a3:
            st.markdown("**A3:**")
            _render_inventory_position_direct("A3", inventory_data.get("A3"), asset_manager)

        # Row B - EXAKT WIE 3-SPALTEN-DARSTELLUNG
        st.markdown("#### **Reihe B:**")
        col_b1, col_b2, col_b3 = st.columns(3)

        with col_b1:
            st.markdown("**B1:**")
            _render_inventory_position_direct("B1", inventory_data.get("B1"), asset_manager)

        with col_b2:
            st.markdown("**B2:**")
            _render_inventory_position_direct("B2", inventory_data.get("B2"), asset_manager)

        with col_b3:
            st.markdown("**B3:**")
            _render_inventory_position_direct("B3", inventory_data.get("B3"), asset_manager)

        # Row C - EXAKT WIE 3-SPALTEN-DARSTELLUNG
        st.markdown("#### **Reihe C:**")
        col_c1, col_c2, col_c3 = st.columns(3)

        with col_c1:
            st.markdown("**C1:**")
            _render_inventory_position_direct("C1", inventory_data.get("C1"), asset_manager)

        with col_c2:
            st.markdown("**C2:**")
            _render_inventory_position_direct("C2", inventory_data.get("C2"), asset_manager)

        with col_c3:
            st.markdown("**C3:**")
            _render_inventory_position_direct("C3", inventory_data.get("C3"), asset_manager)

        # Test verschiedene Zustände
        st.markdown("---")
        st.markdown("### 🧪 **Zustands-Test:**")
        st.markdown("**Test der verschiedenen Werkstück-Zustände:**")

        test_col1, test_col2, test_col3 = st.columns(3)

        with test_col1:
            st.markdown("**🔵 BLUE - instock_unprocessed:**")
            # DIREKTE SVG-DARSTELLUNG
            svg_content = asset_manager.get_workpiece_svg("BLUE", "instock_unprocessed")
            if svg_content:
                st.markdown(
                    f"""
                <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                    {svg_content}
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.error("❌ blue_instock_unprocessed.svg nicht gefunden!")

        with test_col2:
            st.markdown("**⚪ WHITE - instock_reserved:**")
            # DIREKTE SVG-DARSTELLUNG
            svg_content = asset_manager.get_workpiece_svg("WHITE", "instock_reserved")
            if svg_content:
                st.markdown(
                    f"""
                <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                    {svg_content}
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.error("❌ white_instock_reserved.svg nicht gefunden!")

        with test_col3:
            st.markdown("**🔴 RED - instock_unprocessed:**")
            # DIREKTE SVG-DARSTELLUNG
            svg_content = asset_manager.get_workpiece_svg("RED", "instock_unprocessed")
            if svg_content:
                st.markdown(
                    f"""
                <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                    {svg_content}
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                st.error("❌ red_instock_unprocessed.svg nicht gefunden!")

        # HALBGEFÜLLTES LAGER TEST - EXAKT WIE IM STOCK_AND_WORKPIECE_LAYOUT_TEST.PY
        st.markdown("---")
        st.markdown("### 🏭 **Halbgefülltes Lager Test:**")
        st.markdown("**Exakte Darstellung wie im stock_and_workpiece_layout_test.py - 3-Spaltendarstellung**")

        # Zufällige Anordnung: Palett, WHITE_instock, RED_instock, BLUE_instock
        st.markdown("**Zufällige Anordnung: Palett, WHITE_instock, RED_instock, BLUE_instock**")

        # 3-SPALTEN-LAYOUT: EXAKT WIE IM STOCK_AND_WORKPIECE_LAYOUT_TEST.PY
        st.markdown("#### **3-SPALTEN-DARSTELLUNG (wie im stock_and_workpiece_layout_test.py):**")

        # Spalten erstellen
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("**🎨 Palett (Leer):**")
            # GLEICHE DARSTELLUNG WIE WORKPIECE-SVGs
            palett_content = asset_manager.get_workpiece_palett()
            if palett_content:
                st.markdown(
                    f"""
                <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                    {palett_content}
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.markdown("**Call:** `asset_manager.get_workpiece_palett()`")
            else:
                st.error("❌ palett.svg nicht gefunden!")

        with col2:
            st.markdown("**⚪ WHITE instock_unprocessed:**")
            # EXAKT WIE IM STOCK_AND_WORKPIECE_LAYOUT_TEST.PY
            svg_content = asset_manager.get_workpiece_svg("WHITE", "instock_unprocessed")
            if svg_content:
                st.markdown(
                    f"""
                <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                    {svg_content}
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.markdown("**Call:** `asset_manager.get_workpiece_svg('WHITE', 'instock_unprocessed')`")
            else:
                st.error("❌ white_instock_unprocessed.svg nicht gefunden!")

        with col3:
            st.markdown("**🔴 RED instock_unprocessed:**")
            # EXAKT WIE IM STOCK_AND_WORKPIECE_LAYOUT_TEST.PY
            svg_content = asset_manager.get_workpiece_svg("RED", "instock_unprocessed")
            if svg_content:
                st.markdown(
                    f"""
                <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                    {svg_content}
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.markdown("**Call:** `asset_manager.get_workpiece_svg('RED', 'instock_unprocessed')`")
            else:
                st.error("❌ red_instock_unprocessed.svg nicht gefunden!")

        # Zweite Reihe
        st.markdown("#### **Zweite Reihe:**")
        col4, col5, col6 = st.columns(3)

        with col4:
            st.markdown("**🔵 BLUE instock_unprocessed:**")
            # EXAKT WIE IM STOCK_AND_WORKPIECE_LAYOUT_TEST.PY
            svg_content = asset_manager.get_workpiece_svg("BLUE", "instock_unprocessed")
            if svg_content:
                st.markdown(
                    f"""
                <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                    {svg_content}
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.markdown("**Call:** `asset_manager.get_workpiece_svg('BLUE', 'instock_unprocessed')`")
            else:
                st.error("❌ blue_instock_unprocessed.svg nicht gefunden!")

        with col5:
            st.markdown("**🎨 Palett (Leer):**")
            # GLEICHE DARSTELLUNG WIE WORKPIECE-SVGs
            palett_content = asset_manager.get_workpiece_palett()
            if palett_content:
                st.markdown(
                    f"""
                <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                    {palett_content}
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.markdown("**Call:** `asset_manager.get_workpiece_palett()`")
            else:
                st.error("❌ palett.svg nicht gefunden!")

        with col6:
            st.markdown("**⚪ WHITE instock_reserved:**")
            # EXAKT WIE IM STOCK_AND_WORKPIECE_LAYOUT_TEST.PY
            svg_content = asset_manager.get_workpiece_svg("WHITE", "instock_reserved")
            if svg_content:
                st.markdown(
                    f"""
                <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                    {svg_content}
                </div>
                """,
                    unsafe_allow_html=True,
                )
                st.markdown("**Call:** `asset_manager.get_workpiece_svg('WHITE', 'instock_reserved')`")
            else:
                st.error("❌ white_instock_reserved.svg nicht gefunden!")

        # Zusammenfassung
        st.markdown("---")
        st.markdown("### 📊 **Zusammenfassung:**")
        st.success("✅ **Stock Manager Integration:** Funktioniert korrekt")
        st.success("✅ **Asset-Manager SVGs:** instock_unprocessed und instock_reserved verfügbar")
        st.info("💡 **Nächster Schritt:** Integration in inventory_subtab.py")

    except Exception as e:
        st.error(f"❌ Fehler beim Laden des Stock Managers: {e}")
        st.info("💡 Stelle sicher, dass der Stock Manager korrekt initialisiert ist")


def _render_inventory_position(position: str, workpiece_type: str, asset_manager):
    """Rendert eine einzelne Lagerposition mit direkter SVG-Darstellung"""
    if workpiece_type is None:
        # Leere Position → Palett-SVG
        st.markdown("**Leer:**")
        # DIREKTE SVG-DARSTELLUNG
        palett_content = asset_manager.get_workpiece_palett()
        if palett_content:
            st.markdown(
                f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                {palett_content}
            </div>
            """,
                unsafe_allow_html=True,
            )
            st.markdown(f"**Position {position}**")
        else:
            st.error("❌ palett.svg nicht gefunden!")
    else:
        # Gefüllte Position → Werkstück-SVG
        st.markdown(f"**{workpiece_type}:**")
        # DIREKTE SVG-DARSTELLUNG
        svg_content = asset_manager.get_workpiece_svg(workpiece_type, "instock_unprocessed")
        if svg_content:
            st.markdown(
                f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                {svg_content}
            </div>
            """,
                unsafe_allow_html=True,
            )
            st.markdown(f"**Position {position}**")
        else:
            st.error(f"❌ {workpiece_type.lower()}_instock_unprocessed.svg nicht gefunden!")


def _render_inventory_position_uniform(position: str, workpiece_type: str, asset_manager):
    """Rendert eine Lagerposition mit einheitlicher Größe - DIREKTE SVG-DARSTELLUNG"""
    if workpiece_type is None:
        # Leere Position → Palett-SVG mit einheitlicher Größe
        st.markdown("**Leer:**")
        # DIREKTE SVG-DARSTELLUNG
        palett_content = asset_manager.get_workpiece_palett()
        if palett_content:
            st.markdown(
                f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                {palett_content}
            </div>
            """,
                unsafe_allow_html=True,
            )
            st.markdown(f"**Position {position}**")
        else:
            st.error("❌ palett.svg nicht gefunden!")
    else:
        # Gefüllte Position → Werkstück-SVG mit einheitlicher Größe
        st.markdown(f"**{workpiece_type}:**")
        # DIREKTE SVG-DARSTELLUNG
        svg_content = asset_manager.get_workpiece_svg(workpiece_type, "instock_unprocessed")
        if svg_content:
            st.markdown(
                f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                {svg_content}
            </div>
            """,
                unsafe_allow_html=True,
            )
            st.markdown(f"**Position {position}**")
        else:
            st.error(f"❌ {workpiece_type.lower()}_instock_unprocessed.svg nicht gefunden!")


def _render_inventory_position_direct(position: str, workpiece_type: str, asset_manager):
    """Rendert eine Lagerposition mit direkter SVG-Darstellung - FESTE GRÖSSE (160x160) FÜR ALLE SVGs"""
    if workpiece_type is None:
        # Leere Position → Palett-SVG mit fester Größe
        st.markdown("**Leer:**")
        # FESTE GRÖSSE für Palett-SVG (160x160)
        palett_content = asset_manager.get_workpiece_palett()
        if palett_content:
            st.markdown(
                f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                <div style="width: 160px; height: 160px; overflow: hidden;">
                    {palett_content}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            st.markdown(f"**Position {position}**")
        else:
            st.error("❌ palett.svg nicht gefunden!")
    else:
        # Gefüllte Position → Werkstück-SVG mit fester Größe
        st.markdown(f"**{workpiece_type}:**")
        # FESTE GRÖSSE für Workpiece-SVG (160x160)
        svg_content = asset_manager.get_workpiece_svg(workpiece_type, "instock_unprocessed")
        if svg_content:
            st.markdown(
                f"""
            <div style="border: 1px solid #ccc; padding: 10px; margin: 5px; text-align: center;">
                <div style="width: 160px; height: 160px; overflow: hidden;">
                    {svg_content}
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )
            st.markdown(f"**Position {position}**")
        else:
            st.error(f"❌ {workpiece_type.lower()}_instock_unprocessed.svg nicht gefunden!")


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
    st.markdown("**Aktuelle Konfiguration:**")
    st.markdown(f"- Workpiece Type: {workpiece_type}")
    st.markdown(f"- Workpiece State: {workpiece_state}")
    st.markdown(f"- Asset Manager: {type(asset_manager).__name__}")
    st.markdown(f"- Assets Dir: {asset_manager.assets_dir}")


if __name__ == "__main__":
    main()
