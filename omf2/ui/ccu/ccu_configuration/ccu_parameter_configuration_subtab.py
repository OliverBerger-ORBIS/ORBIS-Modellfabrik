#!/usr/bin/env python3
"""
CCU Configuration - Parameter Configuration Subtab
Displays production settings from CCU Config Loader
"""

import streamlit as st
from omf2.ccu.config_loader import get_ccu_config_loader
from omf2.common.logger import get_logger
from omf2.ui.utils.ui_refresh import request_refresh
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_ccu_parameter_configuration_subtab():
    """Render CCU Parameter Configuration Subtab"""
    logger.info("⚙️ Rendering CCU Parameter Configuration Subtab")
    try:
        st.subheader("⚙️ Parameter Configuration")
        st.markdown("Configure CCU production parameters and settings")
        
        # Load configuration data
        config_loader = get_ccu_config_loader()
        production_settings = config_loader.load_production_settings()
        
        # Initialize session state for configuration values
        _init_configuration_state(production_settings)
        
        # 1. Production Durations (BLUE, WHITE, RED)
        _show_production_durations_section()
        
        st.divider()
        
        # 2. Production Settings
        _show_production_settings_section()
        
        st.divider()
        
        # 3. FTS Settings
        _show_fts_settings_section()
        
        st.divider()
        
        # Save Button
        _show_save_button()
        
    except Exception as e:
        logger.error(f"❌ CCU Parameter Configuration Subtab rendering error: {e}")
        st.error(f"❌ CCU Parameter Configuration Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def _init_configuration_state(production_settings):
    """Initialize session state for configuration values"""
    if "ccu_production_settings" not in st.session_state:
        st.session_state.ccu_production_settings = production_settings
        logger.info("CCU Production Settings initialized from config file")


def _show_production_durations_section():
    """Show production durations section (BLUE, WHITE, RED order)"""
    st.subheader("⏱️ Production Durations")
    st.write("Production durations for different workpiece types")
    
    # 3 columns for BLUE, WHITE, RED (always in this order)
    col1, col2, col3 = st.columns(3)
    
    # BLUE (Column 1)
    with col1:
        st.markdown("**🔵 Blue Workpiece**")
        blue_duration = st.number_input(
            "Duration (seconds)",
            min_value=0,
            max_value=3600,
            value=st.session_state.ccu_production_settings["productionDurations"]["BLUE"],
            key="blue_duration",
            help="Production duration for blue workpieces in seconds"
        )
        st.session_state.ccu_production_settings["productionDurations"]["BLUE"] = blue_duration
    
    # WHITE (Column 2)
    with col2:
        st.markdown("**⚪ White Workpiece**")
        white_duration = st.number_input(
            "Duration (seconds)",
            min_value=0,
            max_value=3600,
            value=st.session_state.ccu_production_settings["productionDurations"]["WHITE"],
            key="white_duration",
            help="Production duration for white workpieces in seconds"
        )
        st.session_state.ccu_production_settings["productionDurations"]["WHITE"] = white_duration
    
    # RED (Column 3)
    with col3:
        st.markdown("**🔴 Red Workpiece**")
        red_duration = st.number_input(
            "Duration (seconds)",
            min_value=0,
            max_value=3600,
            value=st.session_state.ccu_production_settings["productionDurations"]["RED"],
            key="red_duration",
            help="Production duration for red workpieces in seconds"
        )
        st.session_state.ccu_production_settings["productionDurations"]["RED"] = red_duration


def _show_production_settings_section():
    """Show production settings section"""
    st.subheader("🏭 Production Settings")
    st.write("General production configuration")
    
    # Max parallel orders
    max_parallel_orders = st.number_input(
        "Max Parallel Orders",
        min_value=1,
        max_value=20,
        value=st.session_state.ccu_production_settings["productionSettings"]["maxParallelOrders"],
        key="max_parallel_orders",
        help="Maximum number of orders that can be processed in parallel"
    )
    st.session_state.ccu_production_settings["productionSettings"]["maxParallelOrders"] = max_parallel_orders


def _show_fts_settings_section():
    """Show FTS settings section"""
    st.subheader("🚗 FTS Settings")
    st.write("FTS (Fahrerloses Transportsystem) configuration")
    
    # Charge threshold
    charge_threshold = st.number_input(
        "Charge Threshold (%)",
        min_value=0,
        max_value=100,
        value=st.session_state.ccu_production_settings["ftsSettings"]["chargeThresholdPercent"],
        key="charge_threshold",
        help="Battery charge threshold percentage for FTS"
    )
    st.session_state.ccu_production_settings["ftsSettings"]["chargeThresholdPercent"] = charge_threshold


def _show_save_button():
    """Show save button with error handling"""
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button(f"{UISymbols.get_status_icon('save')} Save Configuration", 
                    key="save_ccu_config", use_container_width=True):
            try:
                # TODO: Implement actual save functionality via CCU Gateway
                # For now, just show success message
                st.success(f"{UISymbols.get_status_icon('success')} Configuration saved!")
                logger.info("CCU Production Settings saved successfully")
                
                # Request UI refresh
                request_refresh()
                
            except Exception as e:
                st.error(f"{UISymbols.get_status_icon('error')} Save failed: {e}")
                logger.error(f"Failed to save CCU Production Settings: {e}")


def get_ccu_production_settings():
    """Get current CCU production settings"""
    if "ccu_production_settings" not in st.session_state:
        config_loader = get_ccu_config_loader()
        return config_loader.load_production_settings()
    
    return st.session_state.ccu_production_settings


def set_ccu_production_settings(settings):
    """Set CCU production settings"""
    st.session_state.ccu_production_settings = settings
