#!/usr/bin/env python3
"""
Dashboard Gateway Configuration Subtab

Allows viewing and editing gateway.yml configuration,
specifically the refresh_triggers section.
"""

import streamlit as st
import yaml
from pathlib import Path

from omf2.common.logger import get_logger
from omf2.registry.manager.registry_manager import get_registry_manager

logger = get_logger(__name__)


def show_dashboard_gateway_configuration_subtab(i18n):
    """Render Dashboard Gateway Configuration Subtab"""
    logger.info("📝 Rendering Dashboard Gateway Configuration Subtab")
    
    try:
        st.markdown("### Gateway Configuration")
        st.markdown("Configure refresh triggers for UI auto-refresh based on MQTT topics.")
        
        # Get registry manager
        registry_manager = get_registry_manager()
        
        # Load current gateway config
        gateway_config = registry_manager.get_gateway_config()
        refresh_triggers = gateway_config.get('refresh_triggers', {})
        
        # Display current configuration
        st.markdown("#### Current Refresh Triggers")
        
        if not refresh_triggers:
            st.info("No refresh triggers configured yet.")
        else:
            for group_name, topics in refresh_triggers.items():
                with st.expander(f"📋 {group_name}", expanded=False):
                    st.markdown(f"**Group:** `{group_name}`")
                    st.markdown("**Topics:**")
                    for topic in topics:
                        st.code(topic, language="text")
        
        # Edit mode
        st.divider()
        st.markdown("#### Edit Refresh Triggers")
        
        # Use session_state to store edited configuration
        if 'edited_refresh_triggers' not in st.session_state:
            st.session_state.edited_refresh_triggers = yaml.dump(refresh_triggers, default_flow_style=False)
        
        # Text area for editing YAML
        edited_yaml = st.text_area(
            "Edit refresh triggers (YAML format)",
            value=st.session_state.edited_refresh_triggers,
            height=300,
            help="Edit the refresh triggers configuration in YAML format. Each group contains a list of topic patterns."
        )
        
        # Update session_state
        st.session_state.edited_refresh_triggers = edited_yaml
        
        # Buttons
        col1, col2, col3 = st.columns([1, 1, 2])
        
        with col1:
            if st.button("💾 Save Changes", type="primary"):
                _save_refresh_triggers(edited_yaml, registry_manager)
        
        with col2:
            if st.button("🔄 Reset"):
                st.session_state.edited_refresh_triggers = yaml.dump(refresh_triggers, default_flow_style=False)
                st.rerun()
        
        # Show example
        st.divider()
        st.markdown("#### Example Configuration")
        st.code("""
# Example refresh_triggers configuration
order_updates:
  - ccu/order/active
  - ccu/order/completed
  - ccu/order/request
  - ccu/order/response

module_updates:
  - module/v1/ff/*/state
  - module/v1/ff/*/connection
  - fts/v1/ff/*/state

sensor_updates:
  - /j1/txt/1/i/bme680
  - /j1/txt/1/i/ldr

stock_updates:
  - /j1/txt/1/f/i/stock
  - ccu/state/stock
""", language="yaml")
        
    except Exception as e:
        logger.error(f"❌ Dashboard Gateway Configuration Subtab error: {e}")
        st.error(f"❌ Failed to render configuration: {e}")


def _save_refresh_triggers(yaml_content: str, registry_manager):
    """
    Save edited refresh triggers back to gateway.yml
    
    Args:
        yaml_content: YAML string with refresh triggers
        registry_manager: Registry manager instance
    """
    try:
        # Parse YAML
        new_refresh_triggers = yaml.safe_load(yaml_content)
        
        if not isinstance(new_refresh_triggers, dict):
            st.error("❌ Invalid YAML: Expected a dictionary at root level")
            return
        
        # Validate structure
        for group_name, topics in new_refresh_triggers.items():
            if not isinstance(topics, list):
                st.error(f"❌ Invalid YAML: Group '{group_name}' must contain a list of topics")
                return
        
        # Load full gateway config
        gateway_config_path = Path(registry_manager.registry_root) / "gateway.yml"
        
        with open(gateway_config_path, 'r') as f:
            full_config = yaml.safe_load(f)
        
        # Update refresh_triggers section
        if 'gateway' not in full_config:
            full_config['gateway'] = {}
        
        full_config['gateway']['refresh_triggers'] = new_refresh_triggers
        
        # Save back to file
        with open(gateway_config_path, 'w') as f:
            yaml.dump(full_config, f, default_flow_style=False, sort_keys=False)
        
        st.success("✅ Configuration saved successfully!")
        logger.info(f"✅ Gateway refresh_triggers saved: {len(new_refresh_triggers)} groups")
        
        # Update session_state to reflect saved state
        st.session_state.edited_refresh_triggers = yaml_content
        
    except yaml.YAMLError as e:
        st.error(f"❌ Invalid YAML syntax: {e}")
        logger.error(f"❌ YAML parse error: {e}")
    except Exception as e:
        st.error(f"❌ Failed to save configuration: {e}")
        logger.error(f"❌ Save error: {e}")
