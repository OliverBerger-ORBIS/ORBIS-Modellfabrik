"""
OMF Dashboard Shopfloor Routes - FTS-Routenplanung
Anzeige und Verwaltung der FTS-Routen zwischen Modulen
"""

from typing import Any, Dict

import pandas as pd
import streamlit as st

from .shopfloor_utils import find_route_between_modules, get_fts_routes, get_product_routes

def show_shopfloor_routes():
    """Zeigt die FTS-Routenplanung"""
    st.subheader("🛣️ FTS-Routenplanung")

    try:
        # FTS-Routen laden
        fts_routes = get_fts_routes()
        product_routes = get_product_routes()

        if not fts_routes and not product_routes:
            st.warning("⚠️ Keine Routen-Konfiguration gefunden")
            return

        # Tabs für verschiedene Routen-Typen
        routes_tab1, routes_tab2 = st.tabs(["🚛 FTS-Routen", "📦 Produkt-Routen"])

        # Tab 1: FTS-Routen
        with routes_tab1:
            if fts_routes:
                st.markdown("### FTS-Transportrouten")

                # Routen als DataFrame anzeigen
                routes_data = []
                for route_name, route_info in fts_routes.items():
                    routes_data.append(
                        {
                            "Route": route_name,
                            "Start": route_info.get("start", "N/A"),
                            "Ziel": route_info.get("end", "N/A"),
                            "Typ": route_info.get("type", "transport"),
                            "Status": route_info.get("status", "aktiv"),
                        }
                    )

                if routes_data:
                    df_routes = pd.DataFrame(routes_data)
                    st.dataframe(df_routes, use_container_width=True)

                    # Route-Details
                    selected_route = st.selectbox(
                        "Route-Details anzeigen:", options=list(fts_routes.keys()), key="fts_route_details"
                    )

                    if selected_route:
                        route_info = fts_routes[selected_route]
                        st.json(route_info)
                else:
                    st.info("Keine FTS-Routen konfiguriert")
            else:
                st.info("Keine FTS-Routen verfügbar")

        # Tab 2: Produkt-Routen
        with routes_tab2:
            if product_routes:
                st.markdown("### Produkt-Workflow-Routen")

                # Produkt-Routen als DataFrame anzeigen
                product_data = []
                for product_name, product_info in product_routes.items():
                    product_data.append(
                        {
                            "Produkt": product_name,
                            "Workflow": product_info.get("workflow", "N/A"),
                            "Module": ", ".join(product_info.get("modules", [])),
                            "Status": product_info.get("status", "aktiv"),
                        }
                    )

                if product_data:
                    df_products = pd.DataFrame(product_data)
                    st.dataframe(df_products, use_container_width=True)

                    # Produkt-Details
                    selected_product = st.selectbox(
                        "Produkt-Details anzeigen:", options=list(product_routes.keys()), key="product_route_details"
                    )

                    if selected_product:
                        product_info = product_routes[selected_product]
                        st.json(product_info)
                else:
                    st.info("Keine Produkt-Routen konfiguriert")
            else:
                st.info("Keine Produkt-Routen verfügbar")

        # Route-Suche
        st.markdown("---")
        st.markdown("### 🔍 Route-Suche")

        col1, col2 = st.columns(2)
        with col1:
            start_module = st.selectbox(
                "Start-Modul:", options=["MILL", "DRILL", "AIQS", "HBW", "DPS", "FTS", "CHRG"], key="route_search_start"
            )
        with col2:
            end_module = st.selectbox(
                "Ziel-Modul:", options=["MILL", "DRILL", "AIQS", "HBW", "DPS", "FTS", "CHRG"], key="route_search_end"
            )

        if st.button("Route suchen", key="search_route"):
            if start_module == end_module:
                st.warning("⚠️ Start- und Ziel-Modul sind identisch")
            else:
                route = find_route_between_modules(start_module, end_module)
                if route:
                    st.success(f"✅ Route gefunden: {start_module} → {end_module}")
                    st.json(route)
                else:
                    st.error(f"❌ Keine direkte Route von {start_module} zu {end_module} gefunden")

    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Routen: {e}")

def get_route_statistics() -> Dict[str, Any]:
    """Gibt Routen-Statistiken zurück"""
    try:
        fts_routes = get_fts_routes()
        product_routes = get_product_routes()

        return {
            "fts_routes": {
                "total": len(fts_routes),
                "active": len([r for r in fts_routes.values() if r.get("status") == "aktiv"]),
                "inactive": len([r for r in fts_routes.values() if r.get("status") == "inaktiv"]),
            },
            "product_routes": {
                "total": len(product_routes),
                "active": len([r for r in product_routes.values() if r.get("status") == "aktiv"]),
                "inactive": len([r for r in product_routes.values() if r.get("status") == "inaktiv"]),
            },
        }
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Routen-Statistiken: {e}")
        return {
            "fts_routes": {"total": 0, "active": 0, "inactive": 0},
            "product_routes": {"total": 0, "active": 0, "inactive": 0},
        }
