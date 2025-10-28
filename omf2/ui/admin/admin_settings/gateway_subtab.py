#!/usr/bin/env python3
"""
Gateway Subtab - Gateway Configuration Management for Admin Settings
Shows gateway.yml configuration with routing hints and refresh triggers
"""

from pathlib import Path

import streamlit as st

from omf2.assets.heading_icons import get_svg_inline
from omf2.common.logger import get_logger

logger = get_logger(__name__)


def render_gateway_subtab():
    """Render Gateway Configuration Subtab"""
    try:
        # Initialize i18n
        i18n = st.session_state.get("i18n_manager")
        if not i18n:
            logger.error("❌ I18n Manager not found in session state")
            return

        # SVG-Header mit Fallback - einfache Lösung mit größerer SVG
        gateway_svg = get_svg_inline("GATEWAY", size_px=32)
        header_icon = gateway_svg if gateway_svg else "🔀"
        st.markdown(
            f'<h3 style="margin-top: 0; margin-bottom: 1rem;">{header_icon} <strong>{i18n.t("admin.gateway")} Configuration</strong></h3>',
            unsafe_allow_html=True,
        )
        st.markdown("Gateway-Routing-Hints und UI-Refresh-Trigger Verwaltung")

        # Get registry manager from session state
        registry_manager = st.session_state.get("registry_manager")
        if not registry_manager:
            st.error("❌ Registry Manager nicht verfügbar")
            return

        # Get gateway configuration from registry
        gateway_config = registry_manager.get_gateway_config()
        routing_hints = gateway_config.get("routing_hints", {})
        refresh_triggers = gateway_config.get("refresh_triggers", {})

        # Display statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🔀 Routing Hints", len(routing_hints))
        with col2:
            total_routed_topics = sum(len(hint.get("routed_topics", [])) for hint in routing_hints.values())
            st.metric("📡 Total Routed Topics", total_routed_topics)
        with col3:
            st.metric("🔄 Refresh Trigger Groups", len(refresh_triggers))

        # Tabs for different sections
        tab1, tab2, tab3 = st.tabs(["📋 Routing Hints", "🔄 Refresh Triggers", "📝 YAML Editor"])

        with tab1:
            _render_routing_hints(routing_hints)

        with tab2:
            _render_refresh_triggers(refresh_triggers)

        with tab3:
            _render_yaml_editor(registry_manager)

    except Exception as e:
        logger.error(f"❌ Error rendering gateway subtab: {e}")
        st.error(f"❌ Fehler beim Laden der Gateway-Konfiguration: {e}")


def _render_routing_hints(routing_hints: dict):
    """Render Gateway Routing Hints"""
    st.markdown("### 🔀 Gateway Routing Hints")
    st.info("ℹ️ Routing Hints definieren, welche Topics vom Gateway an welche Business-Functions geroutet werden.")

    if not routing_hints:
        st.warning("⚠️ Keine Routing Hints gefunden")
        return

    # Display each manager's routing hints
    for manager_name, manager_config in routing_hints.items():
        with st.expander(f"📦 {manager_name} ({len(manager_config.get('routed_topics', []))} topics)", expanded=False):
            routed_topics = manager_config.get("routed_topics", [])

            if routed_topics:
                st.markdown(f"**Routed Topics:** {len(routed_topics)}")

                # Group topics by category for better visualization
                topic_categories = _categorize_topics(routed_topics)

                for category, topics in topic_categories.items():
                    st.markdown(f"**{category}:**")
                    for topic in topics:
                        st.text(f"  • {topic}")
            else:
                st.text("Keine routed topics definiert")


def _render_refresh_triggers(refresh_triggers: dict):
    """Render UI Refresh Triggers"""
    st.markdown("### 🔄 UI Refresh Triggers")
    st.info("ℹ️ Refresh Triggers definieren, welche Topics UI-Refresh-Events triggern sollen.")

    if not refresh_triggers:
        st.warning("⚠️ Keine Refresh Triggers gefunden")
        return

    # Display each refresh trigger group
    for trigger_group, topics in refresh_triggers.items():
        with st.expander(f"🔄 {trigger_group} ({len(topics)} topics)", expanded=False):
            if topics:
                for topic in topics:
                    st.text(f"  • {topic}")
            else:
                st.text("Keine topics definiert")


def _render_yaml_editor(registry_manager):
    """Render YAML Editor for gateway.yml"""
    st.markdown("### 📝 YAML Editor")
    st.warning(
        "⚠️ **Read-Only** - Änderungen zur Laufzeit sind nicht möglich. Bearbeite gateway.yml direkt im Dateisystem."
    )

    # Load gateway.yml from file
    project_root = Path(__file__).parent.parent.parent.parent.parent
    gateway_file = project_root / "omf2" / "registry" / "gateway.yml"

    if not gateway_file.exists():
        st.error(f"❌ gateway.yml nicht gefunden: {gateway_file}")
        return

    try:
        with open(gateway_file, encoding="utf-8") as f:
            gateway_yaml = f.read()

        # Display YAML content
        st.code(gateway_yaml, language="yaml", line_numbers=True)

        # File info
        st.caption(f"📁 Dateipfad: {gateway_file}")
        st.caption(f"📊 Dateigröße: {len(gateway_yaml)} Bytes")

    except Exception as e:
        st.error(f"❌ Fehler beim Laden der gateway.yml: {e}")
        logger.error(f"Failed to load gateway.yml: {e}")


def _categorize_topics(topics: list) -> dict:
    """Categorize topics by their prefix for better visualization"""
    categories = {
        "Sensor Topics": [],
        "Module Topics": [],
        "FTS Topics": [],
        "CCU Topics": [],
        "Order Topics": [],
        "Stock Topics": [],
        "Other Topics": [],
    }

    for topic in topics:
        if topic.startswith("/j1/txt/1/i/"):
            categories["Sensor Topics"].append(topic)
        elif topic.startswith("module/v1/ff/"):
            categories["Module Topics"].append(topic)
        elif topic.startswith("fts/v1/ff/"):
            categories["FTS Topics"].append(topic)
        elif topic.startswith("ccu/order/"):
            categories["Order Topics"].append(topic)
        elif topic.startswith("ccu/"):
            categories["CCU Topics"].append(topic)
        elif "stock" in topic.lower():
            categories["Stock Topics"].append(topic)
        else:
            categories["Other Topics"].append(topic)

    # Remove empty categories
    return {k: v for k, v in categories.items() if v}


def show_gateway_subtab():
    """Main function for gateway configuration subtab"""
    render_gateway_subtab()
