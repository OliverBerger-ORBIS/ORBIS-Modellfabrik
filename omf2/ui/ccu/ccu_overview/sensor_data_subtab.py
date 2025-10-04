#!/usr/bin/env python3
"""
CCU Overview - Sensor Data Subtab (Refactored)
Real-time Sensordaten von BME680 und LDR mit Kamera-Steuerung
Business Logic über SensorManager (Gateway-Pattern)
"""

import streamlit as st
import time
import base64
from datetime import datetime
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.sensor_manager import get_ccu_sensor_manager
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols
from omf2.ui.utils.ui_refresh import request_refresh

logger = get_logger(__name__)


def render_sensor_data_subtab(ccu_gateway: CcuGateway, registry_manager):
    """Render Sensor Data Subtab - Business Logic über SensorManager"""
    logger.info("🌡️ Rendering Sensor Data Subtab")
    print("🔍 UI DEBUG: Sensor Data Subtab wird gerendert")
    try:
        # Header mit UISymbols
        st.header(f"{UISymbols.get_functional_icon('sensor_data')} Sensor Data")
        st.markdown("Real-time Sensordaten von BME680, LDR und Kamera mit Gateway-Pattern")
        
        # Sensor Controls
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button(f"{UISymbols.get_status_icon('refresh')} Refresh Data", use_container_width=True, key="sensor_refresh"):
                print("🔍 UI DEBUG: Refresh Button gedrückt!")
                logger.info("🔄 DEBUG: Refresh Sensor Data Button clicked")
                _refresh_sensor_data()
        
        with col2:
            if st.button(f"{UISymbols.get_functional_icon('dashboard')} Show Statistics", use_container_width=True, key="sensor_statistics"):
                _show_sensor_statistics(ccu_gateway)
        
        with col3:
            if st.button(f"{UISymbols.get_functional_icon('settings')} Clear History", use_container_width=True, key="sensor_clear"):
                _clear_sensor_history(ccu_gateway)
        
        st.divider()
        
        # Sensor Panels mit Business Logic über SensorManager
        _show_sensor_panels(ccu_gateway, registry_manager)
        
    except Exception as e:
        logger.error(f"❌ Sensor Data Subtab error: {e}")
        st.error(f"❌ Sensor Data Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def _show_sensor_panels(ccu_gateway: CcuGateway, registry_manager):
    """Zeigt die Sensordaten-Panels mit echten MQTT-Daten - Business Logic über SensorManager"""
    logger.info("🌡️ Rendering Sensor Panels")
    try:
        # NEU: Business Logic über SensorManager State-Holder (Business-Manager Pattern)
        sensor_manager = get_ccu_sensor_manager()
        sensor_data = sensor_manager.get_sensor_data()  # Liest aus State-Holder
        
        # Zeige Sensor-Status
        if sensor_data:
            st.success(f"✅ **{len(sensor_data)} Sensor-Topics mit Live-Daten verfügbar**")
            logger.info(f"Sensor data processed: {len(sensor_data)} topics")
        else:
            st.warning("⚠️ Keine Sensor-Daten verfügbar")
        
        # Zeige Sensor-Panels mit verarbeiteten Daten
        bme680_data = sensor_data.get("/j1/txt/1/i/bme680", {})
        ldr_data = sensor_data.get("/j1/txt/1/i/ldr", {})
        cam_data = sensor_data.get("/j1/txt/1/i/cam", {})
        
        # 1. Temperatur
        _show_temperature_panel(bme680_data)
        st.divider()
        
        # 2. Luftfeuchtigkeit
        _show_humidity_panel(bme680_data)
        st.divider()
        
        # 3. Luftdruck
        _show_pressure_panel(bme680_data)
        st.divider()
        
        # 4. Luftqualität
        _show_air_quality_panel(bme680_data)
        st.divider()
        
        # 5. Lichtsensor
        _show_light_panel(ldr_data)
        st.divider()
        
        # 6. Kamera-Steuerung
        _show_camera_control_panel(ccu_gateway)
        st.divider()
        
        # 7. Kamera-Bild Anzeige
        _show_camera_image_panel(cam_data)
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Laden der Sensordaten: {e}")
        st.error(f"❌ Fehler beim Laden der Sensordaten: {e}")
        
        # Fallback: Zeige leere Panels
        _show_temperature_panel({})
        _show_humidity_panel({})
        _show_pressure_panel({})
        _show_air_quality_panel({})
        _show_light_panel({})
        _show_camera_control_panel(ccu_gateway)


def _show_temperature_panel(bme680_data):
    """Zeigt das Temperatur-Panel mit verarbeiteten BME680-Daten"""
    st.subheader("🌡️ Aktuelle Temperatur")
    
    if bme680_data and bme680_data.get("temperature") is not None:
        temperature = bme680_data.get("temperature", 0.0)
        timestamp = bme680_data.get("timestamp", "")
        message_count = bme680_data.get("message_count", 0)
        
        # Thermometer-Gauge
        st.metric("Temperatur", f"{temperature:.1f}°C")
        
        # Thermometer-Visualisierung (normalisiert auf 0-50°C)
        normalized_temp = max(0, min(1, temperature / 50.0))
        st.progress(normalized_temp)
        
        # Zeitstempel
        if timestamp:
            try:
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%H:%M:%S")
                else:
                    formatted_time = str(timestamp)
            except:
                formatted_time = str(timestamp)
            st.caption(f"{formatted_time} ({message_count} Nachrichten)")
            
    else:
        st.warning("⚠️ Keine BME680-Daten verfügbar")


def _show_humidity_panel(bme680_data):
    """Zeigt das Luftfeuchtigkeit-Panel mit verarbeiteten BME680-Daten"""
    st.subheader("💧 Aktuelle Luftfeuchtigkeit")
    
    if bme680_data and bme680_data.get("humidity") is not None:
        humidity = bme680_data.get("humidity", 0.0)
        timestamp = bme680_data.get("timestamp", "")
        message_count = bme680_data.get("message_count", 0)
        
        # Luftfeuchtigkeit-Gauge
        st.metric("Luftfeuchtigkeit", f"{humidity:.1f}%")
        
        # Luftfeuchtigkeit-Visualisierung (normalisiert auf 0-100%)
        normalized_humidity = max(0, min(1, humidity / 100.0))
        st.progress(normalized_humidity)
        
        # Zeitstempel
        if timestamp:
            try:
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%H:%M:%S")
                else:
                    formatted_time = str(timestamp)
            except:
                formatted_time = str(timestamp)
            st.caption(f"{formatted_time} ({message_count} Nachrichten)")
            
    else:
        st.warning("⚠️ Keine BME680-Daten verfügbar")


def _show_pressure_panel(bme680_data):
    """Zeigt das Luftdruck-Panel mit verarbeiteten BME680-Daten"""
    st.subheader("🌬️ Aktueller Luftdruck")
    
    if bme680_data and bme680_data.get("pressure") is not None:
        pressure = bme680_data.get("pressure", 0.0)
        timestamp = bme680_data.get("timestamp", "")
        message_count = bme680_data.get("message_count", 0)
        
        # Luftdruck-Gauge
        st.metric("Luftdruck", f"{pressure:.1f} hPa")
        
        # Luftdruck-Visualisierung (normalisiert auf 950-1050 hPa)
        normalized_pressure = (pressure - 950) / 100.0
        st.progress(max(0, min(1, normalized_pressure)))
        
        # Zeitstempel
        if timestamp:
            try:
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%H:%M:%S")
                else:
                    formatted_time = str(timestamp)
            except:
                formatted_time = str(timestamp)
            st.caption(f"{formatted_time} ({message_count} Nachrichten)")
            
    else:
        st.warning("⚠️ Keine BME680-Daten verfügbar")


def _show_air_quality_panel(bme680_data):
    """Zeigt das Luftqualität-Panel mit verarbeiteten BME680-Daten"""
    st.subheader("🌫️ Aktuelle Luftqualität")
    
    if bme680_data and bme680_data.get("air_quality") is not None:
        air_quality = bme680_data.get("air_quality", 0.0)
        timestamp = bme680_data.get("timestamp", "")
        message_count = bme680_data.get("message_count", 0)
        
        # Luftqualität-Gauge
        st.metric("Luftqualität", f"{air_quality:.1f} IAQ")
        
        # Luftqualität-Visualisierung (normalisiert auf 0-500 IAQ)
        normalized_air_quality = max(0, min(1, air_quality / 500.0))
        st.progress(normalized_air_quality)
        
        # Zeitstempel
        if timestamp:
            try:
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%H:%M:%S")
                else:
                    formatted_time = str(timestamp)
            except:
                formatted_time = str(timestamp)
            st.caption(f"{formatted_time} ({message_count} Nachrichten)")
            
    else:
        st.warning("⚠️ Keine BME680-Daten verfügbar")


def _show_light_panel(ldr_data):
    """Zeigt das Licht-Panel mit verarbeiteten LDR-Daten"""
    st.subheader("💡 Aktuelle Lichtstärke")
    
    if ldr_data and ldr_data.get("light") is not None:
        light = ldr_data.get("light", 0.0)
        timestamp = ldr_data.get("timestamp", "")
        message_count = ldr_data.get("message_count", 0)
        
        # Licht-Gauge
        st.metric("Lichtstärke", f"{light:.1f} Lux")
        
        # Licht-Visualisierung (normalisiert auf 0-1000 Lux)
        normalized_light = max(0, min(1, light / 1000.0))
        st.progress(normalized_light)
        
        # Zeitstempel
        if timestamp:
            try:
                if isinstance(timestamp, str):
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    formatted_time = dt.strftime("%H:%M:%S")
                else:
                    formatted_time = str(timestamp)
            except:
                formatted_time = str(timestamp)
            st.caption(f"{formatted_time} ({message_count} Nachrichten)")
            
    else:
        st.warning("⚠️ Keine LDR-Daten verfügbar")


def _show_camera_control_panel(ccu_gateway: CcuGateway):
    """Zeigt das Kamera-Steuerungs-Panel"""
    st.subheader("📸 Kamera-Steuerung")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("⬆️ Hoch", use_container_width=True, key="camera_up"):
            _move_camera(ccu_gateway, "relmove_up", 10)
    
    with col2:
        if st.button("📷 Foto", use_container_width=True, key="camera_photo"):
            _take_camera_photo(ccu_gateway)
    
    with col3:
        if st.button("⬇️ Runter", use_container_width=True, key="camera_down"):
            _move_camera(ccu_gateway, "relmove_down", 10)


def _show_camera_image_panel(cam_data):
    """Zeigt das Kamera-Bild-Panel mit Base64-dekodierten Bildern"""
    st.subheader("📸 Kamera-Bild")
    
    if cam_data and cam_data.get("image_data"):
        image_data = cam_data.get("image_data", "")
        timestamp = cam_data.get("timestamp", "")
        message_count = cam_data.get("message_count", 0)
        
        if image_data:
            _display_base64_image(image_data, timestamp, message_count)
        else:
            st.warning("⚠️ Keine Kamera-Bilddaten verfügbar")
    else:
        st.info("📸 Kamera-Bild wird geladen...")
        
        # Placeholder-Bild
        placeholder_url = "https://via.placeholder.com/400x300/CCCCCC/666666?text=Kamera-Bild+Placeholder"
        st.image(placeholder_url, caption="Kamera-Bild (Placeholder)", use_container_width=True)


def _display_base64_image(base64_data: str, timestamp: str, message_count: int):
    """Zeigt Base64-dekodiertes Bild in Streamlit"""
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
        
        # Bild in Streamlit anzeigen
        st.image(
            image_bytes,
            caption=f"📸 Kamera-Bild ({image_format.upper()}) - {timestamp} ({message_count} Nachrichten)",
            use_container_width=True
        )
        
        # Bild-Informationen anzeigen
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Bildformat", image_format.upper())
        with col2:
            st.metric("Nachrichten", message_count)
        with col3:
            if timestamp:
                try:
                    if isinstance(timestamp, str):
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        formatted_time = dt.strftime("%H:%M:%S")
                    else:
                        formatted_time = str(timestamp)
                except:
                    formatted_time = str(timestamp)
                st.metric("Zeitstempel", formatted_time)
        
    except Exception as e:
        logger.error(f"❌ Fehler beim Dekodieren des Kamera-Bildes: {e}")
        st.error(f"❌ Fehler beim Dekodieren des Kamera-Bildes: {e}")


def _move_camera(ccu_gateway: CcuGateway, command: str, degree: int):
    """Bewegt die Kamera um angegebene Grad"""
    try:
        # Kamera-Befehl über Gateway senden (Gateway-Pattern)
        topic = "/j1/txt/1/o/ptu"
        payload = {
            "ts": datetime.now().isoformat() + "Z",
            "cmd": command,
            "degree": degree
        }
        
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


def _take_camera_photo(ccu_gateway: CcuGateway):
    """Macht ein Foto mit der Kamera"""
    try:
        # Kamera-Foto-Befehl über Gateway senden (Gateway-Pattern)
        topic = "/j1/txt/1/o/ptu"
        payload = {
            "ts": datetime.now().isoformat() + "Z",
            "cmd": "photo"
        }
        
        # Send via Gateway (Gateway-Pattern)
        success = ccu_gateway.publish_message(topic, payload)
        
        if success:
            st.success("✅ Kamera-Foto ausgelöst")
            logger.info("📸 Camera photo triggered")
        else:
            st.error("❌ Fehler beim Auslösen des Kamera-Fotos")
            
    except Exception as e:
        logger.error(f"❌ Fehler beim Auslösen des Kamera-Fotos: {e}")
        st.error(f"❌ Fehler beim Auslösen des Kamera-Fotos: {e}")


def _refresh_sensor_data():
    """Refresh sensor data - UI Refresh Pattern"""
    print("🔍 UI DEBUG: _refresh_sensor_data() wird ausgeführt")
    logger.info("🔄 Refreshing sensor data")
    try:
        # UI Refresh Pattern (statt st.rerun())
        request_refresh()
        st.success("✅ Sensor data refreshed!")
        logger.info("✅ Sensor data refreshed successfully")
        print("🔍 UI DEBUG: Sensor data refresh abgeschlossen")
    except Exception as e:
        logger.error(f"❌ Failed to refresh sensor data: {e}")
        st.error(f"❌ Failed to refresh sensor data: {e}")
        print(f"🔍 UI DEBUG: Error beim Refresh: {e}")


def _show_sensor_statistics(ccu_gateway: CcuGateway):
    """Show sensor statistics"""
    try:
        sensor_manager = get_ccu_sensor_manager()
        sensor_data = sensor_manager.get_sensor_data()  # Liest aus State-Holder
        stats = sensor_manager.get_sensor_statistics(sensor_data)
        
        st.info("📊 **Sensor Statistics**")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
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
    try:
        # Clear via Gateway (Gateway-Pattern)
        ccu_gateway.clear_message_history()
        st.success("✅ Sensor message history cleared!")
        logger.info("✅ Sensor message history cleared successfully")
    except Exception as e:
        logger.error(f"❌ Failed to clear sensor history: {e}")
        st.error(f"❌ Failed to clear sensor history: {e}")
