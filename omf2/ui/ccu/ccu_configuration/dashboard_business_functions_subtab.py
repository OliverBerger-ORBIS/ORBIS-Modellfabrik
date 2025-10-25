#!/usr/bin/env python3
"""
Dashboard Business Functions Configuration Subtab

Displays and allows editing of business_functions.yml configuration.
Provides viewing, quick-edit capabilities, validation, and save functionality.
"""

import streamlit as st
import yaml

from omf2.common.logger import get_logger
from omf2.config.business_functions_loader import BusinessFunctionsLoader
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_business_functions_section():
    """
    Render Business Functions Configuration Section
    
    Provides UI for:
    - Viewing YAML configuration
    - Per-function quick-edit (enable/disable and routed_topics bulk edit)
    - Validation
    - Save back to file
    """
    logger.info("⚙️ Rendering Business Functions Configuration Section")
    
    try:
        st.subheader(f"{UISymbols.get_tab_icon('configuration')} Business Functions Configuration")
        st.markdown("Configure business function metadata and topic routing")
        
        # Initialize loader
        loader = BusinessFunctionsLoader()
        
        # Load configuration
        if "business_functions_config" not in st.session_state:
            try:
                st.session_state.business_functions_config = loader.load_raw()
                logger.info("Business functions config loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load business functions config: {e}")
                st.error(f"❌ Failed to load configuration: {e}")
                return
        
        config = st.session_state.business_functions_config
        
        # Create tabs for different views
        tab1, tab2, tab3 = st.tabs([
            "📋 Quick Edit",
            "📝 YAML View",
            "ℹ️ Info"
        ])
        
        with tab1:
            _render_quick_edit_tab(config, loader)
        
        with tab2:
            _render_yaml_view_tab(config, loader)
        
        with tab3:
            _render_info_tab(config)
    
    except Exception as e:
        logger.error(f"❌ Business Functions section rendering error: {e}")
        st.error(f"❌ Failed to render Business Functions section: {e}")
        st.info("💡 This component is currently under development.")


def _render_quick_edit_tab(config, loader):
    """Render quick edit tab with per-function controls"""
    st.markdown("### 🎛️ Quick Edit Functions")
    st.markdown("Enable/disable functions and edit routed topics")
    
    business_functions = config.get('business_functions', {})
    
    if not business_functions:
        st.warning("No business functions defined in configuration")
        return
    
    # Show each function with quick edit controls
    for func_name, func_config in business_functions.items():
        with st.expander(f"**{func_name}** - {func_config.get('description', 'No description')}", expanded=False):
            _render_function_editor(func_name, func_config)
    
    st.divider()
    
    # Save button
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("💾 Save Configuration", use_container_width=True):
            _save_configuration(config, loader)
    
    with col2:
        if st.button("🔄 Reload", use_container_width=True):
            _reload_configuration(loader)
    
    with col3:
        if st.button("✅ Validate", use_container_width=True):
            _validate_configuration(loader)


def _render_function_editor(func_name, func_config):
    """Render editor for a single function"""
    
    # Enable/Disable toggle
    enabled = st.checkbox(
        "Enabled",
        value=func_config.get('enabled', False),
        key=f"enabled_{func_name}",
        help=f"Enable or disable {func_name}"
    )
    
    # Update config
    func_config['enabled'] = enabled
    
    # Display metadata
    col1, col2 = st.columns(2)
    
    with col1:
        st.text_input(
            "Module Path",
            value=func_config.get('module_path', ''),
            key=f"module_{func_name}",
            disabled=True,
            help="Python module path (read-only)"
        )
    
    with col2:
        st.text_input(
            "Class Name",
            value=func_config.get('class_name', ''),
            key=f"class_{func_name}",
            disabled=True,
            help="Class name (read-only)"
        )
    
    # Priority
    priority = st.slider(
        "Priority",
        min_value=1,
        max_value=10,
        value=func_config.get('priority', 5),
        key=f"priority_{func_name}",
        help="Priority level (1-10, higher = more important)"
    )
    func_config['priority'] = priority
    
    # Routed topics - editable as text area
    st.markdown("**Routed Topics:**")
    current_topics = func_config.get('routed_topics', [])
    topics_text = '\n'.join(current_topics)
    
    edited_topics = st.text_area(
        "Topics (one per line)",
        value=topics_text,
        key=f"topics_{func_name}",
        height=150,
        help="MQTT topics this function handles (one per line, supports wildcards like +)"
    )
    
    # Update topics in config
    new_topics = [t.strip() for t in edited_topics.split('\n') if t.strip()]
    func_config['routed_topics'] = new_topics
    
    # Metadata info
    metadata = func_config.get('metadata', {})
    if metadata:
        st.markdown("**Metadata:**")
        st.json(metadata, expanded=False)


def _render_yaml_view_tab(config, loader):
    """Render YAML view tab with full configuration display"""
    st.markdown("### 📝 Full YAML Configuration")
    st.markdown("View and edit the complete configuration in YAML format")
    
    # Display current YAML
    yaml_str = yaml.safe_dump(config, default_flow_style=False, sort_keys=False)
    
    edited_yaml = st.text_area(
        "YAML Content",
        value=yaml_str,
        height=400,
        help="Edit the YAML configuration directly",
        key="yaml_editor"
    )
    
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("💾 Save YAML", use_container_width=True):
            _save_yaml_configuration(edited_yaml, loader)
    
    with col2:
        if st.button("🔄 Reload", use_container_width=True):
            _reload_configuration(loader)
    
    with col3:
        if st.button("✅ Validate YAML", use_container_width=True):
            _validate_yaml(edited_yaml)


def _render_info_tab(config):
    """Render info tab with configuration metadata"""
    st.markdown("### ℹ️ Configuration Information")
    
    metadata = config.get('metadata', {})
    if metadata:
        st.markdown("**Metadata:**")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Version", metadata.get('version', 'N/A'))
            st.metric("Author", metadata.get('author', 'N/A'))
        
        with col2:
            st.metric("Last Updated", metadata.get('last_updated', 'N/A'))
        
        if 'description' in metadata:
            st.markdown("**Description:**")
            st.info(metadata['description'])
    
    # Statistics
    business_functions = config.get('business_functions', {})
    enabled_count = sum(1 for f in business_functions.values() if f.get('enabled', False))
    
    st.markdown("**Statistics:**")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Functions", len(business_functions))
    
    with col2:
        st.metric("Enabled", enabled_count)
    
    with col3:
        st.metric("Disabled", len(business_functions) - enabled_count)
    
    # QoS and Routing info
    if 'qos_settings' in config:
        st.markdown("**QoS Settings:**")
        st.json(config['qos_settings'], expanded=False)
    
    if 'routing' in config:
        st.markdown("**Routing Configuration:**")
        st.json(config['routing'], expanded=False)


def _save_configuration(config, loader):
    """Save configuration to file"""
    try:
        loader.save(config)
        st.success("✅ Configuration saved successfully!")
        logger.info("Business functions configuration saved")
    except Exception as e:
        logger.error(f"Failed to save configuration: {e}")
        st.error(f"❌ Failed to save configuration: {e}")


def _save_yaml_configuration(yaml_str, loader):
    """Save YAML configuration from text editor"""
    try:
        # Parse YAML
        config = yaml.safe_load(yaml_str)
        
        # Update session state
        st.session_state.business_functions_config = config
        
        # Save to file
        loader.save(config)
        
        st.success("✅ YAML configuration saved successfully!")
        logger.info("Business functions configuration saved from YAML editor")
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML: {e}")
        st.error(f"❌ Invalid YAML: {e}")
    except Exception as e:
        logger.error(f"Failed to save YAML configuration: {e}")
        st.error(f"❌ Failed to save configuration: {e}")


def _reload_configuration(loader):
    """Reload configuration from file"""
    try:
        config = loader.load_raw()
        st.session_state.business_functions_config = config
        st.success("✅ Configuration reloaded successfully!")
        logger.info("Business functions configuration reloaded")
        st.rerun()
    except Exception as e:
        logger.error(f"Failed to reload configuration: {e}")
        st.error(f"❌ Failed to reload configuration: {e}")


def _validate_configuration(loader):
    """Validate current configuration"""
    try:
        # Try to validate with pydantic if available
        config = st.session_state.business_functions_config
        
        # Basic validation
        if 'business_functions' not in config:
            st.error("❌ Validation failed: 'business_functions' key missing")
            return
        
        business_functions = config['business_functions']
        if not business_functions:
            st.warning("⚠️ No business functions defined")
            return
        
        # Validate each function
        errors = []
        for func_name, func_config in business_functions.items():
            if not func_config.get('module_path'):
                errors.append(f"{func_name}: Missing module_path")
            if not func_config.get('class_name'):
                errors.append(f"{func_name}: Missing class_name")
        
        if errors:
            st.error("❌ Validation errors found:")
            for error in errors:
                st.write(f"- {error}")
        else:
            st.success(f"✅ Validation passed! {len(business_functions)} functions configured correctly.")
            
            # Try Pydantic validation if available
            try:
                loader.load_validated()
                st.success("✅ Pydantic schema validation passed!")
            except Exception as e:
                st.warning(f"⚠️ Pydantic validation info: {e}")
        
        logger.info("Business functions configuration validation completed")
    
    except Exception as e:
        logger.error(f"Validation error: {e}")
        st.error(f"❌ Validation error: {e}")


def _validate_yaml(yaml_str):
    """Validate YAML syntax"""
    try:
        config = yaml.safe_load(yaml_str)
        st.success("✅ YAML syntax is valid!")
        
        # Basic structure check
        if 'business_functions' not in config:
            st.warning("⚠️ Warning: 'business_functions' key not found")
        else:
            st.info(f"ℹ️ Found {len(config['business_functions'])} business functions")
    
    except yaml.YAMLError as e:
        st.error(f"❌ Invalid YAML: {e}")
    except Exception as e:
        st.error(f"❌ Validation error: {e}")
