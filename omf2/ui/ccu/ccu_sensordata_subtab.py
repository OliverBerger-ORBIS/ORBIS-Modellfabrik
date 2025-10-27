#!/usr/bin/env python3
"""
CCU Overview - Sensor Data Subtab (OMF-Style)
Real-time sensor data visualization with normalized displays and IAQ traffic light
Uses sensors_display_utils for normalization and configuration
"""

from datetime import datetime
from typing import Dict

import plotly.graph_objects as go
import streamlit as st

from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.sensor_manager import get_ccu_sensor_manager
from omf2.common.logger import get_logger
from omf2.ui.ccu.sensors_display_utils import (
    get_iaq_info,
    load_sensor_display_config,
    normalize_brightness,
    normalize_humidity,
    normalize_pressure,
    normalize_temperature,
)
from omf2.ui.common.symbols import UISymbols
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_sensor_data_subtab(ccu_gateway: CcuGateway, registry_manager, asset_manager):
    """Render Sensor Data Subtab with OMF-style visualization"""
    logger.info("🌡️ Rendering Sensor Data Subtab (OMF-Style)")

    # I18n Manager aus Session State holen
    i18n = st.session_state.get("i18n_manager")
    if not i18n:
        logger.error("❌ I18n Manager not found in session state")
        return

    try:
        # Load sensor display configuration
        config = load_sensor_display_config()

        # Header with UISymbols
        st.header(f"{UISymbols.get_functional_icon('sensor_data')} {i18n.t('ccu_overview.sensor_data.title')}")
        subtitle_text = i18n.t("ccu_overview.sensor_data.subtitle")
        st.markdown(subtitle_text)

        # Sensor Controls
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            refresh_text = i18n.t("ccu_overview.sensor_data.refresh_data")
            if st.button(
                f"{UISymbols.get_status_icon('refresh')} {refresh_text}", use_container_width=True, key="sensor_refresh"
            ):
                _refresh_sensor_data()

        with col2:
            statistics_text = i18n.t("ccu_overview.sensor_data.show_statistics")
            if st.button(
                f"{UISymbols.get_functional_icon('dashboard')} {statistics_text}",
                use_container_width=True,
                key="sensor_statistics",
            ):
                _show_sensor_statistics(ccu_gateway)

        with col3:
            clear_text = i18n.t("ccu_overview.sensor_data.clear_history")
            if st.button(
                f"{UISymbols.get_functional_icon('settings')} {clear_text}",
                use_container_width=True,
                key="sensor_clear",
            ):
                _clear_sensor_history(ccu_gateway)

        st.divider()

        # Show sensor panels with OMF-style visualization
        _show_sensor_panels(ccu_gateway, config, i18n)

    except Exception as e:
        logger.error(f"❌ Sensor Data Subtab error: {e}")
        st.error(f"❌ Sensor Data Subtab failed: {e}")
        i18n_fallback = st.session_state.get("i18n_manager")
        if i18n_fallback:
            st.info(f"💡 {i18n_fallback.t('common.status.under_development')}")


def get_latest_sensor_values() -> Dict:
    """
    Placeholder function to get latest sensor values from state store

    NOTE: This should be adapted to your actual state store (Redis/DB/etc.)
    Currently returns dummy data for demonstration

    Returns:
        Dict: Sensor data dictionary with temperature, humidity, brightness, pressure, iaq
    """
    # TODO: Integrate with actual state store
    # Example: Get from Redis, database, or existing sensor manager

    sensor_manager = get_ccu_sensor_manager()
    sensor_data = sensor_manager.get_sensor_data()

    if sensor_data:
        bme680_data = sensor_data.get("/j1/txt/1/i/bme680", {})
        ldr_data = sensor_data.get("/j1/txt/1/i/ldr", {})

        return {
            "temperature": bme680_data.get("temperature"),
            "humidity": bme680_data.get("humidity"),
            "pressure": bme680_data.get("pressure"),
            "iaq": bme680_data.get("air_quality"),
            "brightness": ldr_data.get("light"),  # Note: might need conversion from % to lux
            "timestamp": bme680_data.get("timestamp", datetime.now().isoformat()),
        }

    # Return None values if no data available
    return {
        "temperature": None,
        "humidity": None,
        "pressure": None,
        "iaq": None,
        "brightness": None,
        "timestamp": None,
    }


def _show_sensor_panels(ccu_gateway: CcuGateway, config: Dict, i18n):
    """Display sensor panels with OMF-style visualization"""
    logger.info("🌡️ Rendering Sensor Panels (OMF-Style)")

    try:
        # Get latest sensor values
        sensor_values = get_latest_sensor_values()

        # Check if we have any data
        has_data = any(v is not None for k, v in sensor_values.items() if k != "timestamp")

        if has_data:
            live_data_text = i18n.t("ccu_overview.sensor_data.live_data_available")
            st.success(f"✅ **{live_data_text}**")
        else:
            no_data_text = i18n.t("ccu_overview.sensor_data.no_data")
            st.warning(f"⚠️ {no_data_text}")

        # Row 1: Temperature + Humidity + IAQ
        col1, col2, col3 = st.columns(3)

        with col1:
            _show_temperature_gauge(sensor_values.get("temperature"), config, i18n)

        with col2:
            _show_humidity_gauge(sensor_values.get("humidity"), config, i18n)

        with col3:
            _show_iaq_badge(sensor_values.get("iaq"), config, i18n)

        st.divider()

        # Row 2: Pressure + Brightness
        col4, col5 = st.columns(2)

        with col4:
            _show_pressure_gauge(sensor_values.get("pressure"), config, i18n)

        with col5:
            _show_brightness_gauge(sensor_values.get("brightness"), config, i18n)

        # Show timestamp if available
        if sensor_values.get("timestamp"):
            st.caption(f"⏰ Last update: {_format_timestamp(sensor_values.get('timestamp'))}")

    except Exception as e:
        logger.error(f"❌ Error displaying sensor panels: {e}")
        st.error(f"❌ Error displaying sensor data: {e}")


def _show_temperature_gauge(temperature: float, config: Dict, i18n):
    """Display temperature as OMF-style gauge with normalization"""
    title_text = i18n.t("ccu_overview.sensor_data.current_temperature")
    st.subheader(f"🌡️ {title_text}")

    if temperature is not None:
        # Normalize temperature to percentage
        temp_percent = normalize_temperature(temperature, config)
        temp_config = config.get("temperature", {})
        min_temp = temp_config.get("min", -30.0)
        max_temp = temp_config.get("max", 60.0)

        # Create Plotly gauge
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number+delta",
                value=temperature,
                number={"suffix": "°C"},
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": f"Range: {min_temp}°C to {max_temp}°C"},
                gauge={
                    "axis": {"range": [min_temp, max_temp]},
                    "bar": {"color": "darkred"},
                    "steps": [
                        {"range": [min_temp, min_temp + (max_temp - min_temp) * 0.4], "color": "lightblue"},
                        {
                            "range": [min_temp + (max_temp - min_temp) * 0.4, min_temp + (max_temp - min_temp) * 0.6],
                            "color": "lightgreen",
                        },
                        {"range": [min_temp + (max_temp - min_temp) * 0.6, max_temp], "color": "lightyellow"},
                    ],
                },
            )
        )

        fig.update_layout(height=250, margin={"l": 20, "r": 20, "t": 50, "b": 20}, font={"size": 12})
        st.plotly_chart(fig, use_container_width=True)

        # Show normalized percentage
        st.metric("Fill Level", f"{temp_percent:.1f}%")
    else:
        st.warning("⚠️ No temperature data")


def _show_humidity_gauge(humidity: float, config: Dict, i18n):
    """Display humidity as OMF-style gauge (already 0-100%)"""
    title_text = i18n.t("ccu_overview.sensor_data.current_humidity")
    st.subheader(f"💧 {title_text}")

    if humidity is not None:
        # Normalize humidity (clamp to 0-100)
        humidity_norm = normalize_humidity(humidity)

        # Create Plotly gauge
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=humidity_norm,
                number={"suffix": "%"},
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Relative Humidity"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [0, 30], "color": "lightyellow"},
                        {"range": [30, 60], "color": "lightgreen"},
                        {"range": [60, 100], "color": "lightblue"},
                    ],
                },
            )
        )

        fig.update_layout(height=250, margin={"l": 20, "r": 20, "t": 50, "b": 20}, font={"size": 12})
        st.plotly_chart(fig, use_container_width=True)

        st.metric("Humidity Level", f"{humidity_norm:.1f}%")
    else:
        st.warning("⚠️ No humidity data")


def _show_brightness_gauge(brightness: float, config: Dict, i18n):
    """Display brightness as OMF-style gauge (normalized to 0-100%)"""
    title_text = i18n.t("ccu_overview.sensor_data.current_light")
    st.subheader(f"💡 {title_text}")

    if brightness is not None:
        # Normalize brightness to percentage (never > 100%)
        brightness_percent = normalize_brightness(brightness, config)
        max_lux = config.get("brightness", {}).get("max_lux", 1000.0)

        # Create Plotly gauge
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=brightness_percent,
                number={"suffix": "%"},
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": f"Brightness (max: {max_lux} lux)"},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "gold"},
                    "steps": [
                        {"range": [0, 20], "color": "darkblue"},
                        {"range": [20, 50], "color": "lightblue"},
                        {"range": [50, 80], "color": "yellow"},
                        {"range": [80, 100], "color": "orange"},
                    ],
                },
            )
        )

        fig.update_layout(height=250, margin={"l": 20, "r": 20, "t": 50, "b": 20}, font={"size": 12})
        st.plotly_chart(fig, use_container_width=True)

        st.metric("Light Level", f"{brightness_percent:.1f}%", delta=f"{brightness:.1f} lux")
    else:
        st.warning("⚠️ No brightness data")


def _show_pressure_gauge(pressure: float, config: Dict, i18n):
    """Display air pressure as OMF-style gauge"""
    title_text = i18n.t("ccu_overview.sensor_data.current_pressure")
    st.subheader(f"🌡️ {title_text}")

    if pressure is not None:
        # Normalize pressure to percentage
        pressure_percent = normalize_pressure(pressure, config)
        pressure_config = config.get("pressure", {})
        min_pressure = pressure_config.get("min", 900.0)
        max_pressure = pressure_config.get("max", 1100.0)

        # Create Plotly gauge
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=pressure,
                number={"suffix": " hPa"},
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": f"Range: {min_pressure}-{max_pressure} hPa"},
                gauge={
                    "axis": {"range": [min_pressure, max_pressure]},
                    "bar": {"color": "darkgreen"},
                    "steps": [
                        {
                            "range": [min_pressure, min_pressure + (max_pressure - min_pressure) * 0.4],
                            "color": "lightblue",
                        },
                        {
                            "range": [
                                min_pressure + (max_pressure - min_pressure) * 0.4,
                                min_pressure + (max_pressure - min_pressure) * 0.6,
                            ],
                            "color": "lightgreen",
                        },
                        {
                            "range": [min_pressure + (max_pressure - min_pressure) * 0.6, max_pressure],
                            "color": "lightyellow",
                        },
                    ],
                },
            )
        )

        fig.update_layout(height=250, margin={"l": 20, "r": 20, "t": 50, "b": 20}, font={"size": 12})
        st.plotly_chart(fig, use_container_width=True)

        st.metric("Fill Level", f"{pressure_percent:.1f}%")
    else:
        st.warning("⚠️ No pressure data")


def _show_iaq_badge(iaq: float, config: Dict, i18n):
    """Display IAQ as traffic light badge"""
    air_quality_label = i18n.t("ccu_overview.sensor_data.air_quality_label")
    st.subheader(f"🌬️ {air_quality_label}")

    if iaq is not None:
        # Get IAQ information
        level, color, label = get_iaq_info(iaq, config)

        # Display as colored badge
        st.markdown(
            f"""
            <div style="padding: 20px; background-color: {color}; border-radius: 10px; text-align: center; color: white; margin: 20px 0;">
                <h1 style="margin: 0; color: white;">{iaq:.0f}</h1>
                <h3 style="margin: 10px 0; color: white;">{label}</h3>
                <p style="margin: 0; color: white; font-size: 14px;">Indoor Air Quality Index</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Show threshold information
        thresholds = config.get("iaq", {}).get("thresholds", {})
        st.caption(
            f"Thresholds: Good ≤{thresholds.get('good', 50)}, "
            f"Moderate ≤{thresholds.get('moderate', 100)}, "
            f"Unhealthy ≤{thresholds.get('unhealthy', 150)}"
        )
    else:
        st.warning("⚠️ No IAQ data")


def _format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return str(timestamp)
    except Exception:
        return str(timestamp)


def _refresh_sensor_data():
    """Refresh sensor data"""
    logger.info("🔄 Refreshing sensor data")
    request_refresh("sensor_data_refresh")
    st.success("✅ Sensor data refresh requested")


def _show_sensor_statistics(ccu_gateway: CcuGateway):
    """Show sensor statistics"""
    logger.info("📊 Showing sensor statistics")
    st.info("📊 Sensor statistics feature - coming soon")


def _clear_sensor_history(ccu_gateway: CcuGateway):
    """Clear sensor history"""
    logger.info("🗑️ Clearing sensor history")
    st.info("🗑️ Clear sensor history feature - coming soon")
