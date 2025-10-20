#!/usr/bin/env python3
"""
Topics Subtab - Topics Verwaltung für Admin Settings
Zeigt alle Topics aus der Registry nach Kategorien an
"""

import streamlit as st

from omf2.common.logger import get_logger
from omf2.common.message_manager import MessageManager
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_topics_subtab():
    """Render Topics Subtab mit Registry-Daten"""
    try:
        st.subheader(f"{UISymbols.get_functional_icon('topic_driven')} Topics Konfiguration")
        st.markdown("Registry-basierte Topics-Verwaltung aus omf2/registry")

        # Load registry manager from session state (initialized in omf.py)
        if "registry_manager" not in st.session_state:
            from omf2.registry.manager.registry_manager import get_registry_manager

            st.session_state["registry_manager"] = get_registry_manager("omf2/registry/")
        registry_manager = st.session_state["registry_manager"]

        # MessageManager will be initialized when needed in button callbacks

        # Get all topics
        all_topics = registry_manager.get_topics()

        if not all_topics:
            st.warning(f"{UISymbols.get_status_icon('warning')} Keine Topics in der Registry gefunden")
            return

        # Gruppiere Topics nach Kategorien
        topics_by_category = _group_topics_by_category(all_topics)

        # Zeige Topics nach Kategorien
        for category, topics in topics_by_category.items():
            with st.expander(f"📂 {category} ({len(topics)} topics)", expanded=False):
                # Erstelle DataFrame für diese Kategorie
                topic_data = []
                for topic_name, topic_info in topics.items():
                    topic_data.append(
                        {
                            "Topic": topic_name,
                            "QoS": topic_info.get("qos", 1),
                            "Retain": topic_info.get("retain", 0),
                            "Schema": topic_info.get("schema", "No schema"),
                            "Description": topic_info.get("description", "No description"),
                            "Category": topic_info.get("category", "unknown"),
                            "File": topic_info.get("file", "unknown"),
                        }
                    )

                if topic_data:
                    st.dataframe(
                        topic_data,
                        column_config={
                            "Topic": st.column_config.TextColumn("Topic", width="large"),
                            "QoS": st.column_config.NumberColumn("QoS", width="small"),
                            "Retain": st.column_config.NumberColumn("Retain", width="small"),
                            "Schema": st.column_config.TextColumn("Schema", width="medium"),
                            "Description": st.column_config.TextColumn("Description", width="large"),
                            "Category": st.column_config.TextColumn("Category", width="medium"),
                            "File": st.column_config.TextColumn("File", width="medium"),
                        },
                        hide_index=True,
                    )

        # Schema Validation Test
        with st.expander("🧪 Schema Validation Test", expanded=False):
            _render_schema_validation_test(registry_manager, all_topics)

        # Registry Information
        with st.expander(f"{UISymbols.get_functional_icon('dashboard')} Registry Information", expanded=False):
            stats = registry_manager.get_registry_stats()
            st.write(f"**Load Timestamp:** {stats['load_timestamp']}")
            st.write(f"**Total Topics:** {len(all_topics)}")
            st.write(f"**Categories:** {len(topics_by_category)}")

            # Schema Statistics
            topics_with_schema = sum(1 for info in all_topics.values() if info.get("schema"))
            st.write(f"**Topics with Schema:** {topics_with_schema}")
            st.write(f"**Topics without Schema:** {len(all_topics) - topics_with_schema}")

            # Zeige Kategorien-Übersicht
            st.write("**Categories Overview:**")
            for category, topics in topics_by_category.items():
                st.write(f"- {category}: {len(topics)} topics")

    except Exception as e:
        logger.error(f"{UISymbols.get_status_icon('error')} Topics Subtab rendering error: {e}")
        st.error(f"{UISymbols.get_status_icon('error')} Topics Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def _group_topics_by_category(all_topics):
    """Gruppiert Topics nach Kategorien"""
    topics_by_category = {}

    for topic_name, topic_info in all_topics.items():
        category = topic_info.get("category", "unknown")

        if category not in topics_by_category:
            topics_by_category[category] = {}

        topics_by_category[category][topic_name] = topic_info

    return topics_by_category


def _render_schema_validation_test(registry_manager, all_topics):
    """Rendert Schema-Validierungstest"""
    st.write("**Test Payload Validation:**")

    # Topic Selection
    topics_with_schema = [topic for topic, info in all_topics.items() if info.get("schema")]

    if not topics_with_schema:
        st.warning("Keine Topics mit Schema gefunden")
        return

    selected_topic = st.selectbox("Select Topic:", topics_with_schema, key="admin_settings_topics_validation_topic")

    if selected_topic:
        topic_info = all_topics[selected_topic]
        st.write(f"**Schema:** {topic_info.get('schema')}")
        st.write(f"**Description:** {topic_info.get('description', 'No description')}")

        # Test Payload Input
        st.write("**Test Payload (JSON):**")
        default_payload = {"example": "payload", "timestamp": "2025-01-01T12:00:00Z"}

        import json

        payload_text = st.text_area(
            "JSON Payload:",
            value=json.dumps(default_payload, indent=2),
            height=200,
            key="admin_settings_topics_validation_payload",
        )

        if st.button(
            f"{UISymbols.get_functional_icon('search')} Validate Payload",
            key="admin_settings_topics_validation_validate",
        ):
            try:
                payload = json.loads(payload_text)
                # Re-initialize MessageManager for button callback scope
                msg_mgr = MessageManager("admin", registry_manager)
                validation_result = msg_mgr.validate_message(selected_topic, payload)

                if not validation_result.get("errors"):
                    st.success(f"{UISymbols.get_status_icon('success')} Payload is valid!")
                else:
                    st.error(
                        f"{UISymbols.get_status_icon('error')} Payload validation failed: {validation_result.get('errors')}"
                    )

            except json.JSONDecodeError as e:
                st.error(f"{UISymbols.get_status_icon('error')} Invalid JSON: {e}")
            except Exception as e:
                st.error(f"{UISymbols.get_status_icon('error')} Validation error: {e}")


def show_topics_subtab():
    """Wrapper für Topics Subtab"""
    render_topics_subtab()
