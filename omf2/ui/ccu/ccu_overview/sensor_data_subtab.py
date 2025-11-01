#!/usr/bin/env python3
"""
CCU Overview - Sensor Data Subtab (OMF-Style)
Real-time sensor data visualization with normalized displays and IAQ traffic light
Uses sensors_display_utils for normalization and configuration
"""

import base64
import math
from datetime import datetime
from typing import Dict

import plotly.graph_objects as go
import streamlit as st

from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.sensor_manager import get_ccu_sensor_manager
from omf2.common.logger import get_logger
from omf2.ui.ccu.sensors_display_utils import (
    get_aq_info,
    get_iaq_info,
    load_sensor_display_config,
    normalize_aq,
    normalize_humidity,
)
from omf2.ui.common.symbols import UISymbols

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

        # Header with heading SVG (fallback to emoji)
        try:
            from omf2.assets.heading_icons import get_svg_inline

            icon_html = get_svg_inline("SENSOR_DATA", size_px=32) or ""
            st.markdown(
                f"<h2 style='margin-bottom: 0.25rem; display:flex; align-items:center; gap:8px;'>{icon_html} {i18n.t('ccu_overview.sensor_data.title')}</h2>",
                unsafe_allow_html=True,
            )
        except Exception:
            st.header(f"{UISymbols.get_functional_icon('sensor_data')} {i18n.t('ccu_overview.sensor_data.title')}")
        subtitle_text = i18n.t("ccu_overview.sensor_data.subtitle")
        st.markdown(subtitle_text)

        # Controls section removed (non-implemented features)

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
            "aq": bme680_data.get("aq_score"),  # Air Quality Score (0-5)
            "brightness": ldr_data.get("light"),  # Note: might need conversion from % to lux
            "timestamp": bme680_data.get("timestamp", datetime.now().isoformat()),
        }

    # Return default demo values if no data available so panels always render
    now_iso = datetime.now().isoformat()
    return {
        "temperature": 22.0,
        "humidity": 50.0,
        "pressure": 1013.0,
        "iaq": 75.0,
        "aq": 2.5,
        "brightness": 1000.0,
        "timestamp": now_iso,
        "init_defaults": True,
    }


def _show_sensor_panels(ccu_gateway: CcuGateway, config: Dict, i18n):
    """Display sensor panels with OMF-style visualization"""
    logger.info("🌡️ Rendering Sensor Panels (OMF-Style)")

    try:
        # Get latest sensor values
        sensor_values = get_latest_sensor_values()

        # Check if we have any data
        has_data = any(v is not None for k, v in sensor_values.items() if k not in ["timestamp", "init_defaults"])

        if has_data:
            live_data_text = i18n.t("ccu_overview.sensor_data.live_data_available")
            timestamp_text = None
            if sensor_values.get("timestamp"):
                timestamp_text = _format_timestamp(sensor_values.get("timestamp"))

            # Show live data status + last update in one info box
            if timestamp_text:
                st.info(f"✅ **{live_data_text}** | ⏰ **Last update:** {timestamp_text}")
            else:
                st.success(f"✅ **{live_data_text}**")
        else:
            # Initialized defaults info
            init_msg = i18n.t("ccu_overview.sensor_data.initialized_defaults")
            st.info(f"ℹ️ {init_msg}")

        # Row 1: Temperature + Humidity + IAQ (2:2:1 ratio)
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            _show_temperature_gauge(sensor_values.get("temperature"), config, i18n)

        with col2:
            _show_humidity_gauge(sensor_values.get("humidity"), config, i18n)

        with col3:
            _show_iaq_badge(sensor_values.get("iaq"), config, i18n)

        st.divider()

        # Row 2: Pressure + Brightness + AQ (2:2:1 ratio)
        col4, col5, col6 = st.columns([2, 2, 1])

        with col4:
            _show_pressure_gauge(sensor_values.get("pressure"), config, i18n)

        with col5:
            _show_brightness_gauge(sensor_values.get("brightness"), config, i18n)

        with col6:
            _show_aq_bar_chart(sensor_values.get("aq"), config, i18n)

        st.divider()

        # Row 3: Camera (if available)

        # Camera section (restored from e314cf8)
        sensor_manager = get_ccu_sensor_manager()
        sensor_data = sensor_manager.get_sensor_data()
        cam_data = sensor_data.get("/j1/txt/1/i/cam", {}) if sensor_data else {}
        _show_camera_section(cam_data, ccu_gateway, i18n)

    except Exception as e:
        logger.error(f"❌ Error displaying sensor panels: {e}")
        st.error(f"❌ Error displaying sensor data: {e}")


def _show_temperature_gauge(temperature: float, config: Dict, i18n):
    """Display temperature as OMF-style gauge with normalization"""
    title_text = i18n.t("ccu_overview.sensor_data.current_temperature")
    st.markdown(f"<h3 style='text-align: center;'>🌡️ {title_text}</h3>", unsafe_allow_html=True)

    if temperature is not None:
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

        # Show normalized percentage - REMOVED (redundant)
    else:
        st.warning("⚠️ No temperature data")


def _show_humidity_gauge(humidity: float, config: Dict, i18n):
    """Display humidity as OMF-style gauge (already 0-100%)"""
    title_text = i18n.t("ccu_overview.sensor_data.current_humidity")
    st.markdown(f"<h3 style='text-align: center;'>💧 {title_text}</h3>", unsafe_allow_html=True)

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

        # Show normalized percentage - REMOVED (redundant)
    else:
        st.warning("⚠️ No humidity data")


def _show_brightness_gauge(brightness: float, config: Dict, i18n):
    """Display brightness as OMF-style gauge with logarithmic scale"""
    title_text = i18n.t("ccu_overview.sensor_data.current_light")
    st.markdown(f"<h3 style='text-align: center;'>💡 {title_text}</h3>", unsafe_allow_html=True)

    if brightness is not None:
        # Calculate logarithmic percentage for gauge display
        max_lux = config.get("brightness", {}).get("max_lux", 65000.0)
        log_percent = (math.log(1 + brightness) / math.log(1 + max_lux)) * 100

        # Create Plotly gauge with logarithmic percentage scale
        # Use mode="gauge" (without "number") to hide default number, then add custom annotation
        fig = go.Figure(
            go.Indicator(
                mode="gauge",  # Gauge only, no automatic number display
                value=log_percent,  # Use logarithmic percentage for gauge position
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": f"Brightness (max: {max_lux} lux)"},
                gauge={
                    "axis": {"range": [0, 100]},  # Scale from 0 to 100% (logarithmic)
                    "bar": {"color": "gold"},
                    "steps": [
                        {"range": [0, 5], "color": "darkblue", "name": "Dunkel, Nacht"},
                        {"range": [5, 15], "color": "navy", "name": "Innenraum, gedämpft"},
                        {"range": [15, 30], "color": "lightblue", "name": "Normale Raumbeleuchtung"},
                        {"range": [30, 60], "color": "yellow", "name": "Helles Zimmer"},
                        {"range": [60, 80], "color": "orange", "name": "Draußen, bewölkt"},
                        {"range": [80, 100], "color": "red", "name": "Sonnig, pralle Sonne"},
                    ],
                },
            )
        )

        # Add annotation to show absolute lux value in center of gauge
        fig.add_annotation(
            x=0.5,
            y=0.5,
            text=f"{brightness:.0f} lux",
            showarrow=False,
            font={"size": 24, "color": "black", "family": "Arial Black"},
            xref="paper",
            yref="paper",
            bgcolor="rgba(255,255,255,0.8)",
            bordercolor="rgba(0,0,0,0)",
            borderpad=4,
        )

        fig.update_layout(height=250, margin={"l": 20, "r": 20, "t": 50, "b": 20}, font={"size": 12})

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("⚠️ No brightness data")


def _show_pressure_gauge(pressure: float, config: Dict, i18n):
    """Display air pressure as OMF-style gauge"""
    title_text = i18n.t("ccu_overview.sensor_data.current_pressure")
    st.markdown(f"<h3 style='text-align: center;'>🌡️ {title_text}</h3>", unsafe_allow_html=True)

    if pressure is not None:
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

        # Show normalized percentage - REMOVED (redundant)
    else:
        st.warning("⚠️ No pressure data")


def _show_iaq_badge(iaq: float, config: Dict, i18n):
    """Display IAQ as traffic light (three-block system without legend)"""
    air_quality_label = i18n.t("ccu_overview.sensor_data.air_quality_label")
    st.markdown(f"<h3 style='text-align: center;'>🌬️ {air_quality_label}</h3>", unsafe_allow_html=True)

    if iaq is not None:
        # Get IAQ information
        level, color, label = get_iaq_info(iaq, config)

        # Create centered layout for IAQ display
        col1, col2, col3 = st.columns([1, 3, 1])

        with col2:  # Center column for content
            # Three-Block Traffic Light using Streamlit components
            st.markdown("**Status:**")

            # Determine which block to highlight based on IAQ value
            if iaq <= 50:
                # Good: Bottom block green
                st.markdown("⚪")  # Empty top
                st.markdown("⚪")  # Empty middle
                st.markdown("🟢")  # Active bottom
            elif iaq <= 100:
                # Moderate: Middle block yellow
                st.markdown("⚪")  # Empty top
                st.markdown("🟡")  # Active middle
                st.markdown("⚪")  # Empty bottom
            else:
                # Unhealthy: Top block red
                st.markdown("🔴")  # Active top
                st.markdown("⚪")  # Empty middle
                st.markdown("⚪")  # Empty bottom

        # Show IAQ info
        st.caption(f"IAQ: {iaq:.0f} - {label}")
    else:
        st.warning("⚠️ No IAQ data")


def _show_aq_bar_chart(aq_value: float, config: Dict, i18n):
    """Display AQ (Air Quality Score) as bar chart (0-5 scale)"""
    title_text = i18n.t("ccu_overview.sensor_data.current_aq")
    st.markdown(f"<h3 style='text-align: center;'>📊 {title_text}</h3>", unsafe_allow_html=True)

    if aq_value is not None:
        # Get AQ information
        level, color, label = get_aq_info(aq_value, config)

        # Create centered layout for AQ Score display
        col1, col2, col3 = st.columns([1, 3, 1])

        with col2:  # Center column for content
            # Vertical Bar Chart using Streamlit components
            st.markdown("**Score:**")

            # Create vertical bar representation (continuous bar from bottom to top)
            aq_percent = normalize_aq(aq_value, config)

            # Display scale markers
            st.markdown("**5**")

            # Create continuous vertical bar using HTML/CSS
            st.markdown(
                f"""
                <div style="background-color: #f0f0f0; border-radius: 10px; width: 20px; height: 100px; position: relative; overflow: hidden; margin: 5px auto;">
                    <div style="background-color: {color}; width: 100%; height: {aq_percent:.1f}%; border-radius: 10px; position: absolute; bottom: 0; transition: height 0.3s ease;"></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            st.markdown("**0**")
            # REMOVED redundant percentage display

        # Show AQ score info
        st.caption(f"AQ Score: {aq_value:.1f}/5.0 - {label}")
    else:
        st.warning("⚠️ No AQ data")


def _format_timestamp(timestamp: str) -> str:
    """Format timestamp for display"""
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        return str(timestamp)
    except Exception:
        return str(timestamp)


# Removed refresh/statistics/history helpers as the Controls section was removed


def _show_camera_section(cam_data, ccu_gateway: CcuGateway, i18n):
    """Zeigt Kamera-Bild und Steuerung nebeneinander (restored from e314cf8)"""
    # Section-level heading removed; headings shown per column

    # Kamera-Bild und Steuerung nebeneinander
    col_camera, col_controls = st.columns([2, 1])

    with col_camera:
        # Kamera-Bild anzeigen
        _show_camera_image_panel(cam_data, i18n)

    with col_controls:
        st.subheader(i18n.t("ccu_overview.sensor_data.camera_control") if i18n else "Camera Control")
        # Kamera-Steuerung mit separater Schrittweite
        _show_camera_control_panel(ccu_gateway, i18n)


def _show_camera_control_panel(ccu_gateway: CcuGateway, i18n):
    """Zeigt das Kamera-Steuerungs-Panel mit 3x3 Grid und Center-Control (restored from e314cf8)"""

    # Schrittweite-Einstellung (separat)
    step_size_text = i18n.t("ccu_overview.sensor_data.camera_step_size")
    step_size = st.number_input(
        f"{step_size_text}",
        min_value=1,
        max_value=90,
        value=st.session_state.get("camera_step_size", 10),
        step=1,
        key="camera_step_size_input",
    )
    st.session_state["camera_step_size"] = step_size

    st.divider()

    # 3x3 Grid für Kamera-Controls
    # Zeile 1: Leer, HOCH, Leer
    col1, col2, col3 = st.columns(3)

    with col1:
        st.empty()  # Leer

    with col2:
        up_text = i18n.t("ccu_overview.sensor_data.camera_up")
        if st.button(f"⬆️ {up_text}", use_container_width=True, key="camera_up"):
            _move_camera(ccu_gateway, "relmove_up", step_size, i18n)

    with col3:
        st.empty()  # Leer

    # Zeile 2: LINKS, ZENTRIEREN, RECHTS
    col4, col5, col6 = st.columns(3)

    with col4:
        left_text = i18n.t("ccu_overview.sensor_data.camera_left")
        if st.button(f"⬅️ {left_text}", use_container_width=True, key="camera_left"):
            _move_camera(ccu_gateway, "relmove_left", step_size, i18n)

    with col5:
        center_text = i18n.t("ccu_overview.sensor_data.camera_center")
        if st.button(f"🎯 {center_text}", use_container_width=True, key="camera_center"):
            _move_camera(ccu_gateway, "center", 0, i18n)

    with col6:
        right_text = i18n.t("ccu_overview.sensor_data.camera_right")
        if st.button(f"➡️ {right_text}", use_container_width=True, key="camera_right"):
            _move_camera(ccu_gateway, "relmove_right", step_size, i18n)

    # Zeile 3: Leer, RUNTER, Leer
    col7, col8, col9 = st.columns(3)

    with col7:
        st.empty()  # Leer

    with col8:
        down_text = i18n.t("ccu_overview.sensor_data.camera_down")
        if st.button(f"⬇️ {down_text}", use_container_width=True, key="camera_down"):
            _move_camera(ccu_gateway, "relmove_down", step_size, i18n)

    with col9:
        st.empty()  # Leer

    st.divider()

    # Foto-Button separat
    photo_text = i18n.t("ccu_overview.sensor_data.camera_photo")
    if st.button(f"📷 {photo_text}", use_container_width=True, key="camera_photo"):
        _take_camera_photo(ccu_gateway, i18n)


def _show_camera_image_panel(cam_data, i18n):
    """Zeigt das Kamera-Bild-Panel mit Base64-dekodierten Bildern (kompakte Größe) (restored from e314cf8)"""
    title_text = i18n.t("ccu_overview.sensor_data.camera_image")
    st.subheader(f"📸 {title_text}")

    if cam_data and cam_data.get("image_data"):
        image_data = cam_data.get("image_data", "")
        timestamp = cam_data.get("timestamp", "")
        message_count = cam_data.get("message_count", 0)

        if image_data:
            _display_base64_image_compact(image_data, timestamp, message_count, i18n)
        else:
            no_camera_data_text = i18n.t("ccu_overview.sensor_data.no_camera_data")
            st.warning(f"⚠️ {no_camera_data_text}")
    else:
        loading_text = i18n.t("ccu_overview.sensor_data.camera_loading")
        st.info(f"📸 {loading_text}")

        # Local placeholder via Asset Manager for offline consistency
        try:
            from omf2.assets import get_asset_manager

            asset_manager = get_asset_manager()
            placeholder_path = asset_manager.get_module_icon_path("CAMERA_PLACEHOLDER")
            if placeholder_path:
                st.image(placeholder_path, caption=i18n.t("ccu_overview.sensor_data.camera_image"), width=300)
            else:
                st.caption("Camera placeholder not available")
        except Exception:
            st.caption("Camera placeholder not available")


def _display_base64_image_compact(base64_data: str, timestamp: str, message_count: int, i18n):
    """Zeigt Base64-dekodiertes Bild in Streamlit (kompakte Größe) (restored from e314cf8)"""
    try:
        # Extract image format from data URL
        if base64_data.startswith("data:image/"):
            # Format: data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD...
            format_part = base64_data.split(";")[0]
            image_format = format_part.split("/")[-1]
            # Extract base64 part after comma
            base64_part = base64_data.split(",")[1]
        else:
            # Assume JPEG if no data URL format
            image_format = "jpeg"
            base64_part = base64_data

        # Base64 dekodieren
        image_bytes = base64.b64decode(base64_part)

        # Format timestamp for caption
        formatted_time = ""
        if timestamp:
            try:
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                    formatted_time = f" {dt.strftime('%H:%M:%S')}"
                else:
                    formatted_time = f" {str(timestamp)}"
            except Exception:
                formatted_time = f" {str(timestamp)}"

        # Bild in kompakter Größe anzeigen mit Zeitstempel in Caption
        caption_text = f"📸 Kamera-Bild ({image_format.upper()}){formatted_time}"
        st.image(image_bytes, caption=caption_text, width=400)

    except Exception as e:
        logger.error(f"❌ Fehler beim Dekodieren des Kamera-Bildes: {e}")
        st.error(f"❌ Fehler beim Dekodieren des Kamera-Bildes: {e}")


def _move_camera(ccu_gateway: CcuGateway, command: str, degree: int, i18n):
    """Bewegt die Kamera um angegebene Grad (restored from e314cf8)"""
    try:
        # Kamera-Befehl über Gateway senden (Gateway-Pattern)
        topic = "/j1/txt/1/o/ptu"
        payload = {"ts": datetime.now().isoformat() + "Z", "cmd": command, "degree": degree}

        # Send via Gateway (Gateway-Pattern)
        success = ccu_gateway.publish_message(topic, payload)

        if success:
            st.success(f"✅ Kamera bewegt: {command} {degree}°")
            logger.info(f"📸 Camera moved: {command} {degree}°")
        else:
            st.error(f"❌ Fehler beim Bewegen der Kamera: {command}")

    except Exception as e:
        logger.error(f"❌ Fehler beim Bewegen der Kamera: {e}")
        st.error(f"❌ Fehler beim Bewegen der Kamera: {e}")


def _take_camera_photo(ccu_gateway: CcuGateway, i18n):
    """Macht ein Foto mit der Kamera (restored from e314cf8)"""
    try:
        # Kamera-Foto-Befehl über Gateway senden (Gateway-Pattern)
        topic = "/j1/txt/1/o/ptu"
        payload = {"ts": datetime.now().isoformat() + "Z", "cmd": "photo"}

        # Send via Gateway (Gateway-Pattern)
        success = ccu_gateway.publish_message(topic, payload)

        if success:
            success_text = i18n.t("ccu_overview.sensor_data.photo_triggered")
            st.success(f"✅ {success_text}")
            logger.info("📸 Camera photo triggered")
        else:
            error_text = i18n.t("ccu_overview.sensor_data.photo_error")
            st.error(f"❌ {error_text}")

    except Exception as e:
        logger.error(f"❌ Fehler beim Auslösen des Kamera-Fotos: {e}")
        st.error(f"❌ Fehler beim Auslösen des Kamera-Fotos: {e}")
