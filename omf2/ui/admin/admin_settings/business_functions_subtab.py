#!/usr/bin/env python3
"""
Admin Settings - Business Functions Subtab

Relocated from CCU Configuration to Admin Settings.
Uses the same UI as before to edit business_functions.yml.
"""

import streamlit as st
import yaml

from omf2.common.logger import get_logger
from omf2.config.business_functions_loader import BusinessFunctionsLoader
from omf2.ui.common.symbols import UISymbols
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_business_functions_subtab():
    """Render Business Functions configuration UI under Admin Settings."""
    try:
        # Ensure i18n available (no assignment to avoid linter warnings)
        st.session_state.get("i18n_manager")

        st.subheader(f"{UISymbols.get_tab_icon('business_functions')} Business Functions")
        st.markdown("Configure business function metadata and topic routing")

        loader = BusinessFunctionsLoader()

        if "business_functions_config" not in st.session_state:
            try:
                st.session_state.business_functions_config = loader.load_raw()
            except Exception as e:
                logger.error(f"Failed to load business functions config: {e}")
                st.error(f"❌ Failed to load configuration: {e}")
                return

        config = st.session_state.business_functions_config

        tab1, tab2, tab3 = st.tabs(["📋 Quick Edit", "📝 YAML View", "ℹ️ Info"])

        with tab1:
            _render_quick_edit_tab(config, loader)

        with tab2:
            _render_yaml_view_tab(config, loader)

        with tab3:
            _render_info_tab(config)

    except Exception as e:
        logger.error(f"❌ Business Functions subtab rendering error: {e}")
        st.error(f"❌ Failed to render Business Functions subtab: {e}")


def _render_quick_edit_tab(config, loader):
    st.markdown("### 🎛️ Quick Edit Functions")
    st.markdown("Enable/disable functions and edit routed topics")

    business_functions = config.get("business_functions", {})
    if not business_functions:
        st.warning("No business functions defined in configuration")
        return

    for idx, (func_name, func_config) in enumerate(business_functions.items()):
        unique_title = f"**{func_name}** - {func_config.get('description', 'No description')} [{idx}]"
        with st.expander(unique_title, expanded=False):
            _render_function_editor(func_name, func_config)

    st.divider()

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("💾 Save Configuration", use_container_width=True, key="save_config_btn"):
            _save_configuration(config, loader)
    with col2:
        if st.button("🔄 Reload", use_container_width=True, key="reload_config_btn"):
            _reload_configuration(loader)
    with col3:
        if st.button("✅ Validate", use_container_width=True, key="validate_config_btn"):
            _validate_configuration(loader)


def _render_function_editor(func_name, func_config):
    enabled = st.checkbox("Enabled", value=func_config.get("enabled", False), key=f"enabled_{func_name}")
    func_config["enabled"] = enabled

    col1, col2 = st.columns(2)
    with col1:
        st.text_input("Module Path", value=func_config.get("module_path", ""), key=f"module_{func_name}", disabled=True)
    with col2:
        st.text_input("Class Name", value=func_config.get("class_name", ""), key=f"class_{func_name}", disabled=True)

    priority = st.slider(
        "Priority", min_value=1, max_value=10, value=func_config.get("priority", 5), key=f"priority_{func_name}"
    )
    func_config["priority"] = priority

    st.markdown("**Routed Topics:**")
    current_topics = func_config.get("routed_topics", [])
    topics_text = "\n".join(current_topics)
    edited_topics = st.text_area("Topics (one per line)", value=topics_text, key=f"topics_{func_name}", height=150)
    new_topics = [t.strip() for t in edited_topics.split("\n") if t.strip()]
    func_config["routed_topics"] = new_topics

    metadata = func_config.get("metadata", {})
    if metadata:
        st.markdown("**Metadata:**")
        st.json(metadata, expanded=False)


def _render_yaml_view_tab(config, loader):
    st.markdown("### 📝 Full YAML Configuration")
    yaml_str = yaml.safe_dump(config, default_flow_style=False, sort_keys=False)
    edited_yaml = st.text_area("YAML Content", value=yaml_str, height=400, key="yaml_editor")

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        if st.button("💾 Save YAML", use_container_width=True, key="save_yaml_btn"):
            _save_yaml_configuration(edited_yaml, loader)
    with col2:
        if st.button("🔄 Reload", use_container_width=True, key="reload_yaml_btn"):
            _reload_configuration(loader)
    with col3:
        if st.button("✅ Validate YAML", use_container_width=True, key="validate_yaml_btn"):
            _validate_yaml(edited_yaml)


def _render_info_tab(config):
    st.markdown("### ℹ️ Configuration Information")
    metadata = config.get("metadata", {})
    if metadata:
        st.markdown("**Metadata:**")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Version", metadata.get("version", "N/A"))
            st.metric("Author", metadata.get("author", "N/A"))
        with col2:
            st.metric("Last Updated", metadata.get("last_updated", "N/A"))
        if "description" in metadata:
            st.markdown("**Description:**")
            st.info(metadata["description"])

    business_functions = config.get("business_functions", {})
    enabled_count = sum(1 for f in business_functions.values() if f.get("enabled", False))
    st.markdown("**Statistics:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Functions", len(business_functions))
    with col2:
        st.metric("Enabled", enabled_count)
    with col3:
        st.metric("Disabled", len(business_functions) - enabled_count)


def _save_configuration(config, loader):
    try:
        loader.save(config)
        st.success("✅ Configuration saved successfully!")
    except Exception as e:
        st.error(f"❌ Failed to save configuration: {e}")


def _save_yaml_configuration(yaml_str, loader):
    try:
        config = yaml.safe_load(yaml_str)
        st.session_state.business_functions_config = config
        loader.save(config)
        st.success("✅ YAML configuration saved successfully!")
    except yaml.YAMLError as e:
        st.error(f"❌ Invalid YAML: {e}")
    except Exception as e:
        st.error(f"❌ Failed to save configuration: {e}")


def _reload_configuration(loader):
    try:
        config = loader.load_raw()
        st.session_state.business_functions_config = config
        st.success("✅ Configuration reloaded successfully!")
        request_refresh()
    except Exception as e:
        st.error(f"❌ Failed to reload configuration: {e}")


def _validate_configuration(loader):
    try:
        config = st.session_state.business_functions_config
        if "business_functions" not in config:
            st.error("❌ Validation failed: 'business_functions' key missing")
            return
        business_functions = config["business_functions"]
        if not business_functions:
            st.warning("⚠️ No business functions defined")
            return
        errors = []
        for func_name, func_config in business_functions.items():
            if not func_config.get("module_path"):
                errors.append(f"{func_name}: Missing module_path")
            if not func_config.get("class_name"):
                errors.append(f"{func_name}: Missing class_name")
        if errors:
            st.error("❌ Validation errors found:")
            for error in errors:
                st.write(f"- {error}")
        else:
            st.success(f"✅ Validation passed! {len(business_functions)} functions configured correctly.")
            try:
                loader.load_validated()
                st.success("✅ Pydantic schema validation passed!")
            except Exception as e:
                st.warning(f"⚠️ Pydantic validation info: {e}")
    except Exception as e:
        st.error(f"❌ Validation error: {e}")


def _validate_yaml(yaml_str):
    try:
        config = yaml.safe_load(yaml_str)
        st.success("✅ YAML syntax is valid!")
        if "business_functions" not in config:
            st.warning("⚠️ Warning: 'business_functions' key not found")
        else:
            st.info(f"ℹ️ Found {len(config['business_functions'])} business functions")
    except yaml.YAMLError as e:
        st.error(f"❌ Invalid YAML: {e}")
    except Exception as e:
        st.error(f"❌ Validation error: {e}")
