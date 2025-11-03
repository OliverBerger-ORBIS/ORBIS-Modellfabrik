#!/usr/bin/env python3
"""
CCU Configuration - Parameter Configuration Subtab
Displays production settings from CCU Config Loader
"""

import streamlit as st

from omf2.assets.asset_manager import get_asset_manager
from omf2.ccu.config_loader import get_ccu_config_loader
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols, get_icon_html
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_ccu_parameter_configuration_subtab():
    """Render CCU Parameter Configuration Subtab"""
    logger.info("⚙️ Rendering CCU Parameter Configuration Subtab")
    try:
        # Subheading: try heading SVG (32px for subtabs), fallback to emoji
        try:
            i18n = st.session_state.get("i18n_manager")
        except Exception:
            i18n = None

        try:
            cfg_icon = get_asset_manager().get_asset_inline("CONFIGURATION", size_px=32) or ""
            title = i18n.t("ccu_configuration.parameter.title") if i18n else "Parameter Configuration"
            st.markdown(
                f"<h3 style='margin: 0.25rem 0 0.5rem 0; display:flex; align-items:center; gap:8px;'>{cfg_icon} {title}</h3>",
                unsafe_allow_html=True,
            )
        except Exception:
            st.subheader(
                f"{UISymbols.get_tab_icon('parameter')} "
                f"{(i18n.t('ccu_configuration.parameter.title') if i18n else 'Parameter Configuration')}"
            )
        # Subtitle (i18n): neutral/OMF wording
        st.markdown(
            i18n.t("ccu_configuration.parameter.subtitle") if i18n else "OMF production parameters and settings"
        )

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
    i18n = st.session_state.get("i18n_manager")
    _title = None
    _subtitle = None
    if i18n:
        try:
            _title = i18n.t("ccu_configuration.parameter.durations.title")
            _subtitle = i18n.t("ccu_configuration.parameter.durations.subtitle")
        except Exception:
            _title = None
            _subtitle = None
    if not isinstance(_title, str) or not _title:
        _title = "Production Durations"
    if not isinstance(_subtitle, str) or not _subtitle:
        _subtitle = "Production durations for different workpiece types"
    st.subheader(f"⏱️ {_title}")
    st.write(_subtitle)

    # 3 columns for BLUE, WHITE, RED (always in this order)
    col1, col2, col3 = st.columns(3)

    # BLUE (Column 1)
    with col1:
        st.markdown(
            "**" + (i18n.t("ccu_configuration.parameter.durations.labels.blue") if i18n else "🔵 Blue Workpiece") + "**"
        )
        blue_duration = st.number_input(
            (i18n.t("ccu_configuration.parameter.durations.fields.duration_seconds") if i18n else "Duration (seconds)"),
            min_value=0,
            max_value=3600,
            value=st.session_state.ccu_production_settings["productionDurations"]["BLUE"],
            key="blue_duration",
            help=(
                i18n.t("ccu_configuration.parameter.durations.help.blue")
                if i18n
                else "Production duration for blue workpieces in seconds"
            ),
        )
        st.session_state.ccu_production_settings["productionDurations"]["BLUE"] = blue_duration

    # WHITE (Column 2)
    with col2:
        st.markdown(
            "**"
            + (i18n.t("ccu_configuration.parameter.durations.labels.white") if i18n else "⚪ White Workpiece")
            + "**"
        )
        white_duration = st.number_input(
            (i18n.t("ccu_configuration.parameter.durations.fields.duration_seconds") if i18n else "Duration (seconds)"),
            min_value=0,
            max_value=3600,
            value=st.session_state.ccu_production_settings["productionDurations"]["WHITE"],
            key="white_duration",
            help=(
                i18n.t("ccu_configuration.parameter.durations.help.white")
                if i18n
                else "Production duration for white workpieces in seconds"
            ),
        )
        st.session_state.ccu_production_settings["productionDurations"]["WHITE"] = white_duration

    # RED (Column 3)
    with col3:
        st.markdown(
            "**" + (i18n.t("ccu_configuration.parameter.durations.labels.red") if i18n else "🔴 Red Workpiece") + "**"
        )
        red_duration = st.number_input(
            (i18n.t("ccu_configuration.parameter.durations.fields.duration_seconds") if i18n else "Duration (seconds)"),
            min_value=0,
            max_value=3600,
            value=st.session_state.ccu_production_settings["productionDurations"]["RED"],
            key="red_duration",
            help=(
                i18n.t("ccu_configuration.parameter.durations.help.red")
                if i18n
                else "Production duration for red workpieces in seconds"
            ),
        )
        st.session_state.ccu_production_settings["productionDurations"]["RED"] = red_duration


def _show_production_settings_section():
    """Show production settings section"""
    # Get SVG icon for Production Settings
    try:
        prod_icon = get_asset_manager().get_asset_inline("PRODUCTION_ORDERS", size_px=32) or ""
        i18n = st.session_state.get("i18n_manager")
        title = i18n.t("ccu_configuration.parameter.settings.title") if i18n else "Production Settings"
        st.markdown(
            f"<h4 style='margin: 0.25rem 0 0.25rem 0; display:flex; align-items:center; gap:8px;'>{prod_icon} {title}</h4>",
            unsafe_allow_html=True,
        )
    except Exception:
        st.subheader("🏭 " + (i18n.t("ccu_configuration.parameter.settings.title") if i18n else "Production Settings"))
    _ps_subtitle = None
    if i18n:
        try:
            _ps_subtitle = i18n.t("ccu_configuration.parameter.settings.subtitle")
        except Exception:
            _ps_subtitle = None
    if not isinstance(_ps_subtitle, str) or not _ps_subtitle:
        _ps_subtitle = "General production configuration"
    st.write(_ps_subtitle)

    # Max parallel orders
    max_parallel_orders = st.number_input(
        (i18n.t("ccu_configuration.parameter.settings.max_parallel_orders") if i18n else "Max Parallel Orders"),
        min_value=1,
        max_value=20,
        value=st.session_state.ccu_production_settings["productionSettings"]["maxParallelOrders"],
        key="max_parallel_orders",
        help=(
            i18n.t("ccu_configuration.parameter.settings.help.max_parallel_orders")
            if i18n
            else "Maximum number of orders that can be processed in parallel"
        ),
    )
    st.session_state.ccu_production_settings["productionSettings"]["maxParallelOrders"] = max_parallel_orders


def _show_fts_settings_section():
    """Show FTS settings section"""
    # Get SVG icon for FTS Settings (using module icon for FTS)
    try:
        fts_icon = get_icon_html("FTS", size_px=32)
        i18n = st.session_state.get("i18n_manager")
        title = i18n.t("ccu_configuration.parameter.fts.title") if i18n else "FTS Settings"
        st.markdown(
            f"<h4 style='margin: 0.25rem 0 0.25rem 0; display:flex; align-items:center; gap:8px;'>{fts_icon} {title}</h4>",
            unsafe_allow_html=True,
        )
    except Exception:
        st.subheader("🚗 " + (i18n.t("ccu_configuration.parameter.fts.title") if i18n else "FTS Settings"))
    _fts_subtitle = None
    if i18n:
        try:
            _fts_subtitle = i18n.t("ccu_configuration.parameter.fts.subtitle")
        except Exception:
            _fts_subtitle = None
    if not isinstance(_fts_subtitle, str) or not _fts_subtitle:
        _fts_subtitle = "FTS (Fahrerloses Transportsystem) configuration"
    st.write(_fts_subtitle)

    # Charge threshold
    charge_threshold = st.number_input(
        (i18n.t("ccu_configuration.parameter.fts.charge_threshold_percent") if i18n else "Charge Threshold (%)"),
        min_value=0,
        max_value=100,
        value=st.session_state.ccu_production_settings["ftsSettings"]["chargeThresholdPercent"],
        key="charge_threshold",
        help=(
            i18n.t("ccu_configuration.parameter.fts.help.charge_threshold")
            if i18n
            else "Battery charge threshold percentage for FTS"
        ),
    )
    st.session_state.ccu_production_settings["ftsSettings"]["chargeThresholdPercent"] = charge_threshold


def _show_save_button():
    """Show save button with error handling"""
    col1, col2, col3 = st.columns([1, 1, 1])

    with col2:
        i18n = st.session_state.get("i18n_manager")
        label = f"{UISymbols.get_status_icon('save')} " + (
            i18n.t("ccu_configuration.parameter.save.button_label") if i18n else "Save Configuration"
        )
        if st.button(label, key="save_ccu_config", use_container_width=True):
            try:
                # TODO: Implement actual save functionality via CCU Gateway
                # For now, just show success message
                st.success(
                    f"{UISymbols.get_status_icon('success')} "
                    + (i18n.t("ccu_configuration.parameter.save.success") if i18n else "Configuration saved!")
                )
                logger.info("CCU Production Settings saved successfully")

                # Request UI refresh
                request_refresh()

            except Exception as e:
                st.error(
                    f"{UISymbols.get_status_icon('error')} "
                    + (i18n.t("ccu_configuration.parameter.save.failed", error=e) if i18n else f"Save failed: {e}")
                )
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
