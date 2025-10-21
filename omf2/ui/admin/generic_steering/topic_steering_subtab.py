"""
Topic Steering Subtab - Refactored
Clean, modular implementation with separated concerns
"""

import streamlit as st

from omf2.registry.manager.registry_manager import get_registry_manager
from omf2.ui.common.components.schema_tester import SchemaTester
from omf2.ui.common.components.topic_selector import TopicSelector
from omf2.ui.common.symbols import UISymbols


def render_topic_steering_subtab(admin_gateway=None, registry_manager=None):
    """Renders the topic steering subtab with clean separation of concerns"""

    # Use provided registry manager or get from session state (PERFORMANCE: Cache in session state)
    if not registry_manager:
        if "registry_manager" not in st.session_state:
            st.session_state.registry_manager = get_registry_manager("omf2/registry/")
        registry_manager = st.session_state.registry_manager

    # PERFORMANCE: Cache components in session state to avoid re-initialization
    if "topic_selector" not in st.session_state:
        st.session_state.topic_selector = TopicSelector(registry_manager)
    if "schema_tester" not in st.session_state:
        st.session_state.schema_tester = SchemaTester(registry_manager)

    # Use cached components
    topic_selector = st.session_state.topic_selector
    schema_tester = st.session_state.schema_tester

    # Main UI
    st.markdown(f"### {UISymbols.get_functional_icon('target')} Topic Steering")
    st.markdown("Schema-driven message sending and testing")

    # Mode selection
    mode = st.radio(
        "Select Mode:", ["Topic-driven", "Schema-driven", "Schema Test"], horizontal=True, key="topic_steering_mode"
    )

    if mode == "Topic-driven":
        topic_selector.render_topic_driven_ui()
    elif mode == "Schema-driven":
        topic_selector.render_schema_driven_ui()
    elif mode == "Schema Test":
        schema_tester.render_test_ui()
