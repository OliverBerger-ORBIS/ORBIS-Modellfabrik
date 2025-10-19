#!/usr/bin/env python3
"""
CCU Overview - Sensor Data Subtab (Refactored)
Real-time Sensordaten von BME680 und LDR mit Kamera-Steuerung
Business Logic über SensorManager (Gateway-Pattern)
"""

import base64
from datetime import datetime

import plotly.graph_objects as go
import streamlit as st

from omf2.assets.asset_manager import get_asset_manager
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.sensor_manager import get_ccu_sensor_manager
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_sensor_data_subtab(ccu_gateway: CcuGateway, registry_manager, asset_manager):
    """Render Sensor Data Subtab - Business Logic über SensorManager"""
    logger.info("🌡️ Rendering Sensor Data Subtab")

    # I18n Manager aus Session State holen
    i18n = st.session_state.get("i18n_manager")
    if not i18n:
        logger.error("❌ I18n Manager not found in session state")
        return

    try:
        # Header mit UISymbols
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

        # Sensor Panels mit Business Logic über SensorManager
        _show_sensor_panels(ccu_gateway, registry_manager)

    except Exception as e:
        logger.error(f"❌ Sensor Data Subtab error: {e}")
        st.error(f"❌ Sensor Data Subtab failed: {e}")
        i18n_fallback = st.session_state.get("i18n_manager")
        if i18n_fallback:
            st.info(f"💡 {i18n_fallback.t('common.status.under_development')}")


def _show_sensor_panels(ccu_gateway: CcuGateway, registry_manager):
    """Zeigt die Sensordaten-Panels mit echten MQTT-Daten - Business Logic über SensorManager"""
    logger.info("🌡️ Rendering Sensor Panels")

    # I18n Manager holen
    i18n = st.session_state.get("i18n_manager")
    if not i18n:
        logger.error("❌ I18n Manager not found in session state")
        return

    try:
        # NEU: Business Logic über SensorManager State-Holder (Business-Manager Pattern)
        sensor_manager = get_ccu_sensor_manager()
        sensor_data = sensor_manager.get_sensor_data()  # Liest aus State-Holder

        # Zeige Sensor-Status
        if sensor_data:
            live_data_text = i18n.t("ccu_overview.sensor_data.live_data_available")
            st.success(f"✅ **{len(sensor_data)} {live_data_text}**")
            logger.info(f"Sensor data processed: {len(sensor_data)} topics")
        else:
            no_data_text = i18n.t("ccu_overview.sensor_data.no_data")
            st.warning(f"⚠️ {no_data_text}")

        # Zeige Sensor-Panels mit verarbeiteten Daten
        bme680_data = sensor_data.get("/j1/txt/1/i/bme680", {}) if sensor_data else {}
        ldr_data = sensor_data.get("/j1/txt/1/i/ldr", {}) if sensor_data else {}
        cam_data = sensor_data.get("/j1/txt/1/i/cam", {}) if sensor_data else {}

        # Sensor-Daten in Zeilen-Anordnung
        # Zeile 1: Temperatur + Luftqualität + Luftfeuchtigkeit
        col1, col2, col3 = st.columns(3)

        with col1:
            _show_temperature_panel(bme680_data, i18n)

        with col2:
            _show_air_quality_panel(bme680_data, i18n)

        with col3:
            _show_humidity_panel(bme680_data, i18n)

        st.divider()

        # Zeile 2: Luftdruck + Lichtstärke
        col4, col5 = st.columns(2)

        with col4:
            _show_pressure_panel(bme680_data, i18n)

        with col5:
            _show_light_panel(ldr_data, i18n)

        st.divider()

        # 6. Kamera-Bild und Steuerung (nebeneinander)
        _show_camera_section(cam_data, ccu_gateway, i18n)
        st.divider()

    except Exception as e:
        logger.error(f"❌ Fehler beim Laden der Sensordaten: {e}")
        st.error(f"❌ Fehler beim Laden der Sensordaten: {e}")

        # Fallback: Zeige leere Panels in Zeilen-Anordnung
        # Zeile 1: Temperatur + Luftqualität + Luftfeuchtigkeit
        col1, col2, col3 = st.columns(3)

        with col1:
            _show_temperature_panel({}, i18n)

        with col2:
            _show_air_quality_panel({}, i18n)

        with col3:
            _show_humidity_panel({}, i18n)

        st.divider()

        # Zeile 2: Luftdruck + Lichtstärke
        col4, col5 = st.columns(2)

        with col4:
            _show_pressure_panel({}, i18n)

        with col5:
            _show_light_panel({}, i18n)

        st.divider()

        # Kamera-Sektion
        _show_camera_section({}, ccu_gateway, i18n)


def _show_temperature_panel(bme680_data, i18n):
    """Zeigt das Temperatur-Panel mit verarbeiteten BME680-Daten"""
    title_text = i18n.t("ccu_overview.sensor_data.current_temperature")
    st.subheader(f"🌡️ {title_text}")

    if bme680_data and bme680_data.get("temperature") is not None:
        temperature = bme680_data.get("temperature", 0.0)
        timestamp = bme680_data.get("timestamp", "")
        message_count = bme680_data.get("message_count", 0)

        # Thermometer-Gauge mit Plotly
        col1, col2 = st.columns([2, 1])

        with col1:
            # SVG-Thermometer mit Füllstand und Farbskala
            st.markdown("**🌡️ Temperatur-Thermometer:**")

            # Asset Manager für SVG-Thermometer
            asset_manager = get_asset_manager()
            thermometer_svg_path = asset_manager.svgs_dir / "thermometer_complete.svg"
            gradient_svg_path = asset_manager.svgs_dir / "thermometer_color_gradient.svg"

            if thermometer_svg_path.exists() and gradient_svg_path.exists():
                # SVG-Thermometer mit Füllstand anzeigen
                with open(thermometer_svg_path, encoding="utf-8") as svg_file:
                    svg_content = svg_file.read()

                with open(gradient_svg_path, encoding="utf-8") as gradient_file:
                    gradient_content = gradient_file.read()

                # Berechne Füllstand (0-100% für -30°C bis 60°C)
                max(0, min(100, ((temperature + 30) / 90) * 100))

                # SVG-Größe anpassen
                svg_content = svg_content.replace("<svg", '<svg width="150" height="250"')
                gradient_content = gradient_content.replace("<svg", '<svg width="150" height="250"')

                # Einfache SVG-Thermometer-Anzeige (ohne komplexe Überlagerungen)
                st.markdown(
                    f"""
                <div style="position: relative; display: inline-block;">
                    {svg_content}
                    <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 18px; font-weight: bold; color: #333; text-align: center; background: white; padding: 5px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        {temperature:.1f}°C
                    </div>
                </div>
                """,
                    unsafe_allow_html=True,
                )
            else:
                # Fallback: Einfacher Fortschrittsbalken
                normalized_temp = max(0, min(1, (temperature + 30) / 90))  # -30°C bis 60°C = 90°C Spanne
                st.progress(normalized_temp)
                st.caption("Bereich: -30°C bis 60°C")

        with col2:
            # Textuelle Informationen
            temp_label = i18n.t("ccu_overview.sensor_data.temperature_label")
            st.metric(temp_label, f"{temperature:.1f}°C")

            # Zeitstempel
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        formatted_time = dt.strftime("%H:%M:%S")
                    else:
                        formatted_time = str(timestamp)
                except Exception:
                    formatted_time = str(timestamp)
                messages_label = i18n.t("ccu_overview.sensor_data.messages_count")
                st.caption(f"{formatted_time} ({message_count} {messages_label})")

    else:
        no_data_text = i18n.t("ccu_overview.sensor_data.no_bme680_data")
        st.warning(f"⚠️ {no_data_text}")


def _show_humidity_panel(bme680_data, i18n):
    """Zeigt das Luftfeuchtigkeit-Panel mit verarbeiteten BME680-Daten"""
    title_text = i18n.t("ccu_overview.sensor_data.current_humidity")
    st.subheader(f"💧 {title_text}")

    if bme680_data and bme680_data.get("humidity") is not None:
        humidity = bme680_data.get("humidity", 0.0)
        timestamp = bme680_data.get("timestamp", "")
        message_count = bme680_data.get("message_count", 0)

        # Kreisförmiger Gauge für Luftfeuchtigkeit
        col1, col2 = st.columns([2, 1])

        with col1:
            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=humidity,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "% r.H."},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "darkblue"},
                        "steps": [
                            {"range": [0, 30], "color": "lightblue"},
                            {"range": [30, 60], "color": "lightgreen"},
                            {"range": [60, 80], "color": "yellow"},
                            {"range": [80, 100], "color": "orange"},
                        ],
                        "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 90},
                    },
                )
            )

            fig.update_layout(height=300, margin={"l": 20, "r": 20, "t": 40, "b": 20}, font={"size": 14})

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Textuelle Informationen
            humidity_label = i18n.t("ccu_overview.sensor_data.humidity_label")
            st.metric(humidity_label, f"{humidity:.1f}%")

            # Zeitstempel
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        formatted_time = dt.strftime("%H:%M:%S")
                    else:
                        formatted_time = str(timestamp)
                except Exception:
                    formatted_time = str(timestamp)
                messages_label = i18n.t("ccu_overview.sensor_data.messages_count")
                st.caption(f"{formatted_time} ({message_count} {messages_label})")

    else:
        no_data_text = i18n.t("ccu_overview.sensor_data.no_bme680_data")
        st.warning(f"⚠️ {no_data_text}")


def _show_pressure_panel(bme680_data, i18n):
    """Zeigt das Luftdruck-Panel mit verarbeiteten BME680-Daten"""
    title_text = i18n.t("ccu_overview.sensor_data.current_pressure")
    st.subheader(f"🌬️ {title_text}")

    if bme680_data and bme680_data.get("pressure") is not None:
        pressure = bme680_data.get("pressure", 0.0)
        timestamp = bme680_data.get("timestamp", "")
        message_count = bme680_data.get("message_count", 0)

        # Kreisförmiger Gauge für Luftdruck
        col1, col2 = st.columns([2, 1])

        with col1:
            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=pressure,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "hPa"},
                    gauge={
                        "axis": {"range": [900, 1100]},
                        "bar": {"color": "darkgreen"},
                        "steps": [
                            {"range": [900, 940], "color": "lightcoral"},
                            {"range": [940, 980], "color": "lightblue"},
                            {"range": [980, 1020], "color": "lightgreen"},
                            {"range": [1020, 1060], "color": "yellow"},
                            {"range": [1060, 1100], "color": "orange"},
                        ],
                        "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 1080},
                    },
                )
            )

            fig.update_layout(height=300, margin={"l": 20, "r": 20, "t": 40, "b": 20}, font={"size": 14})

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Textuelle Informationen
            pressure_label = i18n.t("ccu_overview.sensor_data.pressure_label")
            st.metric(pressure_label, f"{pressure:.1f} hPa")

            # Zeitstempel
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        formatted_time = dt.strftime("%H:%M:%S")
                    else:
                        formatted_time = str(timestamp)
                except Exception:
                    formatted_time = str(timestamp)
                messages_label = i18n.t("ccu_overview.sensor_data.messages_count")
                st.caption(f"{formatted_time} ({message_count} {messages_label})")

    else:
        no_data_text = i18n.t("ccu_overview.sensor_data.no_bme680_data")
        st.warning(f"⚠️ {no_data_text}")


def _show_air_quality_panel(bme680_data, i18n):
    """Zeigt das Luftqualität-Panel mit verarbeiteten BME680-Daten"""
    title_text = i18n.t("ccu_overview.sensor_data.current_air_quality")
    st.subheader(f"🌫️ {title_text}")

    if bme680_data and bme680_data.get("air_quality") is not None:
        air_quality = bme680_data.get("air_quality", 0.0)
        timestamp = bme680_data.get("timestamp", "")
        message_count = bme680_data.get("message_count", 0)

        # Farbige Indikatoren für Luftqualität (wie im Dashboard-Bild)
        col1, col2 = st.columns([2, 1])

        with col1:
            # Drei vertikale Indikatoren (gestapelt)
            st.markdown("**IAQ Indikatoren:**")

            # Bestimme Farbe basierend auf IAQ-Wert
            if air_quality <= 50:
                color = "green"
                status = "Gut"
            elif air_quality <= 100:
                color = "yellow"
                status = "Mäßig"
            elif air_quality <= 150:
                color = "orange"
                status = "Ungesund"
            else:
                color = "red"
                status = "Sehr ungesund"

            # Drei Indikatoren (wie im Dashboard-Bild)
            indicator_height = 60
            st.markdown(
                f"""
            <div style="display: flex; flex-direction: column; gap: 5px; margin: 10px 0;">
                <div style="width: 100%; height: {indicator_height}px; background-color: #e0e0e0; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #666;">
                    <span style="font-size: 12px;">Inaktiv</span>
                </div>
                <div style="width: 100%; height: {indicator_height}px; background-color: #e0e0e0; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #666;">
                    <span style="font-size: 12px;">Inaktiv</span>
                </div>
                <div style="width: 100%; height: {indicator_height}px; background-color: {color}; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold;">
                    <span style="font-size: 12px;">{status}</span>
                </div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        with col2:
            # Textuelle Informationen
            air_quality_label = i18n.t("ccu_overview.sensor_data.air_quality_label")
            st.metric(air_quality_label, f"{air_quality:.0f}")
            st.metric("Accuracy", "3")

            # Zeitstempel
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        formatted_time = dt.strftime("%H:%M:%S")
                    else:
                        formatted_time = str(timestamp)
                except Exception:
                    formatted_time = str(timestamp)
                messages_label = i18n.t("ccu_overview.sensor_data.messages_count")
                st.caption(f"{formatted_time} ({message_count} {messages_label})")

    else:
        no_data_text = i18n.t("ccu_overview.sensor_data.no_bme680_data")
        st.warning(f"⚠️ {no_data_text}")


def _show_light_panel(ldr_data, i18n):
    """Zeigt das Licht-Panel mit verarbeiteten LDR-Daten"""
    title_text = i18n.t("ccu_overview.sensor_data.current_light")
    st.subheader(f"💡 {title_text}")

    if ldr_data and ldr_data.get("light") is not None:
        light = ldr_data.get("light", 0.0)
        timestamp = ldr_data.get("timestamp", "")
        message_count = ldr_data.get("message_count", 0)

        # Kreisförmiger Gauge für Helligkeit
        col1, col2 = st.columns([2, 1])

        with col1:
            fig = go.Figure(
                go.Indicator(
                    mode="gauge+number",
                    value=light,
                    domain={"x": [0, 1], "y": [0, 1]},
                    title={"text": "%"},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "gold"},
                        "steps": [
                            {"range": [0, 20], "color": "darkblue"},
                            {"range": [20, 40], "color": "lightblue"},
                            {"range": [40, 70], "color": "yellow"},
                            {"range": [70, 100], "color": "orange"},
                        ],
                        "threshold": {"line": {"color": "red", "width": 4}, "thickness": 0.75, "value": 90},
                    },
                )
            )

            fig.update_layout(height=300, margin={"l": 20, "r": 20, "t": 40, "b": 20}, font={"size": 14})

            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Textuelle Informationen
            light_label = i18n.t("ccu_overview.sensor_data.light_label")
            st.metric(light_label, f"{light:.1f}%")

            # Zeitstempel
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        formatted_time = dt.strftime("%H:%M:%S")
                    else:
                        formatted_time = str(timestamp)
                except Exception:
                    formatted_time = str(timestamp)
                messages_label = i18n.t("ccu_overview.sensor_data.messages_count")
                st.caption(f"{formatted_time} ({message_count} {messages_label})")

    else:
        no_data_text = i18n.t("ccu_overview.sensor_data.no_bme680_data")
        st.warning(f"⚠️ {no_data_text}")


def _show_camera_section(cam_data, ccu_gateway: CcuGateway, i18n):
    """Zeigt Kamera-Bild und Steuerung nebeneinander"""
    title_text = i18n.t("ccu_overview.sensor_data.camera_control")
    st.subheader(f"📸 {title_text}")

    # Kamera-Bild und Steuerung nebeneinander
    col_camera, col_controls = st.columns([2, 1])

    with col_camera:
        # Kamera-Bild anzeigen
        _show_camera_image_panel(cam_data, i18n)

    with col_controls:
        # Kamera-Steuerung mit separater Schrittweite
        _show_camera_control_panel(ccu_gateway, i18n)


def _show_camera_control_panel(ccu_gateway: CcuGateway, i18n):
    """Zeigt das Kamera-Steuerungs-Panel mit 3x3 Grid und Center-Control"""

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
    """Zeigt das Kamera-Bild-Panel mit Base64-dekodierten Bildern (kompakte Größe)"""
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

        # Placeholder-Bild (kompakte Größe)
        placeholder_url = "https://via.placeholder.com/300x200/CCCCCC/666666?text=Kamera+Placeholder"
        st.image(placeholder_url, caption="Kamera-Bild (Placeholder)", width=300)


def _display_base64_image_compact(base64_data: str, timestamp: str, message_count: int, i18n):
    """Zeigt Base64-dekodiertes Bild in Streamlit (kompakte Größe)"""
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

        # Kompakte Darstellung mit fester Breite
        col1, col2 = st.columns([2, 1])

        with col1:
            # Bild in kompakter Größe anzeigen (max. 400px breit)
            st.image(image_bytes, caption=f"📸 Kamera-Bild ({image_format.upper()})", width=400)

        with col2:
            # Bild-Informationen kompakt anzeigen
            format_label = i18n.t("ccu_overview.sensor_data.image_format_label")
            st.metric(format_label, image_format.upper())

            messages_label = i18n.t("ccu_overview.sensor_data.messages_count")
            st.metric(messages_label, message_count)

            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                        formatted_time = dt.strftime("%H:%M:%S")
                    else:
                        formatted_time = str(timestamp)
                except Exception:
                    formatted_time = str(timestamp)
                timestamp_label = i18n.t("ccu_overview.sensor_data.timestamp_label")
                st.metric(timestamp_label, formatted_time)

    except Exception as e:
        logger.error(f"❌ Fehler beim Dekodieren des Kamera-Bildes: {e}")
        st.error(f"❌ Fehler beim Dekodieren des Kamera-Bildes: {e}")


def _move_camera(ccu_gateway: CcuGateway, command: str, degree: int, i18n):
    """Bewegt die Kamera um angegebene Grad"""
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
    """Macht ein Foto mit der Kamera"""
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


def _refresh_sensor_data():
    """Refresh sensor data - UI Refresh Pattern"""
    logger.info("🔄 Refreshing sensor data")

    i18n = st.session_state.get("i18n_manager")

    try:
        # UI Refresh Pattern (statt st.rerun())
        request_refresh()
        if i18n:
            success_text = i18n.t("ccu_overview.sensor_data.data_refreshed")
            st.success(f"✅ {success_text}")
        logger.info("✅ Sensor data refreshed successfully")
    except Exception as e:
        logger.error(f"❌ Failed to refresh sensor data: {e}")
        st.error(f"❌ Failed to refresh sensor data: {e}")


def _show_sensor_statistics(ccu_gateway: CcuGateway):
    """Show sensor statistics"""

    i18n = st.session_state.get("i18n_manager")

    try:
        sensor_manager = get_ccu_sensor_manager()
        sensor_data = sensor_manager.get_sensor_data()  # Liest aus State-Holder
        stats = sensor_manager.get_sensor_statistics(sensor_data) if sensor_data else {}

        if i18n:
            stats_text = i18n.t("ccu_overview.sensor_data.statistics")
            st.info(f"📊 **{stats_text}**")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            if i18n:
                total_label = i18n.t("ccu_overview.sensor_data.total_sensors")
                st.metric(total_label, stats.get("total_sensors", 0))
            else:
                st.metric("Total Sensors", stats.get("total_sensors", 0))
        with col2:
            st.metric("BME680", "✅" if stats.get("bme680_available") else "❌")
        with col3:
            st.metric("LDR", "✅" if stats.get("ldr_available") else "❌")
        with col4:
            st.metric("Camera", "✅" if stats.get("camera_available") else "❌")

        if stats.get("temperature") is not None:
            st.info(f"🌡️ Temperature: {stats.get('temperature', 0):.1f}°C")
        if stats.get("humidity") is not None:
            st.info(f"💧 Humidity: {stats.get('humidity', 0):.1f}%")
        if stats.get("light") is not None:
            st.info(f"💡 Light: {stats.get('light', 0):.1f} Lux")

    except Exception as e:
        logger.error(f"❌ Failed to show sensor statistics: {e}")
        st.error(f"❌ Failed to show sensor statistics: {e}")


def _clear_sensor_history(ccu_gateway: CcuGateway):
    """Clear sensor message history"""

    i18n = st.session_state.get("i18n_manager")

    try:
        # Clear via Gateway (Gateway-Pattern)
        ccu_gateway.clear_message_history()
        if i18n:
            success_text = i18n.t("ccu_overview.sensor_data.history_cleared")
            st.success(f"✅ {success_text}")
        logger.info("✅ Sensor message history cleared successfully")
    except Exception as e:
        logger.error(f"❌ Failed to clear sensor history: {e}")
        st.error(f"❌ Failed to clear sensor history: {e}")
