#!/usr/bin/env python3
"""
Templates Subtab - Templates Verwaltung für Admin Settings
Zeigt alle Templates aus der Registry nach Kategorien an
"""

import streamlit as st
from omf2.common.logger import get_logger
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_templates_subtab():
    """Render Templates Subtab mit Registry-Daten"""
    try:
        st.subheader("📝 Templates Konfiguration")
        st.markdown("Registry-basierte Templates-Verwaltung aus omf2/registry")

        # Load registry manager from session state (initialized in omf.py)
        if 'registry_manager' not in st.session_state:
            from omf2.registry.manager.registry_manager import get_registry_manager
            st.session_state['registry_manager'] = get_registry_manager("omf2/registry/")
        registry_manager = st.session_state['registry_manager']
        
        # Get all templates
        all_templates = registry_manager.get_templates()
        
        if not all_templates:
            st.warning("⚠️ Keine Templates in der Registry gefunden")
            return
        
        # Gruppiere Templates nach Kategorien
        templates_by_category = _group_templates_by_category(all_templates)
        
        # Zeige Templates nach Kategorien
        for category, templates in templates_by_category.items():
            with st.expander(f"📂 {category} ({len(templates)} templates)", expanded=False):
                # Erstelle DataFrame für diese Kategorie
                template_data = []
                for template_name, template_info in templates.items():
                    template_data.append({
                        "Name": template_name,
                        "Template Category": template_info.get('template_category', 'unknown'),
                        "Template Sub Category": template_info.get('template_sub_category', 'unknown'),
                        "Version": template_info.get('version', 'unknown'),
                        "Description": template_info.get('description', 'No description')
                    })
                
                if template_data:
                    st.dataframe(
                        template_data,
                        column_config={
                            "Name": st.column_config.TextColumn("Template Name", width="medium"),
                            "Template Category": st.column_config.TextColumn("Template Category", width="small"),
                            "Template Sub Category": st.column_config.TextColumn("Template Sub Category", width="small"),
                            "Version": st.column_config.TextColumn("Version", width="small"),
                            "Description": st.column_config.TextColumn("Description", width="large"),
                        },
                        hide_index=True,
                    )
        
        # Registry Information
        with st.expander("📊 Registry Information", expanded=False):
            stats = registry_manager.get_registry_stats()
            st.write(f"**Load Timestamp:** {stats['load_timestamp']}")
            st.write(f"**Total Templates:** {len(all_templates)}")
            st.write(f"**Categories:** {len(templates_by_category)}")
            
            # Zeige Kategorien-Übersicht
            st.write("**Categories Overview:**")
            for category, templates in templates_by_category.items():
                st.write(f"- {category}: {len(templates)} templates")
        
    except Exception as e:
        logger.error(f"❌ Templates Subtab rendering error: {e}")
        st.error(f"❌ Templates Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def _group_templates_by_category(all_templates):
    """Gruppiert Templates nach Kategorien"""
    templates_by_category = {}
    
    for template_name, template_info in all_templates.items():
        category = template_info.get('template_category', 'unknown')
        
        if category not in templates_by_category:
            templates_by_category[category] = {}
        
        templates_by_category[category][template_name] = template_info
    
    return templates_by_category


def show_templates_subtab():
    """Wrapper für Templates Subtab"""
    render_templates_subtab()