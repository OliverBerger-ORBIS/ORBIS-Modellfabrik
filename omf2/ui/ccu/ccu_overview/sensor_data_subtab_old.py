#!/usr/bin/env python3
"""
CCU Overview - Sensor Data Subtab
Real-time Sensordaten von BME680 und LDR mit Kamera-Steuerung
Basiert auf _show_sensor_panels() aus omf/dashboard/components/operator/aps_overview.py
"""

import streamlit as st
import time
from datetime import datetime
from omf2.ccu.ccu_gateway import CcuGateway
from omf2.ccu.sensor_manager import get_ccu_sensor_manager
from omf2.common.logger import get_logger
from omf2.ui.common.symbols import UISymbols

logger = get_logger(__name__)


def render_sensor_data_subtab(ccu_gateway: CcuGateway, registry_manager):
    """Render Sensor Data Subtab
    
    Args:
        ccu_gateway: CcuGateway Instanz (Gateway-Pattern)
        registry_manager: RegistryManager Instanz (Singleton)
    """
    logger.info("📊 Rendering Sensor Data Subtab")
    try:
        # Use UISymbols for consistent icon usage
        st.subheader(f"{UISymbols.get_functional_icon('sensor_data')} Sensor Data")
        st.markdown("Real-time Sensordaten von BME680 und LDR")
        
        # Refresh Button (wie in ccu_modules)
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if st.button(f"{UISymbols.get_status_icon('refresh')} Refresh Data", use_container_width=True, key="sensor_refresh_data"):
                logger.info("🔄 DEBUG: Refresh Sensor Data Button clicked")
                _refresh_sensor_data(ccu_gateway)
        
        with col2:
            if st.button(f"{UISymbols.get_functional_icon('dashboard')} Show Statistics", use_container_width=True, key="sensor_show_statistics"):
                _show_sensor_statistics(ccu_gateway)
        
        with col3:
            if st.button(f"{UISymbols.get_status_icon('clear')} Clear History", use_container_width=True, key="sensor_clear_history"):
                _clear_sensor_history(ccu_gateway)
        
        st.divider()
        
        # Show Sensor Panels (wie in omf/ aps_overview.py)
        _show_sensor_panels(ccu_gateway, registry_manager)
        
    except Exception as e:
        logger.error(f"❌ Sensor Data Subtab rendering error: {e}")
        st.error(f"❌ Sensor Data Subtab failed: {e}")
        st.info("💡 This component is currently under development.")


def _show_sensor_panels(ccu_gateway: CcuGateway, registry_manager):
    """Zeigt die Sensordaten-Panels mit echten MQTT-Daten - wie in omf/ aps_overview.py"""
    logger.info("🌡️ Rendering Sensor Panels")
    try:
        # Abonniere Sensor-Topics (INBOUND - echte Sensordaten empfangen)
        sensor_topics = [
            "/j1/txt/1/i/bme680",  # BME680 Sensor Input (Temperatur, Luftfeuchtigkeit, Luftdruck, Luftqualität)
            "/j1/txt/1/i/ldr",     # LDR Sensor Input (Licht)
            "/j1/txt/1/i/cam"      # Kamera Input (Kamera-Daten)
        ]
        
        # Sensor-Topics sind bereits in mqtt_clients.yml subscribed
        
        # Business Logic über SensorManager (Gateway-Pattern)
        sensor_manager = get_ccu_sensor_manager()
        sensor_data = sensor_manager.process_sensor_messages(ccu_gateway)
        
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
        
        # Fallback: Zeige Mock-Daten
        _show_temperature_panel({})
        _show_humidity_panel({})
        _show_pressure_panel({})
        _show_air_quality_panel({})
        _show_light_panel({})
        _show_camera_control_panel(ccu_gateway)


def _get_sensor_messages(ccu_gateway: CcuGateway, topic: str):
    """Holt Sensor-Messages über Gateway mit MessageManager Validator"""
    try:
        # Hole Messages über Gateway (MessageManager mit Validator)
        all_messages = ccu_gateway.get_all_message_buffers()
        messages = all_messages.get(topic, [])
        
        logger.info(f"🔍 DEBUG: Topic {topic} hat {len(messages)} Messages")
        if messages:
            logger.info(f"🔍 DEBUG: Erste Message: {messages[0]}")
        
        return messages
    except Exception as e:
        logger.error(f"❌ Fehler beim Laden der Sensor-Messages für {topic}: {e}")
        return []


def _show_temperature_panel(bme680_data):
    """Zeigt das Temperatur-Panel mit verarbeiteten BME680-Daten"""
    st.subheader("🌡️ Aktuelle Temperatur")
    
    if bme680_data and bme680_data.get("temperature") is not None:
        # Verarbeite die neueste BME680-Nachricht
        latest_message = bme680_messages[-1]
        try:
            # Parse BME680-Daten (String-Format aus MQTT)
            payload = latest_message.get("payload", "{}")
            if isinstance(payload, str):
                import json
                sensor_data = json.loads(payload)
            else:
                sensor_data = payload
            
            logger.info(f"🔍 DEBUG: Parsed sensor_data: {sensor_data}")
            
            temperature = sensor_data.get("t", 0.0)
            timestamp = datetime.fromtimestamp(latest_message.get("ts", time.time())).strftime("%Y-%m-%d %H:%M:%S")
            
            # Thermometer-Gauge
            st.metric("Temperatur", f"{temperature:.1f}°C")
            
            # Thermometer-Visualisierung
            st.progress(temperature / 50.0)  # Normalisiert auf 0-50°C
            
            # Zeitstempel
            st.caption(f"{timestamp} ({len(bme680_messages)} Nachrichten)")
            
        except Exception as e:
            st.error(f"❌ Fehler beim Parsen der BME680-Daten: {e}")
            logger.error(f"Fehler beim Parsen der BME680-Daten: {e}")
            _show_temperature_fallback()
    else:
        # Keine Daten verfügbar
        st.warning("⚠️ Keine BME680-Daten verfügbar")
        _show_temperature_fallback()


def _show_temperature_fallback():
    """Fallback für Temperatur-Panel ohne echte Daten"""
    st.metric("Temperatur", "22.3°C")
    st.progress(0.446)  # 22.3/50
    st.caption("Mock-Daten - keine echten Sensordaten verfügbar")


def _show_humidity_panel(bme680_messages):
    """Zeigt das Luftfeuchtigkeit-Panel mit echten BME680-Daten"""
    st.subheader("💧 Aktuelle Luftfeuchtigkeit")
    
    if bme680_messages:
        latest_message = bme680_messages[-1]
        try:
            payload = latest_message.get("payload", "{}")
            if isinstance(payload, str):
                import json
                sensor_data = json.loads(payload)
            else:
                sensor_data = payload
            
            humidity = sensor_data.get("h", 0.0)
            timestamp = datetime.fromtimestamp(latest_message.get("ts", time.time())).strftime("%Y-%m-%d %H:%M:%S")
            
            st.metric("Luftfeuchtigkeit", f"{humidity:.1f}%")
            st.progress(humidity / 100.0)  # Normalisiert auf 0-100%
            st.caption(f"{timestamp} ({len(bme680_messages)} Nachrichten)")
            
        except Exception as e:
            st.error(f"❌ Fehler beim Parsen der BME680-Daten: {e}")
            _show_humidity_fallback()
    else:
        st.warning("⚠️ Keine BME680-Daten verfügbar")
        _show_humidity_fallback()


def _show_humidity_fallback():
    """Fallback für Luftfeuchtigkeit-Panel ohne echte Daten"""
    st.metric("Luftfeuchtigkeit", "45.2%")
    st.progress(0.452)
    st.caption("Mock-Daten - keine echten Sensordaten verfügbar")


def _show_pressure_panel(bme680_messages):
    """Zeigt das Luftdruck-Panel mit echten BME680-Daten"""
    st.subheader("🌬️ Aktueller Luftdruck")
    
    if bme680_messages:
        latest_message = bme680_messages[-1]
        try:
            payload = latest_message.get("payload", "{}")
            if isinstance(payload, str):
                import json
                sensor_data = json.loads(payload)
            else:
                sensor_data = payload
            
            pressure = sensor_data.get("p", 0.0)
            timestamp = datetime.fromtimestamp(latest_message.get("ts", time.time())).strftime("%Y-%m-%d %H:%M:%S")
            
            st.metric("Luftdruck", f"{pressure:.1f} hPa")
            st.progress(pressure / 1100.0)  # Normalisiert auf 0-1100 hPa
            st.caption(f"{timestamp} ({len(bme680_messages)} Nachrichten)")
            
        except Exception as e:
            st.error(f"❌ Fehler beim Parsen der BME680-Daten: {e}")
            _show_pressure_fallback()
    else:
        st.warning("⚠️ Keine BME680-Daten verfügbar")
        _show_pressure_fallback()


def _show_pressure_fallback():
    """Fallback für Luftdruck-Panel ohne echte Daten"""
    st.metric("Luftdruck", "1013.2 hPa")
    st.progress(0.921)
    st.caption("Mock-Daten - keine echten Sensordaten verfügbar")


def _show_air_quality_panel(bme680_messages):
    """Zeigt das Luftqualität-Panel mit echten BME680-Daten"""
    st.subheader("🌪️ Aktuelle Luftqualität")
    
    if bme680_messages:
        latest_message = bme680_messages[-1]
        try:
            payload = latest_message.get("payload", "{}")
            if isinstance(payload, str):
                import json
                sensor_data = json.loads(payload)
            else:
                sensor_data = payload
            
            air_quality = sensor_data.get("gas", 0.0)
            timestamp = datetime.fromtimestamp(latest_message.get("ts", time.time())).strftime("%Y-%m-%d %H:%M:%S")
            
            st.metric("Luftqualität", f"{air_quality:.1f} ppm")
            st.progress(air_quality / 1000.0)  # Normalisiert auf 0-1000 ppm
            st.caption(f"{timestamp} ({len(bme680_messages)} Nachrichten)")
            
        except Exception as e:
            st.error(f"❌ Fehler beim Parsen der BME680-Daten: {e}")
            _show_air_quality_fallback()
    else:
        st.warning("⚠️ Keine BME680-Daten verfügbar")
        _show_air_quality_fallback()


def _show_air_quality_fallback():
    """Fallback für Luftqualität-Panel ohne echte Daten"""
    st.metric("Luftqualität", "156.7 ppm")
    st.progress(0.157)
    st.caption("Mock-Daten - keine echten Sensordaten verfügbar")


def _show_light_panel(ldr_messages):
    """Zeigt das Lichtsensor-Panel mit echten LDR-Daten"""
    st.subheader("💡 Aktuelle Lichtstärke")
    
    if ldr_messages:
        latest_message = ldr_messages[-1]
        try:
            payload = latest_message.get("payload", "{}")
            if isinstance(payload, str):
                import json
                sensor_data = json.loads(payload)
            else:
                sensor_data = payload
            
            light_level = sensor_data.get("ldr", 0.0)
            timestamp = datetime.fromtimestamp(latest_message.get("ts", time.time())).strftime("%Y-%m-%d %H:%M:%S")
            
            st.metric("Lichtstärke", f"{light_level:.1f} lux")
            normalized_light = min(max(light_level / 4095.0, 0.0), 1.0)
            st.progress(normalized_light)
            st.caption(f"{timestamp} ({len(ldr_messages)} Nachrichten)")
            
        except Exception as e:
            st.error(f"❌ Fehler beim Parsen der LDR-Daten: {e}")
            _show_light_fallback()
    else:
        st.warning("⚠️ Keine LDR-Daten verfügbar")
        _show_light_fallback()


def _show_light_fallback():
    """Fallback für Lichtsensor-Panel ohne echte Daten"""
    st.metric("Lichtstärke", "2048.5 lux")
    st.progress(0.5)
    st.caption("Mock-Daten - keine echten Sensordaten verfügbar")


def _show_camera_control_panel(ccu_gateway: CcuGateway):
    """Zeigt das Kamera-Steuerung-Panel mit Gateway Pattern"""
    st.subheader("📹 Kamera-Steuerung")
    st.write("Kamera-Ausrichtung steuern")
    
    # Kamera-Controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⬆️ Hoch", use_container_width=True, key="ccu_camera_up"):
            _move_camera(ccu_gateway, "up")
    
    with col2:
        if st.button("⬇️ Runter", use_container_width=True, key="ccu_camera_down"):
            _move_camera(ccu_gateway, "down")
    
    with col3:
        if st.button("⬅️ Links", use_container_width=True, key="ccu_camera_left"):
            _move_camera(ccu_gateway, "left")
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button("➡️ Rechts", use_container_width=True, key="ccu_camera_right"):
            _move_camera(ccu_gateway, "right")
    
    with col5:
        if st.button("🎯 Zentrieren", use_container_width=True, key="ccu_camera_center"):
            _move_camera(ccu_gateway, "center")
    
    with col6:
        if st.button("📸 Foto", use_container_width=True, key="ccu_camera_photo"):
            _take_camera_photo(ccu_gateway)
    
    # Kamera-Status
    st.info("💡 Kamera-Steuerung aktiv - Ausrichtung kann geändert werden")


def _move_camera(ccu_gateway: CcuGateway, direction: str):
    """Bewegt die Kamera in die angegebene Richtung über Gateway"""
    try:
        # Kamera-Steuerung über PTU Topic: /j1/txt/1/o/ptu
        topic = "/j1/txt/1/o/ptu"
        
        # Mapping der Richtungen zu PTU-Kommandos
        command_map = {
            "up": "relmove_up",
            "down": "relmove_down", 
            "left": "relmove_left",
            "right": "relmove_right",
            "center": "home"
        }
        
        cmd = command_map.get(direction)
        if not cmd:
            st.error(f"❌ Unbekannte Kamera-Richtung: {direction}")
            return
        
        # Erstelle PTU-Kommando-Payload (10° Schritte)
        payload = {
            "ts": datetime.now().isoformat() + "Z",
            "cmd": cmd
        }
        
        if cmd != "home":
            payload["degree"] = 10
        
        # Sende Kommando über Gateway (MessageManager mit Validator)
        success = ccu_gateway.publish_message(topic, payload, qos=1, retain=False)
        
        if success:
            st.success(f"✅ Kamera nach {direction} bewegt (10°)")
            logger.info(f"PTU-Kommando gesendet: {cmd} über Gateway")
        else:
            st.error(f"❌ Kamera-Kommando fehlgeschlagen: {cmd}")
            logger.error(f"PTU-Kommando fehlgeschlagen: {cmd}")
        
        # UI-Refresh Pattern
        from omf2.ui.utils.ui_refresh import request_refresh
        request_refresh()
        
    except Exception as e:
        st.error(f"❌ Fehler beim Bewegen der Kamera: {e}")
        logger.error(f"Fehler beim Bewegen der Kamera: {e}")


def _take_camera_photo(ccu_gateway: CcuGateway):
    """Macht ein Foto mit der Kamera über Gateway"""
    try:
        # Kamera-Foto über PTU Topic: /j1/txt/1/o/ptu
        topic = "/j1/txt/1/o/ptu"
        
        # Erstelle Foto-Kommando-Payload
        payload = {
            "ts": datetime.now().isoformat() + "Z",
            "cmd": "photo"
        }
        
        # Sende Kommando über Gateway (MessageManager mit Validator)
        success = ccu_gateway.publish_message(topic, payload, qos=1, retain=False)
        
        if success:
            st.success("✅ Foto-Kommando gesendet")
            logger.info("PTU-Foto-Kommando gesendet über Gateway")
        else:
            st.error("❌ Foto-Kommando fehlgeschlagen")
            logger.error("PTU-Foto-Kommando fehlgeschlagen")
        
        # UI-Refresh Pattern
        from omf2.ui.utils.ui_refresh import request_refresh
        request_refresh()
        
    except Exception as e:
        st.error(f"❌ Fehler beim Senden des Foto-Kommandos: {e}")
        logger.error(f"Fehler beim Senden des Foto-Kommandos: {e}")


def _refresh_sensor_data(ccu_gateway: CcuGateway):
    """Refresh sensor data from MQTT buffers (wie in ccu_modules)"""
    try:
        logger.info("🔄 Refreshing sensor data")
        
        # Get all sensor messages from Gateway
        all_messages = ccu_gateway.get_all_message_buffers()
        
        # Count messages per sensor
        bme680_count = len(all_messages.get("/j1/txt/1/i/bme680", []))
        ldr_count = len(all_messages.get("/j1/txt/1/i/ldr", []))
        cam_count = len(all_messages.get("/j1/txt/1/i/cam", []))
        
        st.success(f"✅ Sensor data refreshed! BME680: {bme680_count}, LDR: {ldr_count}, CAM: {cam_count}")
        logger.info(f"📊 Refreshed sensor data: BME680={bme680_count}, LDR={ldr_count}, CAM={cam_count}")
        
        # CRITICAL: Request UI refresh to update the display
        from omf2.ui.utils.ui_refresh import request_refresh
        request_refresh()
        
    except Exception as e:
        logger.error(f"❌ Failed to refresh sensor data: {e}")
        st.error(f"❌ Failed to refresh sensor data: {e}")


def _show_sensor_statistics(ccu_gateway: CcuGateway):
    """Show sensor statistics (wie in ccu_modules)"""
    try:
        logger.info("📊 Showing sensor statistics")
        
        # Get all sensor messages from Gateway
        all_messages = ccu_gateway.get_all_message_buffers()
        
        # Calculate statistics
        bme680_messages = all_messages.get("/j1/txt/1/i/bme680", [])
        ldr_messages = all_messages.get("/j1/txt/1/i/ldr", [])
        cam_messages = all_messages.get("/j1/txt/1/i/cam", [])
        
        total_messages = len(bme680_messages) + len(ldr_messages) + len(cam_messages)
        
        # Show statistics
        st.info(f"📊 **Sensor Statistics:**")
        st.write(f"• **BME680 Messages:** {len(bme680_messages)}")
        st.write(f"• **LDR Messages:** {len(ldr_messages)}")
        st.write(f"• **Camera Messages:** {len(cam_messages)}")
        st.write(f"• **Total Messages:** {total_messages}")
        
        logger.info(f"📊 Sensor statistics: Total={total_messages}")
        
    except Exception as e:
        logger.error(f"❌ Failed to show sensor statistics: {e}")
        st.error(f"❌ Failed to show sensor statistics: {e}")


def _clear_sensor_history(ccu_gateway: CcuGateway):
    """Clear sensor message history (wie in ccu_modules)"""
    try:
        logger.info("🗑️ Clearing sensor message history")
        
        # Clear message history via Gateway
        success = ccu_gateway.clear_message_history()
        
        if success:
            st.success("✅ Sensor message history cleared!")
            logger.info("🗑️ Sensor message history cleared")
        else:
            st.error("❌ Failed to clear sensor message history!")
            logger.error("❌ Failed to clear sensor message history")
        
        # CRITICAL: Request UI refresh to update the display
        from omf2.ui.utils.ui_refresh import request_refresh
        request_refresh()
        
    except Exception as e:
        logger.error(f"❌ Failed to clear sensor history: {e}")
        st.error(f"❌ Failed to clear sensor history: {e}")


def _show_camera_image_panel(cam_messages):
    """Zeigt das Kamera-Bild-Panel mit Base64-dekodierten Bildern"""
    st.subheader("📸 Kamera-Bild")
    
    if cam_messages:
        # Verarbeite die neueste Kamera-Nachricht
        latest_message = cam_messages[-1]
        try:
            # Parse Kamera-Daten (Dictionary-Format aus get_buffer)
            payload = latest_message.get("payload", "{}")
            if isinstance(payload, str):
                import json
                camera_data = json.loads(payload)
            else:
                camera_data = payload
            
            # Extrahiere Base64-Bilddaten
            image_data = camera_data.get("data", "")
            timestamp = datetime.fromtimestamp(latest_message.get("ts", time.time())).strftime("%Y-%m-%d %H:%M:%S")
            
            if image_data and image_data.startswith("data:image/"):
                # Base64-Bilddaten dekodieren und anzeigen
                _display_base64_image(image_data, timestamp, len(cam_messages))
            else:
                st.warning("⚠️ Keine gültigen Bilddaten in der Kamera-Nachricht")
                _show_camera_image_fallback()
            
        except Exception as e:
            st.error(f"❌ Fehler beim Parsen der Kamera-Daten: {e}")
            logger.error(f"Fehler beim Parsen der Kamera-Daten: {e}")
            _show_camera_image_fallback()
    else:
        # Keine Daten verfügbar
        st.warning("⚠️ Keine Kamera-Bilddaten verfügbar")
        _show_camera_image_fallback()


def _display_base64_image(image_data: str, timestamp: str, message_count: int):
    """Zeigt ein Base64-kodiertes Bild in der UI an"""
    try:
        # Base64-Header entfernen (data:image/jpeg;base64,)
        if "," in image_data:
            header, base64_data = image_data.split(",", 1)
            image_format = header.split("/")[1].split(";")[0]  # jpeg, png, etc.
        else:
            base64_data = image_data
            image_format = "jpeg"
        
        # Base64 dekodieren
        import base64
        image_bytes = base64.b64decode(base64_data)
        
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
            st.metric("Bildgröße", f"{len(image_bytes):,} bytes")
        with col3:
            st.metric("Nachrichten", message_count)
        
        logger.info(f"📸 Kamera-Bild angezeigt: {image_format}, {len(image_bytes)} bytes")
        
    except Exception as e:
        st.error(f"❌ Fehler beim Dekodieren des Kamera-Bildes: {e}")
        logger.error(f"Fehler beim Dekodieren des Kamera-Bildes: {e}")
        _show_camera_image_fallback()


def _show_camera_image_fallback():
    """Fallback für Kamera-Bild-Panel ohne echte Daten"""
    st.info("📸 **Kamera-Bild wird geladen...**")
    
    # Placeholder-Bild
    placeholder_url = "https://via.placeholder.com/400x300/CCCCCC/666666?text=Kamera-Bild+Placeholder"
    st.image(placeholder_url, caption="Kamera-Bild (Placeholder)", use_container_width=True)
    
    # Fallback-Informationen
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Bildformat", "JPEG")
    with col2:
        st.metric("Bildgröße", "0 bytes")
    with col3:
        st.metric("Nachrichten", "0")
    
    st.caption("Mock-Daten - keine echten Kamera-Bilddaten verfügbar")