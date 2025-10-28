#!/usr/bin/env python3
"""
Schemas Subtab - Schema Verwaltung für Admin Settings
Zeigt alle Schemas aus der Registry nach Kategorien an - NEUE ARCHITEKTUR: topic-schema-payload
"""

import streamlit as st

from omf2.assets.heading_icons import get_svg_inline
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_schemas_subtab():
    """Render Schemas Subtab mit Registry-Daten - NEUE ARCHITEKTUR"""
    try:
        # Initialize i18n
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            logger.error("❌ I18n Manager not found in session state")
            return

        # SVG-Header mit Fallback - einfache Lösung mit größerer SVG
        schemas_svg = get_svg_inline("SCHEMAS", size_px=32)
        header_icon = schemas_svg if schemas_svg else UISymbols.get_functional_icon("schema_driven")
        st.markdown(
            f'<h3 style="margin-top: 0; margin-bottom: 1rem;">{header_icon} <strong>{i18n.t("admin.schemas")} Konfiguration</strong></h3>',
            unsafe_allow_html=True,
        )
        st.markdown("Registry-basierte Schema-Verwaltung aus omf2/registry - NEUE ARCHITEKTUR: topic-schema-payload")

        # Load registry manager from session state (initialized in omf.py)
        if "registry_manager" not in st.session_state:
            from omf2.registry.manager.registry_manager import get_registry_manager

            st.session_state["registry_manager"] = get_registry_manager("omf2/registry/")
        registry_manager = st.session_state["registry_manager"]

        # Get all schemas - NEUE ARCHITEKTUR
        all_schemas = registry_manager.get_schemas()

        if not all_schemas:
            st.warning(f"{UISymbols.get_status_icon('warning')} Keine Schemas in der Registry gefunden")
            st.info("💡 Schemas werden aus dem omf2/registry/schemas/ Verzeichnis geladen.")
            return

        # Gruppiere Schemas nach Kategorien
        schemas_by_category = _group_schemas_by_category(all_schemas)

        # Zeige Schemas nach Kategorien
        for category, schemas in schemas_by_category.items():
            with st.expander(f"📂 {category} ({len(schemas)} schemas)", expanded=False):
                # Erstelle DataFrame für diese Kategorie
                schema_data = []
                for schema_name, schema_info in schemas.items():
                    schema_data.append(
                        {
                            "Name": schema_name,
                            "Schema Category": schema_info.get("schema_category", "unknown"),
                            "Schema Sub Category": schema_info.get("schema_sub_category", "unknown"),
                            "Version": schema_info.get("version", "unknown"),
                            "Description": schema_info.get("description", "No description"),
                        }
                    )

                if schema_data:
                    st.dataframe(
                        schema_data,
                        use_container_width=True,
                        column_config={
                            "Name": st.column_config.TextColumn("Schema Name", width="medium"),
                            "Schema Category": st.column_config.TextColumn("Schema Category", width="small"),
                            "Schema Sub Category": st.column_config.TextColumn("Schema Sub Category", width="small"),
                            "Version": st.column_config.TextColumn("Version", width="small"),
                            "Description": st.column_config.TextColumn("Description", width="large"),
                        },
                        hide_index=True,
                    )

        # Registry Information
        with st.expander(f"{UISymbols.get_functional_icon('dashboard')} Registry Information", expanded=False):
            stats = registry_manager.get_registry_stats()
            st.write(f"**Load Timestamp:** {stats['load_timestamp']}")
            st.write(f"**Total Schemas:** {len(all_schemas)}")
            st.write(f"**Categories:** {len(schemas_by_category)}")

            # Zeige Kategorien-Übersicht
            st.write("**Categories Overview:**")
            for category, schemas in schemas_by_category.items():
                st.write(f"- {category}: {len(schemas)} schemas")

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Schemas Subtab rendering error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Schemas Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def _group_schemas_by_category(all_schemas):
    """Gruppiert Schemas nach Kategorien"""
    schemas_by_category = {}

    for schema_name, schema_info in all_schemas.items():
        category = schema_info.get("schema_category", "unknown")

        if category not in schemas_by_category:
            schemas_by_category[category] = {}

        schemas_by_category[category][schema_name] = schema_info

    return schemas_by_category


def show_schemas_subtab():
    """Wrapper für Schemas Subtab"""
    render_schemas_subtab()
