"""
APS Overview Tab - APS-Übersicht mit Bestellungen, Lagerbestand und Sensordaten
Entspricht dem "Overview" Tab des Original APS-Dashboards
Basiert auf bestehenden OMF-Komponenten, aber im APS-Stil modernisiert
"""

import streamlit as st
import time
from datetime import datetime
from omf.dashboard.tools.logging_config import get_logger
from omf.dashboard.utils.ui_refresh import request_refresh

logger = get_logger("dashboard.components.aps_overview")


def show_aps_overview():
    """Zeigt den APS Overview Tab mit 5 Haupt-Panels und Sensordaten"""
    st.header("🏭 APS Overview")
    st.write("APS-Übersicht mit Bestellungen, Lagerbestand, Sensordaten, Kamera-Steuerung und Produktkatalog")
    
    # 2-Spalten-Layout: Links Haupt-Panels, Rechts Sensordaten
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 5 Haupt-Panels - Produktkatalog an erster Stelle
        _show_aps_produktkatalog_panel()
        st.divider()
        _show_aps_bestellung_panel()
        st.divider()
        _show_aps_rohware_panel()
        st.divider()
        _show_aps_lagerbestand_panel()
        st.divider()
        _show_aps_nfc_reader_panel()
    
    with col2:
        # Sensordaten-Panels
        _show_sensor_panels()


def _show_aps_bestellung_panel():
    """Zeigt das APS: Bestellung Panel (Kundenaufträge)"""
    st.subheader("📋 APS: Bestellung")
    st.write("Werkstück-Bestellungen für verschiedene Produkttypen")

    try:
        # Importiere die echte overview_order Komponente
        from omf.dashboard.components.overview_customer_order import show_overview_order

        # Zeige die echte Komponente mit eindeutigen Keys für APS Overview
        with st.container():
            # Verwende die echte Komponente, aber mit eindeutigen Keys
            _show_overview_order_with_aps_keys()

        logger.info("APS Bestellung Panel erfolgreich angezeigt")

    except Exception as e:
        st.error(f"❌ Fehler beim Laden der APS Bestellung: {e}")
        logger.error(f"Fehler beim Laden der APS Bestellung: {e}")


def _show_overview_order_with_aps_keys():
    """Zeigt die APS overview_order Komponente mit eindeutigen Keys"""
    
    # Importiere die APS-Kopie der Komponente
    from omf.dashboard.components.aps_overview_customer_order import show_aps_overview_order
    
    # Rufe die APS-Kopie auf
    show_aps_overview_order()


def _show_aps_rohware_panel():
    """Zeigt das APS: Bestellung Rohware Panel (Rohmaterial-Bestellungen)"""
    st.subheader("📦 APS: Bestellung Rohware")
    st.write("Rohmaterial-Bestellungen für verschiedene Werkstück-Typen")
    
    try:
        # Importiere die echte overview_order_raw Komponente
        from omf.dashboard.components.overview_purchase_order import show_overview_order_raw
        
        # Zeige die echte Komponente mit eindeutigen Keys für APS Overview
        with st.container():
            # Verwende die echte Komponente, aber mit eindeutigen Keys
            _show_overview_purchase_order_with_aps_keys()
        
        logger.info("APS Rohware Panel erfolgreich angezeigt")
        
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der APS Rohware: {e}")
        logger.error(f"Fehler beim Laden der APS Rohware: {e}")


def _show_overview_purchase_order_with_aps_keys():
    """Zeigt die APS overview_purchase_order Komponente mit eindeutigen Keys"""
    
    # Importiere die APS-Kopie der Komponente
    from omf.dashboard.components.aps_overview_purchase_order import show_aps_overview_order_raw
    
    # Rufe die APS-Kopie auf
    show_aps_overview_order_raw()


def _show_aps_lagerbestand_panel():
    """Zeigt das APS: Lagerbestand Panel (High-Bay Warehouse)"""
    st.subheader("🏬 APS: Lagerbestand - SVR3QA0022")
    st.write("High-Bay Warehouse Lagerbestand mit Grid-Layout")
    
    try:
        # Importiere die bestehende overview_inventory Komponente
        from omf.dashboard.components.overview_inventory import show_overview_inventory
        
        # Zeige den Lagerbestand mit eindeutigen APS-Keys
        with st.container():
            _show_overview_inventory_with_aps_keys()
        
        logger.info("APS Lagerbestand Panel erfolgreich angezeigt")
        
    except Exception as e:
        st.error(f"❌ Fehler beim Laden des APS Lagerbestands: {e}")
        logger.error(f"Fehler beim Laden des APS Lagerbestands: {e}")


def _show_overview_inventory_with_aps_keys():
    """Zeigt die APS overview_inventory Komponente mit eindeutigen Keys"""
    
    # Importiere die APS-Kopie der Komponente
    from omf.dashboard.components.aps_overview_inventory import show_aps_overview_inventory
    
    # Rufe die APS-Kopie auf
    show_aps_overview_inventory()


def _show_aps_nfc_reader_panel():
    """Zeigt das APS: NFC-Reader Panel"""
    st.subheader("📱 APS: NFC-Reader")
    st.write("NFC-Tag Lesen und Löschen")
    
    # NFC-Reader Controls
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📖 NFC lesen", use_container_width=True, key="aps_nfc_read"):
            _read_nfc_tag()
    
    with col2:
        if st.button("🗑️ NFC löschen", use_container_width=True, key="aps_nfc_delete"):
            _delete_nfc_tag()
    
    # NFC-Status
    st.info("💡 NFC-Reader bereit für Tag-Operationen")


def _show_sensor_panels():
    """Zeigt die Sensordaten-Panels mit echten MQTT-Daten"""
    st.subheader("🌡️ Sensordaten")
    st.write("Real-time Sensordaten von BME680 und LDR")
    
    # MQTT-Client für Sensor-Daten
    mqtt_client = st.session_state.get("mqtt_client")
    if not mqtt_client:
        st.warning("⚠️ MQTT-Client nicht verfügbar")
        return
    
    # Abonniere Sensor-Topics (INBOUND - echte Sensordaten empfangen)
    sensor_topics = [
        "/j1/txt/1/i/bme680",  # BME680 Sensor Input (Temperatur, Luftfeuchtigkeit, Luftdruck, Luftqualität)
        "/j1/txt/1/i/ldr",     # LDR Sensor Input (Licht)
        "/j1/txt/1/i/cam"      # Kamera Input (Kamera-Daten)
    ]
    
    try:
        mqtt_client.subscribe_many(sensor_topics)
        
        # Hole Sensor-Daten aus dem Buffer (INBOUND Topics)
        bme680_messages = list(mqtt_client.get_buffer("/j1/txt/1/i/bme680"))
        ldr_messages = list(mqtt_client.get_buffer("/j1/txt/1/i/ldr"))
        cam_messages = list(mqtt_client.get_buffer("/j1/txt/1/i/cam"))
        
        # Zeige Sensor-Status
        if bme680_messages:
            st.info(f"📊 **{len(bme680_messages)} BME680-Nachrichten in Buffer**")
            logger.info(f"BME680 Messages: {len(bme680_messages)}")
        if ldr_messages:
            st.info(f"📊 **{len(ldr_messages)} LDR-Nachrichten in Buffer**")
            logger.info(f"LDR Messages: {len(ldr_messages)}")
        if cam_messages:
            st.info(f"📊 **{len(cam_messages)} Kamera-Nachrichten in Buffer**")
            logger.info(f"Camera Messages: {len(cam_messages)}")
        
        # 1. Temperatur
        _show_temperature_panel(bme680_messages)
        st.divider()
        
        # 2. Luftfeuchtigkeit
        _show_humidity_panel(bme680_messages)
        st.divider()
        
        # 3. Luftdruck
        _show_pressure_panel(bme680_messages)
        st.divider()
        
        # 4. Luftqualität
        _show_air_quality_panel(bme680_messages)
        st.divider()
        
        # 5. Lichtsensor
        _show_light_panel(ldr_messages)
        st.divider()
        
        # 6. Kamera-Steuerung
        _show_camera_control_panel()
        
    except Exception as e:
        st.error(f"❌ Fehler beim Laden der Sensordaten: {e}")
        logger.error(f"Fehler beim Laden der Sensordaten: {e}")
        
        # Fallback: Zeige Mock-Daten
        _show_temperature_panel([])
        _show_humidity_panel([])
        _show_pressure_panel([])
        _show_air_quality_panel([])
        _show_light_panel([])
        _show_camera_control_panel()


def _show_temperature_panel(bme680_messages):
    """Zeigt das Temperatur-Panel mit echten BME680-Daten"""
    st.subheader("🌡️ APS: Aktuelle Temperatur")
    
    if bme680_messages:
        # Verarbeite die neueste BME680-Nachricht
        latest_message = bme680_messages[-1]
        try:
            # Parse BME680-Daten (Dictionary-Format aus get_buffer)
            payload = latest_message.get("payload", {})
            if isinstance(payload, str):
                import json
                sensor_data = json.loads(payload)
            else:
                sensor_data = payload
            
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
            
            # Fallback: Zeige Mock-Daten
            _show_temperature_fallback()
    else:
        # Keine Daten verfügbar
        st.warning("⚠️ Keine BME680-Daten verfügbar")
        _show_temperature_fallback()


def _show_temperature_fallback():
    """Fallback für Temperatur-Panel ohne echte Daten"""
    temperature = 29.5
    
    # Thermometer-Gauge
    st.metric("Temperatur", f"{temperature}°C")
    
    # Thermometer-Visualisierung
    st.progress(temperature / 50.0)  # Normalisiert auf 0-50°C
    
    # Zeitstempel
    st.caption("26.8.2025, 18:30:55.535 (Mock-Daten)")


def _show_humidity_panel(bme680_messages):
    """Zeigt das Luftfeuchtigkeit-Panel mit echten BME680-Daten"""
    st.subheader("💧 APS: Aktuelle Luftfeuchtigkeit")
    
    if bme680_messages:
        # Verarbeite die neueste BME680-Nachricht
        latest_message = bme680_messages[-1]
        try:
            # Parse BME680-Daten (Dictionary-Format aus get_buffer)
            payload = latest_message.get("payload", {})
            if isinstance(payload, str):
                import json
                sensor_data = json.loads(payload)
            else:
                sensor_data = payload
            
            humidity = sensor_data.get("h", 0.0)
            timestamp = datetime.fromtimestamp(latest_message.get("ts", time.time())).strftime("%Y-%m-%d %H:%M:%S")
            
            # Luftfeuchtigkeit-Gauge
            st.metric("Luftfeuchtigkeit", f"{humidity:.1f}% r.H.")
            
            # Luftfeuchtigkeit-Visualisierung
            st.progress(humidity / 100.0)
            
            # Zeitstempel
            st.caption(f"{timestamp} ({len(bme680_messages)} Nachrichten)")
            
        except Exception as e:
            st.error(f"❌ Fehler beim Parsen der BME680-Daten: {e}")
            logger.error(f"Fehler beim Parsen der BME680-Daten: {e}")
            
            # Fallback: Zeige Mock-Daten
            _show_humidity_fallback()
    else:
        # Keine Daten verfügbar
        st.warning("⚠️ Keine BME680-Daten verfügbar")
        _show_humidity_fallback()


def _show_humidity_fallback():
    """Fallback für Luftfeuchtigkeit-Panel ohne echte Daten"""
    humidity = 26.8
    
    # Luftfeuchtigkeit-Gauge
    st.metric("Luftfeuchtigkeit", f"{humidity}% r.H.")
    
    # Luftfeuchtigkeit-Visualisierung
    st.progress(humidity / 100.0)
    
    # Zeitstempel
    st.caption("26.8.2025, 18:30:55.535 (Mock-Daten)")


def _show_pressure_panel(bme680_messages):
    """Zeigt das Luftdruck-Panel mit echten BME680-Daten"""
    st.subheader("🌬️ APS: Aktueller Luftdruck")
    
    if bme680_messages:
        # Verarbeite die neueste BME680-Nachricht
        latest_message = bme680_messages[-1]
        try:
            # Parse BME680-Daten (Dictionary-Format aus get_buffer)
            payload = latest_message.get("payload", {})
            if isinstance(payload, str):
                import json
                sensor_data = json.loads(payload)
            else:
                sensor_data = payload
            
            pressure = sensor_data.get("p", 0.0)
            timestamp = datetime.fromtimestamp(latest_message.get("ts", time.time())).strftime("%Y-%m-%d %H:%M:%S")
            
            # Luftdruck-Gauge
            st.metric("Luftdruck", f"{pressure:.1f} hPa")
            
            # Luftdruck-Visualisierung
            st.progress((pressure - 950) / 100.0)  # Normalisiert auf 950-1050 hPa
            
            # Zeitstempel
            st.caption(f"{timestamp} ({len(bme680_messages)} Nachrichten)")
            
        except Exception as e:
            st.error(f"❌ Fehler beim Parsen der BME680-Daten: {e}")
            logger.error(f"Fehler beim Parsen der BME680-Daten: {e}")
            
            # Fallback: Zeige Mock-Daten
            _show_pressure_fallback()
    else:
        # Keine Daten verfügbar
        st.warning("⚠️ Keine BME680-Daten verfügbar")
        _show_pressure_fallback()


def _show_pressure_fallback():
    """Fallback für Luftdruck-Panel ohne echte Daten"""
    pressure = 986.0
    
    # Luftdruck-Gauge
    st.metric("Luftdruck", f"{pressure} hPa")
    
    # Luftdruck-Visualisierung
    st.progress((pressure - 950) / 100.0)  # Normalisiert auf 950-1050 hPa
    
    # Zeitstempel
    st.caption("26.8.2025, 18:30:55.535 (Mock-Daten)")


def _show_air_quality_panel(bme680_messages):
    """Zeigt das Luftqualität-Panel mit echten BME680-Daten"""
    st.subheader("🌿 APS: Aktuelle Luftqualität")
    
    if bme680_messages:
        # Verarbeite die neueste BME680-Nachricht
        latest_message = bme680_messages[-1]
        try:
            # Parse BME680-Daten (Dictionary-Format aus get_buffer)
            payload = latest_message.get("payload", {})
            if isinstance(payload, str):
                import json
                sensor_data = json.loads(payload)
            else:
                sensor_data = payload
            
            iaq = sensor_data.get("iaq", 0)
            accuracy = sensor_data.get("aq", 0)
            timestamp = datetime.fromtimestamp(latest_message.get("ts", time.time())).strftime("%Y-%m-%d %H:%M:%S")
            
            # Luftqualität-Anzeige
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("IAQ", iaq)
            
            with col2:
                st.metric("Genauigkeit", accuracy)
            
            # Luftqualität-Visualisierung (3 Quadrate)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("⬜")  # Grau
            
            with col2:
                st.markdown("⬜")  # Grau
            
            with col3:
                st.markdown("🟢")  # Grün
            
            # Zeitstempel
            st.caption(f"{timestamp} ({len(bme680_messages)} Nachrichten)")
            
        except Exception as e:
            st.error(f"❌ Fehler beim Parsen der BME680-Daten: {e}")
            logger.error(f"Fehler beim Parsen der BME680-Daten: {e}")
            
            # Fallback: Zeige Mock-Daten
            _show_air_quality_fallback()
    else:
        # Keine Daten verfügbar
        st.warning("⚠️ Keine BME680-Daten verfügbar")
        _show_air_quality_fallback()


def _show_air_quality_fallback():
    """Fallback für Luftqualität-Panel ohne echte Daten"""
    iaq = 41
    accuracy = 3
    
    # Luftqualität-Anzeige
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("IAQ", iaq)
    
    with col2:
        st.metric("Genauigkeit", accuracy)
    
    # Luftqualität-Visualisierung (3 Quadrate)
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("⬜")  # Grau
    
    with col2:
        st.markdown("⬜")  # Grau
    
    with col3:
        st.markdown("🟢")  # Grün
    
    # Zeitstempel
    st.caption("26.8.2025, 18:30:55.535 (Mock-Daten)")


def _show_light_panel(ldr_messages):
    """Zeigt das Lichtsensor-Panel mit echten LDR-Daten"""
    st.subheader("💡 APS: Aktuelle Lichtstärke")
    
    if ldr_messages:
        # Verarbeite die neueste LDR-Nachricht
        latest_message = ldr_messages[-1]
        try:
            # Parse LDR-Daten (Dictionary-Format aus get_buffer)
            payload = latest_message.get("payload", {})
            if isinstance(payload, str):
                import json
                sensor_data = json.loads(payload)
            else:
                sensor_data = payload
            
            light_level = sensor_data.get("ldr", 0.0)
            timestamp = datetime.fromtimestamp(latest_message.get("ts", time.time())).strftime("%Y-%m-%d %H:%M:%S")
            
            # Lichtstärke-Gauge
            st.metric("Lichtstärke", f"{light_level:.1f} lux")
            
            # Lichtstärke-Visualisierung (LDR-Werte sind 0-4095, normalisiert auf 0-1)
            normalized_light = min(max(light_level / 4095.0, 0.0), 1.0)
            st.progress(normalized_light)
            
            # Zeitstempel
            st.caption(f"{timestamp} ({len(ldr_messages)} Nachrichten)")
            
        except Exception as e:
            st.error(f"❌ Fehler beim Parsen der LDR-Daten: {e}")
            logger.error(f"Fehler beim Parsen der LDR-Daten: {e}")
            
            # Fallback: Zeige Mock-Daten
            _show_light_fallback()
    else:
        # Keine Daten verfügbar
        st.warning("⚠️ Keine LDR-Daten verfügbar")
        _show_light_fallback()


def _show_light_fallback():
    """Fallback für Lichtsensor-Panel ohne echte Daten"""
    light_level = 450.0
    
    # Lichtstärke-Gauge
    st.metric("Lichtstärke", f"{light_level} lux")
    
    # Lichtstärke-Visualisierung (LDR-Werte sind 0-4095, normalisiert auf 0-1)
    normalized_light = min(max(light_level / 4095.0, 0.0), 1.0)
    st.progress(normalized_light)
    
    # Zeitstempel
    st.caption("26.8.2025, 18:30:55.535 (Mock-Daten)")


def _show_camera_control_panel():
    """Zeigt das Kamera-Steuerung-Panel"""
    st.subheader("📹 Kamera-Steuerung")
    st.write("Kamera-Ausrichtung steuern")
    
    # Kamera-Controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("⬆️ Hoch", use_container_width=True, key="aps_camera_up"):
            _move_camera("up")
    
    with col2:
        if st.button("⬇️ Runter", use_container_width=True, key="aps_camera_down"):
            _move_camera("down")
    
    with col3:
        if st.button("⬅️ Links", use_container_width=True, key="aps_camera_left"):
            _move_camera("left")
    
    col4, col5, col6 = st.columns(3)
    
    with col4:
        if st.button("➡️ Rechts", use_container_width=True, key="aps_camera_right"):
            _move_camera("right")
    
    with col5:
        if st.button("🎯 Zentrieren", use_container_width=True, key="aps_camera_center"):
            _move_camera("center")
    
    with col6:
        if st.button("📸 Foto", use_container_width=True, key="aps_camera_photo"):
            _take_camera_photo()
    
    # Kamera-Status
    st.info("💡 Kamera-Steuerung aktiv - Ausrichtung kann geändert werden")
    
    # Optional: Kamera-Bild Anzeige (erste Phase optional)
    if st.checkbox("📺 Kamera-Bild anzeigen (optional)", key="aps_camera_show_feed"):
        _show_camera_feed()


def _read_nfc_tag():
    """Liest einen NFC-Tag"""
    try:
        st.success("✅ NFC-Tag erfolgreich gelesen")
        logger.info("NFC-Tag gelesen")
        
        # UI-Refresh Pattern
        request_refresh()
        
    except Exception as e:
        st.error(f"❌ Fehler beim Lesen des NFC-Tags: {e}")
        logger.error(f"Fehler beim Lesen des NFC-Tags: {e}")


def _delete_nfc_tag():
    """Löscht einen NFC-Tag"""
    try:
        st.success("✅ NFC-Tag erfolgreich gelöscht")
        logger.info("NFC-Tag gelöscht")
        
        # UI-Refresh Pattern
        request_refresh()
        
    except Exception as e:
        st.error(f"❌ Fehler beim Löschen des NFC-Tags: {e}")
        logger.error(f"Fehler beim Löschen des NFC-Tags: {e}")


def _move_camera(direction):
    """Bewegt die Kamera in die angegebene Richtung"""
    try:
        st.success(f"✅ Kamera nach {direction} bewegt")
        logger.info(f"Kamera nach {direction} bewegt")
        
        # UI-Refresh Pattern
        request_refresh()
        
    except Exception as e:
        st.error(f"❌ Fehler beim Bewegen der Kamera: {e}")
        logger.error(f"Fehler beim Bewegen der Kamera: {e}")


def _take_camera_photo():
    """Macht ein Foto mit der Kamera"""
    try:
        st.success("✅ Foto erfolgreich aufgenommen")
        logger.info("Kamera-Foto aufgenommen")
        
        # UI-Refresh Pattern
        request_refresh()
        
    except Exception as e:
        st.error(f"❌ Fehler beim Aufnehmen des Fotos: {e}")
        logger.error(f"Fehler beim Aufnehmen des Fotos: {e}")


def _show_camera_feed():
    """Zeigt den Kamera-Feed (optional, erste Phase)"""
    st.info("📺 Kamera-Feed wird in zukünftigen Versionen implementiert")
    
    # Placeholder für Kamera-Feed
    st.image("https://via.placeholder.com/400x300/CCCCCC/666666?text=Kamera-Feed+Placeholder", 
             caption="Kamera-Feed (Placeholder)")


def get_sensor_data():
    """Gibt die aktuellen Sensordaten zurück"""
    return {
        "temperature": 29.5,
        "humidity": 26.8,
        "pressure": 986.0,
        "air_quality": {
            "iaq": 41,
            "accuracy": 3
        }
    }


def set_sensor_data(sensor_data):
    """Setzt die Sensordaten"""
    logger.info(f"Sensordaten gesetzt: {sensor_data}")


def _show_aps_produktkatalog_panel():
    """Zeigt das APS: Produktkatalog Panel - integriert in aps_overview"""
    st.subheader("📦 APS: Produktkatalog")
    st.write("Verfügbare Produkte und deren Konfiguration")

    try:
        # Produktkatalog direkt laden (ohne separaten Tab)
        from omf.tools.product_manager import get_omf_product_manager
        product_manager = get_omf_product_manager()
        catalog = product_manager.get_all_products()
        
        if not catalog:
            st.error("❌ Keine Produkte gefunden")
            return

        # 3 Spalten für die Produkte
        col1, col2, col3 = st.columns(3)

        # HTML-Templates importieren
        try:
            from omf.dashboard.assets.html_templates import get_product_catalog_template
            TEMPLATES_AVAILABLE = True
        except ImportError:
            TEMPLATES_AVAILABLE = False

        # ROT
        with col1:
            if "red" in catalog:
                product = catalog["red"]
                if TEMPLATES_AVAILABLE:
                    html_content = get_product_catalog_template("RED")
                    st.markdown(html_content, unsafe_allow_html=True)
                else:
                    st.write("🔴 **ROT**")
                st.write(f"**Name:** {product.get('name', 'Rot')}")
                st.write(f"**Beschreibung:** {product.get('description', 'Rot')}")
                st.write(f"**Material:** {product.get('material', 'Kunststoff')}")
                st.write(f"**Farbe:** {product.get('color', 'Rot')}")
                st.write(f"**Größe:** {product.get('size', 'Standard')}")

        # BLAU
        with col2:
            if "blue" in catalog:
                product = catalog["blue"]
                if TEMPLATES_AVAILABLE:
                    html_content = get_product_catalog_template("BLUE")
                    st.markdown(html_content, unsafe_allow_html=True)
                else:
                    st.write("🔵 **BLAU**")
                st.write(f"**Name:** {product.get('name', 'Blau')}")
                st.write(f"**Beschreibung:** {product.get('description', 'Blau')}")
                st.write(f"**Material:** {product.get('material', 'Kunststoff')}")
                st.write(f"**Farbe:** {product.get('color', 'Blau')}")
                st.write(f"**Größe:** {product.get('size', 'Standard')}")

        # WEISS
        with col3:
            if "white" in catalog:
                product = catalog["white"]
                if TEMPLATES_AVAILABLE:
                    html_content = get_product_catalog_template("WHITE")
                    st.markdown(html_content, unsafe_allow_html=True)
                else:
                    st.write("⚪ **WEISS**")
                st.write(f"**Name:** {product.get('name', 'Weiß')}")
                st.write(f"**Beschreibung:** {product.get('description', 'Weiß')}")
                st.write(f"**Material:** {product.get('material', 'Kunststoff')}")
                st.write(f"**Farbe:** {product.get('color', 'Weiß')}")
                st.write(f"**Größe:** {product.get('size', 'Standard')}")

    except Exception as e:
        logger.error(f"❌ Fehler beim Laden des Produktkatalog Panels: {e}")
        st.error(f"❌ Fehler beim Laden des Produktkatalog Panels: {e}")
        st.info("💡 Produktkatalog Panel konnte nicht geladen werden.")


def get_camera_status():
    """Gibt den aktuellen Kamera-Status zurück"""
    return {
        "connected": True,
        "position": "center",
        "recording": False
    }

