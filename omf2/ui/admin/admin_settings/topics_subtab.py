#!/usr/bin/env python3
"""
Topics Subtab - Topics Verwaltung für Admin Settings
Zeigt alle Topics aus der Registry nach Kategorien an
"""

import streamlit as st
from omf2.common.logger import get_logger
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_topics_subtab():
    """Render Topics Subtab mit Registry-Daten"""
    try:
        st.subheader("📡 Topics Konfiguration")
        st.markdown("Registry-basierte Topics-Verwaltung aus omf2/registry")

        # Load registry manager
        from omf2.registry.manager.registry_manager import get_registry_manager
        registry_manager = get_registry_manager()
        
        # Get all topics
        all_topics = registry_manager.get_topics()
        
        if not all_topics:
            st.warning("⚠️ Keine Topics in der Registry gefunden")
            return
        
        # Gruppiere Topics nach Kategorien
        topics_by_category = _group_topics_by_category(all_topics)
        
        # Zeige Topics nach Kategorien
        for category, topics in topics_by_category.items():
            with st.expander(f"📂 {category} ({len(topics)} topics)", expanded=False):
                # Erstelle DataFrame für diese Kategorie
                topic_data = []
                for topic_name, topic_info in topics.items():
                    topic_data.append({
                        "Topic": topic_name,
                        "QoS": topic_info.get('qos', 1),
                        "Retain": topic_info.get('retain', 0),
                        "Category": topic_info.get('category', 'unknown'),
                        "File": topic_info.get('file', 'unknown')
                    })
                
                if topic_data:
                    st.dataframe(
                        topic_data,
                        column_config={
                            "Topic": st.column_config.TextColumn("Topic", width="large"),
                            "QoS": st.column_config.NumberColumn("QoS", width="small"),
                            "Retain": st.column_config.NumberColumn("Retain", width="small"),
                            "Category": st.column_config.TextColumn("Category", width="medium"),
                            "File": st.column_config.TextColumn("File", width="medium"),
                        },
                        hide_index=True,
                    )
        
        # Registry Information
        with st.expander("📊 Registry Information", expanded=False):
            stats = registry_manager.get_registry_stats()
            st.write(f"**Load Timestamp:** {stats['load_timestamp']}")
            st.write(f"**Total Topics:** {len(all_topics)}")
            st.write(f"**Categories:** {len(topics_by_category)}")
            
            # Zeige Kategorien-Übersicht
            st.write("**Categories Overview:**")
            for category, topics in topics_by_category.items():
                st.write(f"- {category}: {len(topics)} topics")
        
    except Exception as e:
        logger.error(f"❌ Topics Subtab rendering error: {e}")
        st.error(f"❌ Topics Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def _group_topics_by_category(all_topics):
    """Gruppiert Topics nach Kategorien"""
    topics_by_category = {}
    
    for topic_name, topic_info in all_topics.items():
        category = topic_info.get('category', 'unknown')
        
        if category not in topics_by_category:
            topics_by_category[category] = {}
        
        topics_by_category[category][topic_name] = topic_info
    
    return topics_by_category


def show_topics_subtab():
    """Wrapper für Topics Subtab"""
    render_topics_subtab()