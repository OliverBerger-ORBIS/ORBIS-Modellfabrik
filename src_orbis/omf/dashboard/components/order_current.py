"""
OMF Dashboard Order - Laufende Aufträge
"""

import os
import sys

import streamlit as st

# Template-Import hinzufügen
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "assets"))
try:
    from html_templates import get_module_card_template, get_status_badge_template, get_test_template

    TEMPLATES_AVAILABLE = True
except ImportError as e:
    TEMPLATES_AVAILABLE = False
    st.error(f"❌ Templates nicht verfügbar: {e}")


def show_order_current():
    """Zeigt die laufenden Aufträge"""
    st.subheader("🔄 Laufende Aufträge")

    # Template-Test
    if TEMPLATES_AVAILABLE:
        st.markdown("### 🧪 Template-Test in Order Current")
        st.markdown(get_test_template(), unsafe_allow_html=True)

        st.markdown("### 🏭 Modul-Karten-Test")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown(get_module_card_template("AIQS", "READY", "192.168.1.100"), unsafe_allow_html=True)
            st.markdown(get_module_card_template("MILL", "BUSY", "192.168.1.101"), unsafe_allow_html=True)

        with col2:
            st.markdown(get_module_card_template("DRILL", "BLOCKED", "192.168.1.102"), unsafe_allow_html=True)
            st.markdown(get_module_card_template("HBW", "OFFLINE"), unsafe_allow_html=True)

        st.markdown("### 🏷️ Status-Badges-Test")
        st.markdown(get_status_badge_template("READY", "success"), unsafe_allow_html=True)
        st.markdown(get_status_badge_template("BUSY", "warning"), unsafe_allow_html=True)
        st.markdown(get_status_badge_template("BLOCKED", "error"), unsafe_allow_html=True)
        st.markdown(get_status_badge_template("INFO", "info"), unsafe_allow_html=True)

        st.markdown("---")
    else:
        st.info("Laufende Aufträge werden hier angezeigt")
