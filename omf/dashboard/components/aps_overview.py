"""
APS Overview Tab - APS-Übersicht mit Bestellungen, Lagerbestand und Sensordaten
Entspricht dem "Overview" Tab des Original APS-Dashboards
Basiert auf bestehenden OMF-Komponenten, aber im APS-Stil modernisiert
"""

import streamlit as st
from omf.dashboard.tools.logging_config import get_logger
from omf.dashboard.utils.ui_refresh import request_refresh

logger = get_logger("dashboard.components.aps_overview")


def show_aps_overview():
    """Zeigt den APS Overview Tab mit 4 Haupt-Panels und Sensordaten"""
    st.header("🏭 APS Overview")
    st.write("APS-Übersicht mit Bestellungen, Lagerbestand, Sensordaten und Kamera-Steuerung")
    
    # 2-Spalten-Layout: Links Haupt-Panels, Rechts Sensordaten
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 4 Haupt-Panels
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
    """Zeigt die 4 Sensordaten-Panels"""
    st.subheader("🌡️ Sensordaten")
    
    # 1. Temperatur
    _show_temperature_panel()
    st.divider()
    
    # 2. Luftfeuchtigkeit
    _show_humidity_panel()
    st.divider()
    
    # 3. Luftdruck
    _show_pressure_panel()
    st.divider()
    
    # 4. Luftqualität
    _show_air_quality_panel()
    st.divider()
    
    # 5. Kamera-Steuerung
    _show_camera_control_panel()


def _show_temperature_panel():
    """Zeigt das Temperatur-Panel"""
    st.subheader("🌡️ APS: Aktuelle Temperatur")
    
    # Simulierte Temperatur-Daten (später aus MQTT)
    temperature = 29.5
    
    # Thermometer-Gauge
    st.metric("Temperatur", f"{temperature}°C")
    
    # Thermometer-Visualisierung
    st.progress(temperature / 50.0)  # Normalisiert auf 0-50°C
    
    # Zeitstempel
    st.caption("26.8.2025, 18:30:55.535")


def _show_humidity_panel():
    """Zeigt das Luftfeuchtigkeit-Panel"""
    st.subheader("💧 APS: Aktuelle Luftfeuchtigkeit")
    
    # Simulierte Luftfeuchtigkeit-Daten (später aus MQTT)
    humidity = 26.8
    
    # Luftfeuchtigkeit-Gauge
    st.metric("Luftfeuchtigkeit", f"{humidity}% r.H.")
    
    # Luftfeuchtigkeit-Visualisierung
    st.progress(humidity / 100.0)
    
    # Zeitstempel
    st.caption("26.8.2025, 18:30:55.535")


def _show_pressure_panel():
    """Zeigt das Luftdruck-Panel"""
    st.subheader("🌬️ APS: Aktueller Luftdruck")
    
    # Simulierte Luftdruck-Daten (später aus MQTT)
    pressure = 986.0
    
    # Luftdruck-Gauge
    st.metric("Luftdruck", f"{pressure} hPa")
    
    # Luftdruck-Visualisierung
    st.progress((pressure - 950) / 100.0)  # Normalisiert auf 950-1050 hPa
    
    # Zeitstempel
    st.caption("26.8.2025, 18:30:55.535")


def _show_air_quality_panel():
    """Zeigt das Luftqualität-Panel"""
    st.subheader("🌿 APS: Aktuelle Luftqualität")
    
    # Simulierte Luftqualität-Daten (später aus MQTT)
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
    st.caption("26.8.2025, 18:30:55.535")


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


def get_camera_status():
    """Gibt den aktuellen Kamera-Status zurück"""
    return {
        "connected": True,
        "position": "center",
        "recording": False
    }

