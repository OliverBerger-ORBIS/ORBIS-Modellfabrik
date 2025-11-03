#!/usr/bin/env python3
"""
MQTT Clients Subtab - MQTT Clients Verwaltung für Admin Settings
Zeigt alle MQTT Clients aus der Registry an
"""

import streamlit as st

from omf2.assets.asset_manager import get_asset_manager
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def _group_topics_by_category(topics, registry_manager):
    """Gruppiert Topics nach Kategorien basierend auf Registry-Daten"""
    topic_categories = {}
    all_topics = registry_manager.get_topics()

    for topic in topics:
        # Hole Topic-Daten aus Registry
        topic_data = all_topics.get(topic, {})
        category = topic_data.get("category", "unknown")
        category_name = f"{category.upper()} Topics"

        if category_name not in topic_categories:
            topic_categories[category_name] = []
        topic_categories[category_name].append(topic)

    return topic_categories


def render_mqtt_clients_subtab():
    """Render MQTT Clients Subtab mit Registry-Daten"""
    try:
        # Initialize i18n
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            logger.error("❌ I18n Manager not found in session state")
            return

        # SVG-Header mit Fallback - einfache Lösung mit größerer SVG
        mqtt_svg = get_asset_manager().get_asset_inline("MQTT_CLIENTS", size_px=32)
        header_icon = mqtt_svg if mqtt_svg else UISymbols.get_functional_icon("mqtt_connect")
        st.markdown(
            f'<h3 style="margin-top: 0; margin-bottom: 1rem;">{header_icon} <strong>{i18n.t("admin.mqtt_clients")} Verwaltung</strong></h3>',
            unsafe_allow_html=True,
        )
        st.markdown("Verwaltung aller MQTT Clients aus der Registry")

        # Get registry manager from session state
        registry_manager = st.session_state.get("registry_manager")
        if not registry_manager:
            st.error("❌ Registry Manager nicht verfügbar")
            return

        # Get MQTT clients data
        mqtt_clients = registry_manager.get_mqtt_clients()
        if not mqtt_clients:
            st.warning("⚠️ Keine MQTT Clients gefunden")
            return

        # Display MQTT clients statistics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📡 Total Clients", len(mqtt_clients))
        with col2:
            pub_clients = sum(1 for c in mqtt_clients.values() if len(c.get("published_topics", [])) > 0)
            st.metric("📤 Publisher", pub_clients)
        with col3:
            sub_clients = sum(1 for c in mqtt_clients.values() if len(c.get("subscribed_topics", [])) > 0)
            st.metric("📥 Subscriber", sub_clients)
        with col4:
            total_topics = sum(
                len(c.get("published_topics", [])) + len(c.get("subscribed_topics", [])) for c in mqtt_clients.values()
            )
            st.metric("🔗 Total Topics", total_topics)

        # Display MQTT clients by type
        client_types = {}
        for client_name, client_data in mqtt_clients.items():
            # Determine client type based on name
            if "admin" in client_name:
                client_type = "Admin"
            elif "ccu" in client_name:
                client_type = "CCU"
            elif "nodered" in client_name:
                client_type = "Node-RED"
            elif "txt" in client_name:
                client_type = "TXT Controller"
            else:
                client_type = "Other"

            if client_type not in client_types:
                client_types[client_type] = []
            client_types[client_type].append((client_name, client_data))

        # Render MQTT clients by type
        for client_type, client_list in client_types.items():
            with st.expander(f"📂 {client_type} ({len(client_list)})", expanded=False):
                # Create DataFrame for MQTT clients

                clients_data = []
                for client_name, client_data in client_list:
                    clients_data.append(
                        {
                            "Client": client_name,
                            "Client ID": client_data.get("client_id", "N/A"),
                            "Published": len(client_data.get("published_topics", [])),
                            "Subscribed": len(client_data.get("subscribed_topics", [])),
                            "QoS": client_data.get("qos", 1),
                            "Retain": "✅" if client_data.get("retain") == 1 else "❌",
                        }
                    )

                if clients_data:
                    st.dataframe(
                        clients_data,
                        column_config={
                            "Client": st.column_config.TextColumn("Client", width="large"),
                            "Client ID": st.column_config.TextColumn("Client ID", width="medium"),
                            "Published": st.column_config.NumberColumn("Published", width="small"),
                            "Subscribed": st.column_config.NumberColumn("Subscribed", width="small"),
                            "QoS": st.column_config.NumberColumn("QoS", width="small"),
                            "Retain": st.column_config.TextColumn("Retain", width="small"),
                        },
                        hide_index=True,
                    )

        # Detailed view for selected client
        st.markdown("### 🔍 Client Details")
        selected_client = st.selectbox(
            "Wählen Sie einen MQTT Client für Details:", options=list(mqtt_clients.keys()), key="mqtt_client_selector"
        )

        if selected_client:
            client_data = mqtt_clients[selected_client]

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("**📥 Subscribed Topics:**")
                subscribed_topics = client_data.get("subscribed_topics", [])
                if subscribed_topics:
                    # Gruppiere Topics nach Kategorien
                    topic_categories = _group_topics_by_category(subscribed_topics, registry_manager)
                    for category, topics in topic_categories.items():
                        with st.expander(f"📥 {category} ({len(topics)} topics)", expanded=False):
                            for topic in topics:
                                st.text(f"• {topic}")
                else:
                    st.text("Keine Subscribed Topics")

            with col2:
                st.markdown("**📤 Published Topics:**")
                published_topics = client_data.get("published_topics", [])
                if published_topics:
                    # Gruppiere Topics nach Kategorien
                    topic_categories = _group_topics_by_category(published_topics, registry_manager)
                    for category, topics in topic_categories.items():
                        with st.expander(f"📤 {category} ({len(topics)} topics)", expanded=False):
                            for topic in topics:
                                st.text(f"• {topic}")
                else:
                    st.text("Keine Published Topics")

        # Registry Information
        with st.expander("📊 Registry Information", expanded=False):
            stats = registry_manager.get_registry_stats()
            st.write(f"**Load Timestamp:** {stats['load_timestamp']}")
            st.write(f"**MQTT Clients:** {stats['mqtt_clients_count']}")
            st.write(f"**Topics:** {stats['topics_count']}")
            st.write(f"**Schemas:** {stats['schemas_count']}")
            st.write(f"**Mappings:** {stats['mappings_count']}")
            st.write(f"**Workpieces:** {stats['workpieces_count']}")
            st.write(f"**Modules:** {stats['modules_count']}")
            st.write(f"**Stations:** {stats['stations_count']}")
            st.write(f"**TXT Controllers:** {stats['txt_controllers_count']}")

    except Exception as e:
        logger.error(f"❌ Error rendering MQTT clients subtab: {e}")


def show_mqtt_clients_subtab():
    """Main function for MQTT clients subtab"""
    render_mqtt_clients_subtab()
